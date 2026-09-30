"""T2: EDGAR 10-K Item 1 (Business) extraction with a local text cache.

Filing metadata comes from data.sec.gov submissions (``filings.recent`` plus the older ``filings.files`` pages).
Documents are fetched from www.sec.gov/Archives at <= 8 requests/second through the shared SEC client. Only the
extracted Item 1 text is cached (gzip JSON, one file per accession), so a re-run makes no network calls and raw
filings (often several MB of inline XBRL) are not stored.

Timing: EDGAR's ``acceptanceDateTime`` is published with a "Z" suffix but carries US Eastern wall-clock time
(acceptance window 06:00-22:00 ET). We interpret it as Eastern time; see ``valid_from_session`` in membership.py.
"""
from __future__ import annotations

import gzip
import json
import logging
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

from src.config import PROJECT_ROOT
from src.data.http import ApiError
from src.data.sec import SecClient, cik10

log = logging.getLogger(__name__)
CACHE_DIR = PROJECT_ROOT / "data" / "cache" / "edgar_item1"
ANNUAL_FORMS = ("10-K", "10-K405", "10-KT")

_BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "td"}
_SKIP_TAGS = {"script", "style", "ix:header", "head", "title"}


_VOID_TAGS = {"br", "img", "hr", "meta", "link", "input", "col", "area", "base", "wbr", "source", "param"}


class _TextExtractor(HTMLParser):
    """Keeps an open-element stack so hidden subtrees (display:none, ix:header, script/style) are skipped exactly,
    including in malformed HTML (end tags pop up to the matching open element)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._stack: list[tuple[str, bool]] = []  # (tag, hides_subtree)
        self._hidden = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in _BLOCK_TAGS and not self._hidden:
            self.parts.append("\n")
        if tag in _VOID_TAGS:
            return
        style = (dict(attrs).get("style") or "").replace(" ", "").lower()
        hides = tag in _SKIP_TAGS or "display:none" in style
        self._stack.append((tag, hides))
        if hides:
            self._hidden += 1

    def handle_startendtag(self, tag, attrs):
        if tag.lower() in _BLOCK_TAGS and not self._hidden:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _VOID_TAGS:
            return
        if any(t == tag for t, _ in self._stack):
            while self._stack:
                t, hides = self._stack.pop()
                if hides:
                    self._hidden -= 1
                if t == tag:
                    break
        if tag in _BLOCK_TAGS and not self._hidden:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._hidden:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    """HTML (incl. inline XBRL) to plain text with line breaks at block elements; hidden XBRL headers dropped."""
    p = _TextExtractor()
    p.feed(html)
    text = "".join(p.parts).replace("\xa0", " ").replace("​", "")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


_ITEM1 = re.compile(r"(?im)^\s*item\s*1\s*[.:\-–—]?\s*(?:\n\s*)?business\b")
_ITEM1A = re.compile(r"(?im)^\s*item\s*1a\s*[.:\-–—]?\s*(?:\n\s*)?risk\s+factors\b")
_ITEM2 = re.compile(r"(?im)^\s*item\s*2\s*[.:\-–—]?\s*(?:\n\s*)?(?:description\s+of\s+)?propert(?:y|ies)\b")


def extract_item1(text: str, min_chars: int = 1500) -> str | None:
    """Longest span from an 'Item 1. Business' heading to the next 'Item 1A' (else 'Item 2') heading.

    Taking the longest span skips table-of-contents entries, whose start and end headings are only a line apart.
    """
    starts = [m.start() for m in _ITEM1.finditer(text)]
    if not starts:
        return None
    ends_1a = [m.start() for m in _ITEM1A.finditer(text)]
    ends_2 = [m.start() for m in _ITEM2.finditer(text)]
    best: tuple[int, int] | None = None
    for s in starts:
        nxt = [e for e in ends_1a if e > s] or [e for e in ends_2 if e > s]
        if not nxt:
            continue
        e = nxt[0]
        if best is None or (e - s) > (best[1] - best[0]):
            best = (s, e)
    if best is None or best[1] - best[0] < min_chars:
        return None
    return text[best[0]:best[1]].strip()


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z\-']+", text))


@dataclass
class Filing:
    cik: str
    accession: str
    form: str
    filing_date: str
    acceptance: str
    report_date: str
    primary_document: str

    @property
    def url(self) -> str:
        return (f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{self.accession.replace('-', '')}/"
                f"{self.primary_document}")


def _rows_from(block: dict, cik: str, forms: tuple[str, ...]) -> list[Filing]:
    out = []
    for i, form in enumerate(block.get("form", [])):
        if form in forms and block["primaryDocument"][i]:
            out.append(Filing(cik, block["accessionNumber"][i], form, block["filingDate"][i],
                              block["acceptanceDateTime"][i], block.get("reportDate", [""] * (i + 1))[i],
                              block["primaryDocument"][i]))
    return out


def list_annual_filings(sec: SecClient, cik: int | str, since: str = "2009-01-01",
                        forms: tuple[str, ...] = ANNUAL_FORMS) -> list[Filing]:
    """All 10-K style filings since ``since`` (recent block plus the older paged blocks)."""
    c = cik10(cik)
    sub = sec.submissions(c)
    out = _rows_from(sub["filings"]["recent"], c, forms)
    for f in sub["filings"].get("files", []):
        if f.get("filingTo", "9999") < since:
            continue
        page = sec.get_json(f"{sec.base}/submissions/{f['name']}", ttl_hours=sec.cfg["ttl_hours"]["submissions"],
                            endpoint="submissions_page")
        out += _rows_from(page, c, forms)
    seen, uniq = set(), []
    for r in sorted(out, key=lambda r: r.filing_date):
        if r.accession not in seen and r.filing_date >= since:
            seen.add(r.accession)
            uniq.append(r)
    return uniq


def _cache_path(f: Filing, cache_dir: Path) -> Path:
    return cache_dir / f.cik / f"{f.accession}.json.gz"


def load_item1(f: Filing, cache_dir: Path = CACHE_DIR) -> dict | None:
    p = _cache_path(f, cache_dir)
    if not p.exists():
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def fetch_item1(sec: SecClient, f: Filing, cache_dir: Path = CACHE_DIR) -> dict:
    """Item 1 text for one filing (cache first; a network call only on a cache miss)."""
    cached = load_item1(f, cache_dir)
    if cached is not None:
        return cached
    try:
        html = sec.get_text(f.url, endpoint="archives_10k")
        text = html_to_text(html)
        item1 = extract_item1(text)
        status = "ok" if item1 else "item1_not_found"
    except ApiError as exc:
        item1, status, text = None, f"fetch_failed: {exc}"[:200], ""
    rec = {"cik": f.cik, "accession": f.accession, "form": f.form, "filing_date": f.filing_date,
           "acceptance": f.acceptance, "report_date": f.report_date, "primary_document": f.primary_document,
           "status": status, "doc_words": word_count(text) if text else 0,
           "item1_words": word_count(item1) if item1 else 0, "item1": item1 or ""}
    if not status.startswith("fetch_failed"):  # transient failures are retried on the next run
        p = _cache_path(f, cache_dir)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        with gzip.open(tmp, "wt", encoding="utf-8") as fh:
            json.dump(rec, fh)
        tmp.replace(p)
    return rec


def filings_frame(recs: list[dict]) -> pd.DataFrame:
    return pd.DataFrame([{k: v for k, v in r.items() if k != "item1"} for r in recs])
