"""themes_v1 characteristics and stage flags (THEMES_SPEC §4, §5.2). All inputs are point-in-time.

- stage: ``pre_profit`` when TTM operating cash flow <= 0 (all themes); biotech ``clinical`` when pre_profit or TTM
  revenue < threshold, else ``commercial``; otherwise ``profitable``.
- profitable_growth: rank(revenue_yoy) + rank(fcf_margin) within the scoring cross-section, profitable firms only.
- oil_beta_trend: beta_oil x sign(oil 126-session return); beta_oil from a 104-week regression
  r_i = a + b_m r_SPY + b_oil r_oil (weekly returns up to the rebalance date). The oil series is Brent (BZUSD):
  WTI (CLUSD) requires a higher FMP plan (verified 2026-09-30, HTTP 402); see reports/themes/gate_decisions.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

OIL_SYMBOL = "BZUSD"
MARKET_SYMBOL = "SPY"


def stage_flags(ocf_ttm: pd.Series, revenue_ttm: pd.Series, theme: pd.Series, biotech_threshold: float,
                total_assets: pd.Series | None = None) -> pd.Series:
    """'pre_profit' | 'profitable' | 'clinical' | 'commercial' (biotech) | 'unknown'.

    Missing OCF -> pre_profit only if revenue is also missing. 'unknown' when OCF, revenue and total assets are all
    missing on the date: no usable USD XBRL statements (e.g. a 10-K filer reporting in CAD), so the firm is not
    scored (v2 data fix; previously such firms were labelled pre_profit)."""
    pre = (ocf_ttm <= 0) | (ocf_ttm.isna() & revenue_ttm.isna())
    out = pd.Series(np.where(pre, "pre_profit", "profitable"), index=ocf_ttm.index)
    bio = theme == "biotech"
    clinical = pre | (revenue_ttm.fillna(0) < biotech_threshold)
    out[bio] = np.where(clinical[bio], "clinical", "commercial")
    if total_assets is not None:
        out[ocf_ttm.isna() & revenue_ttm.isna() & total_assets.reindex(ocf_ttm.index).isna()] = "unknown"
    return out


def profitable_growth(revenue_yoy: pd.Series, fcf_margin: pd.Series, stage: pd.Series) -> pd.Series:
    """Sum of percentile ranks, computed only among profitable firms (NaN elsewhere)."""
    mask = stage.isin(["profitable", "commercial"])
    ry = revenue_yoy.where(mask).rank(pct=True)
    fm = fcf_margin.where(mask).rank(pct=True)
    return (ry + fm).where(mask & ry.notna() & fm.notna())


def weekly_returns(close: pd.DataFrame) -> pd.DataFrame:
    w = close.resample("W-FRI").last()
    return w.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)


def oil_beta_trend_at(close: pd.DataFrame, market: pd.Series, oil: pd.Series, at: pd.Timestamp,
                      weeks: int = 104, min_weeks: int = 80, trend_sessions: int = 126) -> pd.Series:
    """beta_oil x sign(oil trend) per symbol, from data up to ``at`` only."""
    c = close.loc[:at]
    m, o = market.loc[:at].dropna(), oil.loc[:at].dropna()
    if len(o) <= trend_sessions:
        return pd.Series(dtype=float)
    trend = np.sign(o.iloc[-1] / o.iloc[-1 - trend_sessions] - 1.0)
    wr = weekly_returns(c).tail(weeks)
    wm = weekly_returns(m.to_frame("m"))["m"].reindex(wr.index)
    wo = weekly_returns(o.to_frame("o"))["o"].reindex(wr.index)
    ok_x = wm.notna() & wo.notna()
    Y = wr[ok_x].to_numpy(float)
    X = np.column_stack([np.ones(int(ok_x.sum())), wm[ok_x].to_numpy(float), wo[ok_x].to_numpy(float)])
    out = {}
    complete = ~np.isnan(Y).any(axis=0)
    if complete.any() and len(X) >= min_weeks:
        coef, *_ = np.linalg.lstsq(X, Y[:, complete], rcond=None)
        for sym, b in zip(wr.columns[complete], coef[2], strict=True):
            out[sym] = float(b * trend)
    for j in np.where(~complete)[0]:
        ok = ~np.isnan(Y[:, j])
        if ok.sum() < min_weeks:
            continue
        coef, *_ = np.linalg.lstsq(X[ok], Y[ok, j], rcond=None)
        out[wr.columns[j]] = float(coef[2] * trend)
    return pd.Series(out, dtype=float)


def beta_252d_at(close: pd.DataFrame, market: pd.Series, at: pd.Timestamp, n: int = 252,
                 min_obs: int = 200) -> pd.Series:
    """Fama-MacBeth control (THEMES_SPEC §7.6): CAPM beta on daily returns, last ``n`` sessions up to ``at``,
    at least ``min_obs`` paired observations. Market proxy: SPY."""
    r = close.loc[:at].pct_change(fill_method=None).tail(n)
    m = market.loc[:at].pct_change(fill_method=None).reindex(r.index)
    out = {}
    for sym in r.columns:
        ok = r[sym].notna() & m.notna()
        if ok.sum() < min_obs:
            continue
        x, y = m[ok].to_numpy(float), r.loc[ok, sym].to_numpy(float)
        var = x.var(ddof=1)
        if var > 0:
            out[sym] = float(np.cov(x, y, ddof=1)[0, 1] / var)
    return pd.Series(out, dtype=float)


def size_ln_mcap(market_cap: pd.Series) -> pd.Series:
    """Fama-MacBeth size control: ln(market cap in USD); non-positive caps -> NaN."""
    return np.log(market_cap.where(market_cap > 0))
