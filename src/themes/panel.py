"""Theme feature panel: one row per (rebalance_date, theme member) with every themes_v1 characteristic, stage flag,
Fama-MacBeth controls and forward-return labels (THEMES_SPEC §4-§7). Persisted as ``theme_feature_panel``.

Reuses the production building blocks (price features, PIT fundamentals, split-aware traded price, eligibility,
delisting-aware forward returns) so the theme layer and the NASDAQ model share one implementation. Membership is
point-in-time (``theme_membership``: valid_from <= date < valid_to). Labels (``label_fwd_<h>``,
``label_fwd_<h>_theme``) are research targets only and are never read by scoring code.
"""
from __future__ import annotations

import logging

import duckdb
import numpy as np
import pandas as pd

from src.config import load_config
from src.data.fundamentals_loader import load_snapshots
from src.features.earnings_events import earnings_features_at
from src.features.fundamentals import asof_join_snapshots, compute_fundamental_features
from src.features.momentum import delisting_haircuts, forward_returns
from src.features.price_features import adv20_at, month_end_rebalance_dates, price_features_at
from src.features.store import exclusion_reasons, load_market_data, split_factors
from src.features.technicals import adjusted_ohlc
from src.features.theme_features import (
    MARKET_SYMBOL,
    OIL_SYMBOL,
    beta_252d_at,
    oil_beta_trend_at,
    profitable_growth,
    size_ln_mcap,
    stage_flags,
)
from src.themes.config import ThemesConfig
from src.themes.membership import members_on

log = logging.getLogger(__name__)

PANEL_TABLE = "theme_feature_panel"
DEFAULT_START = "2010-01-01"
OIL_SUBTHEME = "oil_gas"


def load_closes(con: duckdb.DuckDBPyConnection, symbols: list[str]) -> pd.DataFrame:
    """Adjusted closes (date x symbol) for ETFs / commodity series not part of the stock universe."""
    p = con.execute("SELECT symbol, date, open, high, low, close, adj_close, volume FROM daily_prices "
                    "WHERE symbol IN (SELECT unnest(?))", [symbols]).df()
    if p.empty:
        return pd.DataFrame()
    return adjusted_ohlc(p)["close"]


def theme_benchmark_for(cfg: ThemesConfig, theme: str, at: pd.Timestamp, etf_close: pd.DataFrame) -> str:
    """First configured theme ETF with >= 3 sessions of prices before ``at``, else the market proxy."""
    for b in cfg.themes[theme].benchmarks:
        if b in etf_close and etf_close[b].loc[:at].notna().sum() >= 3:
            return b
    return MARKET_SYMBOL


def membership_frame(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    m = con.execute("SELECT cik, symbol, theme, subtheme, valid_from, valid_to FROM theme_membership").df()
    m["valid_from"] = pd.to_datetime(m["valid_from"])
    m["valid_to"] = pd.to_datetime(m["valid_to"])
    return m


def add_theme_labels(panel: pd.DataFrame, labels: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Raw forward returns and theme-index-adjusted forward returns (minus the equal-weight mean of eligible
    members of the same theme on the same date; the theme index is costless)."""
    out = panel
    for h, fr in labels.items():
        col = f"label_fwd_{h}"
        out = out.merge(fr[["rebalance_date", "symbol", "fwd_return"]].rename(columns={"fwd_return": col}),
                        on=["rebalance_date", "symbol"], how="left")
        elig = out[col].where(out["eligible"])
        mean = elig.groupby([out["rebalance_date"], out["theme"]]).transform("mean")
        out[f"{col}_theme"] = out[col] - mean
    return out


def build_theme_panel(con: duckdb.DuckDBPyConnection, cfg: ThemesConfig, dates: list[pd.Timestamp] | None = None,
                      persist: bool = True, events: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    membership = membership_frame(con)
    if membership.empty:
        raise RuntimeError("theme_membership is empty; run t3-membership first")
    symbols = sorted(membership["symbol"].unique())
    md = load_market_data(con, symbols)
    if dates is None:
        dates = month_end_rebalance_dates(md.calendar, start=DEFAULT_START)
    syms = [s for s in symbols if s in md.mats["close"].columns]
    mats = {k: v[syms] for k, v in md.mats.items()}
    etfs = sorted({b for t in cfg.themes.values() for b in t.benchmarks} | {MARKET_SYMBOL})
    etf_close = load_closes(con, etfs).reindex(md.calendar)
    oil = load_closes(con, [OIL_SYMBOL])
    oil = oil[OIL_SYMBOL] if OIL_SYMBOL in oil else pd.Series(dtype=float)
    market = etf_close[MARKET_SYMBOL] if MARKET_SYMBOL in etf_close else md.bench.get(MARKET_SYMBOL)

    # price characteristics; the group map is constant because PIT subthemes change over time and the
    # group-relative price features are not part of the themes_v1 factor set
    pf = price_features_at(mats, md.bench.get("QQQ"), dates, {s: "all" for s in syms})
    pf = pf.merge(adv20_at(mats["raw_close"], mats["volume"], dates), on=["rebalance_date", "symbol"], how="left")

    cand = con.execute("SELECT symbol, cik, ipo_date FROM theme_candidates").df()
    cik_by_symbol = dict(zip(membership["symbol"], membership["cik"], strict=False))
    snaps = load_snapshots(con, sorted(set(cik_by_symbol.values())))
    splits = con.execute("SELECT symbol, date, ratio FROM stock_splits").df()
    rets = mats["close"].pct_change(fill_method=None)
    etf_rets = etf_close.pct_change(fill_method=None)
    ucfg = cfg.universe
    frames = []
    for d in dates:
        # multi-theme (v2): one membership row per (symbol, theme); symbol-level features are computed once
        mem = members_on(membership, d).drop_duplicates(["symbol", "theme"])
        cross = pf[(pf["rebalance_date"] == d) & pf["symbol"].isin(set(mem["symbol"]))].set_index("symbol")
        if cross.empty:
            continue
        snap = asof_join_snapshots(snaps, cik_by_symbol, d, cross.index.tolist())
        feats, mcap = compute_fundamental_features(snap, cross["raw_close"], splits, d)
        base = cross.join(feats, how="left")
        base["market_cap"] = mcap.reindex(base.index)
        base["fundamental_availability_date"] = (snap["availability_date"].reindex(base.index)
                                                 if "availability_date" in snap else pd.NaT)
        assets = snap["total_assets"].reindex(base.index) if "total_assets" in snap else \
            pd.Series(np.nan, index=base.index)
        base["beta_252d"] = beta_252d_at(mats["close"][base.index], market, d) if market is not None else np.nan
        base["size_ln_mcap"] = size_ln_mcap(base["market_cap"])
        m = mem.loc[mem["symbol"].isin(base.index), ["symbol", "theme", "subtheme", "valid_from"]]
        f = m.rename(columns={"valid_from": "membership_valid_from"}).merge(
            base, left_on="symbol", right_index=True, how="left").reset_index(drop=True)
        f["stage"] = stage_flags(f["ocf_ttm"], f["revenue_ttm"], f["theme"], cfg.stage.biotech_commercial_revenue_usd,
                                 total_assets=pd.Series(assets.reindex(f["symbol"]).to_numpy(), index=f.index))
        f["profitable_growth"] = np.nan
        for _, idx in f.groupby("theme").groups.items():
            g = f.loc[idx]
            f.loc[idx, "profitable_growth"] = profitable_growth(g["revenue_yoy"], g["fcf_margin"], g["stage"])
        f["oil_beta_trend"] = np.nan
        oil_rows = f.index[f["subtheme"] == OIL_SUBTHEME]
        if len(oil_rows) and not oil.empty and market is not None:
            oil_syms = sorted(set(f.loc[oil_rows, "symbol"]))
            ob = oil_beta_trend_at(mats["close"][oil_syms], market, oil, d)
            f.loc[oil_rows, "oil_beta_trend"] = f.loc[oil_rows, "symbol"].map(ob).to_numpy()
        if events:
            f["ear_3d"], f["sue_announce"] = np.nan, np.nan
            allr = pd.concat([rets[sorted(set(f["symbol"]))], etf_rets], axis=1)
            for t, g in f.groupby("theme"):
                syms = sorted(set(g["symbol"]))
                bench_of = pd.Series(theme_benchmark_for(cfg, t, d, etf_close), index=syms)
                ef = earnings_features_at({x: events[x] for x in syms if x in events}, allr, bench_of, d)
                for col in ("ear_3d", "sue_announce"):
                    f.loc[g.index, col] = g["symbol"].map(ef[col]).to_numpy() if col in ef else np.nan
        f["rebalance_date"] = d
        frames.append(f)
    if not frames:
        raise RuntimeError("no theme members with prices on any rebalance date")
    panel = pd.concat(frames, ignore_index=True)
    for c in ("ear_3d", "sue_announce"):
        if c not in panel:
            panel[c] = np.nan

    panel["traded_close"] = panel["raw_close"] * split_factors(splits, panel["symbol"], panel["rebalance_date"])
    ipo = dict(zip(cand["symbol"], pd.to_datetime(cand["ipo_date"]), strict=False))
    panel["exclusion_reason"] = exclusion_reasons(panel, {}, ipo, ucfg.min_history_sessions, ucfg.min_price,
                                                  ucfg.min_market_cap, ucfg.min_adv20)
    no_fund = panel["exclusion_reason"].isna() & (panel["stage"] == "unknown")
    panel.loc[no_fund, "exclusion_reason"] = "fundamentals unavailable (no USD XBRL)"
    panel["eligible"] = panel["exclusion_reason"].isna()

    haircut = delisting_haircuts(mats["close"], mats["raw_close"], load_config("backtest")["costs"])
    labels = {h: forward_returns(mats["close"], dates, h, haircut) for h in cfg.research.horizons}
    panel = add_theme_labels(panel, labels)
    panel = panel.replace([np.inf, -np.inf], np.nan)
    if persist:
        persist_theme_panel(con, panel)
    return panel


DROP_COLS = {"net_income__qhist", "price_date"}


def persist_theme_panel(con: duckdb.DuckDBPyConnection, panel: pd.DataFrame) -> None:
    df = panel[[c for c in panel.columns if c not in DROP_COLS]].copy()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"]).dt.date
    text = {"symbol", "theme", "subtheme", "stage", "exclusion_reason", "rebalance_date", "cik"}
    for c in df.columns:
        if c not in text and df[c].dtype == object:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    con.register("_tp", df)
    try:
        con.execute(f"CREATE OR REPLACE TABLE {PANEL_TABLE} AS SELECT * FROM _tp")
    finally:
        con.unregister("_tp")


def theme_lookahead_audit(con: duckdb.DuckDBPyConnection) -> dict:
    """Counts panel rows that used information not yet available on the rebalance date (must all be zero)."""
    q = f"SELECT count(*) FROM {PANEL_TABLE} WHERE "
    fund = con.execute(q + "CAST(fundamental_availability_date AS DATE) > rebalance_date").fetchone()[0]
    mem = con.execute(q + "CAST(membership_valid_from AS DATE) > rebalance_date").fetchone()[0]
    snaps = con.execute("SELECT count(*) FROM fundamental_snapshots WHERE availability_date > snapshot_date"
                        ).fetchone()[0]
    ev = 0
    if con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'earnings_events'").fetchone()[0]:
        ev = con.execute("SELECT count(*) FROM earnings_events WHERE available_from <= t0").fetchone()[0]
    return {"future_fundamentals": int(fund), "future_membership": int(mem), "future_snapshots": int(snaps),
            "events_available_before_announcement": int(ev), "passed": fund == 0 and mem == 0 and snaps == 0 and ev == 0}


def load_theme_panel(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = con.execute(f"SELECT * FROM {PANEL_TABLE}").df()
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["eligible"] = df["eligible"].astype(bool)
    return df
