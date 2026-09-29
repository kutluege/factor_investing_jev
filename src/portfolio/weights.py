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


def target_weights(symbols: list[str], method: str, final_score: pd.Series, vol: pd.Series,
                   max_weight: float = 0.25) -> pd.Series:
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
    return cap_weights(raw, max_weight)
