"""Literature-grounded characteristics (see docs/RESEARCH.md for definitions and sources).

All computations use data up to and including the rebalance date only.

Price-based
  max_ret_21d      Bali, Cakici & Whitelaw (2011) MAX: largest daily return over the last 21 sessions  [-]
  idio_vol_60d     Ang et al. (2006): volatility of daily returns net of beta x QQQ return, 60 sessions [-]
  spread_est       Abdi & Ranaldo (2017) close-high-low bid-ask spread estimate, 60 sessions (cost model)
  mom_12_7         Novy-Marx (2012) intermediate momentum                                            [+]
  res_mom_12_2     Blitz, Huij & Martens (2011) residual momentum: sum of residuals t-12..t-2 from a 36-month
                   regression on market and sector returns, scaled by their standard deviation        [+]
  season_ret       Heston & Sadka (2008): mean return in the upcoming calendar month over the prior 10 years [+]
  sector_mom_6m    Moskowitz & Grinblatt (1999) industry momentum (sector-group median 6m return)      [+]
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def price_extras(close: pd.DataFrame, raw_close: pd.DataFrame, high: pd.DataFrame, low: pd.DataFrame,
                 bench_close: pd.Series | None) -> dict[str, pd.DataFrame]:
    r = close.pct_change(fill_method=None)
    out = {"max_ret_21d": r.rolling(21, min_periods=15).max(),
           "mom_12_7": close.shift(147) / close.shift(252) - 1.0}
    if bench_close is not None:
        b = bench_close.reindex(close.index).pct_change(fill_method=None)
        cov = r.rolling(60, min_periods=45).cov(b)
        var_b = b.rolling(60, min_periods=45).var()
        beta = cov.div(var_b, axis=0)
        resid = r - beta.mul(b, axis=0)
        out["idio_vol_60d"] = resid.rolling(60, min_periods=45).std() * np.sqrt(TRADING_DAYS)
    # Abdi-Ranaldo: s^2 = 4 * E[(c_t - eta_t)(c_t - eta_{t+1})], eta = mid of log high/low; pairs end at t
    lc, eta = np.log(close), (np.log(high) + np.log(low)) / 2.0
    prod = 4.0 * (lc.shift(1) - eta.shift(1)) * (lc.shift(1) - eta)
    out["spread_est"] = np.sqrt(prod.rolling(60, min_periods=40).mean().clip(lower=0.0))
    return out


def monthly_returns(close: pd.DataFrame) -> pd.DataFrame:
    m = close.resample("ME").last()
    # a month without any trade for the symbol stays NaN (no stale carry-forward)
    traded = close.notna().resample("ME").sum() > 0
    return m.pct_change(fill_method=None).where(traded)


def residual_momentum(mret: pd.DataFrame, mkt: pd.Series, sector_map: dict[str, str], at: pd.Timestamp,
                      window: int = 36, min_obs: int = 24) -> pd.Series:
    """Blitz-Huij-Martens residual momentum at month-end ``at`` (uses months <= at only)."""
    hist = mret.loc[:at].tail(window)
    if len(hist) < min_obs:
        return pd.Series(dtype=float)
    m = mkt.reindex(hist.index)
    groups = pd.Series({s: sector_map.get(s) for s in hist.columns})
    sec_ret = pd.DataFrame({g: hist[cols].mean(axis=1) for g, cols in groups.groupby(groups).groups.items()})
    out: dict[str, float] = {}
    form_mask = np.zeros(len(hist), dtype=bool)
    form_mask[-12:-1] = True  # months t-12 .. t-2 (skip the most recent month)
    mv = m.to_numpy(float)
    Yall = hist.to_numpy(float)
    complete = ~np.isnan(Yall).any(axis=0) & ~np.isnan(mv).any()
    cols = np.array(hist.columns)

    def score(resid: np.ndarray, fmask: np.ndarray) -> np.ndarray:
        e = resid[fmask]
        sd = e.std(axis=0, ddof=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(sd > 0, e.sum(axis=0) / sd, np.nan)

    for g, members in groups.groupby(groups).groups.items():
        sv = sec_ret[g].to_numpy(float) if g in sec_ret else np.zeros(len(hist))
        idx = np.array([hist.columns.get_loc(s) for s in members])
        # fast path: stocks with a complete window share one design matrix -> one multi-RHS least squares
        full = idx[complete[idx]] if not np.isnan(sv).any() else np.array([], dtype=int)
        if len(full):
            X = np.column_stack([np.ones(len(hist)), mv, sv])
            Y = Yall[:, full]
            coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
            for sym, val in zip(cols[full], score(Y - X @ coef, form_mask), strict=True):
                if val == val:
                    out[sym] = float(val)
        # slow path: incomplete windows (IPOs, halts) need per-stock masking
        for j in idx[~np.isin(idx, full)]:
            ok = ~np.isnan(Yall[:, j]) & ~np.isnan(mv) & ~np.isnan(sv)
            if ok.sum() < min_obs or not ok[form_mask].all():
                continue
            X = np.column_stack([np.ones(ok.sum()), mv[ok], sv[ok]])
            coef, *_ = np.linalg.lstsq(X, Yall[ok, j], rcond=None)
            resid = np.full(len(hist), np.nan)
            resid[ok] = Yall[ok, j] - X @ coef
            val = score(resid[:, None], form_mask)[0]
            if val == val:
                out[cols[j]] = float(val)
    return pd.Series(out, dtype=float)


def seasonality(mret: pd.DataFrame, at: pd.Timestamp, years: int = 10, min_obs: int = 3) -> pd.Series:
    """Mean return in the upcoming calendar month over the previous ``years`` years (months <= at only)."""
    target_month = (at + pd.offsets.MonthEnd(1)).month
    hist = mret.loc[:at]
    same = hist[hist.index.month == target_month].tail(years)
    cnt = same.notna().sum()
    return same.mean().where(cnt >= min_obs)


def monthly_features(close: pd.DataFrame, bench_close: pd.Series | None, sector_map: dict[str, str],
                     dates: list[pd.Timestamp]) -> pd.DataFrame:
    mret = monthly_returns(close)
    mkt = monthly_returns(bench_close.to_frame("m"))["m"] if bench_close is not None else mret.mean(axis=1)
    rows = []
    for d in dates:
        at = d + pd.offsets.MonthEnd(0)
        rm = residual_momentum(mret, mkt, sector_map, at)
        se = seasonality(mret, at)
        f = pd.DataFrame({"res_mom_12_2": rm, "season_ret": se})
        f.index.name = "symbol"
        f["rebalance_date"] = d
        rows.append(f.reset_index())
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(
        columns=["symbol", "res_mom_12_2", "season_ret", "rebalance_date"])
