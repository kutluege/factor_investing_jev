"""Overfitting controls and honest benchmarks.

* Equal-weight universe benchmark: the natural hurdle for a factor model (the literature benchmarks long-only factor
  portfolios against the equal-weighted universe, not a cap-weighted index).
* Probability of backtest overfitting (PBO) via combinatorially symmetric cross-validation (Bailey, Borwein,
  Lopez de Prado & Zhu 2017).
* Deflated Sharpe ratio (Bailey & Lopez de Prado 2014), correcting the best Sharpe for the number of trials.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, norm, skew

from src.model.scoring import ScoreCache, universe_mask

EULER_GAMMA = 0.5772156649


def ew_universe_benchmark(cache: ScoreCache, close: pd.DataFrame, min_mcap: float, min_adv: float,
                          initial: float = 10_000.0, start: pd.Timestamp | None = None) -> pd.Series:
    """Daily equity of an equal-weighted, monthly rebalanced portfolio of every eligible name (no costs)."""
    dates = [d for d in cache.dates if start is None or d >= start]
    if not dates:
        return pd.Series(dtype=float)
    rets = close.pct_change(fill_method=None)
    equity, value = [], initial
    idx = close.index
    for i, d in enumerate(dates):
        g = cache.by_date[d]
        members = [s for s in g[universe_mask(g, min_mcap, min_adv)].index if s in close.columns]
        end = dates[i + 1] if i + 1 < len(dates) else idx[-1]
        window = rets.loc[(idx > d) & (idx <= end), members]
        if window.empty or not members:
            continue
        # buy-and-hold within the month: weights drift with returns; delisted names contribute 0 afterwards
        growth = (1 + window.fillna(0.0)).cumprod()
        path = growth.mean(axis=1) * value
        equity.append(path)
        value = float(path.iloc[-1])
    if not equity:
        return pd.Series(dtype=float)
    out = pd.concat(equity)
    return pd.concat([pd.Series([initial], index=[dates[0]]), out[~out.index.duplicated()]])


def monthly_returns_matrix(equities: dict[str, pd.Series], start: pd.Timestamp | None = None) -> pd.DataFrame:
    cols = {}
    for k, e in equities.items():
        e = e.dropna()
        if start is not None:
            e = e[e.index >= start]
        if len(e) > 40:
            cols[k] = e.resample("ME").last().pct_change().dropna()
    return pd.DataFrame(cols).dropna(how="any")


def pbo_cscv(returns: pd.DataFrame, n_blocks: int = 16, max_combos: int = 5000, seed: int = 0) -> dict:
    """Probability that the in-sample-best configuration ranks below the median out of sample."""
    T, N = returns.shape
    if N < 2 or T < n_blocks * 2:
        return {"pbo": None, "reason": f"need >= {n_blocks * 2} months and >= 2 configs (have {T}, {N})"}
    blocks = np.array_split(np.arange(T), n_blocks)
    combos = list(combinations(range(n_blocks), n_blocks // 2))
    rng = np.random.default_rng(seed)
    if len(combos) > max_combos:
        combos = [combos[i] for i in rng.choice(len(combos), max_combos, replace=False)]
    R = returns.to_numpy()
    logits = []
    for is_blocks in combos:
        is_idx = np.concatenate([blocks[b] for b in is_blocks])
        oos_idx = np.concatenate([blocks[b] for b in range(n_blocks) if b not in is_blocks])
        is_sr = R[is_idx].mean(0) / (R[is_idx].std(0, ddof=1) + 1e-12)
        oos_sr = R[oos_idx].mean(0) / (R[oos_idx].std(0, ddof=1) + 1e-12)
        best = int(np.argmax(is_sr))
        rank = (oos_sr < oos_sr[best]).sum() + 0.5 * ((oos_sr == oos_sr[best]).sum() - 1) + 1
        w = rank / (N + 1)
        logits.append(np.log(w / (1 - w)))
    logits = np.array(logits)
    return {"pbo": float((logits <= 0).mean()), "combinations": len(combos), "configs": N, "months": T,
            "median_logit": float(np.median(logits))}


def deflated_sharpe(best_returns: pd.Series, trial_sharpes: np.ndarray) -> dict:
    """Probability that the true (monthly) Sharpe of the selected strategy exceeds the best of N random trials."""
    r = best_returns.dropna().to_numpy()
    T = len(r)
    if T < 24 or len(trial_sharpes) < 2:
        return {"dsr": None, "reason": "insufficient data"}
    sr = r.mean() / r.std(ddof=1)
    g3, g4 = skew(r), kurtosis(r, fisher=False)
    n = len(trial_sharpes)
    var_sr = float(np.var(trial_sharpes, ddof=1))
    sr0 = np.sqrt(var_sr) * ((1 - EULER_GAMMA) * norm.ppf(1 - 1 / n) + EULER_GAMMA * norm.ppf(1 - 1 / (n * np.e)))
    denom = np.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    dsr = norm.cdf((sr - sr0) * np.sqrt(T - 1) / denom)
    return {"dsr": float(dsr), "monthly_sharpe": float(sr), "annualized_sharpe": float(sr * np.sqrt(12)),
            "expected_max_sharpe_of_trials": float(sr0), "trials": n, "months": T}
