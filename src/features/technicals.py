"""Technical indicators computed locally from stored OHLCV.

All functions take date-indexed DataFrames (columns = symbols) and use only trailing windows, so the value on
date t depends only on data up to and including t. Wilder smoothing is used for RSI, ATR and ADX.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def sma(close: pd.DataFrame, n: int) -> pd.DataFrame:
    return close.rolling(n, min_periods=n).mean()


def ema(close: pd.DataFrame, n: int) -> pd.DataFrame:
    return close.ewm(span=n, adjust=False, min_periods=n).mean()


def wilder(x: pd.DataFrame, n: int) -> pd.DataFrame:
    """Wilder's smoothing (RMA): alpha = 1/n, seeded after n observations."""
    return x.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def rsi(close: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain, avg_loss = wilder(gain, n), wilder(loss, n)
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    # all gains, no losses -> RSI 100; flat -> 50
    out = out.mask((avg_loss == 0) & (avg_gain > 0), 100.0).mask((avg_loss == 0) & (avg_gain == 0), 50.0)
    return out


def macd(close: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return line, sig, line - sig


def true_range(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame) -> pd.DataFrame:
    prev = close.shift(1)
    a = high - low
    b = (high - prev).abs()
    c = (low - prev).abs()
    # fmax ignores NaN, so the first bar (no previous close) falls back to high - low
    return np.fmax(np.fmax(a, b), c)


def atr(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    return wilder(true_range(high, low, close), n)


def adx(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame, n: int = 14):
    """Returns (ADX, +DI, -DI)."""
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    tr_s = wilder(true_range(high, low, close), n)
    plus_di = 100.0 * wilder(plus_dm, n) / tr_s.replace(0.0, np.nan)
    minus_di = 100.0 * wilder(minus_dm, n) / tr_s.replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0.0, np.nan)
    return wilder(dx, n), plus_di, minus_di


def volatility(close: pd.DataFrame, n: int) -> pd.DataFrame:
    """Annualized standard deviation of daily simple returns over n sessions."""
    return close.pct_change(fill_method=None).rolling(n, min_periods=n).std() * np.sqrt(TRADING_DAYS)


def rolling_beta(ret: pd.DataFrame, bench_ret: pd.Series, n: int = TRADING_DAYS) -> pd.DataFrame:
    cov = ret.rolling(n, min_periods=int(n * 0.8)).cov(bench_ret)
    var = bench_ret.rolling(n, min_periods=int(n * 0.8)).var()
    return cov.div(var, axis=0)


def max_drawdown_at(close: pd.DataFrame, at: pd.Timestamp, n: int = TRADING_DAYS) -> pd.Series:
    """Worst peak-to-trough drawdown within the n sessions ending at ``at`` (<= 0), per symbol."""
    window = close.loc[:at].tail(n)
    enough = window.notna().sum() >= int(n * 0.8)
    filled = window.ffill()
    peaks = filled.cummax()
    mdd = (filled / peaks - 1.0).min()
    return mdd.where(enough)


def compute_indicator_panel(o: pd.DataFrame, h: pd.DataFrame, lo: pd.DataFrame, c: pd.DataFrame, v: pd.DataFrame,
                            bench_close: pd.Series | None = None) -> dict[str, pd.DataFrame]:
    """All candidate indicators as date x symbol frames (inputs should be adjusted OHLC)."""
    out: dict[str, pd.DataFrame] = {}
    for n in (20, 50, 100, 200):
        out[f"sma{n}"] = sma(c, n)
    out["ema20"], out["ema50"] = ema(c, 20), ema(c, 50)
    out["rsi14"] = rsi(c, 14)
    line, sig, hist = macd(c)
    out["macd"], out["macd_signal"], out["macd_hist"] = line, sig, hist
    out["macd_hist_norm"] = hist / c
    adx14, pdi, mdi = adx(h, lo, c, 14)
    out["adx14"], out["plus_di14"], out["minus_di14"] = adx14, pdi, mdi
    out["adx14_trend"] = adx14 * np.sign(pdi - mdi)
    atr14 = atr(h, lo, c, 14)
    out["atr14"] = atr14
    out["atr14_pct"] = atr14 / c
    out["vol_20d"], out["vol_60d"] = volatility(c, 20), volatility(c, 60)
    out["volume_ratio_20d"] = v.rolling(5, min_periods=5).mean() / v.rolling(20, min_periods=20).mean()
    high_252 = h.rolling(TRADING_DAYS, min_periods=int(TRADING_DAYS * 0.8)).max()
    out["dist_52w_high"] = c / high_252 - 1.0
    out["price_sma200"] = c / out["sma200"] - 1.0
    out["sma50_sma200"] = out["sma50"] / out["sma200"] - 1.0
    prior_max20 = c.shift(1).rolling(20, min_periods=20).max()
    prior_max60 = c.shift(1).rolling(60, min_periods=60).max()
    out["breakout_20d"] = (c > prior_max20).astype(float).where(prior_max20.notna())
    out["breakout_60d_flag"] = (c > prior_max60).astype(float).where(prior_max60.notna())
    out["breakout_60d"] = c / prior_max60 - 1.0
    if bench_close is not None:
        b = bench_close.reindex(c.index)
        r6 = c / c.shift(126) - 1.0
        b6 = b / b.shift(126) - 1.0
        out["rs_qqq_6m"] = (1.0 + r6).div(1.0 + b6, axis=0) - 1.0
        out["beta_qqq_252d"] = rolling_beta(c.pct_change(fill_method=None), b.pct_change(fill_method=None))
    return out


def adjusted_ohlc(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Long daily_prices frame -> adjusted OHLCV matrices (open/high/low scaled by adj_close/close)."""
    p = prices.copy()
    p["date"] = pd.to_datetime(p["date"])
    factor = (p["adj_close"] / p["close"]).where(p["close"] > 0, 1.0)
    p["a_open"], p["a_high"], p["a_low"] = p["open"] * factor, p["high"] * factor, p["low"] * factor
    mats = {}
    for name, col in (("open", "a_open"), ("high", "a_high"), ("low", "a_low"), ("close", "adj_close"),
                      ("volume", "volume"), ("raw_close", "close")):
        mats[name] = p.pivot(index="date", columns="symbol", values=col).sort_index()
    return mats
