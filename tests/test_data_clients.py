from datetime import date

import pandas as pd
import pytest

from src.data.fmp import FmpClient
from src.data.http import BudgetExhausted
from src.data.prices import infer_splits_from_shares, load_prices, split_factor_after
from src.data.sec import SecClient
from src.db.repo import RequestLog
from src.db.schema import connect
from tests.synthetic import fmp_transport, sec_transport


def test_fmp_bandwidth_limit_stops_cleanly(world, cache):
    con = connect(":memory:")
    fmp = FmpClient(transport=fmp_transport(world, bandwidth_exhausted=True), cache=cache)
    with pytest.raises(BudgetExhausted):
        fmp.historical_prices("QQQ", date(2023, 1, 1), date(2023, 2, 1))
    report = load_prices(con, fmp, ["QQQ", "SPY"], end=date(2023, 12, 29))
    assert "Bandwidth" in report["stopped_reason"] and report["loaded"] == 0
    assert con.execute("SELECT status FROM data_load_status WHERE key='QQQ'").fetchone()[0] == "pending"


def test_fmp_daily_budget_enforced(world, cache):
    con = connect(":memory:")
    rl = RequestLog(con)
    fmp = FmpClient(transport=fmp_transport(world), cache=cache, request_logger=rl,
                    calls_today=lambda: rl.live_calls_today("fmp"))
    fmp.daily_budget = 3
    report = load_prices(con, fmp, ["QQQ", "SPY", "XLK"], end=date(2023, 12, 29), fetch_dividend_adjusted=True)
    assert "budget" in report["stopped_reason"]
    assert rl.live_calls_today("fmp") == 3


def test_immutable_history_is_cached_not_refetched(world, cache):
    fmp = FmpClient(transport=fmp_transport(world), cache=cache)
    a = fmp.historical_prices("QQQ", date(2020, 1, 1), date(2020, 6, 30))
    n = len(world.fmp_calls)
    b = FmpClient(transport=fmp_transport(world), cache=cache).historical_prices("QQQ", date(2020, 1, 1), date(2020, 6, 30))
    assert a == b and len(world.fmp_calls) == n  # served from the raw cache


def test_incremental_price_load_chains_adjusted_history(world, cache):
    con = connect(":memory:")
    fmp = FmpClient(transport=fmp_transport(world), cache=cache)
    load_prices(con, fmp, ["QQQ"], end=date(2023, 6, 30))
    n1 = con.execute("SELECT count(*) FROM daily_prices").fetchone()[0]
    load_prices(con, fmp, ["QQQ"], end=date(2023, 12, 29))
    rows = con.execute("SELECT date, close, adj_close FROM daily_prices ORDER BY date").df()
    assert len(rows) > n1 and rows["date"].is_unique
    assert (rows["adj_close"] - rows["close"]).abs().max() < 1e-9  # no dividends -> no artificial jumps


def test_sec_requires_contact_user_agent(world, cache):
    with pytest.raises(Exception, match="SEC_USER_AGENT"):
        SecClient(user_agent="no-email-here", transport=sec_transport(world), cache=cache)
    sec = SecClient(transport=sec_transport(world), cache=cache)
    rows = sec.company_tickers_exchange()
    assert rows and all(r["exchange"] == "Nasdaq" for r in rows)


def test_split_factor_and_inference():
    splits = pd.DataFrame({"symbol": ["A"], "date": [pd.Timestamp("2021-07-15")], "ratio": [2.0]})
    assert split_factor_after(splits, "A", pd.Timestamp("2021-06-30")) == 2.0
    assert split_factor_after(splits, "A", pd.Timestamp("2021-08-01")) == 1.0
    shares = pd.DataFrame({"period_end": pd.to_datetime(["2021-03-31", "2021-06-30", "2021-09-30"]),
                           "value": [100.0, 101.0, 202.0]})
    assert infer_splits_from_shares(shares) == [(pd.Timestamp("2021-09-30"), 2.0)]
