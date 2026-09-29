"""Research diagnostics: automated red flags attached to every backtest run."""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from src.backtest.engine import BacktestResult
from src.backtest.metrics import sector_exposure
from src.config import load_config


def lookahead_audit(con: duckdb.DuckDBPyConnection) -> dict:
    """Checks persisted features for any value whose availability is after its rebalance date."""
    fv = con.execute("SELECT count(*) FROM factor_values WHERE availability_date > rebalance_date").fetchone()[0]
    tv = con.execute("SELECT count(*) FROM technical_values WHERE as_of_price_date > rebalance_date").fetchone()[0]
    snaps = con.execute("SELECT count(*) FROM fundamental_snapshots WHERE availability_date > snapshot_date").fetchone()[0]
    return {"future_factor_values": int(fv), "future_technical_values": int(tv), "future_snapshots": int(snaps),
            "passed": fv == 0 and tv == 0 and snaps == 0}


def survivorship_status(con: duckdb.DuckDBPyConnection) -> dict:
    n_all, n_inactive = con.execute(
        "SELECT count(*), count(*) FILTER (WHERE NOT is_active) FROM securities").fetchone()
    with_prices = con.execute("""SELECT count(*) FROM securities s WHERE NOT is_active AND EXISTS
                                 (SELECT 1 FROM daily_prices p WHERE p.symbol = s.symbol)""").fetchone()[0]
    safe = n_inactive > 0 and with_prices > 0
    return {"securities": int(n_all), "delisted_in_master": int(n_inactive), "delisted_with_prices": int(with_prices),
            "survivorship_safe": False,
            "statement": ("Partially mitigated: delisted securities are included where the data source provided them, "
                          "but coverage of historical delistings is incomplete." if safe else
                          "NOT survivorship-bias free: no delisted securities with price history are in the database; "
                          "historical universes contain only companies that survived to today.")}


def run_diagnostics(con: duckdb.DuckDBPyConnection, result: BacktestResult, metrics: dict, panel: pd.DataFrame,
                    n_folds: int) -> dict:
    d = load_config("backtest")["diagnostics"]
    costs = load_config("backtest")["costs"]
    flags: list[dict] = []

    def flag(code: str, severity: str, message: str):
        flags.append({"code": code, "severity": severity, "message": message})

    la = lookahead_audit(con)
    if not la["passed"]:
        flag("lookahead", "critical", f"look-ahead audit failed: {la}")
    sv = survivorship_status(con)
    flag("survivorship", "warning", sv["statement"])

    elig = panel[panel["base_eligible"]]
    if not elig.empty:
        fund_cols = [c for c in ("revenue_yoy", "roa", "book_to_market") if c in elig]
        missing = elig[fund_cols].isna().all(axis=1).mean() if fund_cols else 1.0
        if missing > d["max_missing_fundamental_share"]:
            flag("missing_fundamentals", "warning", f"{missing:.0%} of eligible names lack core fundamentals")
    months = metrics.get("months", 0)
    if months < d["min_months"]:
        flag("tiny_sample", "warning", f"only {months} months of backtest history (< {d['min_months']})")
    if n_folds < d["min_folds"]:
        flag("few_folds", "warning", f"only {n_folds} walk-forward folds (< {d['min_folds']})")
    if result.stats.get("min_universe_size", 0) < d["min_universe_size"]:
        flag("small_universe", "warning", f"universe fell to {result.stats.get('min_universe_size')} names")

    tr = result.trades
    if tr is not None and not tr.empty:
        pnl = {}
        for sym, g in tr.groupby("symbol"):
            sign = np.where(g["side"] == "SELL", 1.0, -1.0)
            pnl[sym] = float((g["gross"] * sign).sum() - g["commission"].sum() - g["transaction_cost"].sum())
        for sym, _pos in result.stats.get("open_positions", {}).items():
            last = result.holdings[(result.holdings["symbol"] == sym)]
            if not last.empty:
                pnl[sym] = pnl.get(sym, 0.0) + float(last.iloc[-1]["value"])
        total_gain = sum(v for v in pnl.values() if v > 0)
        if total_gain > 0:
            top_sym, top_v = max(pnl.items(), key=lambda kv: kv[1])
            share = top_v / total_gain
            if share > d["max_single_stock_contribution"]:
                flag("single_stock_dominance", "warning", f"{top_sym} contributed {share:.0%} of gross gains")
        avg_trade = tr["gross"].abs().mean()
        if costs["commission_per_trade_usd"] > 0 and avg_trade > 0 and costs["commission_per_trade_usd"] / avg_trade > 0.005:
            flag("commission_heavy", "info", f"commission is {costs['commission_per_trade_usd'] / avg_trade:.2%} of the "
                 f"average trade (${avg_trade:,.0f}); small accounts pay proportionally more")
    if (metrics.get("turnover_annual") or 0) > d["max_annual_turnover"]:
        flag("extreme_turnover", "warning", f"annual turnover {metrics['turnover_annual']:.1f}x")
    if costs["slippage_bps"] == 0 and costs["transaction_cost_bps"] == 0 and costs["commission_per_trade_usd"] == 0:
        flag("zero_costs", "critical", "transaction costs are all zero")

    h = result.holdings
    if h is not None and not h.empty:
        se = sector_exposure(h)
        if not se.empty and se.max(axis=1).mean() > d["max_single_sector_weight"]:
            flag("sector_dominance", "warning", f"average largest-sector weight {se.max(axis=1).mean():.0%}")
        stocks = h[h["symbol"] != "__CASH__"]
        tot = h.groupby("rebalance_date")["value"].sum()
        micro = stocks[stocks["market_cap"] < d["microcap_threshold"]].groupby("rebalance_date")["value"].sum()
        micro_w = (micro / tot).reindex(tot.index).fillna(0).mean() if len(tot) else 0.0
        if micro_w > d["max_microcap_weight"]:
            flag("microcap_exposure", "warning", f"average micro-cap weight {micro_w:.0%}")
    return {"lookahead_audit": la, "survivorship": sv, "flags": flags}
