"""Theme scoring (THEMES_SPEC §6): stage factor sets, direction, coverage and weight-present rules, per-date only."""
import numpy as np
import pandas as pd
import pytest

from src.themes.config import load_themes_config
from src.themes.scoring import score_panel, score_theme

CFG = load_themes_config()
FACTORS = ["mom_12_1", "dist_52w_high", "idio_vol_60d", "max_ret_21d", "share_issuance", "asset_growth", "capex_at",
           "gross_profitability", "cop_at", "sue", "droe", "profitable_growth", "cash_runway_years", "ebit_ev",
           "ocf_ev", "net_debt_ebitda", "oil_beta_trend"]


def cross(n=30, seed=0, theme="robotics") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(rng.normal(size=(n, len(FACTORS))), columns=FACTORS, index=[f"S{i}" for i in range(n)])
    df["stage"] = ["profitable" if i % 3 else "pre_profit" for i in range(n)]
    df["subtheme"] = "industrial_automation"
    df["theme"] = theme
    return df


def test_score_is_standardized_and_uses_stage_groups():
    c = cross()
    s = score_theme(c, CFG, "robotics")
    assert s["score"].notna().all()
    assert abs(s["score"].median()) < 1e-9
    pre = c.index[c["stage"] == "pre_profit"]
    prof = c.index[c["stage"] == "profitable"]
    assert s.loc[pre, "groups_needed"].eq(len(CFG.factor_sets["pre_profit"])).all()
    assert s.loc[prof, "groups_needed"].eq(len(CFG.factor_sets["profitable_general"])).all()
    # group scores exist only for firms whose stage uses the group
    assert s.loc[prof, "grp_survival"].isna().all() and s.loc[pre, "grp_survival"].notna().all()
    assert s.loc[pre, "grp_quality"].isna().all() and s.loc[prof, "grp_quality"].notna().all()


def test_direction_negative_factor_lowers_score():
    c = cross(seed=1)
    base = score_theme(c, CFG, "robotics")["grp_low_risk"]
    c2 = c.copy()
    c2.loc["S1", "idio_vol_60d"] = 50.0  # much riskier -> lower low_risk group score
    assert score_theme(c2, CFG, "robotics").at["S1", "grp_low_risk"] < base["S1"]


def test_low_coverage_factor_dropped_and_min_weight_rule():
    c = cross(seed=2)
    c["sue"] = np.nan
    c.loc[c.index[:5], "sue"] = 1.0  # 5/30 < 30% coverage
    s = score_theme(c, CFG, "robotics")
    assert "sue" in s.attrs["dropped"]
    c2 = cross(seed=3)
    c2.loc["S1", FACTORS] = np.nan
    c2.loc["S1", "mom_12_1"] = 1.0  # only one of six groups present
    assert np.isnan(score_theme(c2, CFG, "robotics").at["S1", "score"])


def test_oil_group_only_for_oil_gas_energy():
    c = cross(theme="energy")
    c["subtheme"] = ["oil_gas" if i < 15 else "power_utilities" for i in range(len(c))]
    s = score_theme(c, CFG, "energy")
    prof = c["stage"] == "profitable"
    oil = prof & (c["subtheme"] == "oil_gas")
    other = prof & (c["subtheme"] != "oil_gas")
    n_prof = len(CFG.factor_sets["energy_profitable"])
    assert set(s.loc[oil, "groups_needed"]) == {n_prof + 1} and set(s.loc[other, "groups_needed"]) == {n_prof}
    assert s.loc[oil, "grp_commodity"].notna().all() and s.loc[other, "grp_commodity"].isna().all()


def test_scores_use_only_their_own_date():
    a, b = cross(seed=4), cross(seed=5)
    p = pd.concat([a.assign(rebalance_date=pd.Timestamp("2020-01-31")),
                   b.assign(rebalance_date=pd.Timestamp("2020-02-28"))]).rename_axis("symbol").reset_index()
    p["eligible"] = True
    s1 = score_panel(p, CFG)
    p2 = p.copy()
    p2.loc[p2["rebalance_date"] == pd.Timestamp("2020-02-28"), FACTORS] *= -7.0  # tamper with the later date
    s2 = score_panel(p2, CFG)
    jan = pd.Timestamp("2020-01-31")
    pd.testing.assert_series_equal(s1.loc[s1["rebalance_date"] == jan, "score"].reset_index(drop=True),
                                   s2.loc[s2["rebalance_date"] == jan, "score"].reset_index(drop=True))
    assert s1["score"].notna().sum() == pytest.approx(60)
