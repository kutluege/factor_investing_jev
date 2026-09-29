"""Characteristic-level research: rank IC and long-only top-quintile excess returns.

Descriptive only. Signals and weights were fixed from the literature before this analysis; these statistics are
reported for transparency (and to spot data problems), not used to pick signals in-sample.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import load_config
from src.features.preprocess import feature_applicable
from src.model.scoring import FAMILIES, ScoreCache


def _stats(x: pd.Series) -> dict:
    x = x.dropna()
    if len(x) < 6:
        return {"mean": None, "t": None, "n": len(x)}
    return {"mean": float(x.mean()), "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), "n": int(len(x))}


def characteristic_ic(cache: ScoreCache, labels: dict[int, pd.DataFrame], min_mcap: float, min_adv: float,
                      start: pd.Timestamp | None = None) -> pd.DataFrame:
    """Per characteristic x horizon: mean rank IC, t-stat, top-quintile excess return (vs eligible mean)."""
    fcfg = load_config("factors")
    feats = {f: (fam, c) for fam, fs in fcfg["families"].items() for f, c in fs.items()}
    lab = {h: lb.set_index(["rebalance_date", "symbol"])["fwd_return"] for h, lb in labels.items()}
    rows: dict[tuple, list[tuple[float, float]]] = {}
    for d in cache.dates:
        if start is not None and d < start:
            continue
        cs = cache.cross_section(d, min_mcap, min_adv)
        if cs.frame.empty:
            continue
        fr = cs.frame
        for h, lb in lab.items():
            try:
                y = lb.xs(d, level="rebalance_date")
            except KeyError:
                continue
            y = y.reindex(fr.index)
            candidates = [(f, fr[f] * float(c.get("direction", 1))) for f, (_, c) in feats.items() if f in fr]
            candidates += [(f"THEME:{t}", cs.family_z[t]) for t in FAMILIES if t in cs.family_z]
            for f, x in candidates:
                if not f.startswith("THEME:"):
                    c = feats[f][1]
                    x = x.where(fr["sector_group"].map(lambda g, c=c: feature_applicable(c, g)).astype(bool))
                j = pd.concat([x, y], axis=1, keys=["x", "y"]).dropna()
                if len(j) < 30:
                    continue
                ic = j["x"].rank().corr(j["y"].rank())
                top = j[j["x"] >= j["x"].quantile(0.8)]["y"].mean() - j["y"].mean()
                rows.setdefault((f, h), []).append((ic, top))
    out = []
    for (f, h), vals in rows.items():
        ic = pd.Series([v[0] for v in vals])
        top = pd.Series([v[1] for v in vals])
        s_ic, s_top = _stats(ic), _stats(top)
        fam = f.split(":", 1)[1] if f.startswith("THEME:") else feats[f][0]
        out.append({"characteristic": f, "theme": fam, "horizon": h, "rank_ic": s_ic["mean"], "ic_t": s_ic["t"],
                    "top_quintile_excess": s_top["mean"], "top_t": s_top["t"], "months": s_ic["n"],
                    "ic_hit_rate": float((ic > 0).mean())})
    return pd.DataFrame(out).sort_values(["horizon", "theme", "characteristic"])


def by_subperiod(cache, labels, min_mcap, min_adv, cuts: list[str]) -> dict[str, pd.DataFrame]:
    out = {}
    bounds = [pd.Timestamp(c) for c in cuts]
    for a, b in zip(bounds[:-1], bounds[1:], strict=False):
        sub = ScoreCache(cache.panel[(cache.panel["rebalance_date"] >= a) & (cache.panel["rebalance_date"] < b)],
                         cache.factors_cfg)
        out[f"{a.date()}..{b.date()}"] = characteristic_ic(sub, labels, min_mcap, min_adv)
    return out


def to_markdown(df: pd.DataFrame, horizon: int) -> str:
    d = df[df["horizon"] == horizon].copy()
    lines = [f"| Characteristic | Theme | Rank IC | t | Top-quintile excess ({horizon}d) | t | IC>0 months |",
             "|---|---|---|---|---|---|---|"]
    for r in d.itertuples():
        def f(v, nd=3, pct=False):
            if v is None or v != v:
                return "—"
            return f"{v * 100:.2f}%" if pct else f"{v:.{nd}f}"
        name = f"**{r.characteristic}**" if r.characteristic.startswith("THEME:") else r.characteristic
        lines.append(f"| {name} | {r.theme} | {f(r.rank_ic)} | {f(r.ic_t, 1)} | {f(r.top_quintile_excess, pct=True)} | "
                     f"{f(r.top_t, 1)} | {f(r.ic_hit_rate, pct=True)} |")
    return "\n".join(lines)
