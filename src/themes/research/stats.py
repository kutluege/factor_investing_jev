"""Statistical helpers for the theme research module: Newey-West (Bartlett) inference, winsorizing, OLS/WLS."""
from __future__ import annotations

import numpy as np
import pandas as pd


def nw_lags(horizon: int) -> int:
    """themes.yaml research.nw_lags = horizon_div_21_min_1 (monthly observations, overlapping h-session labels)."""
    return max(1, horizon // 21)


def _hac_meat(u: np.ndarray, lags: int) -> np.ndarray:
    """Bartlett-weighted long-run covariance of the rows of ``u`` (T x k), already demeaned / scores."""
    T = u.shape[0]
    s = u.T @ u
    for L in range(1, min(lags, T - 1) + 1):
        w = 1.0 - L / (lags + 1.0)
        g = u[L:].T @ u[:-L]
        s += w * (g + g.T)
    return s


def nw_mean(x, lags: int) -> dict:
    """Mean, Newey-West standard error and t-statistic of a time series (NaNs dropped)."""
    v = pd.Series(x, dtype=float).dropna().to_numpy()
    n = len(v)
    if n < 6:
        return {"mean": np.nan, "se": np.nan, "t": np.nan, "n": n}
    m = v.mean()
    lr = _hac_meat((v - m)[:, None], lags)[0, 0] / n
    se = np.sqrt(lr / n) if lr > 0 else np.nan
    return {"mean": float(m), "se": float(se), "t": float(m / se) if se and se > 0 else np.nan, "n": n}


def plain_t(x) -> float:
    v = pd.Series(x, dtype=float).dropna()
    if len(v) < 3 or v.std(ddof=1) == 0:
        return np.nan
    return float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))))


def nw_ols(y, X: pd.DataFrame, lags: int) -> pd.DataFrame:
    """Time-series OLS with intercept and Newey-West covariance. Returns coef, se, t per regressor ('alpha' first)."""
    df = pd.concat([pd.Series(y, name="__y"), X], axis=1).dropna()
    if len(df) < X.shape[1] + 6:
        return pd.DataFrame(columns=["coef", "se", "t"])
    Y = df["__y"].to_numpy(float)
    Z = np.column_stack([np.ones(len(df)), df[X.columns].to_numpy(float)])
    beta, *_ = np.linalg.lstsq(Z, Y, rcond=None)
    e = Y - Z @ beta
    bread = np.linalg.pinv(Z.T @ Z)
    cov = bread @ _hac_meat(Z * e[:, None], lags) @ bread
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    names = ["alpha"] + list(X.columns)
    return pd.DataFrame({"coef": beta, "se": se, "t": beta / np.where(se > 0, se, np.nan)}, index=names)


def winsorize(x: pd.Series, lo: float, hi: float) -> pd.Series:
    v = x.dropna()
    if v.empty:
        return x
    return x.clip(v.quantile(lo), v.quantile(hi))


def cs_regression(y: np.ndarray, X: np.ndarray, w: np.ndarray | None = None) -> tuple[np.ndarray, float, float]:
    """Cross-sectional (W)LS with intercept. Returns (coefficients incl. intercept, R^2, adjusted R^2)."""
    n, k = X.shape
    Z = np.column_stack([np.ones(n), X])
    if w is not None:
        sw = np.sqrt(w)
        Zw, yw = Z * sw[:, None], y * sw
    else:
        Zw, yw = Z, y
    b, *_ = np.linalg.lstsq(Zw, yw, rcond=None)
    resid = yw - Zw @ b
    ybar = np.average(y, weights=w) if w is not None else y.mean()
    tss = float((((y - ybar) * (np.sqrt(w) if w is not None else 1.0)) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / tss if tss > 0 else np.nan
    adj = 1.0 - (1.0 - r2) * (n - 1) / (n - k - 1) if n - k - 1 > 0 else np.nan
    return b, r2, adj
