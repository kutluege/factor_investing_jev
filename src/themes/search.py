"""themes v2 free-search track (user decision 2026-10-01; CLAUDE.md §3 overridden for this track only).

The search is free (factor list fixed; group weights, tilt construction, theme budgets, rebalance speed and
frequency, volatility block are searched), but its overfitting is MEASURED, never hidden:

1. selection on the design window only (default 2011-07 .. 2020-12),
2. the selected configuration reported on the untouched holdout (2021-01 ..),
3. nested walk-forward re-selection (yearly, expanding window) = the realistic estimate,
4. CSCV probability of backtest overfitting over all trials and the deflated Sharpe ratio with the trial count,
5. every trial persisted.

Fast engine: monthly periods. Targets decided at the close of rebalance date d (data <= d) are held from the close
of the next session to the close of the session after the next rebalance date (one-session implementation lag).
Costs: |trade weight| x (slippage + transaction bps + half the Abdi-Ranaldo spread, capped) + commission per trade.
Uninvested cash earns the French risk-free rate. Benchmark: the composite of equal-weight theme indices with the
themes_v1 budgets (fixed, costless), so allocation and selection are both measured against the same yardstick.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from src.backtest.validation import deflated_sharpe, pbo_cscv
from src.portfolio.rebalance import partial_rebalance, theme_tilt_weights
from src.themes.config import ThemesConfig

MAD_SCALE = 1.4826


@dataclass(frozen=True)
class SearchConfig:
    group_mult: tuple[tuple[str, float], ...]
    lam: float
    top_frac: float
    budgets: tuple[tuple[str, float], ...]
    speed: float
    rebalance_months: int
    vol_block: float

    @property
    def key(self) -> str:
        return hashlib.sha1(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:12]

    def as_dict(self) -> dict:
        d = asdict(self)
        d["group_mult"] = dict(self.group_mult)
        d["budgets"] = dict(self.budgets)
        return d


def baseline_configs(groups: list[str], budgets: dict[str, float]) -> list[SearchConfig]:
    """Reference points included in every search: the index replica (lam 0, everything held) and a plain tilt."""
    g = tuple((x, 1.0) for x in groups)
    b = tuple(sorted(budgets.items()))
    return [SearchConfig(g, 0.0, 1.0, b, 1.0, 1, 0.0), SearchConfig(g, 0.5, 0.5, b, 1.0, 1, 0.0)]


def sample_configs(groups: list[str], themes: list[str], base_budgets: dict[str, float], n: int,
                   seed: int = 20261001) -> list[SearchConfig]:
    rng = np.random.default_rng(seed)
    mults = [0.25, 0.5, 1.0, 2.0, 4.0]  # no zero: the factor list stays unchanged (user decision)
    alpha = np.array([base_budgets[t] for t in themes]) * 12
    out = baseline_configs(groups, base_budgets)
    while len(out) < n:
        b = rng.dirichlet(alpha)
        if (b < 0.1).any():
            continue
        out.append(SearchConfig(
            group_mult=tuple((g, float(rng.choice(mults))) for g in groups),
            lam=float(np.round(rng.uniform(0.0, 1.5), 2)),
            top_frac=float(rng.choice([0.2, 0.33, 0.5, 0.75, 1.0])),
            budgets=tuple(sorted(zip(themes, np.round(b, 3).tolist(), strict=True))),
            speed=float(rng.choice([1.0, 0.5])),
            rebalance_months=int(rng.choice([1, 3])),
            vol_block=float(rng.choice([0.0, 0.03, 0.10])),
        ))
    return out


class ScoreInputs:
    """Per-firm group scores (independent of group weights) and the groups each firm's stage needs."""

    def __init__(self, panel: pd.DataFrame, scores: pd.DataFrame, cfg: ThemesConfig):
        el = panel[panel["eligible"]][["rebalance_date", "symbol", "theme", "subtheme", "stage", "vol_60d",
                                       "spread_est"]]
        grp_cols = [c for c in scores.columns if c.startswith("grp_")]
        df = el.merge(scores[["rebalance_date", "symbol"] + grp_cols], on=["rebalance_date", "symbol"], how="left")
        self.groups = [c[4:] for c in grp_cols]
        combos = df[["theme", "stage", "subtheme"]].drop_duplicates()
        need = {}
        for r in combos.itertuples(index=False):
            try:
                gs = set(cfg.factor_groups_for(r.theme, r.stage, r.subtheme))
            except KeyError:
                gs = set()
            need[(r.theme, r.stage, r.subtheme)] = [g in gs for g in self.groups]
        keys = list(zip(df["theme"], df["stage"], df["subtheme"], strict=True))
        self.need = np.array([need[k] for k in keys], dtype=bool).reshape(len(df), len(self.groups))
        self.G = df[grp_cols].to_numpy(float)
        self.df = df[["rebalance_date", "symbol", "theme", "vol_60d", "spread_est"]].reset_index(drop=True)
        self.min_weight_present = cfg.scoring.min_weight_present

    def scores(self, mult: dict[str, float]) -> pd.Series:
        m = np.array([mult.get(g, 1.0) for g in self.groups])
        present = ~np.isnan(self.G) & self.need
        num = np.nansum(np.where(present, self.G, 0.0) * m, axis=1)
        den = (present * m).sum(axis=1)
        need_w = (self.need * m).sum(axis=1)
        raw = np.where((den > 0) & (den >= self.min_weight_present * need_w), num / np.where(den > 0, den, 1), np.nan)
        s = pd.Series(raw, index=self.df.index)
        key = [self.df["rebalance_date"], self.df["theme"]]
        med = s.groupby(key).transform("median")
        mad = (s - med).abs().groupby(key).transform("median") * MAD_SCALE
        return (s - med) / mad.where(mad > 1e-12)


class PeriodData:
    """Monthly holding-period returns per symbol (one-session lag), RF per period, spreads, theme index returns."""

    def __init__(self, close: pd.DataFrame, dates: list[pd.Timestamp], haircut: pd.Series, rf_daily: pd.Series,
                 members: pd.DataFrame, cfg: ThemesConfig, costs: dict):
        cal = close.index
        starts = [cal[cal.searchsorted(d, side="right")] for d in dates if cal.searchsorted(d, side="right") < len(cal)]
        self.dates = dates[:len(starts)]
        rows = {}
        for k in range(len(starts) - 1):
            a, b = starts[k], starts[k + 1]
            c0 = close.loc[a]
            window = close.loc[a:b]
            c1 = window.iloc[-1]
            last = window.ffill().iloc[-1]
            dead = c1.isna() & last.notna()
            hc = haircut.reindex(close.columns).fillna(0.0)
            c1 = c1.where(~dead, last * (1 - hc))
            rows[self.dates[k]] = (c1 / c0 - 1.0).replace([np.inf, -np.inf], np.nan)
        self.R = pd.DataFrame(rows).T  # index: decision date d, value: return over the following period
        self.R = self.R.where(self.R.abs() <= 10.0)  # vendor glitch guard (same rule as labels)
        rf_cum = (1 + rf_daily).cumprod()
        self.rf = pd.Series({self.dates[k]: float(rf_cum.loc[starts[k + 1]] / rf_cum.loc[starts[k]] - 1)
                             for k in range(len(starts) - 1)})
        self.period_end = pd.Series({self.dates[k]: starts[k + 1] for k in range(len(starts) - 1)})
        self.unit_cost = (float(costs["slippage_bps"]) + float(costs["transaction_cost_bps"])) / 1e4
        self.spread_cap = float(costs.get("max_spread_cost_bps", 200)) / 1e4
        self.spread_on = bool(costs.get("spread_cost"))
        self.commission = float(costs["commission_per_trade_usd"])
        # costless equal-weight theme indices and the fixed v1-budget composite benchmark
        idx = {}
        for t in cfg.themes:
            mem = members[members["theme"] == t]
            r = {}
            for d, g in mem.groupby("rebalance_date"):
                if d in self.R.index:
                    v = self.R.loc[d].reindex(g["symbol"]).dropna()
                    if len(v):
                        r[d] = float(v.mean())
            idx[t] = pd.Series(r)
        self.index = pd.DataFrame(idx).reindex(self.R.index)
        w = pd.Series(cfg.enabled_weights())
        avail = self.index[w.index].notna()
        self.benchmark = (self.index[w.index].fillna(0) * w).sum(axis=1) / (avail * w).sum(axis=1)


def tilt_targets(cross: pd.DataFrame, cfg: SearchConfig, position_cap: float) -> pd.Series:
    """Target weights on one date. ``cross``: eligible members with symbol, theme, score, vol_60d columns."""
    budgets = dict(cfg.budgets)
    blocked: set[str] = set()
    if cfg.vol_block > 0:
        v = cross.set_index("symbol")["vol_60d"].dropna()
        blocked = set(v[v >= v.quantile(1 - cfg.vol_block)].index)
    parts = [theme_tilt_weights(g.set_index("symbol")["score"], budgets[t], cfg.lam, cfg.top_frac, position_cap,
                                blocked)
             for t, g in cross.groupby("theme") if budgets.get(t, 0) > 0]
    target = pd.concat(parts) if parts else pd.Series(dtype=float)
    return target.groupby(level=0).sum()


def simulate(cfg: SearchConfig, si: ScoreInputs, pdata: PeriodData, position_cap: float, capital: float = 100_000.0,
             cost_multiplier: float = 1.0, scores: pd.Series | None = None) -> pd.DataFrame:
    """Monthly net portfolio returns, benchmark, contribution and turnover for one configuration."""
    sc = scores if scores is not None else si.scores(dict(cfg.group_mult))
    df = si.df.assign(score=sc)
    by_date = dict(tuple(df.groupby("rebalance_date")))
    held = pd.Series(dtype=float)
    rows = []
    for k, d in enumerate(pdata.R.index):
        cross = by_date.get(d)
        rebalance = k % cfg.rebalance_months == 0 and cross is not None
        if rebalance:
            new = partial_rebalance(held, tilt_targets(cross, cfg, position_cap), cfg.speed)
        else:
            members = set(cross["symbol"]) if cross is not None else set()
            new = held[held.index.isin(members)] if cross is not None else held
        r = pdata.R.loc[d]
        new = new[r.reindex(new.index).notna()]  # names without a holding-period price cannot be held
        names = new.index.union(held.index)
        dw = (new.reindex(names, fill_value=0.0) - held.reindex(names, fill_value=0.0)).abs()
        traded = dw[dw > 1e-6]
        cost = 0.0
        if len(traded):
            half = pd.Series(0.0, index=traded.index)
            if pdata.spread_on and cross is not None:
                sp = cross.set_index("symbol")["spread_est"].reindex(traded.index)
                half = (0.5 * sp).clip(upper=pdata.spread_cap).fillna(0.0)
            cost = float((traded * (pdata.unit_cost + half)).sum() + len(traded) * pdata.commission / capital)
            cost *= cost_multiplier
        rr = r.reindex(new.index).astype(float)
        invested = float(new.sum())
        gross = float((new * rr).sum() + (1 - invested) * pdata.rf.loc[d])
        net = gross - cost
        held = new * (1 + rr) / (1 + gross) if (1 + gross) > 0 else new * 0
        rows.append({"period": d, "end": pdata.period_end.loc[d], "net": net, "gross": gross, "cost": cost,
                     "turnover": float(dw.sum()), "invested": invested, "benchmark": float(pdata.benchmark.loc[d]),
                     "names": len(new)})
    out = pd.DataFrame(rows).set_index("period")
    out["contribution"] = out["net"] - out["benchmark"]
    return out


# --- measurement protocol --------------------------------------------------------------------------------------------

def information_ratio(x: pd.Series) -> float:
    x = x.dropna()
    return float(x.mean() / x.std(ddof=1) * np.sqrt(12)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan


def select_best(contrib: pd.DataFrame, mask: pd.Series) -> str:
    """Configuration with the highest information ratio on the months in ``mask`` (only those months are read)."""
    sub = contrib.loc[mask[mask].index]
    ir = sub.mean() / sub.std(ddof=1)
    return str(ir.idxmax())


def nested_walk_forward(contrib: pd.DataFrame, first_test_year: int, start: pd.Timestamp) -> tuple[pd.Series, list]:
    """Each calendar year from ``first_test_year``: select on all months before it (from ``start``), hold that
    configuration for the year. Returns the stitched contribution series and the yearly choices."""
    out, picks = [], []
    years = sorted({d.year for d in contrib.index if d.year >= first_test_year})
    for y in years:
        train = pd.Series((contrib.index >= start) & (contrib.index < pd.Timestamp(f"{y}-01-01")), index=contrib.index)
        if train.sum() < 24:
            continue
        best = select_best(contrib, train)
        test = contrib.index[(contrib.index >= pd.Timestamp(f"{y}-01-01")) &
                             (contrib.index <= pd.Timestamp(f"{y}-12-31"))]
        out.append(contrib.loc[test, best])
        picks.append({"year": y, "config": best})
    return (pd.concat(out) if out else pd.Series(dtype=float)), picks


def evaluate_search(contrib: pd.DataFrame, design_end: pd.Timestamp, start: pd.Timestamp,
                    first_wf_year: int) -> dict:
    """Design-window selection, holdout performance, nested walk-forward, PBO and deflated Sharpe."""
    c = contrib[contrib.index >= start]
    design = pd.Series(c.index <= design_end, index=c.index)
    best = select_best(c, design)
    hold = c.loc[~design.to_numpy(), best]
    wf, picks = nested_walk_forward(c, first_wf_year, start)
    trial_sr = (c.mean() / c.std(ddof=1)).to_numpy()
    hold_all = c.loc[~design.to_numpy()]
    hold_rank = float((hold_all.mean() / hold_all.std(ddof=1)).rank(pct=True)[best])
    return {
        "selected": best,
        "design_ir": information_ratio(c.loc[design.to_numpy(), best]),
        "design_contribution_ann": float(c.loc[design.to_numpy(), best].mean() * 12),
        "holdout_ir": information_ratio(hold), "holdout_contribution_ann": float(hold.mean() * 12),
        "holdout_months": len(hold), "holdout_percentile_of_selected": hold_rank,
        "wf_ir": information_ratio(wf), "wf_contribution_ann": float(wf.mean() * 12) if len(wf) else np.nan,
        "wf_months": len(wf), "wf_picks": picks,
        "pbo": pbo_cscv(c.dropna(axis=1, how="any")),
        "dsr_full_sample_best": deflated_sharpe(c[select_best(c, pd.Series(True, index=c.index))], trial_sr),
        "trials": c.shape[1],
    }
