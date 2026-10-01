"""Forward (shadow) tracking of theme models: the only clean out-of-sample evidence after the v2 search.

A model's configuration is frozen once (``theme_forward_meta``); each month its target weights on the latest
rebalance date are stored (``theme_forward_targets``). Matured months are evaluated against the composite of
equal-weight theme indices (themes_v1 budgets, costless), with turnover costs at the configured bps.
Nothing here feeds back into the frozen configuration.
"""
from __future__ import annotations

import json

import duckdb
import numpy as np
import pandas as pd

from src.db.repo import utcnow

DDL = [
    """CREATE TABLE IF NOT EXISTS theme_forward_meta (model VARCHAR PRIMARY KEY, config VARCHAR, source VARCHAR,
       frozen_at TIMESTAMP, evaluation_date DATE, min_track_record_months DOUBLE)""",
    """CREATE TABLE IF NOT EXISTS theme_forward_targets (snapshot_date DATE, model VARCHAR, symbol VARCHAR,
       theme VARCHAR, weight DOUBLE, score DOUBLE, created_at TIMESTAMP, PRIMARY KEY (snapshot_date, model, symbol))""",
]


def init(con: duckdb.DuckDBPyConnection) -> None:
    for d in DDL:
        con.execute(d)


def freeze(con: duckdb.DuckDBPyConnection, model: str, config: dict, source: str, evaluation_date: pd.Timestamp,
           min_trl: float | None = None) -> dict:
    """Store the configuration once; later calls return the stored one (never overwritten)."""
    init(con)
    row = con.execute("SELECT config, frozen_at, evaluation_date FROM theme_forward_meta WHERE model = ?",
                      [model]).fetchone()
    if row:
        return {"model": model, "config": json.loads(row[0]), "frozen_at": row[1], "evaluation_date": row[2],
                "new": False}
    con.execute("INSERT INTO theme_forward_meta VALUES (?, ?, ?, ?, ?, ?)",
                [model, json.dumps(config, sort_keys=True), source, utcnow(), pd.Timestamp(evaluation_date).date(),
                 None if min_trl is None or not np.isfinite(min_trl) else float(min_trl)])
    return {"model": model, "config": config, "new": True, "evaluation_date": pd.Timestamp(evaluation_date).date()}


def record(con: duckdb.DuckDBPyConnection, model: str, date: pd.Timestamp, targets: pd.DataFrame) -> int:
    """Replace the model's snapshot for ``date``. ``targets``: symbol, theme, weight, score."""
    init(con)
    d = pd.Timestamp(date).date()
    con.execute("DELETE FROM theme_forward_targets WHERE snapshot_date = ? AND model = ?", [d, model])
    df = targets[["symbol", "theme", "weight", "score"]].assign(snapshot_date=d, model=model, created_at=utcnow())
    con.register("_fw", df)
    try:
        con.execute("INSERT INTO theme_forward_targets SELECT snapshot_date, model, symbol, theme, weight, score, "
                    "created_at FROM _fw")
    finally:
        con.unregister("_fw")
    return len(df)


def realized(snapshots: pd.DataFrame, close: pd.DataFrame, members: pd.DataFrame, budgets: dict[str, float],
             unit_cost: float) -> pd.DataFrame:
    """Matured months per model: net return of the stored weights from the session after the snapshot date to the
    session after the next snapshot date, minus turnover x ``unit_cost``; benchmark = budget-weighted equal-weight
    theme indices of the members eligible on the snapshot date."""
    cal = close.index
    rows = []
    dates = sorted(snapshots["snapshot_date"].unique())
    for model, g in snapshots.groupby("model"):
        prev = pd.Series(dtype=float)
        for d0, d1 in zip(dates[:-1], dates[1:], strict=True):
            a_pos, b_pos = cal.searchsorted(d0, side="right"), cal.searchsorted(d1, side="right")
            if b_pos >= len(cal):
                break  # not matured yet
            a, b = cal[a_pos], cal[b_pos]
            w = g[g["snapshot_date"] == d0].set_index("symbol")["weight"]
            r = (close.loc[b] / close.loc[a] - 1).reindex(w.index)
            ok = r.notna()
            net = float((w[ok] * r[ok]).sum()) - unit_cost * float(
                (w.reindex(w.index.union(prev.index), fill_value=0) - prev.reindex(w.index.union(prev.index),
                                                                                   fill_value=0)).abs().sum())
            mem = members[members["rebalance_date"] == d0]
            bench, tot = 0.0, 0.0
            for t, wt in budgets.items():
                rt = (close.loc[b] / close.loc[a] - 1).reindex(mem.loc[mem["theme"] == t, "symbol"]).dropna()
                if len(rt):
                    bench += wt * float(rt.mean())
                    tot += wt
            rows.append({"model": model, "snapshot_date": d0, "net": net, "benchmark": bench / tot if tot else np.nan})
            prev = w
    out = pd.DataFrame(rows)
    if not out.empty:
        out["contribution"] = out["net"] - out["benchmark"]
    return out


def summary(real: pd.DataFrame) -> pd.DataFrame:
    if real.empty:
        return pd.DataFrame(columns=["model", "months", "contribution_ann", "ir", "t"])
    rows = []
    for m, g in real.groupby("model"):
        c = g["contribution"].dropna()
        sd = c.std(ddof=1) if len(c) > 1 else np.nan
        rows.append({"model": m, "months": len(c), "contribution_ann": float(c.mean() * 12),
                     "ir": float(c.mean() / sd * np.sqrt(12)) if sd and sd > 0 else np.nan,
                     "t": float(c.mean() / sd * np.sqrt(len(c))) if sd and sd > 0 else np.nan})
    return pd.DataFrame(rows)
