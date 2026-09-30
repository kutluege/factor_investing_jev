"""Theme research analyses (THEMES_SPEC §7.1-§7.8, Bali-Engle-Murray order).

Every analysis is two-step: (1) a cross-sectional statistic per rebalance date, (2) its time-series average with
Newey-West inference. Inputs are one "scope" panel (a theme, a subtheme or the pooled themes) with columns
rebalance_date, symbol, the factors, labels, market_cap, beta_252d, size_ln_mcap, score, subtheme.
Return-related analyses use direction-signed factors (positive = the expected direction); descriptive statistics,
correlations and VIF use raw values. Nothing here selects or weights factors (§7.9).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import ndtri
from scipy.stats import rankdata

from src.features.preprocess import rank_normal
from src.themes.research.stats import cs_regression, nw_mean, nw_ols, plain_t, winsorize

QUANTS = {"p5": 0.05, "p25": 0.25, "median": 0.5, "p75": 0.75, "p95": 0.95}


def _dates(panel: pd.DataFrame):
    return panel.groupby("rebalance_date", sort=True)


# --- 7.1 descriptive statistics ---------------------------------------------------------------------------------

def descriptive(panel: pd.DataFrame, factors: list[str], wins: tuple[float, float]) -> pd.DataFrame:
    rows = {f: [] for f in factors}
    for _, g in _dates(panel):
        for f in factors:
            x = winsorize(g[f].astype(float), *wins).dropna()
            if len(x) < 5:
                continue
            r = {"mean": x.mean(), "std": x.std(ddof=1), "skew": x.skew(), "kurt": x.kurt(), "min": x.min(),
                 "max": x.max(), "n": len(x)}
            r.update({k: x.quantile(q) for k, q in QUANTS.items()})
            rows[f].append(r)
    out = {}
    for f, rs in rows.items():
        if not rs:
            continue
        df = pd.DataFrame(rs)
        s = df.mean()
        # drift: how much the cross-sectional mean moves over time relative to the typical dispersion
        s["mean_drift"] = df["mean"].std(ddof=1) / df["std"].mean() if df["std"].mean() > 0 else np.nan
        s["months"] = len(df)
        out[f] = s
    cols = ["mean", "std", "skew", "kurt", "min", "p5", "p25", "median", "p75", "p95", "max", "n", "mean_drift",
            "months"]
    return pd.DataFrame(out).T.reindex(columns=cols)


# --- 7.2 correlation, VIF, orthogonalization ----------------------------------------------------------------------

def correlations(panel: pd.DataFrame, factors: list[str], wins: tuple[float, float]) -> tuple[pd.DataFrame, pd.DataFrame,
                                                                                               pd.DataFrame]:
    """Time-averaged monthly cross-sectional Pearson (winsorized) and Spearman matrices; combined matrix with
    Pearson in the lower and Spearman in the upper triangle."""
    ps, ss = [], []
    for _, g in _dates(panel):
        x = g[factors].astype(float)
        if len(x) < 10:
            continue
        ps.append(x.apply(lambda c: winsorize(c, *wins)).corr(method="pearson", min_periods=10))
        ss.append(x.rank().corr(method="pearson", min_periods=10))
    if not ps:
        empty = pd.DataFrame(index=factors, columns=factors, dtype=float)
        return empty, empty, empty
    p = pd.concat(ps).groupby(level=0).mean().reindex(index=factors, columns=factors)
    s = pd.concat(ss).groupby(level=0).mean().reindex(index=factors, columns=factors)
    arr = p.to_numpy(copy=True)
    iu = np.triu_indices(len(factors), 1)
    arr[iu] = s.to_numpy()[iu]
    return p, s, pd.DataFrame(arr, index=factors, columns=factors)


def redundant_pairs(pearson: pd.DataFrame, spearman: pd.DataFrame, threshold: float) -> pd.DataFrame:
    rows = []
    f = list(pearson.index)
    for i in range(len(f)):
        for j in range(i + 1, len(f)):
            p, s = pearson.iat[i, j], spearman.iat[i, j]
            if (abs(p) > threshold) or (abs(s) > threshold):
                note = ""
                if abs(s) - abs(p) > 0.15:
                    note = "Spearman >> Pearson: doğrusal olmayan monoton ilişki"
                elif abs(p) - abs(s) > 0.15:
                    note = "Pearson >> Spearman: uç değer sorunu"
                rows.append({"a": f[i], "b": f[j], "pearson": p, "spearman": s, "note": note})
    return pd.DataFrame(rows, columns=["a", "b", "pearson", "spearman", "note"])


def vif(panel: pd.DataFrame, factors: list[str], min_n: int = 30) -> pd.Series:
    """Time-average of monthly VIFs on rank-normal values (complete rows)."""
    acc = {f: [] for f in factors}
    for _, g in _dates(panel):
        x = g[factors].apply(rank_normal).dropna()
        if len(x) < max(min_n, len(factors) + 5):
            continue
        X = x.to_numpy(float)
        for j, f in enumerate(factors):
            others = np.delete(X, j, axis=1)
            _, r2, _ = cs_regression(X[:, j], others)
            if np.isfinite(r2) and r2 < 1:
                acc[f].append(1.0 / (1.0 - r2))
    return pd.Series({f: float(np.mean(v)) if v else np.nan for f, v in acc.items()})


def orthogonal_residual(g: pd.DataFrame, factor: str, score: str = "score") -> pd.Series:
    """One date: residual of the rank-normal factor on the rank-normal theme score and subtheme dummies."""
    y = rank_normal(g[factor].astype(float))
    X = pd.DataFrame({"score": rank_normal(g[score].astype(float))})
    if "subtheme" in g and g["subtheme"].nunique() > 1:
        X = X.join(pd.get_dummies(g["subtheme"], drop_first=True, dtype=float))
    ok = y.notna() & X.notna().all(axis=1)
    out = pd.Series(np.nan, index=g.index)
    if ok.sum() < X.shape[1] + 10:
        return out
    b, _, _ = cs_regression(y[ok].to_numpy(float), X[ok].to_numpy(float))
    Z = np.column_stack([np.ones(ok.sum()), X[ok].to_numpy(float)])
    out[ok] = y[ok].to_numpy(float) - Z @ b
    return out


def orthogonal_residuals(panel: pd.DataFrame, factor: str, score: str = "score") -> pd.Series:
    """All dates: residual of the rank-normal factor on the rank-normal score and subtheme dummies (per date)."""
    out = np.full(len(panel), np.nan)
    sub = pd.factorize(panel["subtheme"])[0] if "subtheme" in panel else np.zeros(len(panel), int)
    for _, a, pos in _groups(panel, [factor, score]):
        ok = ~np.isnan(a).any(axis=1)
        if ok.sum() < 12:
            continue
        codes = sub[pos][ok]
        levels = np.unique(codes)
        X = [_rank_normal(a[ok, 1])] + [(codes == c).astype(float) for c in levels[1:]]
        X = np.column_stack(X)
        if ok.sum() < X.shape[1] + 10:
            continue
        y = _rank_normal(a[ok, 0])
        Z = np.column_stack([np.ones(len(y)), X])
        b, *_ = np.linalg.lstsq(Z, y, rcond=None)
        out[pos[ok]] = y - Z @ b
    return pd.Series(out, index=panel.index)


# --- 7.3 persistence ------------------------------------------------------------------------------------------------

def persistence(panel: pd.DataFrame, factors: list[str], lags: list[int], min_n: int = 15) -> pd.DataFrame:
    dates = sorted(panel["rebalance_date"].unique())
    by = {d: g.set_index("symbol") for d, g in _dates(panel)}
    out = {}
    for f in factors:
        row = {}
        for L in lags:
            cs = []
            for i in range(len(dates) - L):
                a, b = by[dates[i]][f], by[dates[i + L]][f]
                j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
                if len(j) >= min_n:
                    cs.append(j["a"].rank().corr(j["b"].rank()))
            row[f"rho_{L}"] = float(np.mean(cs)) if cs else np.nan
        out[f] = row
    return pd.DataFrame(out).T


# --- numpy per-date helpers (the research run makes thousands of cross-sectional passes) ------------------------

def _groups(panel: pd.DataFrame, cols: list[str]):
    """(date, 2-D float array of ``cols``, row positions) per rebalance date, sorted by date."""
    arr = panel[cols].to_numpy(float)
    for d, pos in sorted(panel.groupby("rebalance_date").indices.items()):
        yield d, arr[pos], pos


def _rank_normal(a: np.ndarray) -> np.ndarray:
    return ndtri((rankdata(a) - 0.5) / len(a))


def _wins(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    ql, qh = np.quantile(a, [lo, hi])
    return np.clip(a, ql, qh)


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = rankdata(x), rankdata(y)
    sx, sy = rx.std(), ry.std()
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy)) if sx > 0 and sy > 0 else np.nan


def _bucket_np(x: np.ndarray, n: int) -> np.ndarray:
    """Dynamic breakpoints on the date's own ranks (ties broken by order): 1 (low) .. n (high)."""
    r = rankdata(x, method="ordinal") / len(x)
    return np.clip(np.ceil(r * n), 1, n).astype(int)


def _bucket(x: pd.Series, n: int) -> pd.Series:
    return pd.Series(_bucket_np(x.to_numpy(float), n), index=x.index)


# --- 7.7 rank IC -----------------------------------------------------------------------------------------------------

def rank_ic_series(panel: pd.DataFrame, factor: str, label: str, min_n: int) -> pd.Series:
    """Monthly Spearman correlation between the (signed) factor and the forward return."""
    vals = {}
    for d, a, _ in _groups(panel, [factor, label]):
        a = a[~np.isnan(a).any(axis=1)]
        if len(a) >= min_n:
            vals[d] = _spearman(a[:, 0], a[:, 1])
    return pd.Series(vals, dtype=float)


def ic_summary(ic: pd.Series, horizon: int) -> dict:
    lag = max(1, horizon // 21)
    s = nw_mean(ic, lag)
    nonoverlap = ic.iloc[::lag] if lag > 1 else ic
    return {"ic_mean": s["mean"], "ic_nw_t": s["t"], "ic_nonoverlap_t": plain_t(nonoverlap),
            "ic_hit_rate": float((ic > 0).mean()) if len(ic) else np.nan, "months": s["n"]}


# --- 7.4 univariate portfolio sorts ------------------------------------------------------------------------------

def sort_portfolios(panel: pd.DataFrame, factor: str, label: str, min_n: int, n_ge50: int = 5,
                    n_lt50: int = 3) -> pd.DataFrame:
    """Per date: EW and VW returns of each portfolio, top - bottom (mimic) and top - scope mean."""
    rows = []
    for d, a, _ in _groups(panel, [factor, label, "market_cap"]):
        a = a[~np.isnan(a[:, :2]).any(axis=1)]
        if len(a) < min_n:
            continue
        n = n_ge50 if len(a) >= 50 else n_lt50
        b = _bucket_np(a[:, 0], n)
        y = a[:, 1]
        w = np.where(a[:, 2] > 0, a[:, 2], 0.0)
        cnt = np.bincount(b, minlength=n + 1)[1:]
        ew = np.bincount(b, weights=y, minlength=n + 1)[1:] / np.where(cnt > 0, cnt, np.nan)
        wsum = np.bincount(b, weights=w, minlength=n + 1)[1:]
        vw = np.bincount(b, weights=y * w, minlength=n + 1)[1:] / np.where(wsum > 0, wsum, np.nan)
        r = {"rebalance_date": d, "n_ports": n, "n": len(a)}
        for k in range(n):
            r[f"ew_p{k + 1}"], r[f"vw_p{k + 1}"] = ew[k], vw[k]
        r["mimic_ew"], r["mimic_vw"] = ew[-1] - ew[0], vw[-1] - vw[0]
        r["top_minus_mean_ew"] = ew[-1] - y.mean()
        r["top_ew"], r["top_vw"] = ew[-1], vw[-1]
        rows.append(r)
    return pd.DataFrame(rows)


def sort_summary(ts: pd.DataFrame, horizon: int) -> dict:
    lag = max(1, horizon // 21)
    if ts.empty:
        return {}
    n = int(ts["n_ports"].mode().iloc[0])
    ts = ts[ts["n_ports"] == n]
    out = {"n_ports": n, "months": len(ts)}
    means = []
    for k in range(1, n + 1):
        s = nw_mean(ts[f"ew_p{k}"], lag)
        out[f"ew_p{k}"] = s["mean"]
        means.append(s["mean"])
    diffs = np.diff(means)
    out["monotonic"] = bool(np.all(diffs > 0)) if np.isfinite(diffs).all() else False
    for c in ("mimic_ew", "mimic_vw", "top_minus_mean_ew"):
        s = nw_mean(ts[c], lag)
        out[c], out[f"{c}_t"] = s["mean"], s["t"]
    return out


ALPHA_MODELS = {
    "capm": ["ff_mkt_rf"],
    "ff3": ["ff_mkt_rf", "ff_smb", "ff_hml"],
    "carhart4": ["ff_mkt_rf", "ff_smb", "ff_hml", "ff_mom"],
    "ff5_mom": ["ff_mkt_rf", "ff5_smb", "ff5_hml", "ff_rmw", "ff_cma", "ff_mom"],
}


def alphas(ts: pd.DataFrame, french: pd.DataFrame, models: list[str]) -> pd.DataFrame:
    """Monthly alphas of the top portfolio (excess of RF) and the mimic spread, 21-session labels only.

    A 21-session label starting at the last session of month m is aligned to the month-end of m+1."""
    if ts.empty:
        return pd.DataFrame()
    t = ts.set_index(pd.DatetimeIndex(ts["rebalance_date"]) + pd.offsets.MonthEnd(1))
    f = french.reindex(t.index)
    rows = []
    for name in models:
        X = f[ALPHA_MODELS[name]]
        for series, y in (("top_ew", t["top_ew"] - f["ff_rf"]), ("mimic_ew", t["mimic_ew"])):
            r = nw_ols(y, X, lags=1)
            if r.empty:
                continue
            rows.append({"model": name, "series": series, "alpha_monthly": r.at["alpha", "coef"],
                         "alpha_t": r.at["alpha", "t"], "months": int(y.notna().sum())})
    return pd.DataFrame(rows)


# --- 7.5 dependent bivariate sort -------------------------------------------------------------------------------

def dependent_sort(panel: pd.DataFrame, factor: str, label: str, score: str = "score", min_n: int = 15,
                   n: int = 3) -> pd.DataFrame:
    """Per date: terciles of the theme score, then terciles of the factor within each; top - bottom per score
    tercile and their average."""
    rows = []
    for d, a, _ in _groups(panel, [factor, label, score]):
        a = a[~np.isnan(a).any(axis=1)]
        if len(a) < max(min_n, 3 * n * 2):
            continue
        sb = _bucket_np(a[:, 2], n)
        r = {"rebalance_date": d}
        diffs = []
        for k in range(1, n + 1):
            sub = a[sb == k]
            fb = _bucket_np(sub[:, 0], n)
            hi, lo = sub[fb == n, 1], sub[fb == 1, 1]
            diff = hi.mean() - lo.mean() if len(hi) and len(lo) else np.nan
            r[f"score_t{k}"] = diff
            diffs.append(diff)
        r["avg_diff"] = float(np.nanmean(diffs)) if np.isfinite(diffs).any() else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


# --- 7.6 Fama-MacBeth -----------------------------------------------------------------------------------------------

def fama_macbeth(panel: pd.DataFrame, factors: list[str], label: str, controls: list[str], variant: str,
                 wins: tuple[float, float], min_n: int) -> dict:
    """Monthly cross-sectional regressions label ~ factors + controls. Variants: ols_rank_normal (main),
    ols_winsorized_raw, wls_sqrt_mcap (rank-normal regressors, weights sqrt(market cap))."""
    cols = factors + controls
    k = len(cols)
    coefs, r2s, adj, sds, ds = [], [], [], [], []
    for d, a, _ in _groups(panel, cols + [label, "market_cap"]):
        a = a[~np.isnan(a[:, :k + 1]).any(axis=1)]
        if variant == "wls_sqrt_mcap":
            a = a[a[:, k + 1] > 0]
        if len(a) < max(min_n, k + 5):
            continue
        if variant == "ols_winsorized_raw":
            X = np.column_stack([_wins(a[:, j], *wins) for j in range(k)])
        else:
            X = np.column_stack([_rank_normal(a[:, j]) for j in range(k)])
        w = np.sqrt(a[:, k + 1]) if variant == "wls_sqrt_mcap" else None
        y = _wins(a[:, k], *wins)
        b, r2, ar2 = cs_regression(y, X, w)
        coefs.append(b[1:])
        r2s.append(r2)
        adj.append(ar2)
        sds.append(X[:, :len(factors)].std(axis=0, ddof=1))
        ds.append(d)
    if not coefs:
        return {}
    C = pd.DataFrame(coefs, index=ds, columns=cols)
    sd = pd.Series(np.mean(sds, axis=0), index=factors)
    return {"coefs": C, "sd": sd, "r2": float(np.nanmean(r2s)), "adj_r2": float(np.nanmean(adj)), "months": len(C)}


def fm_summary(fm: dict, factors: list[str], horizon: int, variant: str) -> pd.DataFrame:
    if not fm:
        return pd.DataFrame()
    lag = max(1, horizon // 21)
    rows = []
    for f in factors:
        s = nw_mean(fm["coefs"][f], lag)
        econ = s["mean"] if variant != "ols_winsorized_raw" else s["mean"] * fm["sd"][f]
        rows.append({"factor": f, "coef": s["mean"], "nw_t": s["t"], "economic_magnitude": econ,
                     "avg_r2": fm["r2"], "avg_adj_r2": fm["adj_r2"], "months": fm["months"]})
    return pd.DataFrame(rows)


# --- 7.8 stability ----------------------------------------------------------------------------------------------------

def bucket_means(series: pd.Series, buckets: dict[str, pd.Series]) -> dict:
    """Mean of a monthly series inside each boolean date mask (aligned on the series index)."""
    out = {}
    for name, mask in buckets.items():
        m = mask.reindex(series.index).fillna(False).astype(bool)
        out[name] = float(series[m].mean()) if m.any() else np.nan
    return out


def subperiod_masks(dates: pd.DatetimeIndex, periods: list[list[str]]) -> dict[str, pd.Series]:
    out = {}
    for a, b in periods:
        lo, hi = pd.Timestamp(a), pd.Timestamp(b) + pd.offsets.MonthEnd(0)
        out[f"{a}..{b}"] = pd.Series((dates >= lo) & (dates <= hi), index=dates)
    return out


def regime_masks(dates: pd.DatetimeIndex, market_close: pd.Series, vix_close: pd.Series | None) -> dict[str, pd.Series]:
    """Bull = SPY trailing 252-session return > 0 at the rebalance date; high VIX = VIX above its sample median."""
    m = market_close.dropna()
    ret12 = (m / m.shift(252) - 1.0).reindex(dates, method="ffill")
    out = {"bull": ret12 > 0, "bear": ret12 <= 0}
    if vix_close is not None and not vix_close.dropna().empty:
        v = vix_close.dropna().reindex(dates, method="ffill")
        med = v.median()
        out["vix_high"], out["vix_low"] = v > med, v <= med
    return {k: pd.Series(np.asarray(s, dtype=bool), index=dates) for k, s in out.items()}
