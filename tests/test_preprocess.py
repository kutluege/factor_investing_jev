import numpy as np
import pandas as pd
import pytest

from src.config import load_config
from src.features.preprocess import composite, family_scores, normalize_feature, pct_rank, robust_z


def test_robust_z_median_mad_and_winsorization():
    x = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 1000.0])
    z = robust_z(x, clip=5.0)
    assert z.abs().max() <= 5.0 / 0.5  # re-standardized after clipping, still bounded
    assert z.iloc[-1] == z.max()
    assert robust_z(x, clip=None).median() == pytest.approx(0.0)


def test_robust_z_handles_missing_and_constant():
    x = pd.Series([1.0, np.nan, 1.0, 1.0])
    z = robust_z(x)
    assert np.isnan(z.iloc[1]) and (z.dropna() == 0).all()


def test_percentile_rank():
    p = pct_rank(pd.Series([3.0, 1.0, 2.0, np.nan]))
    assert list(p.iloc[:3]) == [1.0, pytest.approx(1 / 3), pytest.approx(2 / 3)] and np.isnan(p.iloc[3])


def test_sector_relative_normalization_uses_group_statistics():
    x = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 101, 102, 103, 104, 105, 106, 107, 108.0])
    g = pd.Series(["a"] * 8 + ["b"] * 8)
    z = normalize_feature(x, g, clip=5.0, min_group_size=8)
    assert z.iloc[:8].median() == pytest.approx(z.iloc[8:].median())  # both centred within their group


def test_normalization_is_per_cross_section_only():
    """A date's scores are identical whether or not another (e.g. future) cross-section exists."""
    cfg = load_config("factors")
    rng = np.random.default_rng(3)
    idx = [f"S{i}" for i in range(40)]
    today = pd.DataFrame({"mom_12_1": rng.normal(0, 0.2, 40), "idio_vol_60d": rng.uniform(0.2, 0.6, 40),
                          "cop_at": rng.normal(0.05, 0.1, 40),
                          "sector_group": ["technology"] * 20 + ["energy"] * 20}, index=idx)
    fz1, _, _ = family_scores(today, today["sector_group"], cfg)
    future = today.copy()
    future["mom_12_1"] *= 50  # wildly different future cross-section
    fz_future, _, _ = family_scores(future, future["sector_group"], cfg)
    fz2, _, _ = family_scores(today, today["sector_group"], cfg)
    pd.testing.assert_frame_equal(fz1, fz2)
    assert fz1["momentum"].notna().all() and fz1["quality"].notna().all()


def test_biotech_value_excludes_earnings_based_ratios():
    cfg = load_config("factors")
    idx = [f"B{i}" for i in range(12)]
    df = pd.DataFrame({"ebit_ev": np.linspace(-0.5, 0.1, 12)[::-1], "cash_to_mcap": np.linspace(0.1, 1, 12),
                       "sector_group": "biotechnology"}, index=idx)
    fz, _, diag = family_scores(df, df["sector_group"], cfg)
    # value for biotech is driven only by cash/market cap: order follows cash_to_mcap exactly
    assert list(fz["value"].rank()) == list(df["cash_to_mcap"].rank())
    assert diag["coverage"]["ebit_ev"] == 0.0


def test_price_signals_ranked_across_universe_accounting_within_sector():
    cfg = load_config("factors")
    idx = [f"S{i}" for i in range(20)]
    # energy names all have higher momentum AND higher cash profitability than tech names
    df = pd.DataFrame({"mom_12_1": list(range(20)), "cop_at": list(range(20)),
                       "sector_group": ["technology"] * 10 + ["energy"] * 10}, index=idx)
    fz, _, _ = family_scores(df, df["sector_group"], cfg)
    assert fz.loc["S19", "momentum"] > fz.loc["S9", "momentum"]           # universe-wide: energy ranks higher
    assert abs(fz.loc["S19", "quality"] - fz.loc["S9", "quality"]) < 1e-9  # within-sector: both top of group


def test_composite_redistributes_missing_family_weight():
    fz = pd.DataFrame({"value": [1.0, np.nan, -1.0], "quality": [0.0, 1.0, 0.5]}, index=list("abc"))
    c = composite(fz, {"value": 1, "quality": 1})
    assert not np.isnan(c["b"])  # missing value family does not wipe out the name
    c2 = composite(fz, {"value": 3, "quality": 1})
    assert np.isnan(c2["b"])  # but a name missing >50% of the weight is not scored
