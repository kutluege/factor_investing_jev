"""Portfolio weighting methods."""
from __future__ import annotations

import numpy as np
import pandas as pd

METHODS = ("equal", "score", "inverse_vol", "score_inverse_vol")


def cap_weights(w: pd.Series, cap: float, max_iter: int = 50) -> pd.Series:
    """Iteratively cap weights at ``cap`` and redistribute the excess proportionally."""
    w = w / w.sum()
    if cap * len(w) < 1.0:  # cap infeasible (too few names): equal weight is the closest feasible solution
        return pd.Series(1.0 / len(w), index=w.index)
    for _ in range(max_iter):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess = (w[over] - cap).sum()
        w[over] = cap
        under = ~over
        w[under] += excess * w[under] / w[under].sum()
    return w


def cap_sector_weights(w: pd.Series, sectors: pd.Series, sector_cap: float, pos_cap: float,
                       max_iter: int = 50) -> pd.Series:
    """Scale down sectors above ``sector_cap`` and redistribute to other sectors (respecting ``pos_cap``)."""
    sec = sectors.reindex(w.index).fillna("unknown")
    n_sec = sec.nunique()
    cap = max(sector_cap, 1.0 / n_sec) if n_sec else 1.0  # infeasible caps are relaxed
    w = w / w.sum()
    for _ in range(max_iter):
        tot = w.groupby(sec).sum()
        over = tot[tot > cap + 1e-9]
        if over.empty:
            break
        for s_name, t in over.items():
            m = sec == s_name
            w[m] *= cap / t
        free = w.sum()
        excess = 1.0 - free
        under = ~sec.isin(over.index) & (w < pos_cap - 1e-12)
        if not under.any():
            break
        w[under] += excess * w[under] / w[under].sum()
        w = w.clip(upper=pos_cap)
        w = w / w.sum()
    return w


def target_weights(symbols: list[str], method: str, final_score: pd.Series, vol: pd.Series,
                   max_weight: float = 0.25, sectors: pd.Series | None = None,
                   sector_cap: float | None = None) -> pd.Series:
    if not symbols:
        return pd.Series(dtype=float)
    idx = pd.Index(symbols)
    if method == "equal":
        raw = pd.Series(1.0, index=idx)
    else:
        s = final_score.reindex(idx)
        s = (s - s.min() + 0.5).fillna(0.5) if s.notna().any() else pd.Series(1.0, index=idx)  # positive scale
        v = vol.reindex(idx)
        v = v.fillna(v.median() if v.notna().any() else 0.4).clip(lower=0.05)
        if method == "score":
            raw = s
        elif method == "inverse_vol":
            raw = 1.0 / v
        elif method == "score_inverse_vol":
            raw = s / v
        else:
            raise ValueError(f"unknown weighting method {method!r}; use one of {METHODS}")
    raw = raw.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
    if raw.sum() <= 0:
        raw = pd.Series(1.0, index=idx)
    w = cap_weights(raw, max_weight)
    if sectors is not None and sector_cap is not None and sector_cap < 1.0:
        w = cap_sector_weights(w, sectors, sector_cap, max_weight)
    return w
