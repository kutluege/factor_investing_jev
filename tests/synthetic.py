"""Synthetic market used ONLY by tests. Produces FMP- and SEC-shaped payloads served through httpx.MockTransport,
so the production client, parsing and pipeline code paths are exercised without network access."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse

import httpx
import numpy as np
import pandas as pd

GROUPS = {
    "Technology": ("Technology", "Software - Application", 7372),
    "Biotech": ("Healthcare", "Biotechnology", 2836),
    "Energy": ("Energy", "Oil & Gas Exploration & Production", 1311),
    "Mining": ("Basic Materials", "Gold", 1040),
}


@dataclass
class Company:
    symbol: str
    cik: int
    group: str
    quality: float
    shares: float
    start: pd.Timestamp | None = None
    end: pd.Timestamp | None = None     # delisting date (prices stop)
    split: tuple | None = None          # (date, ratio)


@dataclass
class SyntheticWorld:
    calendar: pd.DatetimeIndex
    companies: list[Company]
    prices: dict[str, pd.DataFrame] = field(default_factory=dict)
    facts: dict[int, dict] = field(default_factory=dict)
    fmp_calls: list[str] = field(default_factory=list)
    sec_calls: list[str] = field(default_factory=list)


def make_world(n_per_group: int = 12, years: int = 5, seed: int = 7) -> SyntheticWorld:
    """Five years of business days ending yesterday (FMP history windows are anchored to today)."""
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize() - pd.offsets.BDay(1)
    cal = pd.bdate_range(end - pd.DateOffset(years=years), end)
    companies = []
    k = 0
    for g in GROUPS:
        for i in range(n_per_group):
            sym = f"{g[:2].upper()}{chr(65 + i)}{chr(65 + (k % 26))}"
            companies.append(Company(sym, 100000 + k, g, float(rng.normal()), float(rng.uniform(5e7, 4e8))))
            k += 1
    companies[3].end = cal[int(len(cal) * 0.6)]             # delisted mid-sample
    companies[5].start = cal[int(len(cal) * 0.4)]           # IPO mid-sample
    companies[7].split = (cal[int(len(cal) * 0.5)], 2.0)    # 2:1 split
    w = SyntheticWorld(cal, companies)
    market = np.cumsum(rng.normal(0.0004, 0.011, len(cal)))
    for bench, beta in (("QQQ", 1.0), ("SPY", 0.8), ("XLK", 1.1), ("XBI", 1.2), ("XLE", 0.6), ("XME", 0.9)):
        close = 100 * np.exp(beta * market + np.cumsum(rng.normal(0, 0.004, len(cal))))
        w.prices[bench] = _ohlcv(cal, close, rng, 5e7)
    for c in companies:
        mu = 0.0002 + 0.0006 * c.quality
        idio = rng.normal(mu, 0.02, len(cal))
        close = 20 * np.exp(0.9 * market + np.cumsum(idio))
        df = _ohlcv(cal, close, rng, float(rng.uniform(3e5, 3e6)))
        if c.start is not None:
            df = df[df["date"] >= c.start]
        if c.end is not None:
            df = df[df["date"] <= c.end]
        w.prices[c.symbol] = df.reset_index(drop=True)
        w.facts[c.cik] = _company_facts(c, rng, cal[0].year - 2, cal[-1])
    return w


def _ohlcv(cal, close, rng, vol_level) -> pd.DataFrame:
    close = np.asarray(close)
    open_ = close * (1 + rng.normal(0, 0.004, len(close)))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, len(close))))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, len(close))))
    vol = vol_level * np.exp(rng.normal(0, 0.3, len(close)))
    return pd.DataFrame({"date": cal, "open": open_, "high": high, "low": low, "close": close, "volume": vol})


def _company_facts(c: Company, rng, first_year: int, today: pd.Timestamp) -> dict:
    """Quarterly 10-Q / annual 10-K facts, calendar fiscal year. 10-Q filed 40 days after quarter end, 10-K 60."""
    rev0 = float(rng.uniform(5e7, 5e8))
    growth = 0.03 + 0.03 * c.quality
    margin = 0.05 + 0.08 * c.quality
    concepts: dict[str, list] = {k: [] for k in (
        "Revenues", "GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss", "ResearchAndDevelopmentExpense",
        "NetCashProvidedByUsedInOperatingActivities", "PaymentsToAcquirePropertyPlantAndEquipment",
        "WeightedAverageNumberOfDilutedSharesOutstanding", "Assets", "StockholdersEquity",
        "CashAndCashEquivalentsAtCarryingValue", "LongTermDebt", "LiabilitiesCurrent", "AssetsCurrent")}
    dei: list = []
    ytd_cf: dict[int, float] = {}
    ytd_capex: dict[int, float] = {}
    for year in range(first_year, today.year + 1):
        for q in range(1, 5):
            qs = pd.Timestamp(year=year, month=3 * q - 2, day=1)
            qe = qs + pd.offsets.QuarterEnd(0)
            t = (year - first_year) * 4 + q
            rev = rev0 * (1 + growth) ** t * float(np.exp(rng.normal(0, 0.03)))
            op = rev * (margin + rng.normal(0, 0.01))
            ni = op * 0.8
            cf = ni * 1.1
            capex = rev * 0.05
            form = "10-K" if q == 4 else "10-Q"
            filed = qe + pd.Timedelta(days=60 if q == 4 else 40)
            if filed > today:  # filings that have not happened yet do not exist
                break
            accn = f"{c.cik:010d}-{year % 100:02d}-{q:06d}"
            fp = "FY" if q == 4 else f"Q{q}"
            base = {"accn": accn, "fy": year, "fp": fp, "form": form, "filed": str(filed.date())}
            ytd_cf[q] = ytd_cf.get(q - 1, 0.0) + cf if q > 1 else cf
            ytd_capex[q] = ytd_capex.get(q - 1, 0.0) + capex if q > 1 else capex
            if q < 4:
                for name, v in (("Revenues", rev), ("GrossProfit", rev * 0.55), ("OperatingIncomeLoss", op),
                                ("NetIncomeLoss", ni), ("ResearchAndDevelopmentExpense", rev * 0.12)):
                    concepts[name].append({"start": str(qs.date()), "end": str(qe.date()), "val": v, **base})
            else:
                # 10-K reports the fiscal year only; Q4 must be derived as FY - 9M YTD
                fy_start = pd.Timestamp(year=year, month=1, day=1)
                prior = [x for x in concepts["Revenues"] if x["start"][:4] == str(year)]
                fy_rev = sum(x["val"] for x in prior) + rev
                concepts["Revenues"].append({"start": str(fy_start.date()), "end": str(qe.date()), "val": fy_rev, **base})
                for name, factor in (("GrossProfit", 0.55), ("ResearchAndDevelopmentExpense", 0.12)):
                    concepts[name].append({"start": str(fy_start.date()), "end": str(qe.date()),
                                           "val": fy_rev * factor, **base})
                prior_op = sum(x["val"] for x in concepts["OperatingIncomeLoss"] if x["start"][:4] == str(year))
                concepts["OperatingIncomeLoss"].append({"start": str(fy_start.date()), "end": str(qe.date()),
                                                        "val": prior_op + op, **base})
                prior_ni = sum(x["val"] for x in concepts["NetIncomeLoss"] if x["start"][:4] == str(year))
                concepts["NetIncomeLoss"].append({"start": str(fy_start.date()), "end": str(qe.date()),
                                                  "val": prior_ni + ni, **base})
            ytd_start = pd.Timestamp(year=year, month=1, day=1)
            concepts["NetCashProvidedByUsedInOperatingActivities"].append(
                {"start": str(ytd_start.date()), "end": str(qe.date()), "val": ytd_cf[q], **base})
            concepts["PaymentsToAcquirePropertyPlantAndEquipment"].append(
                {"start": str(ytd_start.date()), "end": str(qe.date()), "val": ytd_capex[q], **base})
            shares = c.shares * (2.0 if c.split and qe >= c.split[0] else 1.0)
            concepts["WeightedAverageNumberOfDilutedSharesOutstanding"].append(
                {"start": str(qs.date()), "end": str(qe.date()), "val": shares, **base})
            assets = rev * 3
            for name, v in (("Assets", assets), ("StockholdersEquity", assets * 0.5),
                            ("CashAndCashEquivalentsAtCarryingValue", assets * 0.15), ("LongTermDebt", assets * 0.2),
                            ("LiabilitiesCurrent", assets * 0.15), ("AssetsCurrent", assets * 0.35)):
                concepts[name].append({"end": str(qe.date()), "val": v, **base})
            dei.append({"end": str((filed - pd.Timedelta(days=10)).date()), "val": shares, **base})
    return {"cik": c.cik, "entityName": f"{c.symbol} Corp", "facts": {
        "us-gaap": {k: {"units": {"shares" if "Shares" in k else "USD": v}} for k, v in concepts.items()},
        "dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": dei}}}}}


def _split_adjusted(w: SyntheticWorld, sym: str) -> pd.DataFrame:
    """FMP serves split-adjusted history: synthetic closes are generated in adjusted units already."""
    return w.prices[sym]


def fmp_transport(w: SyntheticWorld, bandwidth_exhausted: bool = False) -> httpx.MockTransport:
    by_symbol = {c.symbol: c for c in w.companies}

    def handler(request: httpx.Request) -> httpx.Response:
        url = urlparse(str(request.url))
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        path = url.path.replace("/stable/", "")
        w.fmp_calls.append(path)
        if bandwidth_exhausted:
            return httpx.Response(429, json={"Error Message": "Bandwidth Limit Reach . Please upgrade your plan"})
        if path == "company-screener":
            rows = []
            for c in w.companies:
                if c.end is not None:
                    continue
                sector, industry, _ = GROUPS[c.group]
                rows.append({"symbol": c.symbol, "companyName": f"{c.symbol} Corp", "sector": sector,
                             "industry": industry, "isEtf": False, "isFund": False, "isActivelyTrading": True,
                             "exchangeShortName": "NASDAQ"})
            rows.append({"symbol": "ETFX", "companyName": "Some ETF", "sector": "Technology", "industry": "",
                         "isEtf": True, "isFund": False, "isActivelyTrading": True})
            return httpx.Response(200, json=rows)
        if path == "delisted-companies":
            if q.get("page", "0") != "0":
                return httpx.Response(200, json=[])
            return httpx.Response(200, json=[{"symbol": c.symbol, "companyName": f"{c.symbol} Corp",
                                              "exchange": "NASDAQ", "ipoDate": "2010-01-01",
                                              "delistedDate": str(c.end.date())} for c in w.companies if c.end])
        if path == "splits":
            c = by_symbol.get(q["symbol"])
            if c and c.split:
                return httpx.Response(200, json=[{"symbol": c.symbol, "date": str(c.split[0].date()),
                                                  "numerator": c.split[1], "denominator": 1}])
            return httpx.Response(200, json=[])
        if path.startswith("historical-price-eod/"):
            sym = q["symbol"]
            if sym not in w.prices:
                return httpx.Response(200, json=[])
            df = _split_adjusted(w, sym)
            df = df[(df["date"] >= pd.Timestamp(q["from"])) & (df["date"] <= pd.Timestamp(q["to"]))]
            if path.endswith("full"):
                rows = [{"symbol": sym, "date": str(r.date.date()), "open": r.open, "high": r.high, "low": r.low,
                         "close": r.close, "volume": r.volume} for r in df.itertuples()]
            else:  # dividend-adjusted: synthetic stocks pay no dividends
                rows = [{"symbol": sym, "date": str(r.date.date()), "adjOpen": r.open, "adjHigh": r.high,
                         "adjLow": r.low, "adjClose": r.close, "volume": r.volume} for r in df.itertuples()]
            return httpx.Response(200, json=rows[::-1])
        if path == "profile":
            c = by_symbol.get(q["symbol"])
            if not c:
                return httpx.Response(200, json=[])
            sector, industry, _ = GROUPS[c.group]
            return httpx.Response(200, json=[{"symbol": c.symbol, "sector": sector, "industry": industry,
                                              "cik": str(c.cik).zfill(10), "ipoDate": "2010-01-01"}])
        return httpx.Response(404, json={"Error Message": f"unknown path {path}"})
    return httpx.MockTransport(handler)


def sec_transport(w: SyntheticWorld) -> httpx.MockTransport:
    by_cik = {c.cik: c for c in w.companies}

    def handler(request: httpx.Request) -> httpx.Response:
        path = urlparse(str(request.url)).path
        w.sec_calls.append(path)
        if "User-Agent" not in request.headers or "@" not in request.headers["User-Agent"]:
            return httpx.Response(403, text="Your Request Originates from an Undeclared Automated Tool")
        if path.endswith("company_tickers_exchange.json"):
            data = [[c.cik, f"{c.symbol} Corp", c.symbol, "Nasdaq"] for c in w.companies if c.end is None]
            return httpx.Response(200, json={"fields": ["cik", "name", "ticker", "exchange"], "data": data})
        if "/submissions/CIK" in path:
            cik = int(path.split("CIK")[1].split(".")[0])
            c = by_cik.get(cik)
            if not c:
                return httpx.Response(404, text="not found")
            return httpx.Response(200, json={"cik": str(cik), "sic": str(GROUPS[c.group][2]), "entityType": "operating",
                                             "sicDescription": GROUPS[c.group][1]})
        if "/companyfacts/CIK" in path:
            cik = int(path.split("CIK")[1].split(".")[0])
            if cik not in w.facts:
                return httpx.Response(404, text="not found")
            return httpx.Response(200, json=w.facts[cik])
        return httpx.Response(404, text="not found")
    return httpx.MockTransport(handler)


def jev_transport(calls: list | None = None, fail_first: int = 0, status: int = 200) -> httpx.MockTransport:
    """Deterministic fake Jev: answers derived from a hash of the state (never used in production)."""
    state = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        body = json.loads(request.content)
        if calls is not None:
            calls.append(body)
        if state["n"] <= fail_first:
            return httpx.Response(429, headers={"retry-after": "0"},
                                  json={"error": {"message": "Rate limit exceeded", "type": "rate_limit_exceeded"}})
        if status != 200:
            return httpx.Response(status, json={"error": {"message": "Authentication failed",
                                                          "type": "authentication_error"}})
        h = int(hashlib.sha256(body["state"].encode()).hexdigest(), 16)
        answers = {}
        for i, (qid, q) in enumerate(body["questions"].items()):
            p = ((h >> (8 * i)) % 1000) / 1000
            if q["type"] == "boolean":
                answers[qid] = {"type": "boolean", "probability": round(p, 3)}
            elif q["type"] == "score":
                n = len(q["criteria"])
                probs = {str(k): 0.0 for k in range(n)}
                top = int(p * n) % n
                probs[str(top)] = 0.7
                probs[str((top + 1) % n)] = 0.3
                score = sum(int(k) * v for k, v in probs.items())
                answers[qid] = {"type": "score", "score": score, "probabilities": probs, "confidence": 0.5}
            else:
                labels = list(q["criteria"])
                answers[qid] = {"type": "choice", "choice": labels[0], "probabilities": {lb: 1 / len(labels) for lb in labels},
                                "confidence": 0.1}
        return httpx.Response(200, json={"model": body["model"], "answers": answers,
                                         "usage": {"inputTokens": 300, "outputTokens": 20},
                                         "providerMetadata": {"gateway": {"cost": "0", "marketCost": "0.00001",
                                                                          "generationId": f"gen_{state['n']}"}}})
    return httpx.MockTransport(handler)
