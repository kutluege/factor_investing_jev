"""themes v2: tilt construction, fast engine sanity, score recomputation, and the overfitting-measurement protocol."""
import numpy as np
import pandas as pd
import pytest

from src.config import load_config
from src.portfolio.rebalance import partial_rebalance, theme_tilt_weights
from src.themes.config import load_themes_config
from src.themes.scoring import score_panel
from src.themes.search import (
    PeriodData,
    ScoreInputs,
    SearchConfig,
    evaluate_search,
    nested_walk_forward,
    sample_configs,
    select_best,
    simulate,
)

CFG = load_themes_config()
COSTS = load_config("backtest")["costs"]
FACTORS = sorted({f.name for fs in CFG.factor_groups.values() for f in fs})


def test_tilt_weights_budget_cap_and_index_replica():
    s = pd.Series(np.linspace(2, -2, 20), index=[f"S{i}" for i in range(20)])
    eq = theme_tilt_weights(s, 0.4, 0.0, 1.0, 0.08)
    assert eq.sum() == pytest.approx(0.4) and np.allclose(eq, 0.02)
    tilt = theme_tilt_weights(s, 0.4, 1.0, 0.5, 0.08, blocked={"S0"})
    assert tilt.sum() == pytest.approx(0.4) and "S0" not in tilt.index and len(tilt) == 10
    assert tilt.max() <= 0.08 + 1e-12 and tilt["S1"] > tilt["S9"]
    assert theme_tilt_weights(pd.Series(dtype=float), 0.4, 1, 1, 0.08).empty


def test_partial_rebalance_moves_halfway_and_sells_leavers():
    cur = pd.Series({"A": 0.2, "B": 0.2})
    tgt = pd.Series({"A": 0.4, "C": 0.2})
    out = partial_rebalance(cur, tgt, 0.5)
    assert out["A"] == pytest.approx(0.3) and out["C"] == pytest.approx(0.1) and "B" not in out.index


def synthetic(seed=0, months=40, n=30):
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2012-01-02", periods=months * 21 + 40)
    syms = [f"{t[:3].upper()}{i}" for t in ("robotics", "biotech", "energy") for i in range(n)]
    close = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.015, (len(days), len(syms))), axis=0)),
                         index=days, columns=syms)
    dates = list(pd.Series(days, index=days).groupby([days.year, days.month]).max())[:-1]
    rows = []
    for d in dates:
        for s in syms:
            t = {"ROB": "robotics", "BIO": "biotech", "ENE": "energy"}[s[:3]]
            row = {"rebalance_date": d, "symbol": s, "theme": t, "subtheme": {"robotics": "industrial_automation",
                   "biotech": "biotech_all", "energy": "oil_gas"}[t],
                   "stage": "commercial" if t == "biotech" else "profitable", "vol_60d": rng.uniform(0.2, 0.6),
                   "spread_est": 0.002, "eligible": True}
            row.update({f: rng.normal() for f in FACTORS})
            rows.append(row)
    panel = pd.DataFrame(rows)
    return panel, close, dates


@pytest.fixture(scope="module")
def world():
    panel, close, dates = synthetic()
    scores = score_panel(panel, CFG)
    si = ScoreInputs(panel, scores, CFG)
    rf = pd.Series(0.0, index=close.index)
    pdata = PeriodData(close, dates, pd.Series(dtype=float), rf, panel[panel["eligible"]], CFG, COSTS)
    return panel, scores, si, pdata


def test_recomputed_scores_match_scoring_module_with_unit_weights(world):
    panel, scores, si, _ = world
    s = si.scores({g: 1.0 for g in si.groups})
    ref = si.df[["rebalance_date", "symbol"]].merge(scores[["rebalance_date", "symbol", "score"]], how="left")
    np.testing.assert_allclose(s.to_numpy(), ref["score"].to_numpy(), atol=1e-9, equal_nan=True)


def test_index_replica_tracks_benchmark_minus_costs(world):
    _, _, si, pdata = world
    budgets = tuple(sorted(CFG.enabled_weights().items()))
    replica = SearchConfig(tuple((g, 1.0) for g in si.groups), 0.0, 1.0, budgets, 1.0, 1, 0.0)
    out = simulate(replica, si, pdata, position_cap=0.08)
    gap = (out["gross"] - out["benchmark"]).iloc[1:]  # drifted vs re-equal-weighted: small
    assert gap.abs().mean() < 0.002
    assert out["invested"].min() > 0.999 and (out["cost"] > 0).all()


def test_sampling_is_seeded_and_never_drops_a_group():
    a = sample_configs(["x", "y"], ["robotics", "biotech", "energy"], CFG.enabled_weights(), 30, seed=1)
    b = sample_configs(["x", "y"], ["robotics", "biotech", "energy"], CFG.enabled_weights(), 30, seed=1)
    assert [c.key for c in a] == [c.key for c in b] and len({c.key for c in a}) == 30
    assert all(m > 0 for c in a for _, m in c.group_mult)
    assert all(abs(sum(dict(c.budgets).values()) - 1) < 0.01 for c in a)


def contrib_matrix(seed=2, T=150, N=20):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2011-07-31", periods=T, freq="ME")
    return pd.DataFrame(rng.normal(0.0, 0.02, (T, N)), index=idx, columns=[f"c{i}" for i in range(N)])


def test_holdout_isolation_selection_ignores_holdout_months():
    c = contrib_matrix()
    design = pd.Series(c.index <= pd.Timestamp("2020-12-31"), index=c.index)
    best = select_best(c, design)
    c2 = c.copy()
    c2.loc[~design.to_numpy()] = np.random.default_rng(9).normal(0.5, 0.3, c2.loc[~design.to_numpy()].shape)
    assert select_best(c2, design) == best
    ev1 = evaluate_search(c, pd.Timestamp("2020-12-31"), pd.Timestamp("2011-07-31"), 2016)
    ev2 = evaluate_search(c2, pd.Timestamp("2020-12-31"), pd.Timestamp("2011-07-31"), 2016)
    assert ev1["selected"] == ev2["selected"] and ev1["design_ir"] == pytest.approx(ev2["design_ir"])


def test_nested_walk_forward_uses_only_prior_years():
    c = contrib_matrix(T=120)
    wf, picks = nested_walk_forward(c, 2015, pd.Timestamp("2011-07-31"))
    for p in picks:
        y = p["year"]
        c2 = c.copy()
        c2.loc[c2.index >= pd.Timestamp(f"{y}-01-01")] *= -5  # tamper with the test year and later
        _, picks2 = nested_walk_forward(c2, 2015, pd.Timestamp("2011-07-31"))
        assert next(q["config"] for q in picks2 if q["year"] == y) == p["config"]
    assert len(wf) == sum(1 for d in c.index if d.year >= 2015)


def test_pbo_flags_pure_noise_search():
    ev = evaluate_search(contrib_matrix(T=180, N=40), pd.Timestamp("2020-12-31"), pd.Timestamp("2011-07-31"), 2016)
    assert ev["pbo"]["pbo"] > 0.3  # selecting among noise does not persist out of sample
    assert ev["dsr_full_sample_best"]["dsr"] < 0.95
