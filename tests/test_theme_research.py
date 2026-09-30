"""Theme research module (§7): Newey-West, sorts, dependent sorts, Fama-MacBeth, IC, persistence, correlations."""
import numpy as np
import pandas as pd
import pytest

from src.themes.research import analyses as A
from src.themes.research.stats import nw_mean, nw_ols, plain_t

WINS = (0.005, 0.995)


def world(n_dates=60, n=80, beta_f=0.02, seed=0) -> pd.DataFrame:
    """f predicts the label; g is noise; score is independent of f; h = score (no extra information)."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-31", periods=n_dates, freq="ME")
    rows = []
    for d in dates:
        f, g, s = rng.normal(size=n), rng.normal(size=n), rng.normal(size=n)
        y = beta_f * f + 0.02 * s + rng.normal(0, 0.05, n)
        rows.append(pd.DataFrame({"rebalance_date": d, "symbol": [f"S{i}" for i in range(n)], "f": f, "g": g,
                                  "h": s + rng.normal(0, 1e-6, n), "score": s, "y": y,
                                  "market_cap": np.exp(rng.normal(22, 1, n)), "beta_252d": rng.normal(1, 0.3, n),
                                  "size_ln_mcap": rng.normal(22, 1, n), "subtheme": "a"}))
    return pd.concat(rows, ignore_index=True)


def test_nw_mean_iid_close_to_plain_and_larger_under_autocorrelation():
    rng = np.random.default_rng(1)
    x = rng.normal(0.1, 1, 400)
    assert nw_mean(x, 1)["t"] == pytest.approx(plain_t(x), rel=0.15)
    e = rng.normal(0, 1, 400)
    ar = np.zeros(400)
    for i in range(1, 400):
        ar[i] = 0.8 * ar[i - 1] + e[i]
    assert nw_mean(ar + 0.1, 6)["se"] > np.std(ar, ddof=1) / np.sqrt(400)


def test_nw_ols_recovers_alpha_and_beta():
    rng = np.random.default_rng(2)
    x = pd.DataFrame({"m": rng.normal(0, 0.04, 300)})
    y = 0.01 + 1.3 * x["m"] + rng.normal(0, 0.001, 300)
    r = nw_ols(y, x, 1)
    assert r.at["alpha", "coef"] == pytest.approx(0.01, abs=1e-3) and r.at["m", "coef"] == pytest.approx(1.3, 0.02)


def test_rank_ic_matches_spearman_definition():
    p = world(n_dates=3)
    ic = A.rank_ic_series(p, "f", "y", 15)
    d0 = p[p["rebalance_date"] == ic.index[0]]
    assert ic.iloc[0] == pytest.approx(d0["f"].rank().corr(d0["y"].rank()))
    s = A.ic_summary(A.rank_ic_series(world(), "f", "y", 15), 21)
    assert s["ic_mean"] > 0.1 and s["ic_nw_t"] > 5 and s["ic_hit_rate"] > 0.8


def test_sorts_monotonic_and_small_scope_uses_terciles():
    ts = A.sort_portfolios(world(), "f", "y", 15)
    s = A.sort_summary(ts, 21)
    assert s["n_ports"] == 5 and s["monotonic"] and s["mimic_ew"] > 0 and s["mimic_ew_t"] > 3
    small = A.sort_portfolios(world(n=30), "f", "y", 15)
    assert set(small["n_ports"]) == {3}
    noise = A.sort_summary(A.sort_portfolios(world(), "g", "y", 15), 21)
    assert abs(noise["mimic_ew_t"]) < 3


def test_dependent_sort_separates_new_information_from_the_score():
    p = world()
    new = A.dependent_sort(p, "f", "y")
    same = A.dependent_sort(p, "h", "y")
    assert nw_mean(new["avg_diff"], 1)["t"] > 3
    assert abs(nw_mean(same["avg_diff"], 1)["t"]) < abs(nw_mean(new["avg_diff"], 1)["t"])


def test_fama_macbeth_variants_recover_sign():
    p = world()
    for v in ("ols_rank_normal", "ols_winsorized_raw", "wls_sqrt_mcap"):
        fm = A.fama_macbeth(p, ["f", "g"], "y", ["beta_252d", "size_ln_mcap"], v, WINS, 15)
        s = A.fm_summary(fm, ["f", "g"], 21, v).set_index("factor")
        assert s.at["f", "coef"] > 0 and s.at["f", "nw_t"] > 3, v
        assert abs(s.at["g", "nw_t"]) < 3, v
        assert 0 < s.at["f", "avg_r2"] < 1


def test_persistence_and_correlation_layout():
    p = world(n_dates=14)
    p["const"] = p["symbol"].str[1:].astype(float)  # identical ranking every month
    pers = A.persistence(p, ["const", "g"], [1, 3, 12])
    assert pers.at["const", "rho_12"] == pytest.approx(1.0) and abs(pers.at["g", "rho_1"]) < 0.1
    p["f2"] = p["f"] ** 3  # monotone, non-linear transform of f
    pear, spear, comb = A.correlations(p, ["f", "f2"], WINS)
    assert spear.at["f", "f2"] == pytest.approx(1.0)
    assert comb.at["f2", "f"] == pytest.approx(pear.at["f2", "f"]) and comb.at["f", "f2"] == pytest.approx(1.0)
    flagged = A.redundant_pairs(pear, spear, 0.7)
    assert len(flagged) == 1


def test_vif_and_orthogonal_residual():
    p = world(n_dates=4)
    p["f_dup"] = p["f"] + np.random.default_rng(3).normal(0, 0.05, len(p))
    v = A.vif(p, ["f", "f_dup", "g"])
    assert v["f"] > 5 and v["g"] < 2
    g = p[p["rebalance_date"] == p["rebalance_date"].iloc[0]]
    res = A.orthogonal_residual(g, "h")  # h is the score itself -> nothing left
    assert res.abs().max() < 1e-3


def test_alphas_alignment_to_next_month_end():
    ts = pd.DataFrame({"rebalance_date": pd.to_datetime(["2020-01-31", "2020-02-28"] * 10)[:10], "top_ew": 0.0,
                       "mimic_ew": 0.0})
    ts["rebalance_date"] = pd.date_range("2020-01-31", periods=10, freq="ME")
    rng = np.random.default_rng(4)
    fr = pd.DataFrame(rng.normal(0, 0.03, (12, 9)), index=pd.date_range("2020-01-31", periods=12, freq="ME"),
                      columns=["ff_mkt_rf", "ff_smb", "ff_hml", "ff_rf", "ff5_smb", "ff5_hml", "ff_rmw", "ff_cma",
                               "ff_mom"])
    ts["top_ew"] = 0.005 + fr["ff_rf"].shift(-1).to_numpy()[:10] + 1.0 * fr["ff_mkt_rf"].shift(-1).to_numpy()[:10]
    a = A.alphas(ts, fr, ["capm"]).set_index("series")
    assert a.at["top_ew", "alpha_monthly"] == pytest.approx(0.005, abs=1e-9)


def test_vectorized_orthogonal_residuals_match_single_date():
    p = world(n_dates=3)
    p["subtheme"] = np.where(np.arange(len(p)) % 2, "a", "b")
    allr = A.orthogonal_residuals(p, "f")
    d0 = p[p["rebalance_date"] == p["rebalance_date"].iloc[0]]
    np.testing.assert_allclose(allr.loc[d0.index].to_numpy(), A.orthogonal_residual(d0, "f").to_numpy(), atol=1e-10)
