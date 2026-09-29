"""Security master: NASDAQ common equities in the configured sector groups, active and (where available) delisted."""
from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    # 3) FMP delisted-companies list (only page 0 on Starter; paid Premium plans return the full history).
    fcfg = load_config("data")["fmp"]
    delisted = 0
    if fmp is not None:
        try:
            for page in range(int(fcfg.get("delisted_max_pages", 1))):
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
            report["sources"]["fmp_delisted_companies"] = f"{delisted} NASDAQ delisted securities (recent list)"
        except ApiError as exc:
            report["sources"]["fmp_delisted_companies"] = f"unavailable: {exc}"

    # 3b) Inactive-symbol discovery (survivorship): every symbol FMP knows minus those actively trading, profiled
    #     to recover exchange, sector, CIK and IPO date. Profiles of inactive symbols are cached for 30 days.
    inactive_found = 0
    if fmp is not None:
        try:
            all_syms = {str(r.get("symbol", "")).upper(): r.get("companyName") for r in fmp.stock_list()}
            active = {str(r.get("symbol", "")).upper() for r in fmp.actively_trading_list()}
            candidates = [sym for sym, name in all_syms.items()
                          if sym not in active and sym not in records and _plausible_us_common(sym, name, ucfg)]
            candidates = candidates[: int(fcfg.get("max_delisted_profiles_per_run", 20000))]
            profiles = profiles_parallel(fmp, candidates, ttl_hours=fcfg["ttl_hours"].get("inactive_profile", 720))
            for sym, prof in profiles.items():
                if not prof or str(prof.get("exchange", "")).upper() != "NASDAQ" or prof.get("isActivelyTrading"):
                    continue
                if prof.get("isEtf") or prof.get("isFund") or prof.get("isAdr"):
                    continue
                records[sym] = {"symbol": sym, "name": prof.get("companyName"), "exchange": "NASDAQ",
                                "is_active": False, "sector": prof.get("sector"), "industry": prof.get("industry"),
                                "cik": str(prof["cik"]).zfill(10) if prof.get("cik") else None,
                                "ipo_date": _to_date(prof.get("ipoDate")), "reference_source": "fmp_inactive_profile"}
                inactive_found += 1
            report["sources"]["fmp_inactive_discovery"] = (f"{len(candidates)} inactive symbols profiled, "
                                                            f"{inactive_found} NASDAQ common stocks recovered")
        except BudgetExhausted as exc:
            report["sources"]["fmp_inactive_discovery"] = f"budget/bandwidth exhausted: {exc}"
        except ApiError as exc:
            report["sources"]["fmp_inactive_discovery"] = f"unavailable: {exc}"

    if not records:
        raise RuntimeError("No reference data could be loaded from SEC or FMP.")

    # 3c) Profiles for delisted-list names and active target-sector names (sector, CIK, IPO date, ADR flag).
    if fmp is not None:
        todo = [r for r in records.values()
                if (not r.get("is_active") and not r.get("sector"))
                or (r.get("is_active") and r.get("sector")
                    and classify(r.get("sector"), r.get("industry"), None, ucfg)[0] is not None)]
        try:
            profiles = profiles_parallel(fmp, [r["symbol"] for r in todo], ttl_hours=fcfg["ttl_hours"]["reference"])
        except BudgetExhausted:
            profiles = {}
            report["limitations"].append("FMP budget exhausted while fetching profiles; retried on the next run.")
        for rec in todo:
            prof = profiles.get(rec["symbol"])
            if not prof:
                continue
            rec["sector"] = rec.get("sector") or prof.get("sector")
            rec["industry"] = rec.get("industry") or prof.get("industry")
            if prof.get("cik") and not rec.get("cik"):
                rec["cik"] = str(prof["cik"]).zfill(10)
            rec["ipo_date"] = rec.get("ipo_date") or _to_date(prof.get("ipoDate"))
            if prof.get("isAdr"):
                rec["is_adr"] = True
        report["sources"]["fmp_profiles"] = f"{sum(1 for v in profiles.values() if v)}/{len(todo)} profiles"

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
        if group is None or excluded or rec.get("is_etf") or rec.get("is_fund") or rec.get("is_adr"):
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
    disc = str(report["sources"].get("fmp_inactive_discovery", "unavailable"))
    complete = bool(fmp_rows) and "unavailable" not in disc and "exhausted" not in disc
    n_inactive = int((~df["is_active"].astype(bool)).sum()) if not df.empty else 0
    report["delisted_in_universe"] = n_inactive
    if n_inactive == 0:
        report["limitations"].append("No delisted securities in the universe: backtests are NOT survivorship-bias free.")
    else:
        report["limitations"].append(
            "Delisted companies are recovered from FMP symbol lists; tickers later reused by another company and "
            "companies FMP no longer lists remain missing (residual survivorship bias).")
    report["status"] = "ok" if complete else "partial"
    set_status(con, "reference", "security_master", report["status"], str(report["sources"]))
    return report


_OTC_FOREIGN = re.compile(r"^[A-Z]{4}[FY]$")  # OTC foreign ordinaries / ADRs (e.g. BNRPF, DSSMY)
_NON_OPERATING = re.compile(r"(?i)\b(etf|fund|trust|index|portfolio|municipal|income shares)\b")


def _plausible_us_common(sym: str, name: str | None, ucfg: dict) -> bool:
    if not re.fullmatch(r"[A-Z]{1,5}", sym) or _OTC_FOREIGN.match(sym):
        return False
    return is_excluded_instrument(sym, name, ucfg) is None and not _NON_OPERATING.search(name or "")


def profiles_parallel(fmp: FmpClient, symbols: list[str], ttl_hours: float | None, workers: int = 4) -> dict:
    """Fetch profiles concurrently (the client's shared rate limiter keeps the rate within the plan)."""
    out: dict[str, dict | None] = {}
    if not symbols:
        return out
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(fmp.profile, s, ttl_hours): s for s in symbols}
        for i, f in enumerate(as_completed(futs), 1):
            sym = futs[f]
            try:
                out[sym] = f.result()
            except BudgetExhausted:
                pool.shutdown(cancel_futures=True)
                raise
            except ApiError as exc:
                log.debug("profile %s: %s", sym, exc)
                out[sym] = None
            if i % 500 == 0:
                log.info("profiles: %d/%d", i, len(symbols))
    return out


def benchmark_symbols() -> list[str]:
    b = load_config("universe")["benchmarks"]
    return list(dict.fromkeys(b["broad"] + list(b["sector"].values())))
