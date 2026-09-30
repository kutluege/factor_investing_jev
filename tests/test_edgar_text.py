import httpx

from src.data.sec import SecClient
from src.themes.edgar_text import Filing, extract_item1, fetch_item1, html_to_text, list_annual_filings

BODY = "Our company builds industrial robots and motion control systems for factory automation. " * 60

DOC = f"""<html><head><title>10-K</title></head><body>
<div style="display:none"><ix:header><ix:hidden>dei:EntityRegistrantName Hidden Corp item 1. business</ix:hidden>
</ix:header></div>
<p>TABLE OF CONTENTS</p>
<table><tr><td>Item 1.</td><td>Business</td><td>3</td></tr>
<tr><td>Item 1A.</td><td>Risk Factors</td><td>9</td></tr></table>
<p>ITEM 1. BUSINESS</p><p>{BODY}</p><br><p>More detail<br/>on robots.</p>
<p>ITEM 1A. RISK FACTORS</p><p>Risks here.</p>
<p>ITEM 2. PROPERTIES</p><p>We lease offices.</p>
</body></html>"""


def test_html_to_text_drops_hidden_xbrl_and_keeps_body():
    t = html_to_text(DOC)
    assert "Hidden Corp" not in t
    assert "industrial robots" in t and "Risks here." in t


def test_item1_skips_table_of_contents_duplicate():
    item1 = extract_item1(html_to_text(DOC))
    assert item1 is not None and item1.startswith("ITEM 1. BUSINESS")
    assert "industrial robots" in item1 and "Risks here" not in item1


def test_item1_falls_back_to_item2_when_no_1a():
    doc = DOC.replace("ITEM 1A. RISK FACTORS", "SOMETHING ELSE")
    item1 = extract_item1(html_to_text(doc))
    assert item1 is not None and "Risks here" in item1 and "We lease offices" not in item1


def test_item1_missing_returns_none():
    assert extract_item1(html_to_text("<p>Annual report without the usual headings.</p>")) is None


FILLER = "<p>" + "Other annual report content about finance and accounting. " * 200 + "</p>"
BODY = "<p>" + "We design collaborative robots and machine vision systems for factories. " * 40 + "</p>"


def test_item1_fallback_uppercase_business_heading_without_item_labels():
    doc = (f"<html><body><p>FORM 10-K CROSS REFERENCE INDEX</p><p>Business ... page 4</p>{FILLER}"
           f"<p>BUSINESS</p>{BODY}<p>RISK FACTORS</p><p>Risks here.</p>{FILLER}</body></html>")
    item1 = extract_item1(html_to_text(doc))
    assert item1 is not None and item1.startswith("BUSINESS") and "collaborative robots" in item1
    assert "Risks here" not in item1 and "cross reference" not in item1.lower()


def test_item1_fallback_rejects_span_covering_most_of_the_document():
    doc = f"<html><body><p>BUSINESS</p>{BODY}{FILLER}<p>RISK FACTORS</p><p>end</p></body></html>"
    assert extract_item1(html_to_text(doc)) is None


def _submissions(cik: int) -> dict:
    return {"cik": str(cik), "name": "Robo Inc", "filings": {
        "recent": {"form": ["10-Q", "10-K", "8-K", "10-K"], "accessionNumber": ["a-1", "a-2", "a-3", "a-4"],
                   "filingDate": ["2024-05-01", "2024-02-15", "2024-01-10", "2023-02-14"],
                   "acceptanceDateTime": ["2024-05-01T16:30:00.000Z", "2024-02-15T17:05:00.000Z",
                                          "2024-01-10T08:00:00.000Z", "2023-02-14T09:00:00.000Z"],
                   "reportDate": ["2024-03-31", "2023-12-31", "2024-01-09", "2022-12-31"],
                   "primaryDocument": ["q.htm", "k24.htm", "e.htm", "k23.htm"]},
        "files": []}}


def test_filing_listing_and_cache_makes_no_network_calls(tmp_path):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if "submissions" in request.url.path:
            return httpx.Response(200, json=_submissions(42))
        return httpx.Response(200, text=DOC)
    from src.data.http import RawCache
    sec = SecClient(user_agent="tests tests@example.com", transport=httpx.MockTransport(handler),
                    cache=RawCache(tmp_path / "raw"))
    filings = list_annual_filings(sec, 42)
    assert [f.accession for f in filings] == ["a-4", "a-2"]  # 10-Ks only, oldest first
    rec = fetch_item1(sec, filings[-1], tmp_path / "item1")
    assert rec["status"] == "ok" and rec["item1_words"] > 500
    n = len(calls)
    again = fetch_item1(sec, filings[-1], tmp_path / "item1")
    assert again == rec and len(calls) == n  # second run served from the text cache


def test_filing_url():
    f = Filing("0000320193", "0000320193-25-000079", "10-K", "2025-10-31", "2025-10-31T10:01:26.000Z",
               "2025-09-27", "aapl-20250927.htm")
    assert f.url == "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm"


def test_retry_not_found_refetches_only_when_asked(tmp_path):
    import gzip
    import json

    f = Filing("0000000001", "0000000001-24-000001", "10-K", "2024-02-15", "2024-02-15T21:00:00.000Z",
               "2023-12-31", "k.htm")
    p = tmp_path / f.cik / f"{f.accession}.json.gz"
    p.parent.mkdir(parents=True)
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        json.dump({"status": "item1_not_found", "item1": ""}, fh)

    class FakeSec:
        calls = 0

        def get_text(self, url, endpoint):
            FakeSec.calls += 1
            return DOC

    assert fetch_item1(FakeSec(), f, tmp_path)["status"] == "item1_not_found" and FakeSec.calls == 0
    assert fetch_item1(FakeSec(), f, tmp_path, retry_not_found=True)["status"] == "ok" and FakeSec.calls == 1
    assert fetch_item1(FakeSec(), f, tmp_path, retry_not_found=True)["status"] == "ok" and FakeSec.calls == 1
