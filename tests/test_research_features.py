import numpy as np
import pandas as pd
import pytest

from src.features.fundamentals import _sue
from src.features.research_features import monthly_returns, price_extras, residual_momentum, seasonality


def naive_residual_momentum(mret, mkt, sector_map, at, window=36, min_obs=24):
    hist = mret.loc[:at].tail(window)
    groups = pd.Series({s: sector_map.get(s) for s in hist.columns})
    sec = {g: hist[list(c)].mean(axis=1) for g, c in groups.groupby(groups).groups.items()}
    out = {}
    form = hist.index[-12:-1]
    for s in hist.columns:
        df = pd.concat([hist[s], mkt.reindex(hist.index), sec[groups[s]]], axis=1).dropna()
        if len(df) < min_obs or not set(form).issubset(df.index):
            continue
        X = np.column_stack([np.ones(len(df)), df.iloc[:, 1], df.iloc[:, 2]])
        coef = np.linalg.lstsq(X, df.iloc[:, 0].to_numpy(), rcond=None)[0]
        e = pd.Series(df.iloc[:, 0].to_numpy() - X @ coef, index=df.index).loc[form]
        out[s] = e.sum() / e.std(ddof=1)
    return pd.Series(out)


def test_residual_momentum_fast_path_matches_reference():
    rng = np.random.default_rng(0)
    idx = pd.date_range("2018-01-31", periods=48, freq="ME")
    syms = [f"S{i}" for i in range(30)]
    mret = pd.DataFrame(rng.normal(0.01, 0.08, (48, 30)), index=idx, columns=syms)
    mret.iloc[:20, 3] = np.nan          # late listing -> slow path
    mret.iloc[40, 7] = np.nan           # one missing month outside the formation window
    mkt = pd.Series(rng.normal(0.01, 0.04, 48), index=idx)
    sector_map = {s: ("technology" if i < 15 else "energy") for i, s in enumerate(syms)}
    fast = residual_momentum(mret, mkt, sector_map, idx[-1])
    ref = naive_residual_momentum(mret, mkt, sector_map, idx[-1])
    pd.testing.assert_series_equal(fast.sort_index(), ref.sort_index(), check_names=False, atol=1e-9)
    assert "S3" in fast.index  # 28 valid months >= 24


def test_residual_momentum_uses_only_past_months():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2018-01-31", periods=50, freq="ME")
    mret = pd.DataFrame(rng.normal(0, 0.05, (50, 10)), index=idx, columns=list("ABCDEFGHIJ"))
    mkt = pd.Series(rng.normal(0, 0.03, 50), index=idx)
    at = idx[40]
    a = residual_momentum(mret, mkt, {}, at)
    tampered = mret.copy()
    tampered.loc[tampered.index > at] = 5.0
    pd.testing.assert_series_equal(a, residual_momentum(tampered, mkt, {}, at))


def test_sue_standardizes_seasonal_change():
    # quarterly net income, newest first; seasonal changes are all +1 except the latest (+4)
    q = [14, 11, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9]
    changes = [q[k] - q[k + 4] for k in range(8)]
    expected = changes[0] / np.std(changes, ddof=1)
    assert _sue(q) == pytest.approx(expected)
    assert np.isnan(_sue(q[:8])) and np.isnan(_sue([None] * 12))


def test_max_and_spread_estimator():
    idx = pd.bdate_range("2023-01-02", periods=80)
    close = pd.DataFrame({"A": np.linspace(100, 110, 80)}, index=idx)
    close.iloc[70, 0] = close.iloc[69, 0] * 1.2  # a +20% day inside the last 21 sessions
    ex = price_extras(close, close, close * 1.001, close * 0.999, None)
    assert ex["max_ret_21d"]["A"].iloc[-1] == pytest.approx(0.2, rel=1e-6)
    assert (ex["spread_est"]["A"].dropna() >= 0).all()


def test_seasonality_targets_next_calendar_month():
    idx = pd.date_range("2010-01-31", periods=12 * 8, freq="ME")
    mret = pd.DataFrame({"A": [0.05 if d.month == 7 else 0.0 for d in idx]}, index=idx)
    june = pd.Timestamp("2017-06-30")
    assert seasonality(mret, june)["A"] == pytest.approx(0.05)     # July is next
    assert seasonality(mret, pd.Timestamp("2017-07-31"))["A"] == 0.0


def test_monthly_returns_do_not_carry_stale_prices():
    idx = pd.bdate_range("2023-01-02", "2023-04-28")
    close = pd.DataFrame({"A": 10.0}, index=idx)
    close.loc["2023-03-01":, "A"] = np.nan  # stops trading in March
    m = monthly_returns(close)
    assert np.isnan(m.loc["2023-03-31", "A"]) and np.isnan(m.loc["2023-04-30", "A"])
