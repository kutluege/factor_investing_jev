"""T3: point-in-time theme membership from 10-K Item 1 text (THEMES_SPEC §3-B).

Every membership row is tied to one 10-K filing and is valid from the session after its acceptance (one session
later when accepted at/after 16:00 ET) until the next 10-K becomes valid or 18 months pass. A later filing can
therefore never change membership on an earlier date (tested). Subthemes without keywords rely on the stage-A
industry/SIC filter but still require a 10-K filing to anchor the validity window.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import pandas as pd

from src.themes.config import ThemesConfig

MARKET_CLOSE_HOUR = 16
EASTERN = "America/New_York"
MAX_VALIDITY_MONTHS = 18

DDL = """CREATE TABLE IF NOT EXISTS theme_membership (
    cik VARCHAR, symbol VARCHAR, theme VARCHAR, subtheme VARCHAR, valid_from DATE, valid_to DATE,
    hits INTEGER, density DOUBLE, filing_accession VARCHAR, method VARCHAR, matched JSON,
    PRIMARY KEY (symbol, filing_accession))"""


def keyword_hits(text: str, keywords: list[str]) -> tuple[int, dict[str, int]]:
    """Case-insensitive, non-overlapping substring counts per keyword ("robot" also matches "robotic")."""
    low = text.lower()
    counts = {kw: low.count(kw.lower()) for kw in keywords}
    counts = {k: v for k, v in counts.items() if v}
    return sum(counts.values()), counts


def density(hits: int, words: int) -> float:
    return hits / words * 10_000 if words else 0.0


def eastern_time(acceptance: str) -> pd.Timestamp:
    """EDGAR submissions ``acceptanceDateTime`` (UTC, "Z") -> naive US Eastern wall-clock time.

    Verified 2026-09-30 against filing index pages: JSON 2024-02-01T21:12:25Z = "Accepted 2024-02-01 16:12:25"."""
    ts = pd.Timestamp(str(acceptance))
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert(EASTERN).tz_localize(None)


def valid_from_session(acceptance: str, sessions: pd.DatetimeIndex) -> pd.Timestamp:
    """First session at which a filing may be used: +1 session after acceptance; accepted at/after 16:00 ET counts
    as the next session's news, so +1 session after that."""
    ts = eastern_time(acceptance)
    day = ts.normalize()
    effective = day if ts.hour < MARKET_CLOSE_HOUR else _next_session(day, sessions)
    return _next_session(effective, sessions)


def _next_session(day: pd.Timestamp, sessions: pd.DatetimeIndex) -> pd.Timestamp:
    later = sessions[sessions > day]
    if len(later):
        return later[0]
    # beyond the calendar: next business day
    return (day + pd.offsets.BDay(1)).normalize()


@dataclass
class FilingScore:
    accession: str
    acceptance: str
    words: int
    scores: dict[str, tuple[int, float, dict]] = field(default_factory=dict)  # subtheme -> (hits, density, matched)


def choose_primary(qualifying: list[dict], cfg: ThemesConfig) -> dict | None:
    """One theme per firm. Theme conflicts: theme_tie_priority. Within a theme: keyword evidence beats stage-A-only,
    then highest density, then config order."""
    if not qualifying:
        return None
    prio = {t: i for i, t in enumerate(cfg.classification.theme_tie_priority)}
    order = {(t, s): i for i, (t, s) in enumerate((t, s) for t, th in cfg.themes.items() for s in th.subthemes)}
    return sorted(qualifying, key=lambda q: (prio.get(q["theme"], 99), 0 if q["method"] == "keywords" else 1,
                                             -q["density"], order.get((q["theme"], q["subtheme"]), 999)))[0]


_BLANK_CHECK = re.compile(r"(?i)\b(?:we are|the company is|is)\s+a\s+(?:newly\s+(?:incorporated|organized)\s+)?"
                          r"blank[\s-]+check\s+compan(?:y|ies)")


def is_blank_check(item1: str) -> bool:
    """Gate 2 revision (docs/CHANGELOG_THEMES.md): the filing's own Item 1 says the filer is a blank check company
    (SPAC). Text of the filing itself, hence point in time."""
    return bool(item1) and bool(_BLANK_CHECK.search(item1[:20000]))


def membership_rows(symbol: str, cik: str, stage_a: list[dict], filings: list[dict], cfg: ThemesConfig,
                    sessions: pd.DatetimeIndex) -> list[dict]:
    """Membership rows for one company. ``filings``: dicts with accession, acceptance, item1 (text), item1_words,
    status; ordered by acceptance. ``stage_a``: the company's coarse-filter subtheme matches."""
    filings = sorted(filings, key=lambda f: f["acceptance"])
    starts = [valid_from_session(f["acceptance"], sessions) for f in filings]
    rows = []
    for i, f in enumerate(filings):
        vf = starts[i]
        cap = vf + pd.DateOffset(months=MAX_VALIDITY_MONTHS)
        vt = min(starts[i + 1], cap) if i + 1 < len(starts) else cap
        if vt <= vf:
            continue
        if is_blank_check(f.get("item1", "")):
            continue  # SPAC shell: its 10-K describes a (prospective) target, not its own business
        qualifying = []
        for m in stage_a:
            sub = cfg.themes[m["theme"]].subthemes[m["subtheme"]]
            if not sub.keywords:
                qualifying.append({**m, "hits": 0, "density": 0.0, "matched": {}, "method": "stage_a"})
                continue
            if f.get("status") != "ok" or not f.get("item1"):
                continue
            hits, matched = keyword_hits(f["item1"], sub.keywords)
            if hits >= sub.min_hits:
                qualifying.append({**m, "hits": hits, "density": density(hits, f.get("item1_words", 0)),
                                   "matched": matched, "method": "keywords"})
        best = choose_primary(qualifying, cfg)
        if best is None:
            continue
        rows.append({"cik": cik, "symbol": symbol, "theme": best["theme"], "subtheme": best["subtheme"],
                     "valid_from": vf.date(), "valid_to": pd.Timestamp(vt).date(), "hits": int(best["hits"]),
                     "density": float(best["density"]), "filing_accession": f["accession"],
                     "method": best["method"], "matched": json.dumps(best["matched"])})
    return rows


def members_on(membership: pd.DataFrame, date: pd.Timestamp) -> pd.DataFrame:
    """Members whose validity window contains ``date`` (valid_from <= date < valid_to)."""
    d = pd.Timestamp(date)
    m = membership
    return m[(pd.to_datetime(m["valid_from"]) <= d) & (pd.to_datetime(m["valid_to"]) > d)]


def evidence_sentences(text: str, keywords: list[str], n: int = 2, max_len: int = 300) -> list[str]:
    """Up to ``n`` sentences from Item 1 that contain a matched keyword (for the review file)."""
    if not text or not keywords:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    out = []
    for s in sentences:
        low = s.lower()
        if any(k.lower() in low for k in keywords):
            out.append(s.strip()[:max_len])
            if len(out) >= n:
                break
    return out
