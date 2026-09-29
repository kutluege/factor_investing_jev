"""SEC company facts -> financial_facts -> point-in-time fundamental snapshots."""
from __future__ import annotations

import json
import logging
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from src.config import load_config, stable_hash
from src.data.http import ApiError
from src.data.sec import SecClient
from src.data.xbrl import parse_company_facts, snapshots_by_filing
from src.db.repo import set_status, utcnow
from src.db.schema import upsert_df

log = logging.getLogger(__name__)

FACT_COLS = ["cik", "metric", "concept", "unit", "period_start", "period_end", "duration_days", "fiscal_year",
             "fiscal_period", "form", "accn", "filed_date", "availability_date", "value", "loaded_at"]


def _json_default(v):
    if isinstance(v, (pd.Timestamp,)):
        return v.date().isoformat()
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    return str(v)


def _snapshots_for(args: tuple[str, pd.DataFrame, pd.Timestamp | None]) -> tuple[str, list[dict]]:
    cik, facts, min_date = args
    snaps = snapshots_by_filing(facts, min_date=min_date)
    out = []
    for _, row in snaps.iterrows():
        payload = {k: v for k, v in row.items() if k not in ("snapshot_date",) and v is not None
                   and not (isinstance(v, float) and np.isnan(v))}
        out.append({"cik": cik, "snapshot_date": row["snapshot_date"].date(),
                    "availability_date": pd.Timestamp(row["_availability_date"]).date(),
                    "period_end": pd.Timestamp(row["_period_end"]).date() if pd.notna(row.get("_period_end")) else None,
                    "payload": json.dumps(payload, default=_json_default)})
    return cik, out


def load_fundamentals(con: duckdb.DuckDBPyConnection, sec: SecClient, ciks: list[str],
                      snapshot_min_date: pd.Timestamp | None = None, workers: int = 4) -> dict[str, Any]:
    lag = int(load_config("data")["sec"]["availability_lag_days"])
    report = {"requested": len(ciks), "loaded": 0, "no_facts": 0, "failed": {}, "snapshots_rebuilt": 0}
    existing_versions = dict(con.execute(
        "SELECT cik, max(facts_version) FROM fundamental_snapshots GROUP BY cik").fetchall())
    to_snapshot: list[tuple[str, pd.DataFrame, pd.Timestamp | None]] = []
    for i, cik in enumerate(ciks):
        try:
            payload = sec.company_facts(cik)
        except ApiError as exc:
            if exc.status == 404:
                report["no_facts"] += 1
                set_status(con, "sec_facts", cik, "no_facts")
            else:
                report["failed"][cik] = str(exc)[:200]
                set_status(con, "sec_facts", cik, "failed", str(exc))
            continue
        facts = parse_company_facts(payload, availability_lag_days=lag)
        if facts.empty:
            report["no_facts"] += 1
            set_status(con, "sec_facts", cik, "no_mapped_facts")
            continue
        facts["loaded_at"] = utcnow()
        store = facts[FACT_COLS].copy()
        for c in ("period_start", "period_end", "filed_date", "availability_date"):
            store[c] = store[c].dt.date
        # Facts are keyed by filing accession, so new filings add rows and old observations are preserved.
        upsert_df(con, "financial_facts", store, ["cik", "concept", "unit", "period_start", "period_end", "accn"],
                  replace=False)
        version = stable_hash([len(facts), str(facts["filed_date"].max()), str(snapshot_min_date)])
        if existing_versions.get(cik) != version:
            to_snapshot.append((cik, facts.drop(columns=["loaded_at"]), snapshot_min_date))
        report["loaded"] += 1
        set_status(con, "sec_facts", cik, "ok")
        if (i + 1) % 50 == 0:
            log.info("sec facts: %d/%d", i + 1, len(ciks))

    if to_snapshot:
        results: list[tuple[str, list[dict]]] | None = None
        if workers > 1 and len(to_snapshot) > 8:
            try:
                with ProcessPoolExecutor(max_workers=workers) as pool:
                    results = list(pool.map(_snapshots_for, to_snapshot, chunksize=4))
            except (BrokenProcessPool, OSError) as exc:  # e.g. spawn restrictions in embedded contexts
                log.warning("snapshot process pool unavailable (%s); computing sequentially", exc)
        if results is None:
            results = [_snapshots_for(a) for a in to_snapshot]
        for (cik, rows), (_, facts, min_date) in zip(results, to_snapshot, strict=True):
            version = stable_hash([len(facts), str(facts["filed_date"].max()), str(min_date)])
            con.execute("DELETE FROM fundamental_snapshots WHERE cik = ?", [cik])
            if rows:
                df = pd.DataFrame(rows)
                df["facts_version"] = version
                upsert_df(con, "fundamental_snapshots", df, ["cik", "snapshot_date"], replace=True)
            report["snapshots_rebuilt"] += 1
    return report


def load_snapshots(con: duckdb.DuckDBPyConnection, ciks: list[str] | None = None) -> pd.DataFrame:
    """All snapshots as a flat frame: one row per (cik, snapshot_date) with payload fields as columns."""
    q = "SELECT cik, snapshot_date, availability_date, period_end, payload FROM fundamental_snapshots"
    params: list[Any] = []
    if ciks is not None:
        q += " WHERE cik IN (SELECT unnest(?))"
        params.append(ciks)
    df = con.execute(q + " ORDER BY cik, snapshot_date", params).df()
    if df.empty:
        return df
    payload = pd.json_normalize(df["payload"].map(json.loads))
    keep_end = {"shares_outstanding__end"}  # share-count date is needed for split adjustment
    payload = payload.drop(columns=[c for c in payload.columns if c.startswith("_")
                                    or (c.endswith("__end") and c not in keep_end)], errors="ignore")
    if "shares_outstanding__end" in payload:
        payload["shares_outstanding__end"] = pd.to_datetime(payload["shares_outstanding__end"])
    out = pd.concat([df.drop(columns=["payload"]).reset_index(drop=True), payload.reset_index(drop=True)], axis=1)
    out["snapshot_date"] = pd.to_datetime(out["snapshot_date"])
    out["availability_date"] = pd.to_datetime(out["availability_date"])
    out["period_end"] = pd.to_datetime(out["period_end"])
    return out
