"""Forward (live) validation of Jev scores.

Historical backtests of an LLM-based signal are contaminated by look-ahead: the model may have seen what happened
after a historical date, even with anonymized inputs (Lopez-Lira, Tang & Zhu 2025; Sarkar & Vafa 2024). The only
clean evidence is forward: scores recorded in production *before* returns were realized. Every monthly run stores
Jev scores (shadow mode). This module measures their forward rank IC once returns have matured and decides whether
Jev may carry weight in production.
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import load_config


def forward_ic(con: duckdb.DuckDBPyConnection, horizon_days: int = 63, portfolio_id: str = "production") -> pd.DataFrame:
    """Per production run: Spearman IC between the stored Jev score and the realized forward return."""
    runs = con.execute("""SELECT run_key, rebalance_date FROM production_runs
                          WHERE portfolio_id = ? AND status = 'completed' ORDER BY rebalance_date""",
                       [portfolio_id]).fetchall()
    rows = []
    for run_key, d in runs:
        r = con.execute("SELECT symbol, jev_score, quant_score FROM monthly_rankings WHERE run_key = ? "
                        "AND jev_score IS NOT NULL", [run_key]).df()
        if len(r) < 15:
            continue
        px = con.execute("""
            SELECT symbol, date, adj_close FROM daily_prices
            WHERE symbol IN (SELECT unnest(?)) AND date >= ? ORDER BY symbol, date""",
                         [r["symbol"].tolist(), d]).df()
        if px.empty:
            continue
        fwd = {}
        for sym, g in px.groupby("symbol"):
            if len(g) > horizon_days:
                fwd[sym] = g["adj_close"].iloc[horizon_days] / g["adj_close"].iloc[0] - 1
        r["fwd"] = r["symbol"].map(fwd)
        r = r.dropna(subset=["fwd"])
        if len(r) < 15:
            continue  # not matured yet
        rows.append({"run_key": run_key, "rebalance_date": d, "n": len(r),
                     "jev_ic": spearmanr(r["jev_score"], r["fwd"]).statistic,
                     "quant_ic": spearmanr(r["quant_score"], r["fwd"]).statistic,
                     # does Jev add information beyond the quant score? IC of the part of Jev orthogonal to quant
                     "jev_residual_ic": _residual_ic(r)})
    return pd.DataFrame(rows)


def _residual_ic(r: pd.DataFrame) -> float:
    x = r["quant_score"].rank().to_numpy(float)
    y = r["jev_score"].rank().to_numpy(float)
    beta = np.polyfit(x, y, 1)[0] if np.std(x) > 0 else 0.0
    resid = y - beta * x
    return float(spearmanr(resid, r["fwd"]).statistic)


def jev_production_gate(con: duckdb.DuckDBPyConnection) -> dict:
    """May Jev carry weight in production? Requires a matured forward record per config/jev.yaml."""
    pol = load_config("jev").get("production_policy", {})
    if not pol.get("require_forward_validation", True):
        return {"allowed": True, "reason": "forward validation disabled in config"}
    ic = forward_ic(con, int(pol.get("horizon_days", 63)))
    n = len(ic)
    need = int(pol.get("min_forward_months", 12))
    if n < need:
        return {"allowed": False, "reason": f"shadow mode: {n}/{need} matured forward months", "months": n}
    s = ic["jev_residual_ic"].dropna()
    t = float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))) if len(s) > 2 and s.std(ddof=1) > 0 else 0.0
    ok = t >= float(pol.get("min_residual_ic_t", 2.0))
    return {"allowed": ok, "months": n, "mean_residual_ic": float(s.mean()), "t_stat": t,
            "reason": "forward residual IC significant" if ok else "forward residual IC not significant (t < "
            f"{pol.get('min_residual_ic_t', 2.0)}): Jev stays in shadow mode"}
