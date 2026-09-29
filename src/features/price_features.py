"""Build momentum + technical features for every symbol at each rebalance date (point-in-time)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.momentum import momentum_panel, relative_strength
from src.features.research_features import monthly_features, price_extras
from src.features.technicals import compute_indicator_panel, max_drawdown_at

# Indicators persisted to technical_values (candidate features + display state).
TECHNICAL_COLUMNS = [
    "sma20", "sma50", "sma100", "sma200", "ema20", "ema50", "rsi14", "macd", "macd_signal", "macd_hist",
    "macd_hist_norm", "adx14", "plus_di14", "minus_di14", "adx14_trend", "atr14", "atr14_pct", "vol_20d",
    "vol_60d", "volume_ratio_20d", "dist_52w_high", "price_sma200", "sma50_sma200", "breakout_20d",
    "breakout_60d_flag", "breakout_60d", "rs_qqq_6m", "beta_qqq_252d", "max_dd_252d",
]
MOMENTUM_COLUMNS = ["ret_1m", "ret_3m", "ret_6m", "ret_9m", "ret_12m", "mom_3_1", "mom_6_1", "mom_12_1",
                    "rs_qqq_6m", "rs_sector_6m", "dist_52w_high"]
STALE_SESSIONS = 5  # a price older than this many sessions at the rebalance date counts as missing


def month_end_rebalance_dates(calendar: pd.DatetimeIndex, start=None, end=None) -> list[pd.Timestamp]:
    """Last trading session of each calendar month in ``calendar``."""
    cal = pd.DatetimeIndex(sorted(set(calendar)))
    if start is not None:
        cal = cal[cal >= pd.Timestamp(start)]
    if end is not None:
        cal = cal[cal <= pd.Timestamp(end)]
    s = pd.Series(cal, index=cal)
    last = s.groupby([cal.year, cal.month]).max()
    dates = list(last.values)
    # drop the final month if it is not complete (the calendar ends before month end)
    if dates and end is None and cal[-1] == dates[-1]:
        month_end = (pd.Timestamp(dates[-1]) + pd.offsets.MonthEnd(0))
        if pd.Timestamp(dates[-1]) < month_end - pd.Timedelta(days=4):
            dates = dates[:-1]
    return [pd.Timestamp(d) for d in dates]


def price_features_at(mats: dict[str, pd.DataFrame], bench_close: pd.Series | None, dates: list[pd.Timestamp],
                      sector_map: dict[str, str], chunk: int = 300) -> pd.DataFrame:
    """Wide frame indexed by (rebalance_date, symbol) with momentum + technical features.

    ``mats`` holds adjusted open/high/low/close/volume matrices on a shared trading calendar. Only rows up to
    each rebalance date are read (the panels are trailing), which the leakage tests verify. Symbols are processed
    in column chunks to bound memory; cross-sectional features (sector-relative strength) are added afterwards.
    """
    cols = list(mats["close"].columns)
    parts = []
    for c0 in range(0, len(cols), chunk):
        sub = {k: v[cols[c0:c0 + chunk]] for k, v in mats.items()}
        parts.append(_price_features_chunk(sub, bench_close, dates))
    parts = [p for p in parts if not p.empty]
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    # sector-relative 6m strength vs the equal-weight median of the sector group on each date
    grp = out["symbol"].map(sector_map)
    med = out.groupby([out["rebalance_date"], grp])["ret_6m"].transform("median")
    out["rs_sector_6m"] = relative_strength(out["ret_6m"], med)
    out["sector_mom_6m"] = med
    mf = monthly_features(mats["close"], bench_close, sector_map, dates)
    out = out.merge(mf, on=["rebalance_date", "symbol"], how="left")
    return out.replace([np.inf, -np.inf], np.nan)


def _price_features_chunk(mats: dict[str, pd.DataFrame], bench_close: pd.Series | None,
                          dates: list[pd.Timestamp]) -> pd.DataFrame:
    c = mats["close"]
    panel = compute_indicator_panel(mats["open"], mats["high"], mats["low"], c, mats["volume"], bench_close)
    panel.update(momentum_panel(c))
    panel.update(price_extras(c, mats["raw_close"], mats["high"], mats["low"], bench_close))
    keep = set(TECHNICAL_COLUMNS) | set(MOMENTUM_COLUMNS) | set(EXTRA_COLUMNS)
    last_valid_pos = c.notna().cumsum()  # used to detect stale prices
    frames = []
    idx = c.index
    for d in dates:
        prior = idx[idx <= d]
        if len(prior) == 0:
            continue
        d_eff = prior[-1]
        i = idx.get_loc(d_eff)
        # staleness: symbol must have traded within the last STALE_SESSIONS sessions
        recent = c.iloc[max(0, i - STALE_SESSIONS + 1): i + 1].notna().any()
        df = pd.DataFrame({name: frame.iloc[i] for name, frame in panel.items() if name in keep})
        df["max_dd_252d"] = max_drawdown_at(c, d_eff)
        df["close_adj"] = c.iloc[i]
        df["raw_close"] = mats["raw_close"].iloc[i]
        df["history_days"] = last_valid_pos.iloc[i]
        df = df[recent.reindex(df.index).fillna(False).astype(bool)]
        df.index.name = "symbol"
        df["rebalance_date"] = d
        df["price_date"] = d_eff
        frames.append(df.reset_index())
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


EXTRA_COLUMNS = ["max_ret_21d", "mom_12_7", "idio_vol_60d", "spread_est"]
MONTHLY_COLUMNS = ["res_mom_12_2", "season_ret", "sector_mom_6m"]


def adv20_at(raw_close: pd.DataFrame, volume: pd.DataFrame, dates: list[pd.Timestamp]) -> pd.DataFrame:
    """ADV20 = mean(close * volume) over the 20 sessions up to and including each rebalance date (raw prices)."""
    dv = (raw_close * volume).rolling(20, min_periods=15).mean()
    rows = []
    for d in dates:
        prior = dv.index[dv.index <= d]
        if len(prior) == 0:
            continue
        s = dv.loc[prior[-1]].dropna()
        rows.append(pd.DataFrame({"rebalance_date": d, "symbol": s.index, "adv20": s.values}))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["rebalance_date", "symbol", "adv20"])
