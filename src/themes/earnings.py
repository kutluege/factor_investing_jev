"""T4b: FMP earnings dates vs EDGAR 8-K Item 2.02 acceptance times, and the announcement-event loader.

Verification (THEMES_SPEC §4): for a random sample of firm-quarters, the FMP ``earnings`` date is compared with the
US Eastern acceptance date of the nearest 8-K whose ``items`` include 2.02 (Results of Operations and Financial
Condition). Agreement = same calendar date. Agreement >= 90% -> FMP dates; otherwise 8-K dates are used for
``ear_3d`` / ``sue_announce`` timing (src/features/earnings_events.py). Analyst estimates are never used.
"""
from __future__ import annotations

import logging
import random
from concurrent.futures import ThreadPoolExecutor

import duckdb
import pandas as pd

from src.data.fmp import FmpClient
from src.data.http import ApiError
from src.data.sec import SecClient
from src.features.earnings_events import announcement_events
from src.themes.edgar_text import submission_blocks
from src.themes.membership import eastern_time

log = logging.getLogger(__name__)

AGREEMENT_THRESHOLD = 0.90

DDL = """
CREATE TABLE IF NOT EXISTS earnings_events (
    symbol VARCHAR, cik VARCHAR, accession VARCHAR, acceptance_et TIMESTAMP, t0 DATE, available_from DATE,
    eps DOUBLE, fmp_date DATE, PRIMARY KEY (symbol, accession))
"""


def fmp_earnings(fmp: FmpClient, symbol: str, limit: int = 100) -> pd.DataFrame:
    rows = fmp._get("earnings", {"symbol": symbol, "limit": limit}, ttl_hours=fmp.cfg["ttl_hours"]["reference"]) or []
    df = pd.DataFrame(rows)
    if df.empty or "date" not in df:
        return pd.DataFrame(columns=["symbol", "date", "epsActual", "epsEstimated"]).astype({"date": "datetime64[ns]"})
    df["date"] = pd.to_datetime(df["date"])
    return df[df["epsActual"].notna()].sort_values("date").reset_index(drop=True)


def earnings_8k(sec: SecClient, cik: str, since: str = "2004-08-23") -> pd.DataFrame:
    """8-K filings with Item 2.02 (item codes exist since the 2004-08-23 8-K reform), acceptance in US Eastern."""
    rows = []
    for b in submission_blocks(sec, cik, since):
        items = b.get("items") or [""] * len(b.get("form", []))
        for i, form in enumerate(b.get("form", [])):
            if form.startswith("8-K") and "2.02" in str(items[i]):
                rows.append({"accession": b["accessionNumber"][i], "acceptance": eastern_time(b["acceptanceDateTime"][i])})
    if not rows:
        return pd.DataFrame({"accession": pd.Series(dtype=str), "acceptance": pd.Series(dtype="datetime64[ns]")})
    return pd.DataFrame(rows).drop_duplicates("accession").sort_values("acceptance").reset_index(drop=True)


def compare_sample(fmp: FmpClient, sec: SecClient, candidates: pd.DataFrame, n: int = 20, seed: int = 20260930,
                   min_date: str = "2012-01-01") -> pd.DataFrame:
    """One random FMP announcement per randomly ordered firm until ``n`` firm-quarters with 8-K data exist."""
    rng = random.Random(seed)
    out = []
    for c in candidates.sample(frac=1.0, random_state=seed).itertuples():
        if len(out) >= n:
            break
        try:
            e = fmp_earnings(fmp, c.symbol)
            k = earnings_8k(sec, c.cik)
        except ApiError:
            continue
        e = e[e["date"] >= pd.Timestamp(min_date)]
        if e.empty or k.empty:
            continue
        row = e.iloc[rng.randrange(len(e))]
        d = row["date"]
        near = k.iloc[(k["acceptance"].dt.normalize() - d).abs().argsort()[:1]]
        acc = near["acceptance"].iloc[0]
        gap = (acc.normalize() - d).days
        out.append({"symbol": c.symbol, "fmp_date": d.date(), "eps_actual": row["epsActual"],
                    "k8_acceptance_et": acc, "k8_accession": near["accession"].iloc[0], "gap_days": gap,
                    "agree_same_day": gap == 0, "agree_within_1": abs(gap) <= 1, "after_close": acc.hour >= 16})
    return pd.DataFrame(out)


def build_earnings_events(con: duckdb.DuckDBPyConnection, fmp: FmpClient, sec: SecClient, symbols_ciks: pd.DataFrame,
                          sessions: pd.DatetimeIndex, workers: int = 4) -> dict:
    """Announcement events for every (symbol, cik) -> table ``earnings_events`` (replaced per symbol)."""
    con.execute(DDL)

    def one(sym: str, cik: str) -> pd.DataFrame | None:
        try:
            ev = announcement_events(earnings_8k(sec, cik), fmp_earnings(fmp, sym), sessions)
        except ApiError as e:
            log.warning("earnings events %s: %s", sym, e)
            return None
        ev.insert(0, "cik", cik)
        ev.insert(0, "symbol", sym)
        return ev

    pairs = list(symbols_ciks[["symbol", "cik"]].dropna().itertuples(index=False, name=None))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda p: one(*p), pairs))
    frames = [r for r in results if r is not None and not r.empty]
    failed = sum(r is None for r in results)
    if frames:
        con.register("ev_new", pd.concat(frames, ignore_index=True).rename(columns={"acceptance": "acceptance_et"}))
        con.execute("DELETE FROM earnings_events WHERE symbol IN (SELECT DISTINCT symbol FROM ev_new)")
        con.execute("INSERT INTO earnings_events SELECT symbol, cik, accession, acceptance_et, t0, available_from, "
                    "eps, fmp_date FROM ev_new")
        con.unregister("ev_new")
    n = sum(len(f) for f in frames)
    with_eps = sum(int(f["eps"].notna().sum()) for f in frames)
    return {"symbols": len(pairs), "with_events": len(frames), "failed": failed, "events": n,
            "events_with_fmp_eps": with_eps, "eps_match_rate": round(with_eps / n, 3) if n else None}


def load_events(con: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    df = con.execute("SELECT symbol, accession, acceptance_et AS acceptance, t0, available_from, eps, fmp_date "
                     "FROM earnings_events").df()
    for c in ("t0", "available_from", "fmp_date"):
        df[c] = pd.to_datetime(df[c])
    return {s: g.drop(columns="symbol").sort_values("t0").reset_index(drop=True) for s, g in df.groupby("symbol")}
