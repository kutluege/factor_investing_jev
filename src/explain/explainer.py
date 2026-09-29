"""Deterministic, traceable explanations. Every statement is derived from stored inputs and model outputs."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.config import load_config
from src.features.preprocess import feature_applicable, normalize_feature
from src.model.scoring import FAMILIES
from src.portfolio.signals import SignalRules, change_conditions

FEATURE_LABELS = {
    "earnings_yield": "earnings yield", "fcf_yield": "free-cash-flow yield", "ebit_ev": "EBIT / EV",
    "sales_ev": "sales / EV", "book_to_market": "book-to-market", "cash_to_mcap": "cash / market cap",
    "roic": "ROIC", "roe": "ROE", "roa": "ROA", "gross_profitability": "gross profitability",
    "operating_margin": "operating margin", "fcf_margin": "FCF margin", "cash_conversion": "cash conversion",
    "debt_to_assets": "debt / assets", "net_debt_to_assets": "net debt / assets",
    "interest_coverage": "interest coverage", "cash_runway_years": "cash runway (years)",
    "rd_intensity": "R&D / market cap", "revenue_yoy": "revenue growth YoY", "revenue_cagr_2y": "2-year revenue CAGR",
    "eps_growth": "EPS growth", "ebitda_growth": "EBITDA growth", "fcf_growth": "FCF growth",
    "gross_profit_growth": "gross-profit growth", "revenue_growth_accel": "revenue-growth acceleration",
    "operating_margin_chg": "operating-margin change", "roic_chg": "ROIC change", "fcf_margin_chg": "FCF-margin change",
    "eps_accel": "earnings acceleration", "leverage_chg": "leverage change", "share_dilution_yoy": "share dilution YoY",
    "ret_3m": "3-month return", "ret_6m": "6-month return", "mom_6_1": "6-1 momentum", "mom_12_1": "12-1 momentum",
    "rs_qqq_6m": "6-month strength vs QQQ", "rs_sector_6m": "6-month strength vs sector",
    "dist_52w_high": "distance from 52-week high", "price_sma200": "price vs 200-day average",
    "sma50_sma200": "50-day vs 200-day average", "macd_hist_norm": "MACD histogram", "adx14_trend": "directional ADX",
    "breakout_60d": "60-day breakout distance", "volume_ratio_20d": "volume trend (5d/20d)",
    "vol_60d": "60-day volatility", "vol_20d": "20-day volatility", "atr14_pct": "ATR% (14d)",
    "beta_qqq_252d": "beta vs QQQ", "max_dd_252d": "12-month max drawdown",
}
PCT_FEATURES = {f for f in FEATURE_LABELS if f not in ("interest_coverage", "cash_runway_years", "adx14_trend",
                                                       "volume_ratio_20d", "beta_qqq_252d")}


def _fmt_value(feature: str, v: float) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    return f"{v:+.1%}" if feature in PCT_FEATURES else f"{v:.2f}"


def feature_contributions(cross: pd.DataFrame, family_weights: dict[str, float]) -> pd.DataFrame:
    """Per-name, per-feature contribution to the quant composite: family weight share x feature z / n_features."""
    fcfg = load_config("factors")
    pp = fcfg["preprocessing"]
    groups = cross["sector_group"]
    wsum = sum(float(family_weights.get(f, 0)) for f in FAMILIES) or 1.0
    frames = []
    for family, feats in fcfg["families"].items():
        w = float(family_weights.get(family, 0)) / wsum
        if w <= 0:
            continue
        zs = {}
        for feat, c in feats.items():
            if feat not in cross:
                continue
            x = cross[feat].astype(float) * float(c.get("direction", 1))
            x = x.where(groups.map(lambda g, c=c: feature_applicable(c, g)).astype(bool))
            if x.notna().mean() < pp["min_coverage"]:
                continue
            zs[feat] = normalize_feature(x, groups if pp.get("sector_relative") else None, pp["winsorize_mad"],
                                         pp["min_group_size"])
        if not zs:
            continue
        z = pd.DataFrame(zs)
        n = z.notna().sum(axis=1).replace(0, np.nan)
        contrib = z.div(n, axis=0) * w
        frames.append(contrib.stack().rename("contribution").reset_index()
                      .rename(columns={"level_0": "symbol", "level_1": "feature"}).assign(family=family))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=["symbol", "feature", "contribution", "family"])


def explain(symbol: str, company: str | None, signal: str, reasons: list[str], rank_row: pd.Series | None,
            previous_rank: int | None, contributions: pd.DataFrame, cross_row: pd.Series | None,
            jev: dict | None, position: dict | None, current_price: float | None, rules: SignalRules,
            as_of: pd.Timestamp) -> dict:
    rr = rank_row if rank_row is not None else pd.Series(dtype=object)
    fam = {f: rr.get(f"pct_{f}") for f in FAMILIES}
    fundamental = np.nanmean([v for v in (fam["value"], fam["quality"], fam["growth"], fam["fundamental_momentum"])
                              if v is not None and not pd.isna(v)] or [np.nan])
    momentum = fam["price_momentum"]
    c = contributions[contributions["symbol"] == symbol].sort_values("contribution")
    def driver(r):
        val = cross_row.get(r.feature) if cross_row is not None else None
        return {"feature": r.feature, "label": FEATURE_LABELS.get(r.feature, r.feature), "family": r.family,
                "value": None if val is None or pd.isna(val) else float(val),
                "display": _fmt_value(r.feature, val if val is not None else float("nan")),
                "contribution": round(float(r.contribution), 4)}
    positives = [driver(r) for r in c[c["contribution"] > 0].tail(4).iloc[::-1].itertuples()]
    negatives = [driver(r) for r in c[c["contribution"] < 0].head(4).itertuples()]
    out = {
        "ticker": symbol, "company": company, "signal": signal, "as_of": str(as_of.date()),
        "rank": None if pd.isna(rr.get("rank", np.nan)) else int(rr.get("rank")),
        "previous_rank": previous_rank,
        "final_score": _f(rr.get("final_score")), "quant_score": _f(rr.get("quant_score")),
        "fundamental_score_pct": _f(fundamental), "momentum_score_pct": _f(momentum),
        "technical_score_pct": _f(fam["technical_trend"]), "risk_score_pct": _f(fam["risk"]),
        "family_percentiles": {k: _f(v) for k, v in fam.items()},
        "jev_score": _f(rr.get("jev_raw")), "jev_confidence": _f(rr.get("jev_confidence")),
        "jev_answers": (jev or {}).get("answers"), "jev_decision_id": (jev or {}).get("decision_id"),
        "reasons": reasons, "strongest_positive_drivers": positives, "strongest_negative_drivers": negatives,
        "change_conditions": change_conditions(signal, None if pd.isna(rr.get("rank", np.nan)) else int(rr.get("rank")),
                                               rules, reasons),
    }
    if position:
        entry = position.get("entry_price")
        out.update({"entry_date": str(pd.Timestamp(position["entry_date"]).date()) if position.get("entry_date") else None,
                    "entry_price": _f(entry), "current_price": _f(current_price),
                    "unrealized_return": _f(current_price / entry - 1) if entry and current_price else None,
                    "holding_days": int((as_of - pd.Timestamp(position["entry_date"])).days)
                    if position.get("entry_date") else None})
    else:
        out.update({"entry_date": None, "entry_price": None, "current_price": _f(current_price),
                    "unrealized_return": None, "holding_days": None})
    out["summary"] = summary_text(out)
    return out


def _f(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else round(f, 4)


def summary_text(e: dict) -> str:
    """One-paragraph explanation assembled only from fields in ``e``."""
    parts = [f"{e['ticker']}: {e['signal']}"]
    if e.get("rank") is not None:
        prev = f" (previous {e['previous_rank']})" if e.get("previous_rank") is not None else ""
        parts.append(f"rank {e['rank']}{prev}")
    if e["reasons"]:
        parts.append("because " + "; ".join(r.split(":", 1)[-1].strip() for r in e["reasons"]))
    if e["strongest_positive_drivers"]:
        parts.append("supported by " + ", ".join(f"{d['label']} {d['display']}" for d in e["strongest_positive_drivers"][:3]))
    if e["strongest_negative_drivers"]:
        parts.append("held back by " + ", ".join(f"{d['label']} {d['display']}" for d in e["strongest_negative_drivers"][:3]))
    if e.get("jev_score") is not None:
        parts.append(f"Jev composite {e['jev_score']:.2f}")
    return ". ".join(parts) + "."
