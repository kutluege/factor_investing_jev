"""Shared pipeline building blocks used by bootstrap, the monthly run, the CLI and the Streamlit button."""
from __future__ import annotations

import logging
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import duckdb
import pandas as pd

from src.config import PROJECT_ROOT, Settings, database_path, get_settings, load_config
from src.data.fmp import FmpClient
from src.data.fundamentals_loader import load_fundamentals
from src.data.http import ApiError
from src.data.prices import infer_missing_splits, load_prices, load_splits
from src.data.reference import benchmark_symbols, build_security_master
from src.data.sec import SecClient
from src.db.repo import RequestLog
from src.db.schema import connect

log = logging.getLogger(__name__)


@dataclass
class Context:
    con: duckdb.DuckDBPyConnection
    settings: Settings
    progress: Callable[[str, str], None] = lambda step, msg: None
    report: dict[str, Any] = field(default_factory=dict)

    def step(self, name: str, msg: str) -> None:
        log.info("[%s] %s", name, msg)
        self.progress(name, msg)


def open_context(db_path: str | None = None, progress: Callable[[str, str], None] | None = None) -> Context:
    settings = get_settings()
    con = connect(db_path or database_path(settings))
    return Context(con=con, settings=settings, progress=progress or (lambda s, m: None))


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def verify_configuration(ctx: Context) -> dict:
    """Step 1: credentials and configuration. Never prints secret values."""
    creds = ctx.settings.credential_report()
    problems = []
    if not ctx.settings.fmp_api_key:
        problems.append("FMP_API_KEY missing: prices cannot be updated")
    if not ctx.settings.sec_user_agent or "@" not in (ctx.settings.sec_user_agent or ""):
        problems.append("SEC_USER_AGENT missing or without contact email: fundamentals cannot be updated")
    jev = "available" if ctx.settings.jev_available else (
        "disabled (JEV_ENABLED=false)" if not ctx.settings.jev_enabled else "unavailable (AI_GATEWAY_API_KEY missing)")
    for name in ("universe", "factors", "backtest", "jev", "data"):
        load_config(name)  # raises on malformed YAML
    out = {"credentials": creds, "jev": jev, "problems": problems}
    ctx.report["verify"] = out
    ctx.step("verify", f"Jev {jev}; {len(problems)} problem(s)")
    return out


def make_clients(ctx: Context) -> tuple[FmpClient | None, SecClient | None]:
    rl = RequestLog(ctx.con)
    fmp = sec = None
    try:
        fmp = FmpClient(request_logger=rl, calls_today=lambda: rl.live_calls_today("fmp"))
    except ApiError as exc:
        ctx.step("clients", f"FMP unavailable: {exc}")
    try:
        sec = SecClient(request_logger=rl)
    except ApiError as exc:
        ctx.step("clients", f"SEC unavailable: {exc}")
    return fmp, sec


def update_reference(ctx: Context, fmp, sec, max_age_days: int = 7, force: bool = False) -> dict:
    row = ctx.con.execute("SELECT max(updated_at), count(*) FROM securities").fetchone()
    last_status = ctx.con.execute("SELECT status FROM data_load_status WHERE item='reference' AND key='security_master'"
                                  ).fetchone()
    fresh = (row[1] > 0 and row[0] is not None and (pd.Timestamp.now() - pd.Timestamp(row[0])).days < max_age_days
             and last_status is not None and last_status[0] == "ok")
    if fresh and not force:
        out = {"status": "fresh", "securities": row[1]}
    else:
        try:
            out = build_security_master(ctx.con, fmp, sec)
        except RuntimeError as exc:
            out = {"status": "failed", "error": str(exc), "securities": row[1]}
    ctx.report["reference"] = out
    ctx.step("reference", f"security master: {out.get('universe_securities', out.get('securities'))} securities")
    return out


def price_priority(con: duckdb.DuckDBPyConnection, symbols: list[str] | None = None, portfolio_id: str = "production"
                   ) -> list[str]:
    """Benchmarks, then current holdings, then securities (largest last-known market cap first)."""
    held = [r[0] for r in con.execute(
        "SELECT DISTINCT symbol FROM portfolio_positions WHERE portfolio_id = ? AND as_of_date = "
        "(SELECT max(as_of_date) FROM portfolio_positions WHERE portfolio_id = ?)", [portfolio_id, portfolio_id]).fetchall()]
    if symbols is None:
        rows = con.execute("""
            SELECT s.symbol FROM securities s
            LEFT JOIN (SELECT symbol, arg_max(market_cap, rebalance_date) AS mc FROM rebalance_universe GROUP BY symbol) u
              USING (symbol)
            ORDER BY s.is_active DESC, coalesce(u.mc, s.reference_market_cap) DESC NULLS LAST, s.symbol""").fetchall()
        symbols = [r[0] for r in rows]
    return list(dict.fromkeys(benchmark_symbols() + held + symbols))


def update_prices(ctx: Context, fmp, symbols: list[str] | None = None, max_symbols: int | None = None) -> dict:
    if fmp is None:
        out = {"status": "skipped", "reason": "FMP client unavailable"}
    else:
        order = price_priority(ctx.con, symbols)
        out = load_prices(ctx.con, fmp, order, max_symbols=max_symbols)
        out["fmp_unavailable_endpoints"] = dict(fmp.unavailable)
        out["fmp_live_calls_this_run"] = fmp.stats.live_calls
        out["fmp_cache_hits_this_run"] = fmp.stats.cache_hits
        if not out.get("stopped_reason"):
            with_prices = [r[0] for r in ctx.con.execute("SELECT DISTINCT symbol FROM daily_prices").fetchall()]
            out["splits"] = load_splits(ctx.con, fmp, [s for s in order if s in with_prices])
    ctx.report["prices"] = out
    ctx.step("prices", f"prices loaded={out.get('loaded', 0)} stopped={out.get('stopped_reason')}")
    return out


def update_fundamentals(ctx: Context, sec, symbols: list[str] | None = None,
                        snapshot_min_date: pd.Timestamp | None = None) -> dict:
    if sec is None:
        out = {"status": "skipped", "reason": "SEC client unavailable"}
    else:
        q = "SELECT DISTINCT cik FROM securities WHERE cik IS NOT NULL"
        params: list[Any] = []
        if symbols is not None:
            q += " AND symbol IN (SELECT unnest(?))"
            params.append(symbols)
        else:
            q += " AND symbol IN (SELECT DISTINCT symbol FROM daily_prices)"
        ciks = [r[0] for r in ctx.con.execute(q, params).fetchall()]
        scfg = load_config("data")["sec"]
        if snapshot_min_date is None and scfg.get("snapshot_min_date"):
            snapshot_min_date = pd.Timestamp(scfg["snapshot_min_date"])
        out = load_fundamentals(ctx.con, sec, ciks, snapshot_min_date=snapshot_min_date,
                                workers=int(scfg.get("snapshot_workers", 4)))
        out["split_inference"] = infer_missing_splits(ctx.con)
    ctx.report["fundamentals"] = out
    ctx.step("fundamentals", f"SEC facts loaded for {out.get('loaded', 0)} companies")
    return out


def data_snapshot(con: duckdb.DuckDBPyConnection) -> dict:
    """Compact fingerprint of the input data used by a run (for reproducibility)."""
    p = con.execute("SELECT count(*), count(DISTINCT symbol), min(date), max(date), max(loaded_at) FROM daily_prices").fetchone()
    f = con.execute("SELECT count(*), count(DISTINCT cik), max(filed_date), max(loaded_at) FROM financial_facts").fetchone()
    s = con.execute("SELECT count(*), count(*) FILTER (WHERE NOT is_active) FROM securities").fetchone()
    return {"prices": {"rows": p[0], "symbols": p[1], "first": str(p[2]), "last": str(p[3]), "loaded_at": str(p[4])},
            "facts": {"rows": f[0], "companies": f[1], "last_filed": str(f[2]), "loaded_at": str(f[3])},
            "securities": {"rows": s[0], "inactive": s[1]}, "snapshot_date": str(date.today())}
