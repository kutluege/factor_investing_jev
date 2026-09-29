import pandas as pd
import pytest

from src.portfolio.book import CostModel, Order, Portfolio, SimulatedBroker
from src.portfolio.signals import BUY, HOLD, SELL, WAIT, SignalRules, decide
from src.portfolio.weights import cap_weights, target_weights

D = pd.Timestamp("2024-01-31")


def test_fractional_shares_and_costs():
    costs = CostModel(commission_per_trade_usd=1.0, slippage_bps=10, transaction_cost_bps=5)
    broker = SimulatedBroker(costs)
    p = Portfolio(cash=10_000)
    fill = broker.execute(Order("AAA", "BUY", 12.3456, "entry"), 100.0, D)
    assert fill.price == pytest.approx(100.1)
    assert fill.shares == pytest.approx(12.3456)
    p.apply(fill)
    expected_cash = 10_000 - 12.3456 * 100.1 - 1.0 - 12.3456 * 100.1 * 0.0005
    assert p.cash == pytest.approx(expected_cash)
    assert p.positions["AAA"].shares == pytest.approx(12.3456)
    sell = broker.execute(Order("AAA", "SELL", 12.3456, "exit"), 110.0, D + pd.Timedelta(days=30))
    p.apply(sell)
    assert "AAA" not in p.positions
    assert sell.price == pytest.approx(110 * 0.999)
    assert p.cash == pytest.approx(expected_cash + 12.3456 * 109.89 - 1.0 - 12.3456 * 109.89 * 0.0005)


def test_zero_cost_model_is_explicit():
    broker = SimulatedBroker(CostModel(0, 0, 0))
    f = broker.execute(Order("A", "BUY", 1, "x"), 50.0, D)
    assert f.price == 50.0 and f.total_cost == 0.0


def test_insufficient_cash_and_oversell_rejected():
    p = Portfolio(cash=100)
    f = SimulatedBroker(CostModel()).execute(Order("A", "BUY", 10, "x"), 50.0, D)
    with pytest.raises(ValueError):
        p.apply(f)
    with pytest.raises(ValueError):
        p.apply(SimulatedBroker(CostModel()).execute(Order("A", "SELL", 1, "x"), 50.0, D))


def test_equity_and_weights():
    p = Portfolio(cash=1000)
    p.apply(SimulatedBroker(CostModel(0, 0, 0)).execute(Order("A", "BUY", 10, "x"), 100.0, D))
    assert p.equity({"A": 110.0}) == pytest.approx(1100.0)
    assert p.weights({"A": 110.0})["A"] == pytest.approx(1.0)


def test_weighting_methods_and_cap():
    score = pd.Series({"A": 3.0, "B": 2.0, "C": 1.0})
    vol = pd.Series({"A": 0.8, "B": 0.4, "C": 0.2})
    assert target_weights(list("ABC"), "equal", score, vol, 1.0).tolist() == pytest.approx([1 / 3] * 3)
    ivol = target_weights(list("ABC"), "inverse_vol", score, vol, 1.0)
    assert ivol["C"] > ivol["B"] > ivol["A"]
    sw = target_weights(list("ABC"), "score", score, vol, 1.0)
    assert sw["A"] > sw["B"] > sw["C"]
    capped = cap_weights(pd.Series({"A": 10.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0}), 0.25)
    assert capped.max() <= 0.25 + 1e-9 and capped.sum() == pytest.approx(1.0)


def ranking(n=30):
    df = pd.DataFrame({"rank": range(1, n + 1), "final_score": [n - i for i in range(n)], "vol60_pct": 0.5,
                       "price_sma200": 0.05, "sma50_sma200": 0.02, "pct_quality": 0.6,
                       "pct_fundamental_momentum": 0.6}, index=[f"S{i:02d}" for i in range(1, n + 1)])
    return df


def pos(sym):
    from src.portfolio.book import Position
    return Position(sym, 1.0, D - pd.Timedelta(days=90), 10.0, 10.0)


def by_symbol(decisions):
    return {d.symbol: d for d in decisions}


def test_hysteresis_keeps_holding_inside_buffer():
    rules = SignalRules(portfolio_size=5, hold_buffer=1.5)
    r = ranking()
    held = {"S07": pos("S07")}          # rank 7: outside N=5 but inside 7.5 buffer
    dec = by_symbol(decide(r, held, D, rules))
    assert dec["S07"].signal == HOLD
    rules_tight = SignalRules(portfolio_size=5, hold_buffer=1.0)
    dec2 = by_symbol(decide(r, held, D, rules_tight))
    assert dec2["S07"].signal == SELL and "rank_deterioration" in dec2["S07"].reasons[0]


def test_buy_fills_capacity_then_wait():
    rules = SignalRules(portfolio_size=5, hold_buffer=1.5, replace_rank_fraction=0.0)
    dec = by_symbol(decide(ranking(), {}, D, rules))
    assert [s for s, d in dec.items() if d.signal == BUY] == ["S01", "S02", "S03", "S04", "S05"]
    assert dec["S06"].signal == WAIT and "near cutoff" in dec["S06"].reasons[0]
    assert "S11" not in dec  # beyond wait window (2N)


def test_replacement_by_strong_candidate():
    rules = SignalRules(portfolio_size=3, hold_buffer=2.0, replace_rank_fraction=0.67)
    r = ranking()
    held = {"S04": pos("S04"), "S05": pos("S05"), "S06": pos("S06")}  # all inside buffer 6 but outside top 3
    dec = by_symbol(decide(r, held, D, rules))
    assert dec["S01"].signal == BUY          # rank 1 <= 3*0.67 -> replaces the weakest holding
    assert dec["S06"].signal == SELL and "replaced_by_better_candidate" in dec["S06"].reasons[0]
    assert dec["S04"].signal == HOLD


def test_hard_exits_override_rank():
    rules = SignalRules(portfolio_size=5, hold_buffer=2.0)
    r = ranking()
    r.loc["S01", ["price_sma200", "sma50_sma200"]] = [-0.2, -0.05]
    r.loc["S02", ["pct_quality", "pct_fundamental_momentum"]] = [0.05, 0.05]
    dec = by_symbol(decide(r, {"S01": pos("S01"), "S02": pos("S02"), "GONE": pos("GONE")}, D, rules,
                           exclusion_reasons={"GONE": "delisted"}))
    assert dec["S01"].signal == SELL and "technical_breakdown" in dec["S01"].reasons[0]
    assert dec["S02"].signal == SELL and "fundamental_deterioration" in dec["S02"].reasons[0]
    assert dec["GONE"].signal == SELL and "delisted" in dec["GONE"].reasons[0]


def test_entry_gate_blocks_buy_even_with_top_rank():
    """Hard risk gates cannot be overridden by score (and therefore not by Jev)."""
    rules = SignalRules(portfolio_size=3, hold_buffer=1.5, max_vol60_percentile=0.9)
    r = ranking()
    r.loc["S01", "vol60_pct"] = 0.99
    dec = by_symbol(decide(r, {}, D, rules))
    assert dec["S01"].signal == WAIT and "gate:excessive_volatility" in dec["S01"].reasons
    assert dec["S04"].signal == BUY  # next eligible name takes the slot
