"""Event-driven monthly backtest sharing the production scoring, signal and accounting code."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.config import load_config
from src.model.scoring import (
    FAMILIES,
    ModelConfig,
    ScoreCache,
    combine_final,
    family_preset,
    ic_family_weights,
    quant_scores,
)
from src.portfolio.book import CostModel, Order, Portfolio, SimulatedBroker
from src.portfolio.signals import BUY, HOLD, SELL, Decision, SignalRules, decide
from src.portfolio.weights import target_weights


@dataclass
class JevFeatures:
    """Persisted Jev outputs usable as historical features: jev_raw and confidence per (date, symbol)."""
    frame: pd.DataFrame            # columns: rebalance_date, symbol, jev_raw, jev_confidence
    feature_set_id: str | None = None

    def for_date(self, d: pd.Timestamp) -> pd.DataFrame:
        if self.frame is None or self.frame.empty:
            return pd.DataFrame(columns=["jev_raw", "jev_confidence"])
        f = self.frame[self.frame["rebalance_date"] == d]
        return f.set_index("symbol")[["jev_raw", "jev_confidence"]]


@dataclass
class BacktestResult:
    config: ModelConfig | None
    equity: pd.Series
    trades: pd.DataFrame
    signals: pd.DataFrame
    holdings: pd.DataFrame
    rankings: pd.DataFrame
    stats: dict = field(default_factory=dict)


def _ranking_frame(cs, quant: pd.Series, jev: pd.DataFrame | None, cfg: ModelConfig, holdings: list[str],
                   pool_size: int, boundary_extra: int) -> pd.DataFrame:
    eligible = cs.frame.index
    q = quant.reindex(eligible)
    top = q.sort_values(ascending=False).index[: pool_size + boundary_extra]
    pool = pd.Index(top).union(pd.Index([h for h in holdings if h in eligible]))
    jev_raw = jev["jev_raw"] if jev is not None and not jev.empty else None
    ranked = combine_final(q, jev_raw, cfg.jev_weight, pool)
    fr = cs.frame
    ranked["vol60_pct"] = fr["vol_60d"].rank(pct=True) if "vol_60d" in fr else np.nan
    for col in ("price_sma200", "sma50_sma200", "vol_60d", "sector_group", "market_cap"):
        ranked[col] = fr[col].reindex(ranked.index) if col in fr else np.nan
    for f in FAMILIES:
        ranked[f"pct_{f}"] = cs.family_pct[f].reindex(ranked.index) if f in cs.family_pct else np.nan
        ranked[f"z_{f}"] = cs.family_z[f].reindex(ranked.index) if f in cs.family_z else np.nan
    ranked["jev_raw"] = jev_raw.reindex(ranked.index) if jev_raw is not None else np.nan
    ranked["jev_confidence"] = jev["jev_confidence"].reindex(ranked.index) if jev is not None and not jev.empty \
        else np.nan
    return ranked


class Backtester:
    def __init__(self, cache: ScoreCache, open_px: pd.DataFrame, close_px: pd.DataFrame,
                 labels_126: pd.DataFrame | None = None, jev: JevFeatures | None = None,
                 initial_capital: float | None = None, bt_config: dict | None = None, jev_config: dict | None = None):
        bt = bt_config or load_config("backtest")   # a stored snapshot can be supplied for exact reproduction
        self.bt = bt
        self.cache = cache
        self.open = open_px
        self.close = close_px
        self.calendar = close_px.index
        self.labels = labels_126
        self.jev = jev
        self.initial_capital = float(initial_capital or bt["initial_capital_usd"])
        jcfg = (jev_config or load_config("jev"))["candidate_pool"]
        self.pool_size, self.boundary_extra = int(jcfg["top_n"]), int(jcfg["boundary_extra"])
        self.last_valid = close_px.apply(lambda s: s.last_valid_index())
        self._ic_cache: dict[tuple, dict] = {}

    # --- scoring ------------------------------------------------------------------------------------------
    def family_weights(self, cfg: ModelConfig, d: pd.Timestamp) -> dict[str, float]:
        preset = self.bt["family_presets"].get(cfg.preset) or family_preset(cfg.preset)
        if preset.get("dynamic") != "ic":
            return {f: float(preset.get(f, 0)) for f in FAMILIES}
        key = (cfg.preset, cfg.universe_key, d)
        if key not in self._ic_cache:
            if self.labels is None or self.labels.empty:
                self._ic_cache[key] = {f: 1.0 for f in FAMILIES}
            else:
                hist = [(x, self.cache.cross_section(x, *cfg.universe_key).family_z)
                        for x in self.cache.dates if x < d]
                self._ic_cache[key] = ic_family_weights(hist, self.labels, d, int(preset.get("horizon", 126)),
                                                        int(preset.get("lookback_months", 24)),
                                                        int(preset.get("min_obs", 6)))
        return self._ic_cache[key]

    def rank_at(self, cfg: ModelConfig, d: pd.Timestamp, holdings: list[str]) -> tuple[pd.DataFrame, object]:
        cs = self.cache.cross_section(d, *cfg.universe_key)
        if cs.frame.empty:
            return pd.DataFrame(), cs
        quant = quant_scores(cs, self.family_weights(cfg, d))
        jev = self.jev.for_date(d) if (self.jev is not None and cfg.jev_weight > 0) else None
        return _ranking_frame(cs, quant, jev, cfg, holdings, self.pool_size, self.boundary_extra), cs

    # --- simulation ---------------------------------------------------------------------------------------
    def run(self, cfg: ModelConfig, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None,
            schedule: list[tuple[pd.Timestamp, ModelConfig]] | None = None, record_rankings: bool = False) -> BacktestResult:
        """Simulate ``cfg`` (or a date-> config ``schedule`` for walk-forward switching)."""
        dates = [d for d in self.cache.dates if (start is None or d >= start) and (end is None or d <= end)]
        sched = sorted(schedule or [], key=lambda x: x[0])
        pcfg = self.bt["portfolio"]
        port = Portfolio(cash=self.initial_capital)
        entry_meta: dict[str, dict] = {}
        eq_idx, eq_val = [], []
        trade_rows, sig_rows, hold_rows, rank_rows = [], [], [], []
        closed_holding_days: list[int] = []
        jev_cov: list[float] = []
        universe_sizes: list[int] = []
        cal = self.calendar
        if not dates:
            return BacktestResult(cfg, pd.Series(dtype=float), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                                  pd.DataFrame())
        # trade day for each rebalance: next session after d
        trade_day = {}
        for d in dates:
            pos = cal.searchsorted(d, side="right")
            if pos < len(cal):
                trade_day[cal[pos]] = d
        last_close: dict[str, float] = {}
        # simulate through the holding period of the last rebalance (up to the next rebalance date)
        all_dates = self.cache.dates
        nxt = [x for x in all_dates if x > dates[-1]]
        sim_end = nxt[0] if (end is not None and nxt) else cal[-1]
        sim_days = cal[(cal > dates[0]) & (cal <= sim_end)]
        active_cfg = cfg
        for day in sim_days:
            if day in trade_day:
                d = trade_day[day]
                for s_date, s_cfg in sched:
                    if s_date <= d:
                        active_cfg = s_cfg
                self._rebalance(active_cfg, d, day, port, entry_meta, pcfg, trade_rows, sig_rows, hold_rows,
                                rank_rows if record_rankings else None, closed_holding_days, jev_cov,
                                universe_sizes, last_close)
            px = self.close.loc[day]
            for sym in port.positions:
                v = px.get(sym)
                if v is not None and v == v:
                    last_close[sym] = float(v)
            eq_idx.append(day)
            eq_val.append(port.cash + sum(p.shares * last_close.get(s, p.entry_price) for s, p in port.positions.items()))
        equity = pd.Series(eq_val, index=pd.DatetimeIndex(eq_idx), name="equity")
        # prepend initial capital on the first rebalance date for clean return math
        equity = pd.concat([pd.Series([self.initial_capital], index=[dates[0]]), equity])
        trades = pd.DataFrame(trade_rows)
        stats = {
            "avg_holding_days": float(np.mean(closed_holding_days)) if closed_holding_days else None,
            "closed_positions": len(closed_holding_days),
            "jev_pool_coverage": float(np.mean(jev_cov)) if jev_cov else None,
            "median_universe_size": float(np.median(universe_sizes)) if universe_sizes else 0.0,
            "min_universe_size": int(min(universe_sizes)) if universe_sizes else 0,
            "open_positions": {s: {"shares": p.shares, "entry_date": str(p.entry_date.date()),
                                   "entry_price": p.entry_price} for s, p in port.positions.items()},
        }
        return BacktestResult(cfg, equity, trades, pd.DataFrame(sig_rows), pd.DataFrame(hold_rows),
                              pd.DataFrame(rank_rows) if record_rankings else pd.DataFrame(), stats)

    def _rebalance(self, cfg, d, day, port, entry_meta, pcfg, trade_rows, sig_rows, hold_rows, rank_rows,
                   closed_days, jev_cov, universe_sizes, last_close):
        costs = CostModel.from_config(self.bt["costs"], cfg.cost_multiplier)
        broker = SimulatedBroker(costs)
        rules = SignalRules.from_config(pcfg, cfg.portfolio_size, cfg.hold_buffer)
        holdings = list(port.positions)
        ranking, cs = self.rank_at(cfg, d, holdings)
        universe_sizes.append(len(cs.frame))
        if cfg.jev_weight > 0 and not ranking.empty:
            pool = ranking[ranking["in_pool"]]
            jev_cov.append(float(pool["jev_raw"].notna().mean()) if len(pool) else 0.0)
        held_days = {s: int((d - m["entry_date"]).days) for s, m in entry_meta.items()}
        decisions = decide(ranking, port.positions, d, rules, holding_days=held_days) if not ranking.empty else \
            [Decision(s, SELL, ["exit:no_longer_eligible (empty universe)"]) for s in holdings]
        opens = self.open.loc[day]
        # 1) sells
        for dec in decisions:
            sig_rows.append({"rebalance_date": d, "symbol": dec.symbol, "signal": dec.signal,
                             "rank": dec.rank, "reasons": "; ".join(dec.reasons)})
            if dec.signal != SELL or dec.symbol not in port.positions:
                continue
            pos = port.positions[dec.symbol]
            price = opens.get(dec.symbol)
            reason = dec.reasons[0] if dec.reasons else "exit"
            if price is None or not price == price:
                lv = self.last_valid.get(dec.symbol)
                if lv is not None and lv < day:  # stopped trading: liquidate at last close with haircut
                    price = last_close.get(dec.symbol, pos.entry_price) * (1 - float(self.bt["costs"]["delisting_haircut"]))
                    reason += " [delisted: last close]"
                else:
                    continue  # temporary halt: retry next rebalance
            fill = broker.execute(Order(dec.symbol, "SELL", pos.shares, reason), float(price), day)
            if fill:
                port.apply(fill)
                closed_days.append(int((day - entry_meta.get(dec.symbol, {"entry_date": day})["entry_date"]).days))
                entry_meta.pop(dec.symbol, None)
                trade_rows.append(self._trade_row(d, fill))
        # positions that stopped trading but were not flagged (e.g. missing from ranking handled above)
        # 2) targets
        keep = [x.symbol for x in decisions if x.signal in (HOLD, BUY)]
        if ranking.empty or not keep:
            self._snapshot(d, port, hold_rows, last_close)
            return
        tw = target_weights(keep, cfg.weighting, ranking["final_score"], ranking["vol_60d"],
                            float(pcfg["max_position_weight"]))
        prices_now = {s: (opens.get(s) if opens.get(s) == opens.get(s) else last_close.get(s)) for s in keep}
        equity = port.cash + sum(p.shares * float(prices_now.get(s) or last_close.get(s, p.entry_price))
                                 for s, p in port.positions.items())
        band = float(pcfg["drift_band"])
        orders_buy = []
        for sym in keep:
            px = prices_now.get(sym)
            if px is None or not px == px or px <= 0:
                continue
            target_val = equity * float(tw[sym])
            cur_val = port.positions[sym].shares * px if sym in port.positions else 0.0
            if sym in port.positions and abs(cur_val - target_val) <= band * target_val:
                continue
            delta = target_val - cur_val
            if delta < 0:
                fill = broker.execute(Order(sym, "SELL", min(-delta / px, port.positions[sym].shares),
                                            "rebalance:trim to target"), px, day)
                if fill:
                    port.apply(fill)
                    trade_rows.append(self._trade_row(d, fill))
            elif delta > 0:
                orders_buy.append((sym, delta, px))
        # 3) buys, scaled to available cash (costs included)
        need = sum(delta for _, delta, _ in orders_buy)
        slip = costs.slippage_bps / 1e4
        tc = costs.transaction_cost_bps / 1e4
        budget = port.cash - costs.commission_per_trade_usd * len(orders_buy)
        scale = min(1.0, budget / (need * (1 + slip) * (1 + tc))) if need > 0 else 0.0
        for sym, delta, px in orders_buy:
            notional = delta * scale
            if notional < 1.0:  # skip dust trades
                continue
            shares = notional / px
            new = sym not in port.positions
            fill = broker.execute(Order(sym, "BUY", shares, "entry" if new else "rebalance:top up"), px, day)
            if fill and fill.gross + fill.total_cost <= port.cash + 1e-9:
                port.apply(fill)
                if new:
                    entry_meta[sym] = {"entry_date": day}
                trade_rows.append(self._trade_row(d, fill))
        if rank_rows is not None:
            r = ranking.head(max(60, cfg.portfolio_size * 3)).reset_index().rename(columns={"index": "symbol"})
            r["rebalance_date"] = d
            rank_rows.extend(r.to_dict("records"))
        self._snapshot(d, port, hold_rows, last_close, ranking)

    @staticmethod
    def _trade_row(d, fill) -> dict:
        return {"rebalance_date": d, "trade_date": fill.trade_date, "symbol": fill.symbol, "side": fill.side,
                "shares": fill.shares, "price": fill.price, "gross": fill.gross, "commission": fill.commission,
                "slippage_cost": fill.slippage_cost, "transaction_cost": fill.transaction_cost, "reason": fill.reason}

    @staticmethod
    def _snapshot(d, port, hold_rows, last_close, ranking=None):
        for s, p in port.positions.items():
            hold_rows.append({"rebalance_date": d, "symbol": s, "shares": p.shares, "entry_date": p.entry_date,
                              "entry_price": p.entry_price, "cost_basis": p.cost_basis,
                              "sector_group": ranking["sector_group"].get(s) if ranking is not None and s in ranking.index else None,
                              "market_cap": ranking["market_cap"].get(s) if ranking is not None and s in ranking.index else None,
                              "value": p.shares * last_close.get(s, p.entry_price)})
        hold_rows.append({"rebalance_date": d, "symbol": "__CASH__", "shares": None, "entry_date": None,
                          "entry_price": None, "cost_basis": None, "sector_group": None, "market_cap": None,
                          "value": port.cash})
