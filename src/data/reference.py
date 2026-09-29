"""Security master: NASDAQ common equities in the configured sector groups, active and (where available) delisted."""
from __future__ import annotations

import logging
import re
from typing import Any

import duckdb
import pandas as pd

from src.config import load_config
from src.data.fmp import FmpClient
from src.data.http import ApiError, BudgetExhausted
from src.data.sec import SecClient
from src.db.repo import set_status, utcnow
from src.db.schema import upsert_df

log = logging.getLogger(__name__)


def classify(sector: str | None, industry: str | None, sic: int | None, universe_cfg: dict) -> tuple[str | None, str]:
    """Return (sector_group, source). FMP sector/industry takes precedence; SIC is the fallback."""
    groups = universe_cfg["groups"]
    if sector or industry:
        for name, g in groups.items():
            if industry and industry in g.get("fmp_industries", []):
                return name, "fmp_industry"
        for name, g in groups.items():
            if sector and sector in g.get("fmp_sectors", []):
                return name, "fmp_sector"
        if sector:  # FMP classified it outside the target universe
            return None, "fmp_sector"
    if sic is not None and not pd.isna(sic):
        for name, g in groups.items():
            for lo, hi in g.get("sic_ranges", []):
                if lo <= int(sic) <= hi:
                    return name, "sic"
    return None, "unclassified"


def is_excluded_instrument(symbol: str, name: str | None, universe_cfg: dict) -> str | None:
    for pat in universe_cfg.get("exclude_name_patterns", []):
        if name and re.search(pat, name):
            return f"name matches {pat}"
    if len(symbol) == 5 and any(symbol.endswith(s) for s in universe_cfg.get("exclude_symbol_suffixes", [])
                                if len(s) == 1):
        return "NASDAQ 5th-letter suffix indicates warrant/unit/right"
    if not re.fullmatch(r"[A-Z]{1,5}", symbol):
        return "non-standard symbol"
    return None


def _to_date(v: Any):
    if v in (None, "", "None"):
        return None
    d = pd.to_datetime(v, errors="coerce")
    return None if pd.isna(d) else d.date()


def build_security_master(con: duckdb.DuckDBPyConnection, fmp: FmpClient | None, sec: SecClient | None,
                          fetch_sic_for_unclassified: bool = True) -> dict[str, Any]:
    """Assemble and persist the security master. Returns a report of sources used and their limitations."""
    ucfg = load_config("universe")
    report: dict[str, Any] = {"sources": {}, "limitations": []}
    records: dict[str, dict] = {}

    # 1) SEC: current tickers with exchange (free, includes CIK for fundamentals).
    if sec is not None:
        try:
            for r in sec.company_tickers_exchange():
                if (r.get("exchange") or "").lower() != "nasdaq" or not r.get("ticker"):
                    continue
                sym = str(r["ticker"]).upper().replace("-", ".")
                records[sym] = {"symbol": sym, "cik": str(r["cik"]).zfill(10), "name": r.get("name"),
                                "exchange": "NASDAQ", "is_active": True, "reference_source": "sec_tickers"}
            report["sources"]["sec_company_tickers_exchange"] = f"{len(records)} NASDAQ tickers"
        except ApiError as exc:
            report["sources"]["sec_company_tickers_exchange"] = f"unavailable: {exc}"

    # 2) FMP screener: sector/industry/ETF/fund flags for currently listed names.
    fmp_rows: list[dict] = []
    if fmp is not None:
        try:
            fmp_rows = fmp.company_screener(exchange="NASDAQ", isEtf=False, isFund=False,
                                            isActivelyTrading=True, includeAllShareClasses=False)
            report["sources"]["fmp_company_screener"] = f"{len(fmp_rows)} rows"
        except BudgetExhausted as exc:
            report["sources"]["fmp_company_screener"] = f"budget/bandwidth exhausted: {exc}"
        except ApiError as exc:
            report["sources"]["fmp_company_screener"] = f"unavailable: {exc}"
    for r in fmp_rows:
        sym = str(r.get("symbol", "")).upper()
        if not sym:
            continue
        rec = records.setdefault(sym, {"symbol": sym, "exchange": "NASDAQ", "is_active": True,
                                       "reference_source": "fmp_screener"})
        rec.update({"name": rec.get("name") or r.get("companyName"), "sector": r.get("sector"),
                    "industry": r.get("industry"), "is_etf": bool(r.get("isEtf")), "is_fund": bool(r.get("isFund")),
                    "reference_market_cap": r.get("marketCap"),
                    "is_active": bool(r.get("isActivelyTrading", True))})

    # 3) FMP delisted companies (survivorship). Paginated; may be plan-restricted.
    delisted = 0
    if fmp is not None:
        try:
            page = 0
            while page < 200:
                rows = fmp.delisted_companies(page=page, limit=100)
                if not rows:
                    break
                for r in rows:
                    if "NASDAQ" not in str(r.get("exchange", "")).upper():
                        continue
                    sym = str(r.get("symbol", "")).upper()
                    if not sym or (sym in records and records[sym].get("is_active")):
                        continue  # ticker since reused by an active listing; keep the active record
                    records[sym] = {"symbol": sym, "name": r.get("companyName"), "exchange": "NASDAQ",
                                    "is_active": False, "ipo_date": _to_date(r.get("ipoDate")),
                                    "delisted_date": _to_date(r.get("delistedDate")),
                                    "reference_source": "fmp_delisted"}
                    delisted += 1
                page += 1
            report["sources"]["fmp_delisted_companies"] = f"{delisted} NASDAQ delisted securities"
        except ApiError as exc:
            report["sources"]["fmp_delisted_companies"] = f"unavailable: {exc}"
            report["limitations"].append(
                "Delisted-company list unavailable: historical universes contain only securities that are still "
                "listed today (plus any delisted names already stored). Backtests are NOT survivorship-bias free.")

    if not records:
        raise RuntimeError("No reference data could be loaded from SEC or FMP.")

    # 3b) Delisted names carry no sector in the delisted list: classify them via FMP profiles (budget-limited),
    #     otherwise they would silently drop out of the universe and re-introduce survivorship bias.
    if fmp is not None:
        max_profiles = int(load_config("data")["fmp"].get("max_delisted_profiles_per_run", 150))
        todo = [r for r in records.values() if not r.get("is_active") and not r.get("sector")][:max_profiles]
        classified = 0
        for rec in todo:
            try:
                prof = fmp.profile(rec["symbol"])
            except BudgetExhausted:
                report["limitations"].append("FMP budget exhausted while classifying delisted companies; "
                                             "remaining delisted names are classified on later runs.")
                break
            except ApiError:
                continue
            if prof:
                rec["sector"], rec["industry"] = prof.get("sector"), prof.get("industry")
                if prof.get("cik"):
                    rec["cik"] = str(prof["cik"]).zfill(10)
                rec["ipo_date"] = rec.get("ipo_date") or _to_date(prof.get("ipoDate"))
                classified += 1
        report["sources"]["fmp_profiles_for_delisted"] = f"{classified}/{len(todo)} classified"

    # 4) SIC fallback for names FMP did not classify (SEC submissions; free, ~8 req/s).
    if sec is not None and fetch_sic_for_unclassified:
        need = [r for r in records.values() if not r.get("sector") and r.get("cik")]
        fetched = 0
        for rec in need:
            try:
                sub = sec.submissions(rec["cik"])
            except ApiError as exc:
                log.debug("submissions %s: %s", rec["symbol"], exc)
                continue
            fetched += 1
            rec["sic"] = int(sub["sic"]) if str(sub.get("sic", "")).isdigit() else None
            rec["sic_description"] = sub.get("sicDescription")
            if sub.get("entityType") and sub["entityType"] != "operating":
                rec["is_fund"] = True
        report["sources"]["sec_submissions_sic"] = f"{fetched} companies classified by SIC"

    rows = []
    unclassified_delisted = 0
    for rec in records.values():
        group, source = classify(rec.get("sector"), rec.get("industry"), rec.get("sic"), ucfg)
        excluded = is_excluded_instrument(rec["symbol"], rec.get("name"), ucfg)
        if group is None and source == "unclassified" and not rec.get("is_active"):
            unclassified_delisted += 1
        if group is None or excluded or rec.get("is_etf") or rec.get("is_fund"):
            continue
        rows.append({
            "symbol": rec["symbol"], "cik": rec.get("cik"), "name": rec.get("name"), "exchange": "NASDAQ",
            "sector": rec.get("sector"), "industry": rec.get("industry"), "sic": rec.get("sic"),
            "sic_description": rec.get("sic_description"), "sector_group": group, "classification_source": source,
            "is_etf": bool(rec.get("is_etf", False)), "is_fund": bool(rec.get("is_fund", False)),
            "is_active": bool(rec.get("is_active", True)), "ipo_date": rec.get("ipo_date"),
            "delisted_date": rec.get("delisted_date"), "reference_source": rec.get("reference_source"),
            "reference_market_cap": rec.get("reference_market_cap"), "updated_at": utcnow(),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        # Keep price-derived dates already stored; only reference columns are refreshed.
        upsert_df(con, "securities", df, ["symbol"], replace=True)
    report["universe_securities"] = len(df)
    if unclassified_delisted:
        report["limitations"].append(
            f"{unclassified_delisted} delisted NASDAQ securities could not be classified by sector and are excluded "
            "(residual survivorship bias).")
    report["by_group"] = df["sector_group"].value_counts().to_dict() if not df.empty else {}
    report["classification"] = df["classification_source"].value_counts().to_dict() if not df.empty else {}
    report["limitations"].append(
        "Sector/industry classifications are current snapshots (FMP profile or SEC SIC), not point-in-time.")
    # 'partial' when FMP classification/delisting sources failed: the next run rebuilds instead of reusing it
    complete = bool(fmp_rows) and "unavailable" not in str(report["sources"].get("fmp_delisted_companies", ""))
    report["status"] = "ok" if complete else "partial"
    set_status(con, "reference", "security_master", report["status"], str(report["sources"]))
    return report


def benchmark_symbols() -> list[str]:
    b = load_config("universe")["benchmarks"]
    return list(dict.fromkeys(b["broad"] + list(b["sector"].values())))
