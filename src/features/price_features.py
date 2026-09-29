"""Build momentum + technical features for every symbol at each rebalance date (point-in-time)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.momentum import momentum_panel, relative_strength
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
                      sector_map: dict[str, str]) -> pd.DataFrame:
    """Wide frame indexed by (rebalance_date, symbol) with momentum + technical features.

    ``mats`` holds adjusted open/high/low/close/volume matrices on a shared trading calendar. Only rows up to
    each rebalance date are read (the panels are trailing), which the leakage tests verify.
    """
    c = mats["close"]
    panel = compute_indicator_panel(mats["open"], mats["high"], mats["low"], c, mats["volume"], bench_close)
    panel.update({k: v for k, v in momentum_panel(c).items()})
    last_valid_pos = c.notna().cumsum()  # used to detect stale prices
    frames = []
    idx = c.index
    for d in dates:
        if d not in idx:
            prior = idx[idx <= d]
            if len(prior) == 0:
                continue
            d_eff = prior[-1]
        else:
            d_eff = d
        i = idx.get_loc(d_eff)
        # staleness: symbol must have traded within the last STALE_SESSIONS sessions
        recent = c.iloc[max(0, i - STALE_SESSIONS + 1): i + 1].notna().any()
        row = {name: frame.iloc[i] for name, frame in panel.items() if name in TECHNICAL_COLUMNS
               or name in MOMENTUM_COLUMNS}
        df = pd.DataFrame(row)
        df["max_dd_252d"] = max_drawdown_at(c, d_eff)
        df["close_adj"] = c.iloc[i]
        df["raw_close"] = mats["raw_close"].iloc[i]
        df["history_days"] = last_valid_pos.iloc[i]
        df = df[recent.reindex(df.index).fillna(False)]
        # sector-relative 6m strength vs the equal-weight median of the sector group at d
        grp = pd.Series({s: sector_map.get(s) for s in df.index})
        med = df["ret_6m"].groupby(grp).transform("median")
        df["rs_sector_6m"] = relative_strength(df["ret_6m"], med)
        df.index.name = "symbol"
        df["rebalance_date"] = d
        df["price_date"] = d_eff
        frames.append(df.reset_index())
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    return out.replace([np.inf, -np.inf], np.nan)


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
