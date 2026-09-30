"""Announcement-dated earnings features (THEMES_SPEC §4 T4b): ``ear_3d`` and ``sue_announce``.

Timing comes from EDGAR 8-K Item 2.02 acceptance times (US Eastern), because FMP ``earnings`` dates agreed with
8-K dates in only 16/20 sampled firm-quarters (< 90%, reports/themes/T4b_earnings_dates.md). FMP supplies only the
realized EPS value (``epsActual``) of the announcement it is matched to; analyst estimates are never used.

- event session ``t0``: the acceptance day if it is a session and acceptance < 16:00 ET, else the next session.
- ``available_from`` = the session after ``t0`` (spec: t0 + 1 session).
- ear_3d: sum over sessions t0-1..t0+1 of (r_i - r_benchmark), latest event with t0 within the last 90 calendar
  days and a complete window on or before the rebalance date.
- sue_announce: (EPS_q - EPS_{q-4}) / std of the last 8 seasonal changes, same convention as filing-dated ``sue``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MARKET_CLOSE_HOUR = 16
DEDUP_DAYS = 5           # 8-K/A and duplicate 2.02 filings within this window are the same announcement
MATCH_DAYS = 3           # FMP record must lie within +-3 calendar days of the 8-K date
EAR_LOOKBACK_DAYS = 90
SEASONAL_GAP = (300, 430)  # calendar days between an announcement and its q-4 counterpart


def _session_on_or_after(day: pd.Timestamp, sessions: pd.DatetimeIndex) -> pd.Timestamp | None:
    i = sessions.searchsorted(day, side="left")
    return sessions[i] if i < len(sessions) else None


def event_session(acceptance_et: pd.Timestamp, sessions: pd.DatetimeIndex) -> pd.Timestamp | None:
    day = acceptance_et.normalize()
    if acceptance_et.hour >= MARKET_CLOSE_HOUR:
        day = day + pd.Timedelta(days=1)
    return _session_on_or_after(day, sessions)


def announcement_events(k8: pd.DataFrame, fmp_eps: pd.DataFrame, sessions: pd.DatetimeIndex) -> pd.DataFrame:
    """One row per announcement: t0, available_from, eps (FMP epsActual matched within MATCH_DAYS, else NaN).

    ``k8``: columns accession, acceptance (naive US Eastern). ``fmp_eps``: columns date, epsActual."""
    cols = ["accession", "acceptance", "t0", "available_from", "eps", "fmp_date"]
    if k8.empty:
        return pd.DataFrame(columns=cols)
    k8 = k8.sort_values("acceptance")
    keep, last = [], None
    for r in k8.itertuples():
        if last is None or (r.acceptance - last).days > DEDUP_DAYS:
            keep.append(r)
            last = r.acceptance
    fmp = fmp_eps.dropna(subset=["epsActual"]).sort_values("date") if not fmp_eps.empty else fmp_eps
    used: set[int] = set()
    rows = []
    for r in keep:
        t0 = event_session(r.acceptance, sessions)
        if t0 is None:
            continue
        nxt = sessions[sessions > t0]
        avail = nxt[0] if len(nxt) else None
        eps, fdate = np.nan, pd.NaT
        if not fmp.empty:
            gap = (fmp["date"] - r.acceptance.normalize()).dt.days.abs()
            cand = gap[(gap <= MATCH_DAYS) & ~gap.index.isin(list(used))]
            if len(cand):
                j = cand.idxmin()
                used.add(j)
                eps, fdate = float(fmp.at[j, "epsActual"]), fmp.at[j, "date"]
        rows.append({"accession": r.accession, "acceptance": r.acceptance, "t0": t0, "available_from": avail,
                     "eps": eps, "fmp_date": fdate})
    return pd.DataFrame(rows, columns=cols)


def sue_announce_at(events: pd.DataFrame, at: pd.Timestamp) -> float:
    ev = events[events["available_from"].notna() & (events["available_from"] <= at)].sort_values("t0")
    ev = ev.tail(12)
    if len(ev) < 12:
        return np.nan
    t0 = list(ev["t0"])[::-1]
    eps = list(ev["eps"])[::-1]
    changes = []
    for k in range(8):
        gap = (t0[k] - t0[k + 4]).days
        ok = SEASONAL_GAP[0] <= gap <= SEASONAL_GAP[1]
        changes.append(eps[k] - eps[k + 4] if ok else np.nan)
    ch = np.array([c for c in changes if not np.isnan(c)])
    if np.isnan(changes[0]) or len(ch) < 6:
        return np.nan
    sd = ch.std(ddof=1)
    return float(np.clip(changes[0] / sd, -10, 10)) if sd > 0 else np.nan


def ear_3d_at(events: pd.DataFrame, ret: pd.Series, bench_ret: pd.Series, at: pd.Timestamp) -> float:
    """Abnormal 3-session return around the latest announcement whose window closed on or before ``at``."""
    r = ret.loc[:at]
    idx = r.index
    for t0 in sorted(events["t0"].dropna(), reverse=True):
        if t0 < at - pd.Timedelta(days=EAR_LOOKBACK_DAYS):
            return np.nan
        pos = idx.searchsorted(t0)
        if pos >= len(idx) or idx[pos] != t0 or pos == 0 or pos + 1 >= len(idx):
            continue  # window not complete by ``at`` (or t0 not a trading day for this stock)
        win = idx[pos - 1: pos + 2]
        diff = r.loc[win] - bench_ret.reindex(win)
        return float(diff.sum()) if diff.notna().all() else np.nan
    return np.nan


def earnings_features_at(events_by_symbol: dict[str, pd.DataFrame], returns: pd.DataFrame,
                         bench_of: pd.Series, at: pd.Timestamp) -> pd.DataFrame:
    """Cross-section of ear_3d and sue_announce. ``returns`` holds daily simple returns for stocks and benchmark
    ETFs; ``bench_of`` maps symbol -> benchmark ETF symbol (theme ETF)."""
    out = {}
    for sym, ev in events_by_symbol.items():
        if ev.empty:
            continue
        ear = np.nan
        b = bench_of.get(sym)
        if sym in returns and b in returns:
            ear = ear_3d_at(ev, returns[sym], returns[b], at)
        out[sym] = {"ear_3d": ear, "sue_announce": sue_announce_at(ev, at)}
    return pd.DataFrame.from_dict(out, orient="index", columns=["ear_3d", "sue_announce"])
