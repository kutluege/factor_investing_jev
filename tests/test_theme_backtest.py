"""Theme portfolio (§8): selection rules, targets, costless theme index, backtest mechanics, success criteria."""
import numpy as np
import pandas as pd
import pytest

from src.portfolio.rebalance import select_theme, theme_targets
from src.themes.backtest import ThemeBacktester, period_returns, success_table, theme_indices
from src.themes.config import load_themes_config

CFG = load_themes_config()


def ranked(n=30, subs=("a", "b")) -> pd.DataFrame:
    return pd.DataFrame({"score": np.linspace(3, -3, n), "subtheme": [subs[i % len(subs)] for i in range(n)]},
                        index=[f"S{i:02d}" for i in range(n)])


def test_hysteresis_keeps_held_within_buffer_and_sells_outside():
    r = ranked()
    sig = select_theme(r, held={"S19", "S27"}, n_picks=8, hold_buffer=3.0, max_subtheme_share=0.5, blocked=set())
    assert sig["S19"] == "HOLD"          # rank 20 <= 24
    assert sig["S27"] == "SELL"          # rank 28 > 24
    assert sum(v in ("HOLD", "BUY") for v in sig.values()) == 8
    assert sum(v == "WAIT" for v in sig.values()) == 5


def test_subtheme_cap_and_entry_block():
    r = ranked(subs=("a",))
    r.loc[["S20", "S21", "S22", "S23"], "subtheme"] = "b"
    sig = select_theme(r, held=set(), n_picks=8, hold_buffer=3.0, max_subtheme_share=0.5, blocked={"S00"})
    picks = [s for s, v in sig.items() if v == "BUY"]
    assert "S00" not in picks and sig.get("S00") == "WAIT"
    assert (r.loc[picks, "subtheme"] == "a").sum() == 4 and len(picks) == 8
    single = select_theme(ranked(subs=("a",)), held=set(), n_picks=7, hold_buffer=3.0, max_subtheme_share=0.5,
                          blocked=set())
    assert sum(v == "BUY" for v in single.values()) == 7  # one subtheme only: no cap
    odd = select_theme(ranked(), held=set(), n_picks=7, hold_buffer=3.0, max_subtheme_share=0.5, blocked=set())
    assert sum(v == "BUY" for v in odd.values()) == 7  # ceil(3.5) = 4 + 3
    held_blocked = select_theme(r, held={"S00"}, n_picks=8, hold_buffer=3.0, max_subtheme_share=0.5, blocked={"S00"})
    assert held_blocked["S00"] == "HOLD"  # the volatility block applies to entries only


def test_theme_targets_equal_weight_and_cap():
    w = theme_targets({"robotics": ["A", "B"], "energy": ["C"]}, {"robotics": 0.4, "energy": 0.6},
                      {"robotics": 8, "energy": 2}, cap=0.08)
    assert w["A"] == pytest.approx(0.05) and w["C"] == pytest.approx(0.08)  # 0.6/2 = 0.30 capped at 8%
    assert w.sum() == pytest.approx(0.18)  # unfilled slots stay in cash


def test_period_returns_with_delisting_haircut():
    idx = pd.bdate_range("2020-01-01", periods=6)
    close = pd.DataFrame({"A": [10, 11, 12, 12, 12, 13.0], "B": [10, 10, 5, np.nan, np.nan, np.nan]}, index=idx)
    r = period_returns(close, {idx[0]: ["A", "B"]}, [idx[0], idx[5]], haircut=0.3)
    assert r.iloc[0] == pytest.approx(((13 / 10 - 1) + (5 * 0.7 / 10 - 1)) / 2)


def synthetic(seed=0, months=36, n=30):
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2015-01-01", periods=months * 21 + 30)
    syms = [f"{t[:3]}{i}" for t in ("robotics", "biotech", "energy") for i in range(n)]
    rets = rng.normal(0.0003, 0.015, (len(days), len(syms)))
    close = pd.DataFrame(100 * np.exp(np.cumsum(rets, axis=0)), index=days, columns=syms)
    open_ = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, 0.002, close.shape))
    dates = list(pd.Series(days, index=days).groupby([days.year, days.month]).max())[:-1]
    rows = []
    for d in dates:
        for s in syms:
            t = {"rob": "robotics", "bio": "biotech", "ene": "energy"}[s[:3]]
            rows.append({"rebalance_date": d, "symbol": s, "theme": t, "subtheme": "x" if int(s[3:]) % 2 else "y",
                         "stage": "profitable", "vol_60d": rng.uniform(0.2, 0.6), "spread_est": 0.002,
                         "eligible": True})
    panel = pd.DataFrame(rows)
    scores = panel[["rebalance_date", "symbol"]].assign(score=rng.normal(size=len(panel)))
    return panel, scores, open_, close, dates


def test_backtest_runs_invests_and_costs_hurt():
    panel, scores, o, c, dates = synthetic()
    bt = ThemeBacktester(panel, scores, CFG, o, c)
    r1, r2 = bt.run(1.0), bt.run(2.0)
    assert len(r1.trades) > 0 and r1.equity.iloc[-1] > 0
    sig = r1.signals
    assert set(sig["signal"]) <= {"BUY", "HOLD", "SELL", "WAIT"}
    first = sig[sig["rebalance_date"] == dates[0]]
    n_expected = sum(t.n_picks for t in CFG.themes.values() if t.enabled)
    blocked = int(np.ceil(0.03 * 90))
    assert n_expected - blocked <= (first["signal"] == "BUY").sum() <= n_expected
    assert r2.equity.iloc[-1] < r1.equity.iloc[-1]


def test_backtest_prefix_unchanged_by_future_prices():
    panel, scores, o, c, dates = synthetic(seed=1)
    cut = dates[12]
    base = ThemeBacktester(panel, scores, CFG, o, c).run().equity
    o2, c2 = o.copy(), c.copy()
    later = c2.index > cut + pd.Timedelta(days=3)
    o2.loc[later] *= 3.0
    c2.loc[later] *= 3.0
    p2 = panel[panel["rebalance_date"] <= cut]
    alt = ThemeBacktester(p2, scores, CFG, o2, c2).run().equity
    common = base.index[base.index <= cut]
    pd.testing.assert_series_equal(base.loc[common], alt.loc[common])


def test_theme_index_and_success_table():
    panel, _, _, c, dates = synthetic(seed=2)
    idx = theme_indices(panel, c, CFG, dates, 0.3)
    assert {"robotics", "biotech", "energy", "composite"} <= set(idx.columns)
    port = idx["composite"] + 0.002
    t = success_table(port, idx["composite"], port - 0.001, [["2015-01", "2015-12"], ["2016-01", "2016-12"],
                                                             ["2017-01", "2017-12"]])
    assert t["criteria"]["c1_subperiods"] and t["criteria"]["c3_costs_2x"] and t["criteria"]["passed"]
    bad = success_table(idx["composite"] - 0.01, idx["composite"], idx["composite"] - 0.02,
                        [["2015-01", "2015-12"], ["2016-01", "2016-12"], ["2017-01", "2017-12"]])
    assert not bad["criteria"]["passed"]


def test_shortlist_overrides_and_evidence(tmp_path):
    from src.themes.shortlist import build_shortlist, load_overrides, shortlist_markdown
    panel, scores, _, _, dates = synthetic(seed=3)
    d = dates[-1]
    cross = panel[panel["rebalance_date"] == d].merge(scores, on=["rebalance_date", "symbol"]).set_index("symbol")
    cross["grp_momentum"] = cross["score"]
    top = cross[cross["theme"] == "robotics"]["score"].idxmax()
    low = cross[cross["theme"] == "robotics"]["score"].idxmin()
    f = tmp_path / "ov.yaml"
    f.write_text(f"exclude: [{top}]\ninclude: [{low}]\n", encoding="utf-8")
    ov = load_overrides(f)
    ev = pd.DataFrame({"method": ["keywords"], "hits": [7], "matched": ['{"robot": 7}'], "filing_accession": ["a"]},
                      index=[low])
    sl = build_shortlist(cross, CFG, {}, ev, ov).set_index("symbol")
    assert sl.at[top, "signal"] == "EXCLUDED" and sl.at[low, "signal"] == "BUY"
    assert sl.at[low, "override"] == "include" and sl.at[low, "evidence_hits"] == 7
    assert (sl["signal"] == "WAIT").sum() > 0
    assert "Tema seçim listesi" in shortlist_markdown(sl.reset_index(), d, CFG)
    assert load_overrides(tmp_path / "missing.yaml") == {"include": set(), "exclude": set()}
