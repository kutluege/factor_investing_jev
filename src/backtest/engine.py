"""Event-driven monthly backtest sharing the production scoring, signal and accounting code."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.config import load_config
from src.features.momentum import delisting_haircuts
from src.model.scoring import (
    FAMILIES,
    ModelConfig,
    ScoreCache,
    combine_final,
    factor_momentum_signs,
    family_preset,
    ic_family_weights,
    normalize_weights,
    quant_scores,
)
from src.portfolio.book import CostModel, Order, Portfolio, SimulatedBroker
from src.portfolio.rebalance import execute_targets, plan_targets, regime_exposure, spread_cost_fn
from src.portfolio.signals import BUY, HOLD, SELL, Decision, SignalRules, decide


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
                 labels: dict[int, pd.DataFrame] | pd.DataFrame | None = None, jev: JevFeatures | None = None,
                 initial_capital: float | None = None, bt_config: dict | None = None, jev_config: dict | None = None,
                 raw_close_px: pd.DataFrame | None = None, market_close: pd.Series | None = None):
        bt = bt_config or load_config("backtest")   # a stored snapshot can be supplied for exact reproduction
        self.bt = bt
        self.cache = cache
        self.open = open_px
        self.close = close_px
        self.calendar = close_px.index
        # forward labels by horizon (used only by dynamic presets, always restricted to matured labels)
        self.labels = labels if isinstance(labels, dict) or labels is None else {126: labels}
        self.labels = self.labels or {}
        self.jev = jev
        self.initial_capital = float(initial_capital or bt["initial_capital_usd"])
        jcfg = (jev_config or load_config("jev"))["candidate_pool"]
        self.pool_size, self.boundary_extra = int(jcfg["top_n"]), int(jcfg["boundary_extra"])
        self.market_close = market_close  # QQQ, for the optional market-regime overlay
        self.last_valid = close_px.apply(lambda s: s.last_valid_index())
        # per-symbol haircut for securities that stopped trading (distress vs other delistings)
        self.delist_haircut = delisting_haircuts(close_px, raw_close_px, bt["costs"])
        self._ic_cache: dict[tuple, dict] = {}

    # --- scoring ------------------------------------------------------------------------------------------
    def _preset(self, name: str) -> dict:
        return self.bt["family_presets"].get(name) or family_preset(name)

    def family_weights(self, cfg: ModelConfig, d: pd.Timestamp) -> dict[str, float]:
        preset = self._preset(cfg.preset)
        dyn = preset.get("dynamic")
        if not dyn:
            return {f: float(preset.get(f, 0)) for f in FAMILIES}
        base = self._preset(preset["base"]) if preset.get("base") else {f: 1.0 for f in FAMILIES}
        base_w = normalize_weights({f: float(base.get(f, 0)) for f in FAMILIES})
        key = (cfg.preset, cfg.universe_key, d)
        if key in self._ic_cache:
            return self._ic_cache[key]
        horizon = int(preset.get("horizon", 126))
        lab = self.labels.get(horizon)
        lookback = int(preset.get("lookback_months", 24))
        hist = [(x, self.cache.cross_section(x, *cfg.universe_key).family_z) for x in self.cache.dates
                if d - pd.DateOffset(months=lookback + 7) <= x < d]
        if lab is None or lab.empty:
            w = base_w  # no matured labels available: fall back to the base weights
        elif dyn == "ic":
            ic = ic_family_weights(hist, lab, d, horizon, lookback, int(preset.get("min_obs", 6)))
            ic_w = normalize_weights({f: float(ic.get(f, 0)) for f in FAMILIES})
            shrink = float(preset.get("shrink", 0.0))
            w = {f: shrink * base_w[f] + (1 - shrink) * ic_w[f] for f in FAMILIES}
        elif dyn == "factor_momentum":
            perf = factor_momentum_signs(hist, lab, d, lookback)
            tilt = float(preset.get("tilt", 0.3))
            w = {f: base_w[f] * (1 + tilt * float(np.sign(perf.get(f, 0.0)))) for f in FAMILIES}
        else:
            raise ValueError(f"unknown dynamic preset type {dyn!r}")
        self._ic_cache[key] = w
        return w

    def rank_at(self, cfg: ModelConfig, d: pd.Timestamp, holdings: list[str]) -> tuple[pd.DataFrame, object]:
        cs = self.cache.cross_section(d, *cfg.universe_key)
        if cs.frame.empty:
            return pd.DataFrame(), cs
        quant = quant_scores(cs, self.family_weights(cfg, d))
        # Jev scores are attached whenever available (shadow mode at weight 0); they only move the ranking
        # when jev_weight > 0
        jev = self.jev.for_date(d) if self.jev is not None else None
        return _ranking_frame(cs, quant, jev, cfg, holdings, self.pool_size, self.boundary_extra), cs

    # --- simulation ---------------------------------------------------------------------------------------
    def run(self, cfg: ModelConfig, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None,
            schedule: list[tuple[pd.Timestamp, ModelConfig]] | None = None, record_rankings: bool = False) -> BacktestResult:
        """Simulate ``cfg`` (or a date-> config ``schedule`` for walk-forward switching)."""
        if start is None and self.bt.get("start_date"):
            start = pd.Timestamp(self.bt["start_date"])
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
        ccfg = self.bt["costs"]
        rules = SignalRules.from_config(pcfg, cfg.portfolio_size, cfg.hold_buffer)
        holdings = list(port.positions)
        ranking, cs = self.rank_at(cfg, d, holdings)
        universe_sizes.append(len(cs.frame))
        extra_bps = spread_cost_fn(ccfg, self._spread_lookup(d), cfg.cost_multiplier)
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
                    hc = float(self.delist_haircut.get(dec.symbol, self.bt["costs"]["delisting_haircut"]))
                    price = last_close.get(dec.symbol, pos.entry_price) * (1 - hc)
                    reason += " [delisted: last close]"
                else:
                    continue  # temporary halt: retry next rebalance
            fill = broker.execute(Order(dec.symbol, "SELL", pos.shares, reason), float(price), day,
                                  extra_bps(dec.symbol))
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
        tw = plan_targets(keep, cfg.weighting, ranking, pcfg, cfg.portfolio_size)
        tw = tw * regime_exposure(cfg.regime_filter, self.market_close, d)
        prices_now = {s: (opens.get(s) if opens.get(s) == opens.get(s) else last_close.get(s))
                      for s in set(keep) | set(port.positions)}
        # 3) trims / top-ups / new positions, buys scaled to available cash (costs included)
        execute_targets(port, tw, prices_now, broker, costs, extra_bps, float(pcfg["drift_band"]),
                        float(pcfg.get("min_trade_usd", 0.0)), day,
                        on_fill=lambda f: trade_rows.append(self._trade_row(d, f)),
                        on_new_position=lambda s: entry_meta.__setitem__(s, {"entry_date": day}))
        if rank_rows is not None:
            r = ranking.head(max(60, cfg.portfolio_size * 3)).reset_index().rename(columns={"index": "symbol"})
            r["rebalance_date"] = d
            rank_rows.extend(r.to_dict("records"))
        self._snapshot(d, port, hold_rows, last_close, ranking)

    def _spread_lookup(self, d: pd.Timestamp) -> pd.Series:
        """Spread estimates for every name on date d (held names may have left the eligible universe)."""
        full = self.cache.by_date.get(d)
        if full is not None and "spread_est" in full:
            return full["spread_est"]
        return pd.Series(dtype=float)

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
