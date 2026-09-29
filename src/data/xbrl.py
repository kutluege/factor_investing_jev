"""SEC XBRL company-facts normalization with point-in-time (filing-availability) semantics.

Key rules
- A fact becomes usable on ``availability_date = filed + availability_lag_days`` (never on its period end).
- Periods are identified by (start, end); ``fy``/``fp`` describe the *filing*, not the period, so they are not
  used to identify periods.
- When the same period is reported in several filings (original + later comparatives/restatements), the value
  used as of date D is the one from the most recent filing whose availability_date <= D.
- Several XBRL concepts can represent one metric (companies switch tags); a per-metric priority list decides.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

# metric -> (kind, [(taxonomy, concept, unit), ...] in priority order)
FLOW, INSTANT, AVERAGE = "flow", "instant", "average"

METRICS: dict[str, tuple[str, list[tuple[str, str, str]]]] = {
    "revenue": (FLOW, [
        ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
        ("us-gaap", "Revenues", "USD"),
        ("us-gaap", "SalesRevenueNet", "USD"),
        ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax", "USD"),
        ("us-gaap", "SalesRevenueGoodsNet", "USD"),
    ]),
    "cost_of_revenue": (FLOW, [
        ("us-gaap", "CostOfRevenue", "USD"),
        ("us-gaap", "CostOfGoodsAndServicesSold", "USD"),
        ("us-gaap", "CostOfGoodsSold", "USD"),
    ]),
    "gross_profit": (FLOW, [("us-gaap", "GrossProfit", "USD")]),
    "operating_income": (FLOW, [("us-gaap", "OperatingIncomeLoss", "USD")]),
    "pretax_income": (FLOW, [
        ("us-gaap", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "USD"),
        ("us-gaap", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments", "USD"),
    ]),
    "income_tax": (FLOW, [("us-gaap", "IncomeTaxExpenseBenefit", "USD")]),
    "net_income": (FLOW, [
        ("us-gaap", "NetIncomeLoss", "USD"),
        ("us-gaap", "ProfitLoss", "USD"),
        ("us-gaap", "NetIncomeLossAvailableToCommonStockholdersBasic", "USD"),
    ]),
    "interest_expense": (FLOW, [
        ("us-gaap", "InterestExpense", "USD"),
        ("us-gaap", "InterestExpenseNonoperating", "USD"),
        ("us-gaap", "InterestExpenseDebt", "USD"),
    ]),
    "depreciation": (FLOW, [
        ("us-gaap", "DepreciationDepletionAndAmortization", "USD"),
        ("us-gaap", "DepreciationAndAmortization", "USD"),
        ("us-gaap", "DepreciationAmortizationAndAccretionNet", "USD"),
        ("us-gaap", "Depreciation", "USD"),
    ]),
    "rd_expense": (FLOW, [
        ("us-gaap", "ResearchAndDevelopmentExpense", "USD"),
        ("us-gaap", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost", "USD"),
    ]),
    "operating_cf": (FLOW, [
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivities", "USD"),
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations", "USD"),
    ]),
    "capex": (FLOW, [
        ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment", "USD"),
        ("us-gaap", "PaymentsToAcquireProductiveAssets", "USD"),
        ("us-gaap", "PaymentsToExploreAndDevelopOilAndGasProperties", "USD"),   # E&P companies
        ("us-gaap", "PaymentsToAcquireOilAndGasPropertyAndEquipment", "USD"),
    ]),
    "diluted_shares": (AVERAGE, [
        ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
        ("us-gaap", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted", "shares"),
        ("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic", "shares"),
    ]),
    "total_assets": (INSTANT, [("us-gaap", "Assets", "USD")]),
    "current_assets": (INSTANT, [("us-gaap", "AssetsCurrent", "USD")]),
    "current_liabilities": (INSTANT, [("us-gaap", "LiabilitiesCurrent", "USD")]),
    "total_liabilities": (INSTANT, [("us-gaap", "Liabilities", "USD")]),
    "equity": (INSTANT, [
        ("us-gaap", "StockholdersEquity", "USD"),
        ("us-gaap", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", "USD"),
    ]),
    "cash": (INSTANT, [
        ("us-gaap", "CashAndCashEquivalentsAtCarryingValue", "USD"),
        ("us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "USD"),
        ("us-gaap", "Cash", "USD"),
    ]),
    "short_term_investments": (INSTANT, [
        ("us-gaap", "ShortTermInvestments", "USD"),
        ("us-gaap", "MarketableSecuritiesCurrent", "USD"),
        ("us-gaap", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "USD"),
    ]),
    "long_term_debt": (INSTANT, [
        ("us-gaap", "LongTermDebtNoncurrent", "USD"),
        ("us-gaap", "LongTermDebt", "USD"),
        ("us-gaap", "LongTermDebtAndCapitalLeaseObligations", "USD"),
    ]),
    "short_term_debt": (INSTANT, [
        ("us-gaap", "LongTermDebtCurrent", "USD"),
        ("us-gaap", "DebtCurrent", "USD"),
        ("us-gaap", "ShortTermBorrowings", "USD"),
    ]),
    "shares_outstanding": (INSTANT, [
        ("dei", "EntityCommonStockSharesOutstanding", "shares"),
        ("us-gaap", "CommonStockSharesOutstanding", "shares"),
    ]),
}

CONCEPT_TO_METRIC = {(tax, c, u): (m, prio) for m, (_, lst) in METRICS.items() for prio, (tax, c, u) in enumerate(lst)}
METRIC_KIND = {m: k for m, (k, _) in METRICS.items()}

QUARTER_DAYS = (70, 110)
DURATION_BUCKETS = {1: (70, 110), 2: (160, 200), 3: (250, 290), 4: (340, 380)}


def duration_quarters(days: int | float | None) -> int | None:
    if days is None or (isinstance(days, float) and np.isnan(days)):
        return None
    for q, (lo, hi) in DURATION_BUCKETS.items():
        if lo <= days <= hi:
            return q
    return None


def parse_company_facts(payload: dict, availability_lag_days: int = 1) -> pd.DataFrame:
    """Flatten a companyfacts payload into rows for the mapped concepts."""
    cik = str(payload.get("cik", "")).zfill(10)
    rows = []
    for tax, concepts in payload.get("facts", {}).items():
        for concept, body in concepts.items():
            for unit, facts in body.get("units", {}).items():
                mapped = CONCEPT_TO_METRIC.get((tax, concept, unit))
                if mapped is None:
                    continue
                metric, _ = mapped
                for f in facts:
                    if "filed" not in f or "end" not in f or f.get("val") is None:
                        continue
                    rows.append((cik, metric, f"{tax}:{concept}", unit, f.get("start"), f["end"], f.get("fy"),
                                 f.get("fp"), f.get("form"), f.get("accn"), f["filed"], float(f["val"])))
    cols = ["cik", "metric", "concept", "unit", "period_start", "period_end", "fiscal_year", "fiscal_period",
            "form", "accn", "filed_date", "value"]
    df = pd.DataFrame(rows, columns=cols)
    if df.empty:
        return df.assign(duration_days=pd.Series(dtype="Int64"), availability_date=pd.Series(dtype="datetime64[ns]"))
    for c in ("period_start", "period_end", "filed_date"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df = df.dropna(subset=["period_end", "filed_date"])
    df["duration_days"] = (df["period_end"] - df["period_start"]).dt.days.astype("Int64")
    df["availability_date"] = df["filed_date"] + pd.Timedelta(days=availability_lag_days)
    # Amended filings sometimes duplicate identical keys; keep one row per primary key.
    df["period_start"] = df["period_start"].fillna(pd.Timestamp("1900-01-01"))  # instants: sentinel start
    df = df.drop_duplicates(subset=["cik", "concept", "unit", "period_start", "period_end", "accn"], keep="last")
    df["fiscal_year"] = pd.to_numeric(df["fiscal_year"], errors="coerce").astype("Int64")
    return df.reset_index(drop=True)


def pit_filter(facts: pd.DataFrame, as_of: pd.Timestamp | date) -> pd.DataFrame:
    """Facts observable on ``as_of``, one value per (metric, period): highest-priority concept, latest filing."""
    as_of = pd.Timestamp(as_of)
    f = facts[facts["availability_date"] <= as_of]
    if f.empty:
        return f
    if "priority" not in f:
        f = add_priority(f)
    f = f.sort_values(["metric", "period_start", "period_end", "priority", "availability_date"],
                      ascending=[True, True, True, True, False])
    return f.drop_duplicates(subset=["metric", "period_start", "period_end"], keep="first")


def add_priority(facts: pd.DataFrame) -> pd.DataFrame:
    if facts.empty:
        return facts.assign(priority=pd.Series(dtype=int))
    keys = list(zip(facts["concept"].str.split(":").str[0], facts["concept"].str.split(":", n=1).str[1],
                    facts["unit"], strict=False))
    return facts.assign(priority=[CONCEPT_TO_METRIC.get(k, (None, 99))[1] for k in keys])


@dataclass
class Quarter:
    end: pd.Timestamp
    value: float
    availability: pd.Timestamp


def discrete_quarters(flow: pd.DataFrame) -> dict[pd.Timestamp, Quarter]:
    """Derive discrete quarterly values from quarterly and year-to-date facts of one metric (already PIT)."""
    if flow.empty:
        return {}
    f = flow.copy()
    f["nq"] = f["duration_days"].map(lambda d: duration_quarters(None if pd.isna(d) else int(d)))
    f = f.dropna(subset=["nq"])
    by_start_end: dict[tuple, tuple[float, pd.Timestamp]] = {
        (r.period_start, r.period_end): (r.value, r.availability_date) for r in f.itertuples()
    }
    quarters: dict[pd.Timestamp, Quarter] = {}
    for r in f[f["nq"] == 1].itertuples():
        quarters[r.period_end] = Quarter(r.period_end, r.value, r.availability_date)
    # YTD differencing: YTD(n quarters ending E) - YTD(n-1 quarters, same start, ending ~E-91d)
    for n in (2, 3, 4):
        for r in f[f["nq"] == n].itertuples():
            if r.period_end in quarters:
                continue
            prev = None
            for (s, e), (v, a) in by_start_end.items():
                if s == r.period_start and duration_quarters((e - s).days) == n - 1 \
                        and 70 <= (r.period_end - e).days <= 110:
                    prev = (v, a)
                    break
            if prev is None and n == 4:
                # FY minus three discrete quarters inside the fiscal year
                inside = [q for q in quarters.values() if r.period_start < q.end < r.period_end - timedelta(days=45)]
                if len(inside) == 3:
                    prev = (sum(q.value for q in inside), max(q.availability for q in inside))
            if prev is not None:
                quarters[r.period_end] = Quarter(r.period_end, r.value - prev[0], max(r.availability_date, prev[1]))
    return quarters


def _find_quarter(quarters: dict[pd.Timestamp, Quarter], target: pd.Timestamp, tol: int = 25) -> Quarter | None:
    best, best_gap = None, tol + 1
    for end, q in quarters.items():
        gap = abs((end - target).days)
        if gap < best_gap:
            best, best_gap = q, gap
    return best


def ttm_at(quarters: dict[pd.Timestamp, Quarter], annual: pd.DataFrame, end: pd.Timestamp) -> float | None:
    """Trailing-twelve-month value ending at ``end`` (FY fact if it ends there, else 4 discrete quarters)."""
    if annual is not None and not annual.empty:
        fy = annual[(annual["period_end"] - end).abs() <= pd.Timedelta(days=10)]
        if not fy.empty:
            return float(fy.iloc[0]["value"])
    qs = [_find_quarter(quarters, end - pd.Timedelta(days=91 * k)) for k in range(4)]
    if any(q is None for q in qs) or len({q.end for q in qs}) < 4:
        return None
    return float(sum(q.value for q in qs))


def snapshot(facts: pd.DataFrame, as_of: pd.Timestamp) -> dict[str, float | pd.Timestamp | None]:
    """Point-in-time fundamental snapshot for one company as observable on ``as_of``."""
    pit = pit_filter(facts, as_of)
    out: dict[str, float | pd.Timestamp | None] = {}
    if pit.empty:
        return out
    out["_availability_date"] = pit["availability_date"].max()
    latest_end = None
    for metric, kind in METRIC_KIND.items():
        m = pit[pit["metric"] == metric]
        if m.empty:
            continue
        if kind == INSTANT:
            m = m.sort_values("period_end")
            last = m.iloc[-1]
            out[metric] = float(last["value"])
            out[f"{metric}__end"] = last["period_end"]
            yago = m[(m["period_end"] - (last["period_end"] - pd.Timedelta(days=365))).abs() <= pd.Timedelta(days=45)]
            if not yago.empty:
                out[f"{metric}__1y"] = float(yago.iloc[-1]["value"])
        elif kind == AVERAGE:
            q = m[m["duration_days"].between(*QUARTER_DAYS)].sort_values("period_end")
            if q.empty:
                q = m.sort_values("period_end")
            out[metric] = float(q.iloc[-1]["value"])
            yago = q[(q["period_end"] - (q.iloc[-1]["period_end"] - pd.Timedelta(days=365))).abs() <= pd.Timedelta(days=30)]
            if not yago.empty:
                out[f"{metric}__1y"] = float(yago.iloc[-1]["value"])
        else:
            quarters = discrete_quarters(m)
            annual = m[m["duration_days"].between(340, 380)]
            if not quarters and annual.empty:
                continue
            ends = sorted(set(quarters) | set(annual["period_end"]))
            end = ends[-1]
            latest_end = max(latest_end, end) if latest_end is not None else end
            out[f"{metric}__end"] = end
            for label, years in (("ttm", 0), ("ttm_1y", 1), ("ttm_2y", 2)):
                v = ttm_at(quarters, annual, end - pd.Timedelta(days=365 * years))
                if v is not None:
                    out[f"{metric}__{label}"] = v
            # most recent discrete quarter and the same quarter a year earlier (for acceleration/margins)
            q_last = quarters.get(end)
            if q_last is not None:
                out[f"{metric}__q"] = q_last.value
                q_yago = _find_quarter(quarters, end - pd.Timedelta(days=365))
                if q_yago is not None:
                    out[f"{metric}__q_1y"] = q_yago.value
                q_prev = _find_quarter(quarters, end - pd.Timedelta(days=91))
                if q_prev is not None:
                    out[f"{metric}__q_prev"] = q_prev.value
                    q_prev_yago = _find_quarter(quarters, end - pd.Timedelta(days=91 + 365))
                    if q_prev_yago is not None:
                        out[f"{metric}__q_prev_1y"] = q_prev_yago.value
    out["_period_end"] = latest_end
    return out


def snapshots_by_filing(facts: pd.DataFrame, min_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """One PIT snapshot per distinct availability date. Snapshot state only changes when a filing appears.

    ``min_date``: snapshots are only needed for rebalances on/after this date; the last snapshot before it is
    kept so the first rebalance still sees the then-current filing.
    """
    if facts.empty:
        return pd.DataFrame()
    facts = add_priority(facts)
    dates = sorted(pd.Timestamp(a) for a in facts["availability_date"].unique())
    if min_date is not None:
        before = [d for d in dates if d < min_date]
        dates = ([before[-1]] if before else []) + [d for d in dates if d >= min_date]
        # periods older than ~3.5 years before the first snapshot are irrelevant for TTM/growth metrics
        facts = facts[facts["period_end"] >= (dates[0] if dates else min_date) - pd.Timedelta(days=365 * 3 + 200)]
    rows = []
    for a in dates:
        snap = snapshot(facts, a)
        if snap:
            snap["snapshot_date"] = pd.Timestamp(a)
            rows.append(snap)
    return pd.DataFrame(rows)


def asof_snapshot(snapshots: pd.DataFrame, as_of: pd.Timestamp) -> pd.Series | None:
    """Latest snapshot whose availability date is on/before ``as_of`` (strict PIT guard)."""
    if snapshots is None or snapshots.empty:
        return None
    s = snapshots[snapshots["snapshot_date"] <= pd.Timestamp(as_of)]
    if s.empty:
        return None
    row = s.iloc[-1]
    assert row["_availability_date"] <= pd.Timestamp(as_of), "PIT violation: snapshot uses future filing"
    return row
