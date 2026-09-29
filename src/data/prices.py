"""Daily price ingestion (FMP), split handling and PIT share counts."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from src.config import load_config
from src.data.fmp import FmpClient
from src.data.http import ApiError, BudgetExhausted, PlanRestricted
from src.db.repo import set_status, utcnow
from src.db.schema import upsert_df

log = logging.getLogger(__name__)


def _prices_frame(symbol: str, raw: list[dict], adjusted: list[dict] | None) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    df = df.rename(columns=str.lower)
    need = {"date", "open", "high", "low", "close", "volume"}
    if not need.issubset(df.columns):
        raise ApiError("fmp", 200, f"unexpected price payload columns: {sorted(df.columns)[:12]}")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    out = df[["date", "open", "high", "low", "close", "volume"]].copy()
    out["adj_close"] = out["close"]
    source = "fmp_full"
    if adjusted:
        adj = pd.DataFrame(adjusted).rename(columns=str.lower)
        if {"date", "adjclose"}.issubset(adj.columns):
            adj["date"] = pd.to_datetime(adj["date"]).dt.date
            out = out.merge(adj[["date", "adjclose"]], on="date", how="left")
            out["adj_close"] = out["adjclose"].fillna(out["close"])
            out = out.drop(columns=["adjclose"])
            source = "fmp_full+dividend_adjusted"
    out.insert(0, "symbol", symbol)
    out["source"] = source
    out["loaded_at"] = utcnow()
    out = out.dropna(subset=["close"])
    out = out[(out["close"] > 0) & (out["volume"] >= 0)]
    return out.sort_values("date").reset_index(drop=True)


def load_prices(con: duckdb.DuckDBPyConnection, fmp: FmpClient, symbols: list[str], end: date | None = None,
                fetch_dividend_adjusted: bool = True, max_symbols: int | None = None,
                workers: int = 4) -> dict[str, Any]:
    """Load or incrementally update daily prices. Stops cleanly when the FMP budget is exhausted.

    HTTP fetches run on ``workers`` threads (the client's shared rate limiter enforces the plan's request
    rate); every database write happens on the calling thread.
    """
    cfg = load_config("data")["fmp"]
    end = end or date.today()
    if cfg.get("history_start"):
        default_start = pd.Timestamp(cfg["history_start"]).date()
    else:
        default_start = end - timedelta(days=int(365.25 * cfg.get("history_years", 5)))
    last_dates = dict(con.execute("SELECT symbol, max(date) FROM daily_prices GROUP BY symbol").fetchall())
    report = {"requested": 0, "loaded": 0, "up_to_date": 0, "failed": {}, "stopped_reason": None,
              "dividend_adjusted": fetch_dividend_adjusted}
    state = {"div_adj_ok": fetch_dividend_adjusted}

    todo = []
    for sym in symbols:
        last = last_dates.get(sym)
        if last is not None and (end - last).days <= 0:
            report["up_to_date"] += 1
            continue
        todo.append(sym)
    if max_symbols is not None and len(todo) > max_symbols:
        todo = todo[:max_symbols]
        report["stopped_reason"] = f"max_symbols={max_symbols}"

    def fetch(sym: str):
        last = last_dates.get(sym)
        # Incremental windows start ON the last stored date so the overlap can chain adjusted prices.
        start = default_start if last is None else last
        raw = fmp.historical_prices(sym, start, end)
        adjusted = None
        if state["div_adj_ok"] and raw:
            try:
                adjusted = fmp.dividend_adjusted_prices(sym, start, end)
            except PlanRestricted as exc:
                state["div_adj_ok"] = False
                report["dividend_adjusted"] = f"unavailable ({exc}); adj_close = split-adjusted close"
        return raw, adjusted

    stop = False
    chunk = 40
    for c0 in range(0, len(todo), chunk):
        batch = todo[c0:c0 + chunk]
        results: dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = {pool.submit(fetch, s): s for s in batch}
            for f in as_completed(futs):
                results[futs[f]] = f
        for sym in batch:
            report["requested"] += 1
            last = last_dates.get(sym)
            try:
                raw, adjusted = results[sym].result()
                df = _prices_frame(sym, raw, adjusted)
                if last is not None and not df.empty and _rebased(con, sym, last, df):
                    # vendor re-based history (split or correction): replace the whole stored series
                    log.info("prices: %s history re-based by vendor; reloading full window", sym)
                    raw = fmp.historical_prices(sym, default_start, end)
                    adjusted = fmp.dividend_adjusted_prices(sym, default_start, end) if state["div_adj_ok"] else None
                    df = _prices_frame(sym, raw, adjusted)
                    con.execute("DELETE FROM daily_prices WHERE symbol = ?", [sym])
                    report.setdefault("rebased", []).append(sym)
                elif last is not None and not df.empty:
                    df = chain_adjusted(con, sym, last, df)
                if not df.empty:
                    upsert_df(con, "daily_prices", df, ["symbol", "date"], replace=True)
                    report["loaded"] += 1
                set_status(con, "prices", sym, "ok" if not df.empty else "empty")
            except BudgetExhausted as exc:
                report["stopped_reason"] = str(exc)
                set_status(con, "prices", sym, "pending", "budget exhausted")
                stop = True
            except ApiError as exc:
                report["failed"][sym] = str(exc)[:200]
                set_status(con, "prices", sym, "failed", str(exc))
        log.info("prices: %d/%d symbols processed", min(c0 + chunk, len(todo)), len(todo))
        if stop:
            break
    refresh_price_dates(con)
    return report


def _rebased(con: duckdb.DuckDBPyConnection, symbol: str, last: date, new: pd.DataFrame) -> bool:
    stored = con.execute("SELECT close FROM daily_prices WHERE symbol = ? AND date = ?", [symbol, last]).fetchone()
    overlap = new[new["date"] == last]
    if stored is None or overlap.empty or not stored[0]:
        return False
    return abs(float(overlap["close"].iloc[0]) / float(stored[0]) - 1.0) > 0.01


def chain_adjusted(con: duckdb.DuckDBPyConnection, symbol: str, last: date, new: pd.DataFrame) -> pd.DataFrame:
    """Rescale newly fetched adjusted closes so they continue the stored series from the overlap date.

    Vendor dividend adjustment is back-propagated, so a fresh window is on a different adjustment base than
    stored history. Chaining keeps stored history immutable and total-return continuity intact.
    """
    stored = con.execute("SELECT adj_close FROM daily_prices WHERE symbol = ? AND date = ?", [symbol, last]).fetchone()
    overlap = new[new["date"] == last]
    new = new[new["date"] > last].copy()
    if stored is None or overlap.empty or not stored[0] or not overlap["adj_close"].iloc[0]:
        return new
    new["adj_close"] = new["adj_close"] * (float(stored[0]) / float(overlap["adj_close"].iloc[0]))
    return new


def refresh_price_dates(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        UPDATE securities SET first_price_date = p.first_d, last_price_date = p.last_d
        FROM (SELECT symbol, min(date) AS first_d, max(date) AS last_d FROM daily_prices GROUP BY symbol) p
        WHERE securities.symbol = p.symbol
    """)
    # an inactive security without a vendor delisting date is treated as delisted after its last trading day
    con.execute("""
        UPDATE securities SET delisted_date = last_price_date + INTERVAL 1 DAY
        WHERE NOT is_active AND delisted_date IS NULL AND last_price_date IS NOT NULL
    """)


def load_splits(con: duckdb.DuckDBPyConnection, fmp: FmpClient, symbols: list[str]) -> dict[str, Any]:
    report = {"loaded": 0, "stopped_reason": None, "available": True}
    done = set(r[0] for r in con.execute("SELECT key FROM data_load_status WHERE item='splits'").fetchall())
    for sym in symbols:
        if sym in done:
            continue
        try:
            rows = fmp.splits(sym)
        except BudgetExhausted as exc:
            report["stopped_reason"] = str(exc)
            break
        except PlanRestricted as exc:
            report["available"] = False
            report["stopped_reason"] = f"splits endpoint unavailable: {exc}"
            break
        except ApiError as exc:
            set_status(con, "splits", sym, "failed", str(exc))
            continue
        con.execute("DELETE FROM stock_splits WHERE symbol = ? AND source = 'inferred_sec'", [sym])  # vendor wins
        recs = []
        for r in rows or []:
            num, den = r.get("numerator"), r.get("denominator")
            if num and den and float(den) > 0:
                recs.append({"symbol": sym, "date": pd.to_datetime(r["date"]).date(),
                             "ratio": float(num) / float(den), "source": "fmp"})
        if recs:
            upsert_df(con, "stock_splits", pd.DataFrame(recs), ["symbol", "date"], replace=True)
        set_status(con, "splits", sym, "ok")
        report["loaded"] += 1
    return report


_CLEAN_RATIOS = np.array([2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50, 1 / 2, 1 / 3, 1 / 4, 1 / 5, 1 / 8, 1 / 10,
                          1 / 15, 1 / 20, 1 / 25, 1 / 30, 1 / 40, 1 / 50, 1.5, 2 / 3])


def infer_splits_from_shares(shares: pd.DataFrame) -> list[tuple[pd.Timestamp, float]]:
    """Fallback split detection: consecutive reported share counts jumping by a clean ratio (>=1.5x) within a year.

    ``shares`` columns: period_end, value (as-reported share counts, sorted). Only used when the FMP splits
    endpoint is unavailable; recorded with source='inferred_sec' so the limitation stays visible.
    """
    out = []
    s = shares.sort_values("period_end")
    vals, ends = s["value"].to_numpy(float), s["period_end"].to_list()
    for i in range(1, len(vals)):
        if vals[i - 1] <= 0 or (ends[i] - ends[i - 1]).days > 400:
            continue
        r = vals[i] / vals[i - 1]
        if 0.7 < r < 1.4:
            continue
        j = int(np.argmin(np.abs(np.log(_CLEAN_RATIOS) - np.log(r))))
        if abs(np.log(_CLEAN_RATIOS[j]) - np.log(r)) < 0.03:
            out.append((ends[i], float(_CLEAN_RATIOS[j])))
    return out


def infer_missing_splits(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    """Fallback when FMP splits are unavailable: infer splits from as-reported SEC share counts.

    Uses the first-filed value for each share-count date (what was reported before any later restatement), so a
    split appears as a clean-ratio jump between consecutive filings. Stored with source='inferred_sec'.
    """
    have_vendor = {r[0] for r in con.execute(
        "SELECT key FROM data_load_status WHERE item = 'splits' AND status = 'ok'").fetchall()}
    rows = con.execute("""
        SELECT s.symbol, f.period_end, arg_min(f.value, f.filed_date) AS value
        FROM financial_facts f JOIN securities s ON s.cik = f.cik
        WHERE f.metric = 'shares_outstanding' AND f.concept = 'dei:EntityCommonStockSharesOutstanding'
        GROUP BY 1, 2 ORDER BY 1, 2""").df()
    inferred = 0
    for sym, g in rows.groupby("symbol"):
        if sym in have_vendor:
            continue
        g = g.assign(period_end=pd.to_datetime(g["period_end"]))
        found = infer_splits_from_shares(g[["period_end", "value"]])
        con.execute("DELETE FROM stock_splits WHERE symbol = ? AND source = 'inferred_sec'", [sym])
        if found:
            upsert_df(con, "stock_splits", pd.DataFrame([{"symbol": sym, "date": d.date(), "ratio": r,
                                                          "source": "inferred_sec"} for d, r in found]),
                      ["symbol", "date"], replace=False)
            inferred += len(found)
    return {"inferred_splits": inferred, "symbols_with_vendor_splits": len(have_vendor)}


def split_factor_after(splits: pd.DataFrame, symbol: str, after: pd.Timestamp) -> float:
    """Cumulative split ratio for splits strictly after ``after`` (converts as-reported shares to adjusted units)."""
    if splits is None or splits.empty:
        return 1.0
    s = splits[(splits["symbol"] == symbol) & (pd.to_datetime(splits["date"]) > pd.Timestamp(after))]
    return float(np.prod(s["ratio"].to_numpy())) if not s.empty else 1.0


def price_matrix(con: duckdb.DuckDBPyConnection, column: str, symbols: list[str] | None = None,
                 start: date | None = None, end: date | None = None) -> pd.DataFrame:
    q = f"SELECT date, symbol, {column} AS v FROM daily_prices WHERE 1=1"
    params: list[Any] = []
    if symbols is not None:
        q += " AND symbol IN (SELECT unnest(?))"
        params.append(symbols)
    if start is not None:
        q += " AND date >= ?"
        params.append(start)
    if end is not None:
        q += " AND date <= ?"
        params.append(end)
    df = con.execute(q, params).df()
    if df.empty:
        return pd.DataFrame()
    m = df.pivot(index="date", columns="symbol", values="v").sort_index()
    m.index = pd.to_datetime(m.index)
    return m
