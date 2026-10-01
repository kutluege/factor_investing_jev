"""themes_v1 factors: unit tests + leakage-injection tests (future data must not change past values)."""
import numpy as np
import pandas as pd
import pytest

from src.features.fundamentals import asof_join_snapshots, compute_fundamental_features
from src.features.theme_features import oil_beta_trend_at, profitable_growth, stage_flags

D = pd.Timestamp("2024-01-31")


def snap(**kw) -> pd.DataFrame:
    base = {"operating_cf__ttm": 30.0, "capex__ttm": 10.0, "total_assets": 200.0, "revenue__ttm": 100.0,
            "operating_income__ttm": 20.0, "depreciation__ttm": 5.0, "long_term_debt": 60.0, "cash": 10.0,
            "shares_outstanding": 10.0}
    base.update(kw)
    return pd.DataFrame([base], index=["X"])


def feats(s: pd.DataFrame) -> pd.Series:
    f, _ = compute_fundamental_features(s, pd.Series({"X": 10.0}), None, D)
    return f.loc["X"]


def test_capex_at_and_net_debt_ebitda_definitions():
    f = feats(snap())
    assert f["capex_at"] == pytest.approx(10 / 200)
    assert f["net_debt_ebitda"] == pytest.approx((60 - 10) / (20 + 5))
    assert f["fcf_margin"] == pytest.approx((30 - 10) / 100)
    assert f["ocf_ttm"] == 30 and f["revenue_ttm"] == 100


def test_net_debt_ebitda_nan_when_ebitda_not_positive():
    assert np.isnan(feats(snap(operating_income__ttm=-10.0, depreciation__ttm=5.0))["net_debt_ebitda"])


def test_stage_flags():
    ocf = pd.Series({"A": 5.0, "B": -1.0, "C": 5.0, "D": -2.0, "E": np.nan})
    rev = pd.Series({"A": 100.0, "B": 10.0, "C": 20e6, "D": 900e6, "E": np.nan})
    theme = pd.Series({"A": "robotics", "B": "energy", "C": "biotech", "D": "biotech", "E": "robotics"})
    st = stage_flags(ocf, rev, theme, 50e6)
    assert st.to_dict() == {"A": "profitable", "B": "pre_profit", "C": "clinical", "D": "clinical",
                            "E": "pre_profit"}
    st2 = stage_flags(pd.Series({"F": 5.0}), pd.Series({"F": 80e6}), pd.Series({"F": "biotech"}), 50e6)
    assert st2["F"] == "commercial"


def test_profitable_growth_only_for_profitable():
    st = pd.Series({"A": "profitable", "B": "profitable", "C": "pre_profit"})
    pg = profitable_growth(pd.Series({"A": 0.5, "B": 0.1, "C": 9.0}), pd.Series({"A": 0.2, "B": 0.1, "C": 0.9}), st)
    assert np.isnan(pg["C"]) and pg["A"] > pg["B"]


def test_fundamental_factor_leakage_injection():
    """A snapshot that becomes available after the rebalance date must not change the factor values."""
    s = pd.DataFrame({"cik": ["1", "1"], "snapshot_date": pd.to_datetime(["2023-11-02", "2024-02-11"]),
                      "availability_date": pd.to_datetime(["2023-11-02", "2024-02-11"]),
                      "period_end": pd.to_datetime(["2023-09-30", "2023-12-31"]),
                      "capex__ttm": [10.0, 90.0], "total_assets": [200.0, 200.0], "operating_cf__ttm": [30.0, -5.0],
                      "operating_income__ttm": [20.0, 20.0], "long_term_debt": [60.0, 500.0], "cash": [10.0, 10.0]})
    joined = asof_join_snapshots(s, {"X": "1"}, D, ["X"])
    f1, _ = compute_fundamental_features(joined, pd.Series({"X": 10.0}), None, D)
    s2 = s.copy()
    s2.loc[1, ["capex__ttm", "long_term_debt"]] = [9999.0, 9999.0]  # tamper with the future filing only
    f2, _ = compute_fundamental_features(asof_join_snapshots(s2, {"X": "1"}, D, ["X"]), pd.Series({"X": 10.0}), None, D)
    pd.testing.assert_frame_equal(f1, f2)
    assert f1.loc["X", "capex_at"] == pytest.approx(0.05)


def _oil_world(n=900, beta=2.0, seed=3):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    r_m = rng.normal(0.0004, 0.01, n)
    r_o = rng.normal(0.0003, 0.02, n)
    r_x = 0.5 * r_m + beta * r_o + rng.normal(0, 0.005, n)
    r_y = 1.0 * r_m + rng.normal(0, 0.01, n)
    mk = lambda r: 100 * np.cumprod(1 + r)  # noqa: E731
    close = pd.DataFrame({"XOIL": mk(r_x), "YTECH": mk(r_y)}, index=idx)
    return close, pd.Series(mk(r_m), index=idx), pd.Series(mk(r_o), index=idx)


def test_oil_beta_trend_recovers_beta_and_sign():
    close, spy, oil = _oil_world()
    at = close.index[-1]
    v = oil_beta_trend_at(close, spy, oil, at)
    trend = np.sign(oil.iloc[-1] / oil.iloc[-127] - 1)
    assert v["XOIL"] == pytest.approx(2.0 * trend, abs=0.3)
    assert abs(v["YTECH"]) < 0.3


def test_oil_beta_trend_leakage_injection():
    close, spy, oil = _oil_world()
    at = close.index[700]
    base = oil_beta_trend_at(close, spy, oil, at)
    c2, s2, o2 = close.copy(), spy.copy(), oil.copy()
    c2.loc[c2.index > at] *= 5
    o2.loc[o2.index > at] *= 0.1
    s2.loc[s2.index > at] *= 3
    pd.testing.assert_series_equal(base, oil_beta_trend_at(c2, s2, o2, at))


def test_stage_unknown_when_no_usd_statements():
    ocf = pd.Series({"A": np.nan, "B": np.nan, "C": 5.0})
    rev = pd.Series({"A": np.nan, "B": np.nan, "C": 10.0})
    assets = pd.Series({"A": np.nan, "B": 100.0, "C": 50.0})
    theme = pd.Series({"A": "energy", "B": "energy", "C": "energy"})
    st = stage_flags(ocf, rev, theme, 50e6, total_assets=assets)
    assert st.to_dict() == {"A": "unknown", "B": "pre_profit", "C": "profitable"}
