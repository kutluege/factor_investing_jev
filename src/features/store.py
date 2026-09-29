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
from src.db.schema import upsert_df
from src.features.fundamentals import FUNDAMENTAL_FEATURES, asof_join_snapshots, compute_fundamental_features
from src.features.momentum import forward_returns
from src.features.price_features import (
    MOMENTUM_COLUMNS,
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

    # base eligibility (loosest thresholds; configs filter further)
    bt = load_config("backtest")["search"]
    min_mcap, min_adv = min(bt["market_caps"]), min(bt["adv_thresholds"])
    delisted = dict(zip(secs["symbol"], pd.to_datetime(secs["delisted_date"]), strict=False))
    ipo = dict(zip(secs["symbol"], pd.to_datetime(secs["ipo_date"]), strict=False))
    reasons = []
    for r in panel.itertuples():
        reason = None
        dl, ip = delisted.get(r.symbol), ipo.get(r.symbol)
        if pd.notna(dl) and dl <= r.rebalance_date:
            reason = "delisted"
        elif pd.notna(ip) and ip > r.rebalance_date:
            reason = "not yet listed"
        elif r.history_days < ucfg["min_history_days"]:
            reason = "insufficient history"
        elif pd.isna(r.raw_close) or r.raw_close < ucfg["min_price"]:
            reason = "price below minimum"
        elif pd.isna(getattr(r, "market_cap", np.nan)):
            reason = "market cap unavailable"
        elif r.market_cap < min_mcap:
            reason = "market cap below base threshold"
        elif pd.isna(r.adv20) or r.adv20 < min_adv:
            reason = "ADV20 below base threshold"
        reasons.append(reason)
    panel["exclusion_reason"] = reasons
    panel["base_eligible"] = panel["exclusion_reason"].isna()
    panel = panel.replace([np.inf, -np.inf], np.nan)

    if persist:
        persist_features(con, panel)
        persist_labels(con, md, dates, syms)
    return panel


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
    upsert_df(con, "rebalance_universe", uni, ["rebalance_date", "symbol"])

    fam = feature_family_map()
    fcols = [c for c in FUNDAMENTAL_FEATURES + MOMENTUM_COLUMNS if c in panel]
    long = panel[["rebalance_date", "symbol", "observation_period_end", "fundamental_availability_date"] + fcols] \
        if "observation_period_end" in panel else panel[["rebalance_date", "symbol"] + fcols].assign(
            observation_period_end=pd.NaT, fundamental_availability_date=pd.NaT)
    long = long.melt(id_vars=["rebalance_date", "symbol", "observation_period_end", "fundamental_availability_date"],
                     var_name="feature", value_name="value").dropna(subset=["value"])
    is_price = long["feature"].isin(MOMENTUM_COLUMNS)
    # price features are observed on the rebalance date itself
    long.loc[is_price, "observation_period_end"] = long.loc[is_price, "rebalance_date"]
    long.loc[is_price, "fundamental_availability_date"] = long.loc[is_price, "rebalance_date"]
    long["family"] = long["feature"].map(fam).fillna("other")
    long = long.rename(columns={"fundamental_availability_date": "availability_date"})
    long["computed_at"] = now
    for c in ("rebalance_date", "observation_period_end", "availability_date"):
        long[c] = pd.to_datetime(long[c]).dt.date
    long = long.drop_duplicates(subset=["rebalance_date", "symbol", "feature"])
    upsert_df(con, "factor_values", long[["rebalance_date", "symbol", "feature", "family", "value",
                                          "observation_period_end", "availability_date", "computed_at"]],
              ["rebalance_date", "symbol", "feature"])

    tcols = [c for c in TECHNICAL_COLUMNS if c in panel]
    tech = panel[["rebalance_date", "symbol", "price_date"] + tcols].melt(
        id_vars=["rebalance_date", "symbol", "price_date"], var_name="indicator", value_name="value").dropna()
    tech = tech.rename(columns={"price_date": "as_of_price_date"})
    tech["computed_at"] = now
    tech["rebalance_date"] = pd.to_datetime(tech["rebalance_date"]).dt.date
    tech["as_of_price_date"] = pd.to_datetime(tech["as_of_price_date"]).dt.date
    upsert_df(con, "technical_values", tech[["rebalance_date", "symbol", "indicator", "value", "as_of_price_date",
                                             "computed_at"]], ["rebalance_date", "symbol", "indicator"])


def persist_labels(con: duckdb.DuckDBPyConnection, md: MarketData, dates: list[pd.Timestamp], syms: list[str]) -> None:
    haircut = float(load_config("backtest")["costs"]["delisting_haircut"])
    for h in load_config("factors")["horizons"]:
        fr = forward_returns(md.mats["close"][syms], dates, h, haircut)
        if fr.empty:
            continue
        fr["horizon_days"] = h
        fr["rebalance_date"] = pd.to_datetime(fr["rebalance_date"]).dt.date
        fr["label_end_date"] = pd.to_datetime(fr["label_end_date"]).dt.date
        upsert_df(con, "forward_returns", fr[["rebalance_date", "symbol", "horizon_days", "fwd_return",
                                              "label_end_date"]], ["rebalance_date", "symbol", "horizon_days"])


def load_panel(con: duckdb.DuckDBPyConnection, dates: list | None = None) -> pd.DataFrame:
    """Reassemble the wide panel from persisted tables (used by backtests and the dashboard)."""
    cond, params = "", []
    if dates is not None:
        cond = " WHERE rebalance_date IN (SELECT unnest(?))"
        params = [[pd.Timestamp(d).date() for d in dates]]
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
