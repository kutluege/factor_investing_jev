"""Theme portfolio backtest (THEMES_SPEC §8, T6): one fixed pre-registered configuration, no parameter search.

Monthly: scores per theme (src/themes/scoring.py), theme selection and targets (src/portfolio/rebalance.py:
select_theme, theme_targets), execution at the next session's open through the shared ``execute_targets`` with the
existing cost model (commission, slippage, transaction cost, Abdi-Ranaldo half-spread). A held name that stopped
trading is liquidated at its last close minus the delisting haircut.

Benchmarks: each theme's equal-weight index of eligible members (monthly rebalanced, costless, close to close),
the composite index weighted by the theme budgets, theme ETFs, QQQ and SPY. Selection contribution = portfolio
period return - composite index period return. Because themes_v1 estimates no parameters, the full-period
simulation is out-of-sample by construction; the pre-registered subperiods play the role of walk-forward folds.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.config import load_config
from src.portfolio.book import CostModel, Order, Portfolio, SimulatedBroker
from src.portfolio.rebalance import (
    cap_total_weight,
    execute_targets,
    partial_rebalance,
    present_budgets,
    select_theme,
    spread_cost_fn,
    theme_targets,
    theme_tilt_weights,
)
from src.themes.config import ThemesConfig


@dataclass
class ThemeBacktestResult:
    equity: pd.Series
    trades: pd.DataFrame
    signals: pd.DataFrame
    holdings: pd.DataFrame
    stats: dict = field(default_factory=dict)


def entry_block(cross: pd.DataFrame, pct: float) -> set[str]:
    """Top ``pct`` of 60-day volatility among all eligible theme members on the date (entry only)."""
    v = cross["vol_60d"].dropna()
    if v.empty or pct <= 0:
        return set()
    return set(v[v >= v.quantile(1 - pct)].index)


def monthly_signals(cross: pd.DataFrame, cfg: ThemesConfig, held: dict[str, str]) -> dict[str, dict[str, str]]:
    """Per theme signals for one date. ``cross``: eligible scored members (index symbol); ``held``: symbol->theme."""
    blocked = entry_block(cross, cfg.portfolio.entry_block_top_vol_pct)
    out = {}
    for t, th in cfg.themes.items():
        if not th.enabled:
            continue
        ranked = cross[cross["theme"] == t][["score", "subtheme"]]
        held_t = {s for s, ht in held.items() if ht == t}
        out[t] = select_theme(ranked, held_t, th.n_picks, cfg.portfolio.hold_buffer,
                              cfg.portfolio.max_share_per_subtheme, blocked)
    return out


class ThemeBacktester:
    def __init__(self, panel: pd.DataFrame, scores: pd.DataFrame, cfg: ThemesConfig, open_px: pd.DataFrame,
                 close_px: pd.DataFrame, initial_capital: float = 100_000.0, haircuts: pd.Series | None = None):
        """``haircuts``: per-symbol delisting haircuts (``src.features.momentum.delisting_haircuts``; distress
        delistings lose more than mergers); defaults to the flat configured haircut."""
        self.cfg = cfg
        cols = ["rebalance_date", "symbol", "theme", "subtheme", "stage", "vol_60d", "spread_est"]
        p = panel[panel["eligible"]][[c for c in cols if c in panel]]
        keys = ["rebalance_date", "symbol"] + (["theme"] if "theme" in scores else [])  # multi-theme rows
        sc = scores if "theme" in scores else scores.drop(columns=[c for c in ("theme",) if c in scores])
        self.cross = {d: g.set_index("symbol") for d, g in p.merge(sc, on=keys, how="left").groupby("rebalance_date")}
        self.dates = sorted(self.cross)
        self.open, self.close = open_px, close_px
        self.calendar = close_px.index
        self.last_valid = close_px.apply(lambda s: s.last_valid_index())
        self.bt = load_config("backtest")
        self.initial_capital = initial_capital
        self.haircuts = haircuts if haircuts is not None else pd.Series(dtype=float)

    def _tilt_target(self, tilt, cross: pd.DataFrame, port: Portfolio, prices: dict, rebalance: bool) -> pd.Series:
        """v2 construction: score-tilted theme holdings (``theme_tilt_weights``) with partial rebalancing; between
        rebalances current weights are kept for names that are still eligible members."""
        equity = port.cash + sum(p.shares * float(prices.get(s) or p.entry_price) for s, p in port.positions.items())
        current = pd.Series({s: p.shares * float(prices.get(s) or p.entry_price) / equity
                             for s, p in port.positions.items()}, dtype=float)
        if not rebalance:
            return current[current.index.isin(cross.index)]
        blocked: set[str] = set()
        if tilt.vol_block > 0:
            blocked = entry_block(cross, tilt.vol_block)
        budgets = present_budgets(dict(tilt.budgets), set(cross["theme"]))
        parts = [theme_tilt_weights(g["score"], budgets.get(t, 0.0), tilt.lam, tilt.top_frac,
                                    self.cfg.portfolio.position_cap, blocked)
                 for t, g in cross.groupby("theme") if budgets.get(t, 0.0) > 0]
        target = pd.concat(parts).groupby(level=0).sum() if parts else pd.Series(dtype=float)
        target = cap_total_weight(target, self.cfg.portfolio.position_cap)
        return partial_rebalance(current, target, tilt.speed)

    def run(self, cost_multiplier: float = 1.0, start: pd.Timestamp | None = None,
            rf_daily: pd.Series | None = None, tilt=None) -> ThemeBacktestResult:
        """``rf_daily``: risk-free rate per session (``daily_rf``); uninvested cash accrues it (v2 data fix).
        ``tilt``: a ``src.themes.search.SearchConfig`` -> v2 tilt construction instead of the v1 top-N selection
        (scores passed to the constructor must then be that configuration's scores)."""
        n_reb = 0
        cfg, ccfg = self.cfg, self.bt["costs"]
        costs = CostModel.from_config(ccfg, cost_multiplier)
        broker = SimulatedBroker(costs)
        weights = cfg.enabled_weights()
        n_picks = {t: th.n_picks for t, th in cfg.themes.items() if th.enabled}
        dates = [d for d in self.dates if start is None or d >= start]
        trade_day = {}
        for d in dates:
            pos = self.calendar.searchsorted(d, side="right")
            if pos < len(self.calendar):
                trade_day[self.calendar[pos]] = d
        port = Portfolio(cash=self.initial_capital)
        theme_of: dict[str, str] = {}
        last_close: dict[str, float] = {}
        eq_idx, eq_val, trades, sig_rows, hold_rows = [], [], [], [], []
        for day in self.calendar[self.calendar > dates[0]]:
            if rf_daily is not None:
                port.cash *= 1.0 + float(rf_daily.get(day, 0.0))
            if day in trade_day:
                d = trade_day[day]
                cross = self.cross[d]
                opens = self.open.loc[day]
                spread = cross["spread_est"].groupby(level=0).first() if "spread_est" in cross else None
                extra = spread_cost_fn(ccfg, spread, cost_multiplier)
                keep: dict[str, list[str]] = {}
                tilt_target = None
                if tilt is not None:
                    prices0 = {s: (opens.get(s) if opens.get(s) == opens.get(s) else last_close.get(s))
                               for s in port.positions}
                    tilt_target = self._tilt_target(tilt, cross, port, prices0, rebalance=n_reb % tilt.rebalance_months == 0)
                    n_reb += 1
                    first_theme = cross["theme"].groupby(level=0).first()
                    for s in tilt_target.index:
                        keep.setdefault(str(first_theme.get(s)), []).append(s)
                else:
                    sigs = monthly_signals(cross, cfg, {s: theme_of.get(s) for s in port.positions})
                    for t, sg in sigs.items():
                        keep[t] = [s for s, x in sg.items() if x in ("HOLD", "BUY")]
                        for s, x in sg.items():
                            sig_rows.append({"rebalance_date": d, "symbol": s, "theme": t, "signal": x,
                                             "score": cross["score"].get(s)})
                kept = {s for ks in keep.values() for s in ks}
                for s in [s for s in list(port.positions) if s not in kept]:
                    pos = port.positions[s]
                    px = opens.get(s)
                    reason = "exit:rank/membership"
                    if px is None or px != px:
                        lv = self.last_valid.get(s)
                        if lv is not None and lv < day:
                            hc = float(self.haircuts.get(s, ccfg["delisting_haircut"]))
                            px = last_close.get(s, pos.entry_price) * (1 - hc)
                            reason += " [delisted: last close]"
                        else:
                            continue
                    f = broker.execute(Order(s, "SELL", pos.shares, reason), float(px), day, extra(s))
                    if f:
                        port.apply(f)
                        trades.append(_trade(d, f))
                        theme_of.pop(s, None)
                targets = tilt_target if tilt_target is not None else \
                    theme_targets(keep, weights, n_picks, cfg.portfolio.position_cap)
                for t, ks in keep.items():
                    for s in ks:
                        theme_of[s] = t
                prices = {s: (opens.get(s) if opens.get(s) == opens.get(s) else last_close.get(s))
                          for s in set(targets.index) | set(port.positions)}
                execute_targets(port, targets, prices, broker, costs, extra,
                                float(self.bt["portfolio"]["drift_band"]),
                                float(self.bt["portfolio"].get("min_trade_usd", 0.0)), day,
                                on_fill=lambda f, d=d: trades.append(_trade(d, f)))
                for s, p in port.positions.items():
                    hold_rows.append({"rebalance_date": d, "symbol": s, "theme": theme_of.get(s),
                                      "value": p.shares * float(prices.get(s) or p.entry_price)})
            px = self.close.loc[day]
            for s in port.positions:
                v = px.get(s)
                if v is not None and v == v:
                    last_close[s] = float(v)
            eq_idx.append(day)
            eq_val.append(port.cash + sum(p.shares * last_close.get(s, p.entry_price)
                                          for s, p in port.positions.items()))
        equity = pd.concat([pd.Series([self.initial_capital], index=[dates[0]]),
                            pd.Series(eq_val, index=pd.DatetimeIndex(eq_idx))])
        return ThemeBacktestResult(equity, pd.DataFrame(trades), pd.DataFrame(sig_rows), pd.DataFrame(hold_rows),
                                   {"cost_multiplier": cost_multiplier,
                                    "open_positions": {s: theme_of.get(s) for s in port.positions}})


def daily_rf(french: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.Series:
    """Per-session risk-free rate: the month's French RF spread evenly over that month's sessions."""
    cal = pd.Series(calendar, index=calendar)
    month = calendar + pd.offsets.MonthEnd(0)
    n = cal.groupby(month).transform("size")
    rf = french["ff_rf"].reindex(month).to_numpy()
    return pd.Series(np.nan_to_num(rf) / n.to_numpy(), index=calendar)


def _trade(d, f) -> dict:
    return {"rebalance_date": d, "trade_date": f.trade_date, "symbol": f.symbol, "side": f.side, "shares": f.shares,
            "price": f.price, "gross": f.gross, "cost": f.total_cost, "reason": f.reason}


def period_returns(close: pd.DataFrame, members: dict[pd.Timestamp, list[str]], dates: list[pd.Timestamp],
                   haircut: float | pd.Series) -> pd.Series:
    """Equal-weight close-to-close return of ``members[d]`` from d to the next date (costless index). A member
    that stops trading inside the period is valued at its last close minus ``haircut``."""
    out = {}
    for d0, d1 in zip(dates[:-1], dates[1:], strict=True):
        syms = [s for s in members.get(d0, []) if s in close]
        if not syms:
            continue
        c0 = close.loc[d0, syms]
        window = close.loc[d0:d1, syms]
        c1 = close.loc[d1, syms]
        last = window.ffill().iloc[-1]
        dead = c1.isna() & last.notna()
        hc = haircut.reindex(syms).fillna(0.0) if isinstance(haircut, pd.Series) else haircut
        c1 = c1.where(~dead, last * (1 - hc))
        r = (c1 / c0 - 1.0).replace([np.inf, -np.inf], np.nan).dropna()
        if len(r):
            out[d1] = float(r.mean())
    return pd.Series(out, dtype=float)


def theme_indices(panel: pd.DataFrame, close: pd.DataFrame, cfg: ThemesConfig, dates: list[pd.Timestamp],
                  haircut: float | pd.Series) -> pd.DataFrame:
    el = panel[panel["eligible"]]
    out = {}
    for t, th in cfg.themes.items():
        if not th.enabled:
            continue
        mem = {d: list(g["symbol"]) for d, g in el[el["theme"] == t].groupby("rebalance_date")}
        out[t] = period_returns(close, mem, dates, haircut)
    df = pd.DataFrame(out)
    w = pd.Series(cfg.enabled_weights())
    df["composite"] = (df[w.index] * w).sum(axis=1, min_count=1) / (df[w.index].notna() * w).sum(axis=1)
    return df


def equity_period_returns(equity: pd.Series, dates: list[pd.Timestamp]) -> pd.Series:
    e = equity.groupby(level=0).last().reindex(pd.DatetimeIndex(dates), method="ffill")
    return e.pct_change().dropna()


def max_drawdown(returns: pd.Series) -> float:
    w = (1 + returns.fillna(0)).cumprod()
    return float((w / w.cummax() - 1).min())


def annualized(returns: pd.Series, periods: int = 12) -> float:
    r = returns.dropna()
    if r.empty:
        return np.nan
    return float((1 + r).prod() ** (periods / len(r)) - 1)


def success_table(port: pd.Series, index: pd.Series, port_2x: pd.Series, subperiods: list[list[str]]) -> dict:
    """§8 pre-registered success criteria (not a CAGR target)."""
    contrib = (port - index).dropna()
    rows = []
    for a, b in subperiods:
        lo, hi = pd.Timestamp(a), pd.Timestamp(b) + pd.offsets.MonthEnd(0)
        m = (contrib.index >= lo) & (contrib.index <= hi)
        rows.append({"subperiod": f"{a}..{b}", "months": int(m.sum()),
                     "portfolio_ann": annualized(port[m]), "index_ann": annualized(index.reindex(contrib.index)[m]),
                     "selection_contribution_ann": annualized(port[m]) - annualized(index.reindex(contrib.index)[m])})
    sub = pd.DataFrame(rows)
    positive = int((sub["selection_contribution_ann"] > 0).sum())
    need = int(np.ceil(2 * len(sub) / 3))
    mdd_p, mdd_i = max_drawdown(port), max_drawdown(index.reindex(port.index))
    c2 = annualized(port_2x) - annualized(index.reindex(port_2x.index))
    crit = {
        "subperiods_positive": f"{positive}/{len(sub)}", "c1_subperiods": positive >= need,
        "max_dd_portfolio": mdd_p, "max_dd_index": mdd_i, "c2_drawdown": mdd_p >= mdd_i - 0.05,
        "contribution_2x_costs_ann": c2, "c3_costs_2x": bool(c2 >= 0),
        "contribution_ann": annualized(port) - annualized(index.reindex(port.index)),
    }
    crit["passed"] = crit["c1_subperiods"] and crit["c2_drawdown"] and crit["c3_costs_2x"]
    crit.update(contribution_stats(contrib))
    return {"subperiods": sub, "criteria": crit}


def contribution_stats(contrib: pd.Series) -> dict:
    """Arithmetic selection contribution, tracking error, information ratio, Newey-West t (lag 1) and the minimum
    track-record length (months) needed for the observed IR to be significant at 95% one-sided
    (Bailey & Lopez de Prado 2012)."""
    from scipy.stats import kurtosis, skew

    from src.themes.research.stats import nw_mean
    c = contrib.dropna()
    if len(c) < 12:
        return {}
    te = float(c.std(ddof=1) * np.sqrt(12))
    ir_m = float(c.mean() / c.std(ddof=1)) if c.std(ddof=1) > 0 else np.nan
    g3, g4 = float(skew(c)), float(kurtosis(c, fisher=False))
    z = 1.645
    min_trl = (1 + (1 - g3 * ir_m + (g4 - 1) / 4 * ir_m ** 2) * (z / ir_m) ** 2) if ir_m and ir_m > 0 else np.inf
    return {"contribution_arith_ann": float(c.mean() * 12), "tracking_error_ann": te,
            "information_ratio": ir_m * np.sqrt(12), "contribution_nw_t": nw_mean(c, 1)["t"],
            "min_track_record_months": float(min_trl), "months": len(c)}
