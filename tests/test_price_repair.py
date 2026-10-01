"""Adjusted-price breaks: ingestion no longer splices scales, stored breaks are repaired, labels drop glitches."""
import duckdb
import numpy as np
import pandas as pd
import pytest

from src.data.prices import _prices_frame, adjusted_breaks, repair_adjusted, repair_adjusted_series
from src.db.schema import init_schema
from src.features.momentum import forward_returns


def series(n=10):
    close = pd.Series(np.linspace(10, 12, n))
    return close


def test_break_where_adjusted_series_jumps_is_repaired_to_close_return():
    close = series()
    adj = close * 0.01  # wrong scale before the break (vendor glitch, like ESPR)
    adj.iloc[6:] = close.iloc[6:]
    new, br = repair_adjusted_series(close, adj)
    assert list(br.index) == [6] and br.iloc[0] == pytest.approx(100.0)
    np.testing.assert_allclose((new / new.shift(1)).iloc[1:], (close / close.shift(1)).iloc[1:])
    assert new.iloc[-1] == pytest.approx(adj.iloc[-1])  # latest base kept


def test_small_dividend_steps_and_spinoff_style_close_drops_are_not_breaks():
    close = series()
    adj = close.copy()
    adj.iloc[:5] *= 0.98  # 2% dividend
    assert (adjusted_breaks(close, adj) == 1.0).all()
    close2 = close.copy()
    close2.iloc[5:] *= 0.5  # close halves (spin-off), adjusted series smooth
    adj2 = close.copy()
    assert (adjusted_breaks(close2, adj2) == 1.0).all()


def test_ingestion_carries_ratio_across_missing_adjusted_dates():
    raw = [{"date": f"2024-01-0{d}", "open": 10, "high": 10, "low": 10, "close": 10.0 + d, "volume": 1}
           for d in range(1, 6)]
    adjusted = [{"date": f"2024-01-0{d}", "adjClose": (10.0 + d) * 0.5} for d in (1, 2, 3)]  # last two missing
    df = _prices_frame("X", raw, adjusted)
    np.testing.assert_allclose(df["adj_close"] / df["close"], 0.5)


def test_repair_adjusted_in_db_is_idempotent_and_logged(tmp_path):
    con = duckdb.connect(str(tmp_path / "t.duckdb"))
    init_schema(con)
    d = pd.bdate_range("2024-01-01", periods=10).date
    close = np.linspace(10, 12, 10)
    adj = close * 0.01
    adj[6:] = close[6:]
    con.register("_p", pd.DataFrame({"symbol": "BAD", "date": d, "open": close, "high": close, "low": close,
                                     "close": close, "adj_close": adj, "volume": 1.0, "source": "t",
                                     "loaded_at": pd.Timestamp("2026-01-01")}))
    con.execute("INSERT INTO daily_prices SELECT * FROM _p")
    rep = repair_adjusted(con)
    assert rep["symbols_repaired"] == 1 and rep["breaks"] == 1
    assert repair_adjusted(con)["breaks"] == 0
    assert con.execute("SELECT count(*) FROM price_repairs").fetchone()[0] == 1
    fixed = con.execute("SELECT adj_close FROM daily_prices ORDER BY date").df()["adj_close"].to_numpy()
    np.testing.assert_allclose(fixed[1:] / fixed[:-1], close[1:] / close[:-1])


def test_forward_return_labels_drop_glitches():
    idx = pd.bdate_range("2024-01-01", periods=30)
    close = pd.DataFrame({"OK": np.linspace(10, 11, 30), "GLITCH": np.r_[np.full(15, 0.02), np.full(15, 3.2)]},
                         index=idx)
    fr = forward_returns(close, [idx[0]], 21)
    assert list(fr["symbol"]) == ["OK"]
