"""Theme scoring (THEMES_SPEC §6), one rebalance date at a time (no cross-date information).

1. Per theme and date, rank -> normal scores. Price signals are ranked within the theme; accounting ratios within
   the subtheme when it has >= 8 firms with the value, else within the theme.
2. Each firm uses the factor groups of its stage (``theme_factor_map``, plus ``subtheme_extra``).
3. Group score = mean of the firm's available factors in the group; theme score = equal-weight mean of groups,
   then robust z within the theme.
4. A factor whose coverage among the firms that use it is < ``min_coverage`` is dropped on that date; a firm with
   less than ``min_weight_present`` of its group weight present is not scored.
5. Weights are fixed; nothing is learned from returns.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.preprocess import rank_normal, robust_z
from src.themes.config import ThemesConfig

PRICE_SIGNALS = {"mom_12_1", "dist_52w_high", "idio_vol_60d", "max_ret_21d", "oil_beta_trend", "ear_3d"}
SUBTHEME_MIN_N = 8


def _normalize(x: pd.Series, subtheme: pd.Series, price_signal: bool) -> pd.Series:
    if price_signal:
        return rank_normal(x)
    out = rank_normal(x)
    for _, idx in subtheme.groupby(subtheme).groups.items():
        sub = x.loc[idx]
        if sub.notna().sum() >= SUBTHEME_MIN_N:
            out.loc[idx] = rank_normal(sub)
    return out


def score_theme(cross: pd.DataFrame, cfg: ThemesConfig, theme: str) -> pd.DataFrame:
    """``cross``: one date, one theme, eligible firms (index = symbol) with stage, subtheme and factor columns.
    Returns score, per-group scores (``grp_<group>``) and diagnostics columns."""
    groups_of = {s: cfg.factor_groups_for(theme, cross.at[s, "stage"], cross.at[s, "subtheme"]) for s in cross.index}
    used = sorted({g for gs in groups_of.values() for g in gs})
    grp_scores = {}
    dropped = []
    for g in used:
        users = [s for s in cross.index if g in groups_of[s]]
        zs = []
        for f in cfg.factor_groups[g]:
            if f.name not in cross:
                dropped.append(f.name)
                continue
            x = cross.loc[users, f.name].astype(float) * f.direction
            if x.notna().mean() < cfg.scoring.min_coverage:
                dropped.append(f.name)
                continue
            zs.append(_normalize(x, cross.loc[users, "subtheme"], f.name in PRICE_SIGNALS).rename(f.name))
        grp_scores[g] = pd.concat(zs, axis=1).mean(axis=1).reindex(cross.index) if zs else \
            pd.Series(np.nan, index=cross.index)
    gdf = pd.DataFrame(grp_scores, index=cross.index)
    need = pd.DataFrame({g: [g in groups_of[s] for s in cross.index] for g in used}, index=cross.index)
    present = gdf.notna() & need
    n_need, n_present = need.sum(axis=1), present.sum(axis=1)
    raw = gdf.where(need).mean(axis=1)
    raw = raw.where(n_present >= cfg.scoring.min_weight_present * n_need)
    out = gdf.add_prefix("grp_")
    out["score"] = robust_z(raw, clip=None)
    out["groups_present"] = n_present
    out["groups_needed"] = n_need
    out.attrs["dropped"] = sorted(set(dropped))
    return out


def score_panel(panel: pd.DataFrame, cfg: ThemesConfig) -> pd.DataFrame:
    """Scores for every (rebalance_date, theme) cross-section of eligible rows."""
    frames = []
    el = panel[panel["eligible"]]
    for (d, t), g in el.groupby(["rebalance_date", "theme"]):
        if t not in cfg.themes or not cfg.themes[t].enabled:
            continue
        s = score_theme(g.set_index("symbol"), cfg, t)
        s["rebalance_date"], s["theme"] = d, t
        frames.append(s.reset_index())
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
