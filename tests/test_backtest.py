import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import Backtester, JevFeatures
from src.backtest.metrics import performance, segment
from src.backtest.research import objective_scores, pareto_front
from src.model.promotion import evaluate_promotion
from src.model.scoring import ModelConfig, ScoreCache
from src.pipeline.common import open_context, verify_configuration
from src.pipeline.research_run import generate_historical_jev

SYMS = [f"S{i:02d}" for i in range(12)]


def world(delist_after: int | None = 30):
    cal = pd.bdate_range("2023-01-02", periods=90)
    rng = np.random.default_rng(5)
    close = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, (90, 12)), axis=0)), index=cal, columns=SYMS)
    if delist_after is not None:
        close.iloc[delist_after:, 0] = np.nan  # S00 stops trading
    open_ = close * 1.001
    dates = [cal[5], cal[40], cal[75]]
    rows = []
    for d in dates:
        for j, s in enumerate(SYMS):
            if np.isnan(close.loc[d, s]):
                continue  # not trading -> not in the panel (not eligible)
            rows.append({"rebalance_date": d, "symbol": s, "base_eligible": True, "exclusion_reason": None,
                         "market_cap": 1e9, "adv20": 2e7, "sector_group": "technology",
                         "ret_6m": 1.0 - j * 0.05 if s != "S00" else 2.0, "ret_3m": 0.1 - j * 0.01, "mom_6_1": 0.2 - j * 0.01,
                         "mom_12_1": 0.3 - j * 0.02, "vol_60d": 0.3 + j * 0.01, "vol_20d": 0.3, "price_sma200": 0.05,
                         "sma50_sma200": 0.02})
    return ScoreCache(pd.DataFrame(rows)), open_, close


def cfg(**kw):
    base = dict(preset="momentum_only", min_market_cap=1e8, min_adv20=1e6, portfolio_size=3, weighting="equal",
                hold_buffer=1.5)
    base.update(kw)
    return ModelConfig(**base)


def test_delisted_holding_is_liquidated_at_last_close():
    cache, o, c = world(delist_after=30)
    res = Backtester(cache, o, c, initial_capital=10_000).run(cfg())
    sells = res.trades[(res.trades["symbol"] == "S00") & (res.trades["side"] == "SELL")]
    assert len(sells) == 1 and "delisted" in sells.iloc[0]["reason"]
    last_close = c["S00"].dropna().iloc[-1]
    assert sells.iloc[0]["price"] == pytest.approx(last_close * (1 - 0.001))  # slippage on the forced sale


def test_backtest_is_deterministic_and_costs_reduce_equity():
    cache, o, c = world()
    bt = Backtester(cache, o, c, initial_capital=10_000)
    a, b = bt.run(cfg()), bt.run(cfg())
    pd.testing.assert_series_equal(a.equity, b.equity)
    free = bt.run(cfg(cost_multiplier=0.0))
    assert free.equity.iloc[-1] > a.equity.iloc[-1]
    assert (a.trades["commission"] > 0).all() and (free.trades["commission"] == 0).all()


def test_fractional_positions_and_cash_accounting():
    cache, o, c = world(delist_after=None)
    res = Backtester(cache, o, c, initial_capital=10_000).run(cfg())
    buys = res.trades[res.trades["side"] == "BUY"]
    assert (buys["shares"] % 1 != 0).any()          # fractional shares used
    cash_rows = res.holdings[res.holdings["symbol"] == "__CASH__"]
    assert (cash_rows["value"] >= -1e-6).all()       # never negative cash


def test_jev_weight_without_jev_features_equals_quant_only():
    cache, o, c = world()
    bt = Backtester(cache, o, c, initial_capital=10_000, jev=None)
    pd.testing.assert_series_equal(bt.run(cfg(jev_weight=0.0)).equity, bt.run(cfg(jev_weight=0.3)).equity)


def test_jev_features_change_ranking_only_through_final_score():
    cache, o, c = world(delist_after=None)
    d = cache.dates[0]
    raw = np.full(12, 0.5)
    raw[6] = 0.95  # Jev strongly favours one mid-ranked name
    raw[5] = 0.45
    jf = pd.DataFrame({"rebalance_date": d, "symbol": SYMS, "jev_raw": raw, "jev_confidence": 0.5})
    bt = Backtester(cache, o, c, initial_capital=10_000, jev=JevFeatures(jf, "jfs_test"))
    r0, _ = bt.rank_at(cfg(jev_weight=0.0), d, [])
    r1, _ = bt.rank_at(cfg(jev_weight=0.3), d, [])
    assert r1.loc["S06", "rank"] < r0.loc["S06", "rank"]
    assert set(r0.index) == set(r1.index)
    assert (r0["quant_score"] == r1["quant_score"].reindex(r0.index)).all()  # Jev never alters the quant component


def test_metrics_basic():
    idx = pd.bdate_range("2022-01-03", periods=505)
    eq = pd.Series(10_000 * np.exp(np.linspace(0, np.log(1.21), 505)), index=idx)
    m = performance(eq)
    assert m["total_return"] == pytest.approx(0.21, rel=1e-6)
    assert m["cagr"] == pytest.approx(1.21 ** (1 / m["years"]) - 1, rel=1e-6)
    assert m["max_drawdown"] == pytest.approx(0.0)
    seg = segment(eq, idx[100], idx[200])
    assert seg.index[0] == idx[100] and seg.index[-1] == idx[200]


def test_objective_and_pareto():
    df = pd.DataFrame({"folds": [3, 3, 3, 1], "median_cagr": [0.3, 0.1, 0.2, 0.9],
                       "medium_horizon_return": [0.05, 0.02, 0.04, 0.2], "median_calmar": [1.5, 0.5, 1.0, 3],
                       "median_sharpe": [1.2, 0.4, 0.9, 2], "median_drawdown_quality": [-0.1, -0.2, -0.12, -0.05],
                       "worst_drawdown_quality": [-0.2, -0.4, -0.25, -0.1], "turnover": [2, 1, 3, 1],
                       "worst_fold_max_drawdown": [-0.2, -0.4, -0.25, -0.1]}, index=list("abcd"))
    w = {"median_cagr": 0.35, "medium_horizon_return": 0.15, "median_calmar": 0.15, "median_sharpe": 0.1,
         "median_drawdown_quality": 0.15, "worst_drawdown_quality": 0.1}
    s = objective_scores(df, w, 0.05, 2)
    assert s.idxmax() == "a" and s["d"] == -np.inf  # too few folds is never selected
    front = pareto_front(df, ["median_cagr", "worst_fold_max_drawdown"], ["turnover"])
    assert front["d"] and not front["a"] and not front["c"]  # d dominates on all three axes


def test_promotion_requires_material_improvement():
    inc = {"objective": 1.0, "fold_returns": [0.05, 0.04, 0.06], "worst_fold_max_drawdown": -0.15}
    small = {"objective": 1.1, "fold_returns": [0.06, 0.05, 0.07], "worst_fold_max_drawdown": -0.15}
    assert not evaluate_promotion(inc, small, None, pd.Timestamp("2024-06-30"))["promote"]
    big = {"objective": 1.6, "fold_returns": [0.08, 0.07, 0.05], "worst_fold_max_drawdown": -0.16}
    assert evaluate_promotion(inc, big, None, pd.Timestamp("2024-06-30"))["promote"]
    worse_dd = {**big, "worst_fold_max_drawdown": -0.30}
    assert not evaluate_promotion(inc, worse_dd, None, pd.Timestamp("2024-06-30"))["promote"]
    cooldown = evaluate_promotion(inc, big, pd.Timestamp("2024-05-31"), pd.Timestamp("2024-06-30"))
    assert not cooldown["promote"] and "cooldown" in cooldown["reason"]
    assert evaluate_promotion(None, small, None, pd.Timestamp("2024-06-30"))["promote"]  # bootstrap


def test_missing_jev_key_reports_unavailable_and_generates_nothing(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "")
    ctx = open_context()
    v = verify_configuration(ctx)
    assert "unavailable" in v["jev"]
    out = generate_historical_jev(ctx)
    assert out["status"] == "unavailable"
    assert ctx.con.execute("SELECT count(*) FROM jev_decisions").fetchone()[0] == 0
