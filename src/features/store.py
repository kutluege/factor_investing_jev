"""Feature store: builds and persists PIT universe, factor, technical and label data for rebalance dates."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from src.config import load_config
from src.data.fundamentals_loader import load_snapshots
from src.data.reference import benchmark_symbols
from src.db.repo import utcnow
from src.features.fundamentals import FUNDAMENTAL_FEATURES, asof_join_snapshots, compute_fundamental_features
from src.features.momentum import delisting_haircuts, forward_returns
from src.features.price_features import (
    EXTRA_COLUMNS,
    MOMENTUM_COLUMNS,
    MONTHLY_COLUMNS,
    TECHNICAL_COLUMNS,
    adv20_at,
    month_end_rebalance_dates,
    price_features_at,
)
from src.features.technicals import adjusted_ohlc

log = logging.getLogger(__name__)


def feature_family_map() -> dict[str, str]:
    fam = {}
    for family, feats in load_config("factors")["families"].items():
        for f in feats:
            fam[f] = family
    return fam


@dataclass
class MarketData:
    mats: dict[str, pd.DataFrame]
    bench: dict[str, pd.Series]
    calendar: pd.DatetimeIndex


def load_market_data(con: duckdb.DuckDBPyConnection, symbols: list[str] | None = None,
                     end: pd.Timestamp | None = None) -> MarketData:
    q = "SELECT symbol, date, open, high, low, close, adj_close, volume FROM daily_prices"
    params: list[Any] = []
    conds = []
    if symbols is not None:
        conds.append("symbol IN (SELECT unnest(?))")
        params.append(list(set(symbols) | set(benchmark_symbols())))
    if end is not None:
        conds.append("date <= ?")
        params.append(pd.Timestamp(end).date())
    if conds:
        q += " WHERE " + " AND ".join(conds)
    prices = con.execute(q, params).df()
    if prices.empty:
        raise RuntimeError("No prices stored. Run the data update first.")
    mats = adjusted_ohlc(prices)
    bench_syms = [s for s in benchmark_symbols() if s in mats["close"].columns]
    bench = {s: mats["close"][s] for s in bench_syms}
    stock_cols = [c for c in mats["close"].columns if c not in bench_syms]
    calendar = mats["close"].index
    if "QQQ" in bench:
        calendar = bench["QQQ"].dropna().index
    mats = {k: v.reindex(calendar)[stock_cols] for k, v in mats.items()}
    bench = {k: v.reindex(calendar) for k, v in bench.items()}
    return MarketData(mats, bench, calendar)


def default_rebalance_dates(md: MarketData, min_history: int = 252, start=None, end=None) -> list[pd.Timestamp]:
    cal = md.calendar
    if len(cal) <= min_history:
        return []
    first = cal[min_history]
    start = max(pd.Timestamp(start), first) if start is not None else first
    return month_end_rebalance_dates(cal, start=start, end=end)


def build_features(con: duckdb.DuckDBPyConnection, dates: list[pd.Timestamp] | None = None,
                   md: MarketData | None = None, persist: bool = True) -> pd.DataFrame:
    """Compute the full wide feature panel for ``dates`` and (optionally) persist it."""
    ucfg = load_config("universe")
    secs = con.execute("SELECT symbol, cik, sector_group, ipo_date, delisted_date, name FROM securities").df()
    if secs.empty:
        raise RuntimeError("Security master is empty. Run the reference-data update first.")
    md = md or load_market_data(con, secs["symbol"].tolist())
    if dates is None:
        dates = default_rebalance_dates(md, ucfg["min_history_days"])
    if not dates:
        raise RuntimeError("Not enough price history to form any rebalance date.")
    sector_map = dict(zip(secs["symbol"], secs["sector_group"], strict=False))
    cik_by_symbol = {s: c for s, c in zip(secs["symbol"], secs["cik"], strict=False) if isinstance(c, str)}
    syms = [s for s in md.mats["close"].columns if s in sector_map]
    mats = {k: v[syms] for k, v in md.mats.items()}

    pf = price_features_at(mats, md.bench.get("QQQ"), dates, sector_map)
    adv = adv20_at(mats["raw_close"], mats["volume"], dates)
    pf = pf.merge(adv, on=["rebalance_date", "symbol"], how="left")

    snaps = load_snapshots(con, list(set(cik_by_symbol.values())))
    splits = con.execute("SELECT symbol, date, ratio FROM stock_splits").df()
    fund_frames = []
    for d in dates:
        cross = pf[pf["rebalance_date"] == d].set_index("symbol")
        if cross.empty:
            continue
        snap = asof_join_snapshots(snaps, cik_by_symbol, d, cross.index.tolist())
        # market cap uses the vendor close (split-adjusted, not dividend-adjusted)
        feats, mcap = compute_fundamental_features(snap, cross["raw_close"], splits, d)
        feats["market_cap"] = mcap
        feats["observation_period_end"] = snap["period_end"].reindex(feats.index) if "period_end" in snap else pd.NaT
        feats["fundamental_availability_date"] = snap["availability_date"].reindex(feats.index) \
            if "availability_date" in snap else pd.NaT
        feats["rebalance_date"] = d
        fund_frames.append(feats.reset_index())
    fund = pd.concat(fund_frames, ignore_index=True) if fund_frames else pd.DataFrame()
    panel = pf.merge(fund, on=["rebalance_date", "symbol"], how="left") if not fund.empty else pf
    panel["sector_group"] = panel["symbol"].map(sector_map)

    # The minimum-price filter must use the price actually traded on the date: vendor closes are split-adjusted
    # retroactively, so later splits would otherwise make past prices look tiny (look-ahead that drops winners).
    panel["traded_close"] = panel["raw_close"] * split_factors(splits, panel["symbol"], panel["rebalance_date"])
    # base eligibility (loosest thresholds; configs filter further)
    bt = load_config("backtest")["search"]
    min_mcap, min_adv = min(bt["market_caps"]), min(bt["adv_thresholds"])
    delisted = dict(zip(secs["symbol"], pd.to_datetime(secs["delisted_date"]), strict=False))
    ipo = dict(zip(secs["symbol"], pd.to_datetime(secs["ipo_date"]), strict=False))
    panel["exclusion_reason"] = exclusion_reasons(panel, delisted, ipo, ucfg["min_history_days"], ucfg["min_price"],
                                                  min_mcap, min_adv)
    panel["base_eligible"] = panel["exclusion_reason"].isna()
    panel = panel.replace([np.inf, -np.inf], np.nan)

    if persist:
        persist_features(con, panel)
        persist_labels(con, md, dates, syms)
    return panel


def exclusion_reasons(panel: pd.DataFrame, delisted: dict, ipo: dict, min_history: int, min_price: float,
                      min_mcap: float, min_adv: float) -> list[str | None]:
    """First failing eligibility rule per (rebalance_date, symbol) row, or None when eligible. ``panel`` needs
    symbol, rebalance_date, history_days, traded_close, market_cap, adv20."""
    reasons = []
    for r in panel.itertuples():
        reason = None
        dl, ip = delisted.get(r.symbol), ipo.get(r.symbol)
        if pd.notna(dl) and dl <= r.rebalance_date:
            reason = "delisted"
        elif pd.notna(ip) and ip > r.rebalance_date:
            reason = "not yet listed"
        elif r.history_days < min_history:
            reason = "insufficient history"
        elif pd.isna(r.traded_close) or r.traded_close < min_price:
            reason = "price below minimum"
        elif pd.isna(getattr(r, "market_cap", np.nan)):
            reason = "market cap unavailable"
        elif r.market_cap < min_mcap:
            reason = "market cap below base threshold"
        elif pd.isna(r.adv20) or r.adv20 < min_adv:
            reason = "ADV20 below base threshold"
        reasons.append(reason)
    return reasons


def split_factors(splits: pd.DataFrame, symbols: pd.Series, dates: pd.Series) -> pd.Series:
    """Cumulative split ratio after each (symbol, date): converts split-adjusted prices back to traded prices."""
    out = pd.Series(1.0, index=symbols.index)
    if splits is None or splits.empty:
        return out
    sp = splits.assign(date=pd.to_datetime(splits["date"]))
    for sym, g in sp.groupby("symbol"):
        m = symbols == sym
        if not m.any():
            continue
        d = pd.to_datetime(dates[m])
        ratios = g.sort_values("date")
        out[m] = [float(ratios.loc[ratios["date"] > x, "ratio"].prod()) for x in d]
    return out


def persist_features(con: duckdb.DuckDBPyConnection, panel: pd.DataFrame) -> None:
    now = utcnow()
    uni = panel[["rebalance_date", "symbol", "sector_group", "base_eligible", "exclusion_reason", "market_cap",
                 "adv20", "raw_close", "history_days"]].rename(columns={"raw_close": "close"}).copy()
    uni["shares_source"] = "sec_dei_or_diluted"
    uni["computed_at"] = now
    uni["rebalance_date"] = pd.to_datetime(uni["rebalance_date"]).dt.date
    uni["history_days"] = uni["history_days"].astype("Int64")
    dates = sorted(uni["rebalance_date"].unique())
    for table in ("rebalance_universe", "factor_values", "technical_values"):
        con.execute(f"DELETE FROM {table} WHERE rebalance_date IN (SELECT unnest(?))", [dates])
    insert_df(con, "rebalance_universe", uni)
    persist_wide_panel(con, panel, dates)
    # long audit tables (feature, observation period, availability date) for eligible names only
    panel = panel[panel["base_eligible"].astype(bool)]

    fam = feature_family_map()
    price_cols = MOMENTUM_COLUMNS + EXTRA_COLUMNS + MONTHLY_COLUMNS
    fcols = [c for c in dict.fromkeys(FUNDAMENTAL_FEATURES + price_cols) if c in panel]
    long = panel[["rebalance_date", "symbol", "observation_period_end", "fundamental_availability_date"] + fcols] \
        if "observation_period_end" in panel else panel[["rebalance_date", "symbol"] + fcols].assign(
            observation_period_end=pd.NaT, fundamental_availability_date=pd.NaT)
    long = long.melt(id_vars=["rebalance_date", "symbol", "observation_period_end", "fundamental_availability_date"],
                     var_name="feature", value_name="value").dropna(subset=["value"])
    is_price = long["feature"].isin(price_cols)
    # price features are observed on the rebalance date itself
    long.loc[is_price, "observation_period_end"] = long.loc[is_price, "rebalance_date"]
    long.loc[is_price, "fundamental_availability_date"] = long.loc[is_price, "rebalance_date"]
    long["family"] = long["feature"].map(fam).fillna("other")
    long = long.rename(columns={"fundamental_availability_date": "availability_date"})
    long["computed_at"] = now
    for c in ("rebalance_date", "observation_period_end", "availability_date"):
        long[c] = pd.to_datetime(long[c]).dt.date
    long = long.drop_duplicates(subset=["rebalance_date", "symbol", "feature"])
    insert_df(con, "factor_values", long[["rebalance_date", "symbol", "feature", "family", "value",
                                          "observation_period_end", "availability_date", "computed_at"]])

    tcols = [c for c in TECHNICAL_COLUMNS if c in panel]
    tech = panel[["rebalance_date", "symbol", "price_date"] + tcols].melt(
        id_vars=["rebalance_date", "symbol", "price_date"], var_name="indicator", value_name="value").dropna()
    tech = tech.rename(columns={"price_date": "as_of_price_date"})
    tech["computed_at"] = now
    tech["rebalance_date"] = pd.to_datetime(tech["rebalance_date"]).dt.date
    tech["as_of_price_date"] = pd.to_datetime(tech["as_of_price_date"]).dt.date
    insert_df(con, "technical_values", tech[["rebalance_date", "symbol", "indicator", "value", "as_of_price_date",
                                             "computed_at"]])


def insert_df(con: duckdb.DuckDBPyConnection, table: str, df: pd.DataFrame) -> None:
    """Plain bulk insert (callers delete the affected rebalance dates first)."""
    if df is None or df.empty:
        return
    con.register("_ins_src", df)
    try:
        con.execute(f"INSERT INTO {table} ({', '.join(df.columns)}) SELECT {', '.join(df.columns)} FROM _ins_src")
    finally:
        con.unregister("_ins_src")


WIDE_EXCLUDE = {"observation_period_end", "fundamental_availability_date", "price_date", "net_income__qhist"}


def persist_wide_panel(con: duckdb.DuckDBPyConnection, panel: pd.DataFrame, dates: list) -> None:
    """Wide feature panel (one row per rebalance_date x symbol) used by backtests; schema grows with new features."""
    cols = [c for c in panel.columns if c not in WIDE_EXCLUDE]
    df = panel[cols].copy()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"]).dt.date
    for c in df.columns:
        if df[c].dtype == object and c not in ("symbol", "sector_group", "exclusion_reason", "rebalance_date"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    con.register("_wide_src", df)
    try:
        exists = con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'feature_panel'"
                             ).fetchone()[0]
        if not exists:
            con.execute("CREATE TABLE feature_panel AS SELECT * FROM _wide_src WHERE false")
        have = {r[0] for r in con.execute("SELECT column_name FROM information_schema.columns "
                                          "WHERE table_name = 'feature_panel'").fetchall()}
        for c in df.columns:
            if c not in have:
                sqltype = "DOUBLE" if pd.api.types.is_numeric_dtype(df[c]) or df[c].dtype == bool else "VARCHAR"
                if df[c].dtype == bool:
                    sqltype = "BOOLEAN"
                con.execute(f'ALTER TABLE feature_panel ADD COLUMN "{c}" {sqltype}')
        con.execute("DELETE FROM feature_panel WHERE rebalance_date IN (SELECT unnest(?))", [dates])
        con.execute("INSERT INTO feature_panel BY NAME SELECT * FROM _wide_src")
    finally:
        con.unregister("_wide_src")


def persist_labels(con: duckdb.DuckDBPyConnection, md: MarketData, dates: list[pd.Timestamp], syms: list[str]) -> None:
    haircut = delisting_haircuts(md.mats["close"][syms], md.mats["raw_close"][syms], load_config("backtest")["costs"])
    for h in load_config("factors")["horizons"]:
        fr = forward_returns(md.mats["close"][syms], dates, h, haircut)
        if fr.empty:
            continue
        fr["horizon_days"] = h
        fr["rebalance_date"] = pd.to_datetime(fr["rebalance_date"]).dt.date
        fr["label_end_date"] = pd.to_datetime(fr["label_end_date"]).dt.date
        con.execute("DELETE FROM forward_returns WHERE horizon_days = ? AND rebalance_date IN (SELECT unnest(?))",
                    [h, sorted(fr["rebalance_date"].unique())])
        insert_df(con, "forward_returns", fr[["rebalance_date", "symbol", "horizon_days", "fwd_return",
                                              "label_end_date"]])


def load_panel(con: duckdb.DuckDBPyConnection, dates: list | None = None) -> pd.DataFrame:
    """Reassemble the wide panel from persisted tables (used by backtests and the dashboard)."""
    cond, params = "", []
    if dates is not None:
        cond = " WHERE rebalance_date IN (SELECT unnest(?))"
        params = [[pd.Timestamp(d).date() for d in dates]]
    has_wide = con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'feature_panel'"
                           ).fetchone()[0]
    if has_wide:
        panel = con.execute("SELECT * FROM feature_panel" + cond, params).df()
        if not panel.empty:
            panel["rebalance_date"] = pd.to_datetime(panel["rebalance_date"])
            panel["base_eligible"] = panel["base_eligible"].astype(bool)
            return panel
    uni = con.execute("SELECT * FROM rebalance_universe" + cond, params).df()
    if uni.empty:
        return uni
    fv = con.execute("SELECT rebalance_date, symbol, feature, value FROM factor_values" + cond, params).df()
    tv = con.execute("SELECT rebalance_date, symbol, indicator AS feature, value FROM technical_values" + cond,
                     params).df()
    wide = pd.concat([fv, tv]).drop_duplicates(subset=["rebalance_date", "symbol", "feature"]) \
        .pivot(index=["rebalance_date", "symbol"], columns="feature", values="value").reset_index()
    panel = uni.merge(wide, on=["rebalance_date", "symbol"], how="left")
    panel["rebalance_date"] = pd.to_datetime(panel["rebalance_date"])
    return panel


def load_labels(con: duckdb.DuckDBPyConnection, horizon: int) -> pd.DataFrame:
    df = con.execute("SELECT rebalance_date, symbol, fwd_return, label_end_date FROM forward_returns "
                     "WHERE horizon_days = ?", [horizon]).df()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["label_end_date"] = pd.to_datetime(df["label_end_date"])
    return df
