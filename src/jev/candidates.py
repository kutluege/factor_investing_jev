"""Jev candidate reduction and state construction shared by historical generation and production.

States are always built on the *reference universe* (the loosest market-cap / ADV thresholds) so the state of
(symbol, date) is identical for every backtest configuration: a Jev decision is requested once and reused by
every parameter combination (Stage A / Stage B separation).
"""
from __future__ import annotations

import json

import duckdb
import pandas as pd

from src.config import load_config, stable_hash
from src.db.repo import utcnow
from src.jev.state import build_state, regime_context
from src.jev.store import JevTask
from src.model.scoring import FAMILIES, ScoreCache, family_preset, jev_components, jev_raw_score, quant_scores


def reference_universe() -> tuple[float, float]:
    s = load_config("backtest")["search"]
    return float(min(s["market_caps"])), float(min(s["adv_thresholds"]))


def candidate_definition() -> dict:
    j = load_config("jev")
    presets = [p for p, v in load_config("backtest")["family_presets"].items() if not v.get("dynamic")]
    s = load_config("backtest")["search"]
    return {"pool_top_n": j["candidate_pool"]["top_n"], "boundary_extra": j["candidate_pool"]["boundary_extra"],
            "presets": presets, "universes": [list(reference_universe()),
                                              [float(s["defaults"]["min_market_cap"]), float(s["defaults"]["min_adv20"])]],
            "include_holdings": j["candidate_pool"]["include_holdings"]}


def candidate_symbols(cache: ScoreCache, d: pd.Timestamp, extra: list[str] | None = None,
                      definition: dict | None = None) -> list[str]:
    """Union of the top (N + boundary) names under every static family preset and configured universe."""
    definition = definition or candidate_definition()
    n = int(definition["pool_top_n"]) + int(definition["boundary_extra"])
    out: set[str] = set()
    for mcap, adv in definition["universes"]:
        cs = cache.cross_section(d, mcap, adv)
        if cs.frame.empty:
            continue
        for preset in definition["presets"]:
            w = {f: float(family_preset(preset).get(f, 0)) for f in FAMILIES}
            q = quant_scores(cs, w).dropna().sort_values(ascending=False)
            out.update(q.index[:n])
    ref = cache.cross_section(d, *reference_universe()).frame.index
    out.update(s for s in (extra or []) if s in ref)
    return sorted(out)


def build_tasks(cache: ScoreCache, bench_close: pd.Series | None, d: pd.Timestamp, symbols: list[str],
                industries: dict[str, str] | None = None) -> list[JevTask]:
    include_ids = bool(load_config("jev").get("include_identifiers", False))
    cs = cache.cross_section(d, *reference_universe())
    regime = regime_context(bench_close, cs.frame, d)
    tasks = []
    for sym in symbols:
        if sym not in cs.frame.index:
            continue
        row = cs.frame.loc[sym].copy()
        row["industry"] = (industries or {}).get(sym)
        state = build_state(row, cs.family_pct.loc[sym] if sym in cs.family_pct.index else pd.Series(dtype=float),
                            regime, include_identifiers=include_ids,
                            identifiers={"symbol": sym, "date": str(d.date())})
        tasks.append(JevTask(sym, d, state))
    return tasks


def persist_candidate_set(con: duckdb.DuckDBPyConnection, d: pd.Timestamp, fsid: str, symbols: list[str],
                          definition: dict) -> None:
    con.execute("INSERT INTO jev_candidate_sets VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
                [d.date(), fsid, json.dumps({**definition, "definition_hash": stable_hash(definition)}),
                 json.dumps(symbols), utcnow()])


def jev_feature_frame(decisions: pd.DataFrame) -> pd.DataFrame:
    """Decisions -> (rebalance_date, symbol, jev_raw, jev_confidence) for Stage B backtests."""
    if decisions is None or decisions.empty:
        return pd.DataFrame(columns=["rebalance_date", "symbol", "jev_raw", "jev_confidence"])
    comps, questions = jev_components()
    rows = []
    for r in decisions.itertuples():
        raw = jev_raw_score(r.answers, comps, questions)
        conf = [v for v in (r.confidence or {}).values() if v is not None]
        rows.append({"rebalance_date": r.rebalance_date, "symbol": r.symbol, "jev_raw": raw,
                     "jev_confidence": float(sum(conf) / len(conf)) if conf else None,
                     "decision_id": r.decision_id})
    return pd.DataFrame(rows)
