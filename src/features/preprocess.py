"""Cross-sectional preprocessing, performed independently at each rebalance date.

Nothing here looks across dates: statistics (median, MAD, ranks) come from the single cross-section passed in,
so normalization cannot leak information from future periods.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MAD_SCALE = 1.4826


def robust_z(x: pd.Series, clip: float | None = 5.0) -> pd.Series:
    """(x - median) / (1.4826 * MAD); falls back to std when MAD is 0; winsorized at +/- clip then re-centred."""
    x = x.astype(float)
    valid = x.dropna()
    if len(valid) < 3:
        return pd.Series(np.nan, index=x.index)
    med = valid.median()
    mad = (valid - med).abs().median() * MAD_SCALE
    scale = mad if mad > 1e-12 else valid.std(ddof=0)
    if not scale or scale < 1e-12:
        return pd.Series(0.0, index=x.index).where(x.notna())
    z = (x - med) / scale
    if clip is not None:
        z = z.clip(-clip, clip)
        # re-standardize after winsorizing so each feature has comparable spread
        v = z.dropna()
        mad2 = (v - v.median()).abs().median() * MAD_SCALE
        s2 = mad2 if mad2 > 1e-12 else v.std(ddof=0)
        if s2 and s2 > 1e-12:
            z = (z - v.median()) / s2
    return z


def pct_rank(x: pd.Series) -> pd.Series:
    """Percentile rank in (0, 1]; NaN stays NaN."""
    return x.rank(pct=True, method="average")


def normalize_feature(x: pd.Series, groups: pd.Series | None, clip: float, min_group_size: int) -> pd.Series:
    """Robust z within sector group when the group is large enough, else universe-wide."""
    if groups is None:
        return robust_z(x, clip)
    out = pd.Series(np.nan, index=x.index)
    universe_z = robust_z(x, clip)
    for _g, idx in groups.groupby(groups).groups.items():
        sub = x.loc[idx]
        if sub.notna().sum() >= min_group_size:
            out.loc[idx] = robust_z(sub, clip)
        else:
            out.loc[idx] = universe_z.loc[idx]
    ungrouped = groups.isna()
    out[ungrouped] = universe_z[ungrouped]
    return out


def feature_applicable(feature_cfg: dict, group: str | None) -> bool:
    only = feature_cfg.get("only_groups")
    excl = feature_cfg.get("exclude_groups", [])
    if only is not None and group not in only:
        return False
    return group not in excl


def family_scores(features: pd.DataFrame, groups: pd.Series, factors_cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame,
                                                                                         dict]:
    """Normalize candidate features and aggregate them into family z-scores and percentiles.

    ``features``: one cross-section (index = symbol). Returns (family_z, family_pct, diagnostics).
    """
    pp = factors_cfg["preprocessing"]
    clip, min_cov = pp["winsorize_mad"], pp["min_coverage"]
    grp = groups.reindex(features.index) if pp.get("sector_relative", True) else None
    fam_z, diag = {}, {"dropped_low_coverage": [], "coverage": {}}
    for family, feats in factors_cfg["families"].items():
        zs = []
        for feat, fcfg in feats.items():
            if feat not in features:
                continue
            x = features[feat].astype(float) * float(fcfg.get("direction", 1))
            applicable = groups.reindex(features.index).map(lambda g, c=fcfg: feature_applicable(c, g))
            x = x.where(applicable.astype(bool))
            eligible = applicable.sum()
            coverage = x.notna().sum() / eligible if eligible else 0.0
            diag["coverage"][feat] = round(float(coverage), 3)
            if coverage < min_cov:
                diag["dropped_low_coverage"].append(feat)
                continue
            zs.append(normalize_feature(x, grp, clip, pp["min_group_size"]).rename(feat))
        if not zs:
            fam_z[family] = pd.Series(np.nan, index=features.index)
            continue
        zdf = pd.concat(zs, axis=1)
        count = zdf.notna().sum(axis=1)
        raw = zdf.mean(axis=1).where(count >= pp["min_features_per_family"])
        fam_z[family] = robust_z(raw, clip)
    fz = pd.DataFrame(fam_z)
    fp = fz.apply(pct_rank)
    return fz, fp, diag


def composite(family_z: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Weighted mean of available family z-scores (weights re-normalized per name), then robust z.

    Missing families are handled explicitly: their weight is redistributed, so a missing value is neither a
    reward nor an automatic penalty. Names with no weighted family at all get NaN.
    """
    w = pd.Series({k: float(v) for k, v in weights.items() if float(v) > 0 and k in family_z})
    if w.empty:
        return pd.Series(np.nan, index=family_z.index)
    z = family_z[w.index]
    mask = z.notna()
    num = (z.fillna(0.0) * w).sum(axis=1)
    den = (mask * w).sum(axis=1)
    raw = (num / den.where(den > 0))
    # require at least half of the total weight to be present
    raw = raw.where(den >= 0.5 * w.sum())
    return robust_z(raw, clip=None)
