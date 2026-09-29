"""Compact, deterministic point-in-time state text for Jev.

All numbers are precomputed by Python; Jev only reads them. By default identifiers (ticker, company name, calendar
dates) are omitted so Jev cannot recall what happened to a named stock after a historical rebalance date.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any

import pandas as pd

FAMILY_LABELS = {
    "momentum": "price momentum", "quality": "quality/profitability", "investment": "conservative investment",
    "value": "value", "fundamental_momentum": "fundamental momentum", "low_risk": "low risk", "growth": "growth",
}


def _num(v: Any) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else f


def _pct(v: Any) -> str:
    f = _num(v)
    return "n/a" if f is None else f"{f * 100:+.1f}%"


def _pctile(v: Any) -> str:
    f = _num(v)
    return "n/a" if f is None else f"{round(f * 100):d}"


def _fmt(v: Any, nd: int = 1) -> str:
    f = _num(v)
    return "n/a" if f is None else f"{f:.{nd}f}"


def mcap_bucket(mcap: Any) -> str:
    f = _num(mcap)
    if f is None:
        return "unknown"
    for limit, label in ((3e8, "micro"), (2e9, "small"), (1e10, "mid"), (2e11, "large")):
        if f < limit:
            return label
    return "mega"


def adv_bucket(adv: Any) -> str:
    f = _num(adv)
    if f is None:
        return "unknown"
    for limit, label in ((5e6, "low"), (2e7, "moderate"), (1e8, "high")):
        if f < limit:
            return label
    return "very high"


def regime_context(bench_close: pd.Series | None, cross: pd.DataFrame, date: pd.Timestamp) -> dict[str, str]:
    """Market/sector regime from data up to ``date`` only."""
    ctx: dict[str, str] = {}
    if bench_close is not None:
        b = bench_close.loc[:date].dropna()
        if len(b) >= 200:
            sma200 = b.tail(200).mean()
            ret6 = b.iloc[-1] / b.iloc[-127] - 1 if len(b) > 127 else float("nan")
            vol = b.pct_change().tail(20).std() * (252 ** 0.5)
            vol_hist = b.pct_change().rolling(20).std().dropna().tail(252) * (252 ** 0.5)
            vol_pct = (vol_hist < vol).mean() if len(vol_hist) else float("nan")
            ctx["market_trend"] = "uptrend (QQQ above 200-day average)" if b.iloc[-1] > sma200 else \
                "downtrend (QQQ below 200-day average)"
            ctx["market_6m_return"] = _pct(ret6)
            ctx["market_volatility_regime"] = ("high" if vol_pct > 0.8 else "low" if vol_pct < 0.2 else "normal")
    if "sector_group" in cross and "ret_6m" in cross:
        ctx["_sector_median_6m"] = cross.groupby("sector_group")["ret_6m"].median().to_dict()  # type: ignore[assignment]
        if "price_sma200" in cross:
            ctx["_sector_breadth"] = cross.assign(a=cross["price_sma200"] > 0).groupby("sector_group")["a"].mean().to_dict()  # type: ignore[assignment]
    return ctx


def build_state(row: pd.Series, family_pct: pd.Series, regime: dict, include_identifiers: bool = False,
                identifiers: dict | None = None, portfolio: dict | None = None) -> str:
    """Render one stock's state. ``row`` holds raw features; ``family_pct`` holds family percentiles (0-1)."""
    group = row.get("sector_group") or "unknown"
    lines = []
    if include_identifiers and identifiers:
        lines.append(f"ticker: {identifiers.get('symbol')}")
        lines.append(f"company: {identifiers.get('name')}")
        lines.append(f"as_of: {identifiers.get('date')}")
    lines += [
        "context: point-in-time snapshot of a NASDAQ-listed stock for a long-only 3-6 month horizon",
        f"sector_group: {group.replace('_', ' ')}",
        f"industry: {row.get('industry') or 'n/a'}",
        f"market_cap_bucket: {mcap_bucket(row.get('market_cap'))}",
        f"liquidity_bucket: {adv_bucket(row.get('adv20'))}",
        "factor_percentiles_within_universe (0-100, higher is better): " + ", ".join(
            f"{FAMILY_LABELS[f]} {_pctile(family_pct.get(f))}" for f in FAMILY_LABELS),
        f"fundamentals: revenue growth yoy {_pct(row.get('revenue_yoy'))}; operating cash flow / assets "
        f"{_pct(row.get('cop_at'))}; gross profit / assets {_pct(row.get('gross_profitability'))}; "
        f"asset growth yoy {_pct(row.get('asset_growth'))}; share count change yoy {_pct(row.get('share_dilution_yoy'))}; "
        f"change in quarterly ROE yoy {_pct(row.get('droe'))}; earnings surprise (SUE) {_fmt(row.get('sue'), 1)}; "
        f"Piotroski F-score {_fmt(row.get('fscore'), 0)}/9",
        f"momentum: 3m {_pct(row.get('ret_3m'))}; 6m {_pct(row.get('ret_6m'))}; 12-1m {_pct(row.get('mom_12_1'))}; "
        f"residual momentum score {_fmt(row.get('res_mom_12_2'), 1)}; relative to QQQ 6m {_pct(row.get('rs_qqq_6m'))}; "
        f"relative to sector 6m {_pct(row.get('rs_sector_6m'))}; max daily return last month {_pct(row.get('max_ret_21d'))}",
        "technicals: price {} 50-day average; price {} 200-day average ({}); 50-day vs 200-day average {}; "
        "RSI14 {}; ADX14 {}; 60-day volatility {}; distance from 52-week high {}; 60-day breakout {}; "
        "5/20-day volume ratio {}".format(
            "above" if (_num(row.get("close_adj")) or 0) > (_num(row.get("sma50")) or float("inf")) else "below",
            "above" if (_num(row.get("price_sma200")) or -1) > 0 else "below", _pct(row.get("price_sma200")),
            _pct(row.get("sma50_sma200")), _fmt(row.get("rsi14"), 0), _fmt(row.get("adx14"), 0),
            _pct(row.get("vol_60d")), _pct(row.get("dist_52w_high")),
            "yes" if (_num(row.get("breakout_60d")) or -1) > 0 else "no", _fmt(row.get("volume_ratio_20d"), 2)),
    ]
    reg = [f"market trend {regime.get('market_trend', 'n/a')}",
           f"market 6m return {regime.get('market_6m_return', 'n/a')}",
           f"market volatility {regime.get('market_volatility_regime', 'n/a')}"]
    sec_med = regime.get("_sector_median_6m", {}).get(group)
    sec_br = regime.get("_sector_breadth", {}).get(group)
    if sec_med is not None:
        reg.append(f"sector median 6m return {_pct(sec_med)}")
    if sec_br is not None:
        reg.append(f"share of sector above 200-day average {_pctile(sec_br)}%")
    lines.append("regime: " + "; ".join(reg))
    if portfolio is not None:
        lines.append(
            "position: currently owned; held {} trading days; return since entry {}; rank now {} (previous {}); "
            "previous signal {}; family percentiles at entry: {}".format(
                portfolio.get("holding_days", "n/a"), _pct(portfolio.get("entry_return")),
                portfolio.get("rank", "n/a"), portfolio.get("previous_rank", "n/a"),
                portfolio.get("previous_signal", "n/a"), portfolio.get("entry_percentiles", "n/a")))
    return "\n".join(lines)


def state_hash(state: str) -> str:
    normalized = "\n".join(line.strip() for line in state.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def cache_key(model: str, state: str, state_schema_version: str, question_schema_version: str) -> str:
    payload = "\x1f".join([model, state_hash(state), state_schema_version, question_schema_version])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
