"""Model configurations and hierarchical scoring (families -> quant composite -> final with Jev)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import load_config, stable_hash
from src.features.preprocess import composite, family_scores, pct_rank, robust_z

# factor themes come from config/factors.yaml (v2: momentum, quality, investment, value, fundamental_momentum,
# low_risk, growth)
FAMILIES = list(load_config("factors")["families"])


@dataclass(frozen=True)
class ModelConfig:
    preset: str
    min_market_cap: float
    min_adv20: float
    portfolio_size: int
    weighting: str
    hold_buffer: float
    jev_weight: float = 0.0
    cost_multiplier: float = 1.0

    @property
    def model_id(self) -> str:
        return "m_" + stable_hash(self.to_dict(), 12)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["family_weights"] = family_preset(self.preset)
        return d

    def replace(self, **kw) -> ModelConfig:
        d = asdict(self)
        d.update(kw)
        return ModelConfig(**d)

    @property
    def universe_key(self) -> tuple[float, float]:
        return (self.min_market_cap, self.min_adv20)


def family_preset(name: str) -> dict[str, Any]:
    presets = load_config("backtest")["family_presets"]
    if name not in presets:
        raise KeyError(f"unknown family preset {name!r}; configured: {sorted(presets)}")
    return presets[name]


def default_config(**overrides) -> ModelConfig:
    d = load_config("backtest")["search"]["defaults"]
    base = dict(preset="literature", min_market_cap=float(d["min_market_cap"]), min_adv20=float(d["min_adv20"]),
                portfolio_size=int(d["portfolio_size"]), weighting=d["weighting"], hold_buffer=float(d["hold_buffer"]))
    base.update(overrides)
    return ModelConfig(**base)


def universe_mask(cross: pd.DataFrame, min_mcap: float, min_adv: float) -> pd.Series:
    return cross["base_eligible"].astype(bool) & (cross["market_cap"] >= min_mcap) & (cross["adv20"] >= min_adv)


@dataclass
class CrossSection:
    date: pd.Timestamp
    frame: pd.DataFrame            # eligible names, indexed by symbol, with raw features
    family_z: pd.DataFrame
    family_pct: pd.DataFrame
    diagnostics: dict = field(default_factory=dict)


class ScoreCache:
    """Caches family scores per (date, universe) so parameter searches reuse normalization work."""

    def __init__(self, panel: pd.DataFrame, factors_cfg: dict | None = None):
        self.panel = panel
        self.by_date = {d: g.set_index("symbol") for d, g in panel.groupby("rebalance_date")}
        self.factors_cfg = factors_cfg or load_config("factors")
        self._cache: dict[tuple, CrossSection] = {}

    @property
    def dates(self) -> list[pd.Timestamp]:
        return sorted(self.by_date)

    def cross_section(self, date: pd.Timestamp, min_mcap: float, min_adv: float) -> CrossSection:
        key = (date, min_mcap, min_adv)
        if key not in self._cache:
            g = self.by_date[date]
            elig = g[universe_mask(g, min_mcap, min_adv)]
            if elig.empty:
                cs = CrossSection(date, elig, pd.DataFrame(index=elig.index), pd.DataFrame(index=elig.index))
            else:
                fz, fp, diag = family_scores(elig, elig["sector_group"], self.factors_cfg)
                diag["universe_size"] = int(len(elig))
                cs = CrossSection(date, elig, fz, fp, diag)
            self._cache[key] = cs
        return self._cache[key]


def ic_family_weights(history: list[tuple[pd.Timestamp, pd.DataFrame]], labels: pd.DataFrame,
                      as_of: pd.Timestamp, horizon: int, lookback_months: int, min_obs: int) -> dict[str, float]:
    """Family weights from mean rank IC over past rebalances whose labels had fully matured by ``as_of``.

    Purging is structural: a past rebalance t is used only if label_end_date(t, horizon) <= as_of, so no
    forward-return information beyond ``as_of`` enters the weights.
    """
    lab = labels[labels["label_end_date"] <= as_of]
    lab = lab[lab["rebalance_date"] >= as_of - pd.DateOffset(months=lookback_months)]
    ics: dict[str, list[float]] = {f: [] for f in FAMILIES}
    for d, fz in history:
        if d >= as_of:
            continue
        ld = lab[lab["rebalance_date"] == d].set_index("symbol")["fwd_return"]
        if ld.empty:
            continue
        for f in FAMILIES:
            if f not in fz:
                continue
            j = pd.concat([fz[f], ld], axis=1, join="inner").dropna()
            if len(j) >= 20:
                ics[f].append(spearmanr(j.iloc[:, 0], j.iloc[:, 1]).statistic)
    n_obs = min((len(v) for v in ics.values()), default=0)
    if n_obs < min_obs:
        return {f: 1.0 for f in FAMILIES}  # not enough matured history: equal weights
    w = {f: max(0.0, float(np.nanmean(v))) for f, v in ics.items() if v}
    if sum(w.values()) <= 0:
        return {f: 1.0 for f in FAMILIES}
    return w


def normalize_weights(w: dict[str, float]) -> dict[str, float]:
    tot = sum(max(0.0, float(v)) for v in w.values())
    return {k: max(0.0, float(v)) / tot for k, v in w.items()} if tot > 0 else {k: 1.0 / len(w) for k in w}


def factor_momentum_signs(history: list[tuple[pd.Timestamp, pd.DataFrame]], labels: pd.DataFrame,
                          as_of: pd.Timestamp, lookback_months: int) -> dict[str, float]:
    """Mean top-quintile excess forward return per theme over past rebalances whose labels matured by ``as_of``."""
    lab = labels[(labels["label_end_date"] <= as_of) &
                 (labels["rebalance_date"] >= as_of - pd.DateOffset(months=lookback_months))]
    perf: dict[str, list[float]] = {f: [] for f in FAMILIES}
    for d, fz in history:
        if d >= as_of:
            continue
        ld = lab[lab["rebalance_date"] == d].set_index("symbol")["fwd_return"]
        if len(ld) < 25:
            continue
        for f in FAMILIES:
            if f not in fz:
                continue
            j = pd.concat([fz[f], ld], axis=1, join="inner").dropna()
            if len(j) < 25:
                continue
            top = j[j.iloc[:, 0] >= j.iloc[:, 0].quantile(0.8)]
            perf[f].append(float(top.iloc[:, 1].mean() - j.iloc[:, 1].mean()))
    return {f: float(np.mean(v)) for f, v in perf.items() if v}


def quant_scores(cs: CrossSection, weights: dict[str, float]) -> pd.Series:
    fam_w = {f: float(weights.get(f, 0.0)) for f in FAMILIES}
    return composite(cs.family_z, fam_w)


def jev_raw_score(answers: dict[str, dict], components: dict[str, float], questions: dict[str, dict]) -> float | None:
    """Combine one decision's answers into a single raw score in probability units (no arithmetic by Jev)."""
    total, wsum = 0.0, 0.0
    for q, w in components.items():
        a = answers.get(q)
        if not a:
            continue
        if a.get("type") == "boolean" and a.get("probability") is not None:
            p = float(a["probability"])
        elif a.get("type") == "score" and a.get("score") is not None:
            levels = len(questions[q]["criteria"])
            p = float(a["score"]) / max(1, levels - 1)
        else:
            continue
        # negative weights count the probability against the stock: use (1 - p) with |w|
        total += abs(w) * (p if w >= 0 else 1.0 - p)
        wsum += abs(w)
    return total / wsum if wsum > 0 else None


def combine_final(quant: pd.Series, jev: pd.Series | None, jev_weight: float, pool: pd.Index) -> pd.DataFrame:
    """final = (1 - w) * z(quant) + w * z(jev) within the Jev candidate pool; names outside rank after it.

    Both components are robust-z normalized over the same pool, so they are on a common scale. Missing Jev
    values contribute 0 (neutral), never a fabricated score.
    """
    out = pd.DataFrame({"quant_score": quant})
    out["in_pool"] = out.index.isin(pool)
    qz = robust_z(quant.reindex(pool), clip=None)
    if jev is not None and jev_weight > 0:
        jz = robust_z(jev.reindex(pool), clip=None).fillna(0.0)
    else:
        jz = pd.Series(0.0, index=pool)
    final_pool = (1 - jev_weight) * qz.fillna(qz.min() if qz.notna().any() else 0) + jev_weight * jz
    out["jev_z"] = jz.reindex(out.index)
    out["final_score"] = np.nan
    out.loc[pool, "final_score"] = final_pool
    # names outside the pool keep quant ordering below every pool member
    outside = ~out["in_pool"]
    if outside.any():
        floor = (final_pool.min() if len(final_pool) else 0.0) - 1.0
        out.loc[outside, "final_score"] = floor + robust_z(quant[outside], clip=None).fillna(-10) * 1e-3
    out["rank"] = out["final_score"].rank(ascending=False, method="first").astype("Int64")
    out["quant_rank"] = out["quant_score"].rank(ascending=False, method="first").astype("Int64")
    out["final_pct"] = pct_rank(out["final_score"])
    return out.sort_values("rank")


@lru_cache(maxsize=1)
def jev_components() -> tuple[dict[str, float], dict[str, dict]]:
    cfg = load_config("jev")
    return cfg["score_components"], cfg["questions"]
