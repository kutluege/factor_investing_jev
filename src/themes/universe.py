"""T1: theme candidate pool (THEMES_SPEC §2, §3-A) across NASDAQ + NYSE, active and delisted.

Stage A (coarse filter) only decides which companies get their 10-K text scored; it never decides membership,
because FMP industries and EDGAR SIC codes are today's values (not point-in-time).
"""
from __future__ import annotations

import json
import logging
from typing import Any

import duckdb
import pandas as pd

from src.config import load_config
from src.data.fmp import FmpClient
from src.data.http import ApiError, BudgetExhausted
from src.data.reference import _plausible_us_common, profiles_parallel
from src.data.sec import SecClient
from src.db.repo import utcnow
from src.db.schema import upsert_df
from src.themes.config import ThemesConfig

log = logging.getLogger(__name__)

FOREIGN_FORMS = {"20-F", "40-F", "20-F/A", "40-F/A"}
DOMESTIC_FORMS = {"10-K", "10-K405", "10-KT", "10-K/A"}
# FMP exchange codes accepted for each configured exchange (NYSE American is "AMEX" in FMP)
EXCHANGE_ALIASES = {"NASDAQ": {"NASDAQ"}, "NYSE": {"NYSE"}, "NYSE_AMERICAN": {"AMEX"}}

DDL = """CREATE TABLE IF NOT EXISTS theme_candidates (
    symbol VARCHAR PRIMARY KEY, cik VARCHAR, name VARCHAR, exchange VARCHAR, is_active BOOLEAN,
    fmp_sector VARCHAR, fmp_industry VARCHAR, sic INTEGER, sic_description VARCHAR,
    foreign_filer BOOLEAN, is_adr BOOLEAN, stage_a JSON, needs_10k BOOLEAN, ipo_date DATE,
    source VARCHAR, updated_at TIMESTAMP)"""


def allowed_exchanges(cfg: ThemesConfig) -> set[str]:
    out = set()
    for ex in cfg.universe.exchanges:
        out |= EXCHANGE_ALIASES.get(ex.upper(), {ex.upper()})
    if cfg.universe.include_nyse_american:
        out |= EXCHANGE_ALIASES["NYSE_AMERICAN"]
    else:
        out -= EXCHANGE_ALIASES["NYSE_AMERICAN"]
    return out


def stage_a_matches(industry: str | None, sic: int | None, cfg: ThemesConfig) -> list[dict[str, Any]]:
    """Subthemes whose FMP industry list or SIC list contains the company (coarse filter only)."""
    out = []
    for theme, t in cfg.themes.items():
        if not t.enabled:
            continue
        for sub, s in t.subthemes.items():
            by_ind = industry is not None and industry in s.fmp_industries
            by_sic = sic is not None and not pd.isna(sic) and int(sic) in s.sic
            if by_ind or by_sic:
                out.append({"theme": theme, "subtheme": sub, "via": "industry" if by_ind else "sic",
                            "needs_10k": bool(s.keywords)})
    return out


def is_foreign_filer(submissions: dict) -> bool:
    """True when the most recent annual report is a 20-F/40-F (no us-gaap 10-K text or XBRL to work with)."""
    recent = (submissions or {}).get("filings", {}).get("recent", {})
    for form in recent.get("form", []):  # recent filings are newest first
        if form in FOREIGN_FORMS:
            return True
        if form in DOMESTIC_FORMS:
            return False
    return False


def build_candidates(con: duckdb.DuckDBPyConnection, fmp: FmpClient, sec: SecClient, cfg: ThemesConfig,
                     inventory: pd.DataFrame | None = None) -> dict:
    con.execute(DDL)
    ucfg = load_config("universe")  # warrant/unit/preferred exclusion rules
    exch = allowed_exchanges(cfg)
    report: dict[str, Any] = {"exchanges": sorted(exch)}
    # --- active: FMP screener (or the T0 dump) + SEC CIK map ---------------------------------------------------
    if inventory is None:
        rows = []
        for ex in cfg.universe.exchanges:
            rows += fmp.company_screener(exchange=ex, isEtf=False, isFund=False, isActivelyTrading=True)
        inventory = pd.DataFrame(rows)
    # the screener returns both "exchange" (full name) and "exchangeShortName" (code): keep the code only
    inv = inventory.drop(columns=["exchange"], errors="ignore").rename(columns={"exchangeShortName": "exchange"})
    inv = inv[inv["exchange"].isin(exch)]
    cik_map = {str(r["ticker"]).upper(): str(r["cik"]).zfill(10) for r in sec.company_tickers_exchange()}
    records: dict[str, dict] = {}
    for r in inv.itertuples():
        sym = str(r.symbol).upper()
        if not _plausible_us_common(sym, r.companyName, ucfg):
            continue
        records[sym] = {"symbol": sym, "cik": cik_map.get(sym), "name": r.companyName, "exchange": r.exchange,
                        "is_active": True, "fmp_sector": r.sector, "fmp_industry": r.industry, "is_adr": False,
                        "ipo_date": None, "source": "fmp_screener"}
    report["active_screened"] = len(records)
    # --- delisted: FMP symbol list minus actively traded, profiled (profiles cached from earlier runs) ---------
    try:
        all_syms = {str(r.get("symbol", "")).upper(): r.get("companyName") for r in fmp.stock_list()}
        active = {str(r.get("symbol", "")).upper() for r in fmp.actively_trading_list()}
        todo = [s for s, n in all_syms.items() if s not in active and s not in records
                and _plausible_us_common(s, n, ucfg)]
        profiles = profiles_parallel(fmp, todo, ttl_hours=fmp.cfg["ttl_hours"].get("inactive_profile", 720))
        n_del = 0
        for sym, p in profiles.items():
            if not p or str(p.get("exchange", "")).upper() not in exch or p.get("isActivelyTrading"):
                continue
            if p.get("isEtf") or p.get("isFund"):
                continue
            records[sym] = {"symbol": sym, "cik": str(p["cik"]).zfill(10) if p.get("cik") else None,
                            "name": p.get("companyName"), "exchange": str(p.get("exchange")).upper(),
                            "is_active": False, "fmp_sector": p.get("sector"), "fmp_industry": p.get("industry"),
                            "is_adr": bool(p.get("isAdr")), "ipo_date": p.get("ipoDate") or None,
                            "source": "fmp_inactive_profile"}
            n_del += 1
        report["delisted_profiled"] = n_del
    except (BudgetExhausted, ApiError) as exc:
        report["delisted_profiled"] = f"unavailable: {exc}"
    # --- SIC + foreign-filer status from SEC submissions, then stage-A filter -----------------------------------
    rows, n_foreign = [], 0
    for rec in records.values():
        sic, sic_desc, foreign = None, None, False
        if rec["cik"]:
            try:
                sub = sec.submissions(rec["cik"])
                sic = int(sub["sic"]) if str(sub.get("sic", "")).isdigit() else None
                sic_desc = sub.get("sicDescription")
                foreign = is_foreign_filer(sub)
            except ApiError:
                pass
        matches = stage_a_matches(rec["fmp_industry"], sic, cfg)
        if not matches:
            continue
        if rec["is_adr"] and not cfg.universe.include_adr:
            continue
        if foreign and not cfg.universe.include_foreign_filers:
            n_foreign += 1
            continue
        if not rec["cik"]:
            continue  # no SEC filer: no 10-K text and no XBRL fundamentals
        rows.append({**rec, "sic": sic, "sic_description": sic_desc, "foreign_filer": foreign,
                     "stage_a": json.dumps(matches), "needs_10k": any(m["needs_10k"] for m in matches),
                     "updated_at": utcnow()})
    df = pd.DataFrame(rows)
    df["ipo_date"] = pd.to_datetime(df["ipo_date"], errors="coerce").dt.date
    con.execute("DELETE FROM theme_candidates")
    upsert_df(con, "theme_candidates", df, ["symbol"])
    report.update({"candidates": len(df), "excluded_foreign_filers": n_foreign,
                   "needs_10k": int(df["needs_10k"].sum()), "active": int(df["is_active"].sum()),
                   "delisted": int((~df["is_active"]).sum())})
    return report


def candidate_counts(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = con.execute("SELECT symbol, exchange, is_active, stage_a FROM theme_candidates").df()
    rows = []
    for r in df.itertuples():
        for m in json.loads(r.stage_a):
            rows.append({"theme": m["theme"], "subtheme": m["subtheme"], "exchange": r.exchange,
                         "is_active": r.is_active, "via": m["via"]})
    x = pd.DataFrame(rows)
    return (x.groupby(["theme", "subtheme"]).agg(
        candidates=("exchange", "size"), nasdaq=("exchange", lambda s: int((s == "NASDAQ").sum())),
        nyse=("exchange", lambda s: int((s == "NYSE").sum())), delisted=("is_active", lambda s: int((~s).sum())),
        via_sic_only=("via", lambda s: int((s == "sic").sum()))).reset_index())
