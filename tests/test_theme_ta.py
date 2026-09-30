"""T7 TA layer end to end: rules file, indicator table (no look-ahead), journal round trips and evaluation."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.config import PROJECT_ROOT, load_config
from src.themes.ta import (
    evaluate_journal,
    evaluation_markdown,
    indicator_table,
    load_rules,
    net_return,
    round_trips,
)

RULES = load_rules(PROJECT_ROOT / "research" / "ta" / "rules.yaml")
COSTS = load_config("backtest")["costs"]


def prices(n=500, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-01", periods=n)
    trend = np.linspace(0, 0.8, n)
    c = pd.DataFrame({s: 50 * np.exp(trend * k + np.cumsum(rng.normal(0, 0.012, n)))
                      for s, k in (("UP", 1.0), ("FLAT", 0.0))}, index=idx)
    o = c.shift(1).fillna(c.iloc[0]) * (1 + rng.normal(0, 0.002, c.shape))
    return o, c * 1.01, c * 0.99, c


def test_rules_file_is_default_and_not_optimized():
    assert RULES["status"] == "default_not_optimized"
    assert set(RULES["rules"]) == {"golden_cross_50_200", "pullback_to_50d", "trailing_stop_atr"}


def test_indicator_table_columns_and_no_lookahead():
    o, h, lo, c = prices()
    at = c.index[400]
    t = indicator_table(h, lo, c, ["UP", "FLAT", "MISSING"], at, RULES, entries={"UP": c.index[380]})
    assert list(t.index) == ["UP", "FLAT"]
    for col in ("sma50", "sma200", "rsi14", "macd", "adx14", "atr14", "bb_upper", "golden_cross_50_200",
                "pullback_to_50d", "trailing_stop_atr", "stop_hit"):
        assert col in t.columns
    assert t.at["UP", "trailing_stop_atr"] < c.loc[c.index[380]:at, "UP"].max()
    h2, lo2, c2 = h.copy(), lo.copy(), c.copy()
    for m in (h2, lo2, c2):
        m.loc[m.index > at] *= 5
    pd.testing.assert_frame_equal(t, indicator_table(h2, lo2, c2, ["UP", "FLAT"], at, RULES,
                                                     entries={"UP": c.index[380]}))


JOURNAL = pd.DataFrame([
    ["2024-06-10", "UP", "BUY", 0, 100, "pullback_to_50d", "rules_v1", 0, "test"],
    ["2024-07-15", "UP", "SELL", 0, 100, "trailing_stop_atr", "rules_v1", 0, "test"],
    ["2024-08-05", "FLAT", "BUY", 0, 50, "golden_cross_50_200", "rules_v1", 0, "test"],
    ["2024-09-16", "FLAT", "SELL", 0, 20, "trailing_stop_atr", "rules_v1", 0, "partial"],
    ["2024-10-01", "FLAT", "SELL", 0, 30, "trailing_stop_atr", "rules_v1", 0, "rest"],
    ["2024-11-04", "UP", "BUY", 0, 10, "golden_cross_50_200", "rules_v1", 0, "still open"],
], columns=["date", "symbol", "action", "price", "shares", "rule_id", "rule_version", "stop_level", "reason"])


def journal_with_prices(c):
    j = JOURNAL.copy()
    j["price"] = [float(c.loc[pd.Timestamp(d), s]) for d, s in zip(j["date"], j["symbol"], strict=True)]
    return j


def test_round_trips_fifo_partial_and_open_lots():
    _, _, _, c = prices()
    trips, opens = round_trips(journal_with_prices(c))
    assert len(trips) == 3 and trips["shares"].tolist() == [100, 20, 30]
    assert len(opens) == 1 and opens.iloc[0]["symbol"] == "UP"


def test_evaluation_end_to_end(tmp_path: Path):
    o, _, _, c = prices()
    j = journal_with_prices(c)
    path = tmp_path / "journal.csv"
    j.to_csv(path, index=False)
    ev = evaluate_journal(pd.read_csv(path), o, c, COSTS)
    t = ev["table"]
    first = t.iloc[0]
    pnl, ret = net_return(first.entry_price, first.exit_price, 100, COSTS)
    assert first.pnl == pytest.approx(pnl) and first.net_return == pytest.approx(ret)
    june_open = float(o.loc["2024-06"].iloc[0]["UP"])
    assert first.month_start_price == pytest.approx(june_open)
    assert first.ta_contribution == pytest.approx(ret - net_return(june_open, first.exit_price, 100, COSTS)[1])
    assert 0 <= ev["base_rate"] <= 1 and ev["trades"] == 3 and ev["open_lots"] == 1
    wins, losses = t.loc[t.pnl > 0, "pnl"].sum(), -t.loc[t.pnl <= 0, "pnl"].sum()
    assert ev["profit_factor"] == pytest.approx(wins / losses if losses else np.inf)
    assert "ta_contribution_ci95" not in ev  # fewer than 50 trades
    md = evaluation_markdown(ev, RULES["version"])
    assert "Taban oran" in md and "yetersiz örnek" in md
