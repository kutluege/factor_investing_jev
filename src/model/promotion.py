"""Incumbent / challenger production-model management.

Promotion criteria (config/backtest.yaml -> promotion), all evaluated on out-of-sample walk-forward folds:
  1. challenger objective - incumbent objective >= min_objective_improvement (robust-z units)
  2. challenger beats the incumbent's total return in >= min_fold_win_rate of common folds
  3. challenger worst-fold drawdown is not worse than the incumbent's by more than max_worst_dd_deterioration
  4. at least min_months_between_promotions since the last promotion
If there is no incumbent yet, the first challenger becomes the incumbent (recorded as a bootstrap promotion).
"""
from __future__ import annotations

import json
import uuid

import duckdb
import pandas as pd

from src.config import load_config
from src.db.repo import utcnow
from src.model.scoring import ModelConfig


def register_model(con: duckdb.DuckDBPyConnection, cfg: ModelConfig, description: str = "") -> str:
    con.execute("INSERT INTO factor_models VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
                [cfg.model_id, json.dumps(cfg.to_dict()), description, utcnow()])
    return cfg.model_id


def current_incumbent(con: duckdb.DuckDBPyConnection) -> dict | None:
    row = con.execute("""SELECT v.version_id, v.model_id, v.objective, v.decision, m.config, v.created_at
                         FROM model_versions v JOIN factor_models m USING (model_id)
                         WHERE v.role = 'incumbent' ORDER BY v.created_at DESC LIMIT 1""").fetchone()
    if row is None:
        return None
    cfg = json.loads(row[4])
    cfg.pop("family_weights", None)
    return {"version_id": row[0], "model_id": row[1], "objective": row[2], "decision": json.loads(row[3] or "{}"),
            "config": ModelConfig(**cfg), "created_at": row[5]}


def evaluate_promotion(incumbent: dict | None, challenger: dict, last_promotion: pd.Timestamp | None,
                       as_of: pd.Timestamp) -> dict:
    """``challenger``/``incumbent`` dicts: objective, fold_returns (list), worst_fold_max_drawdown."""
    p = load_config("backtest")["promotion"]
    if incumbent is None:
        return {"promote": True, "reason": "no incumbent: bootstrap promotion", "checks": {}, "criteria": p}
    checks = {}
    d_obj = (challenger["objective"] or float("-inf")) - (incumbent["objective"] or float("-inf"))
    checks["objective_improvement"] = {"value": d_obj, "required": p["min_objective_improvement"],
                                       "pass": d_obj >= p["min_objective_improvement"]}
    cr, ir = challenger.get("fold_returns") or [], incumbent.get("fold_returns") or []
    n = min(len(cr), len(ir))
    win = sum(1 for a, b in zip(cr[-n:], ir[-n:], strict=False) if a > b) / n if n else 0.0
    checks["fold_win_rate"] = {"value": win, "required": p["min_fold_win_rate"], "pass": n > 0 and win >= p["min_fold_win_rate"]}
    cdd, idd = challenger.get("worst_fold_max_drawdown"), incumbent.get("worst_fold_max_drawdown")
    dd_det = (idd - cdd) if (cdd is not None and idd is not None) else None
    checks["worst_drawdown"] = {"value": dd_det, "allowed": p["max_worst_dd_deterioration"],
                                "pass": dd_det is not None and dd_det <= p["max_worst_dd_deterioration"]}
    months = None if last_promotion is None else (as_of.year - last_promotion.year) * 12 + as_of.month - last_promotion.month
    checks["cooldown"] = {"months_since_last": months, "required": p["min_months_between_promotions"],
                          "pass": months is None or months >= p["min_months_between_promotions"]}
    promote = all(c["pass"] for c in checks.values())
    return {"promote": promote, "reason": "all criteria passed" if promote else
            "retain incumbent: " + ", ".join(k for k, c in checks.items() if not c["pass"]), "checks": checks,
            "criteria": p}


def record_versions(con: duckdb.DuckDBPyConnection, challenger_cfg: ModelConfig, challenger_stats: dict,
                    incumbent_stats: dict | None, run_id: str, as_of: pd.Timestamp) -> dict:
    """Register the challenger, evaluate promotion and persist the decision (append-only).

    ``incumbent_stats`` must come from re-evaluating the incumbent configuration on the SAME folds as the
    challenger in the current run, so both are compared on identical out-of-sample data. The incumbent is always
    the most recent version with role 'incumbent'; earlier rows are never modified.
    """
    register_model(con, challenger_cfg, "challenger from backtest run " + run_id)
    inc = current_incumbent(con)
    last = con.execute("SELECT max(as_of_date) FROM promotion_decisions WHERE promoted").fetchone()[0]
    if inc is not None and inc["model_id"] == challenger_cfg.model_id:
        decision = {"promote": False, "reason": "challenger identical to incumbent; incumbent retained",
                    "checks": {}, "criteria": load_config("backtest")["promotion"]}
    else:
        decision = evaluate_promotion(incumbent_stats if inc else None, challenger_stats,
                                      pd.Timestamp(last) if last else None, as_of)
    ch_vid = "v_" + uuid.uuid4().hex[:12]
    role = "incumbent" if decision["promote"] else "challenger"
    con.execute("INSERT INTO model_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [ch_vid, challenger_cfg.model_id, role, as_of.date(), run_id, challenger_stats.get("objective"),
                 json.dumps({"stats": challenger_stats, "incumbent_stats": incumbent_stats, "promotion": decision},
                            default=str), utcnow()])
    con.execute("INSERT INTO promotion_decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ["p_" + uuid.uuid4().hex[:12], as_of.date(), inc["version_id"] if inc else None, ch_vid,
                 bool(decision["promote"]), json.dumps(decision["criteria"]),
                 json.dumps({"checks": decision["checks"], "reason": decision["reason"]}, default=str), utcnow()])
    return {"challenger_version_id": ch_vid, "role": role, **decision}
