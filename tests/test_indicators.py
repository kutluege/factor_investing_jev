import numpy as np
import pandas as pd
import pytest

from src.features import technicals as T
from src.features.momentum import forward_returns, momentum_panel


def frame(values, name="X"):
    idx = pd.bdate_range("2022-01-03", periods=len(values))
    return pd.DataFrame({name: np.asarray(values, dtype=float)}, index=idx)


def reference_wilder(x, n):
    """Textbook Wilder recursion: seed with the SMA of the first n values."""
    out = [np.nan] * len(x)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return np.array(out)


def test_sma_and_ema():
    c = frame(np.arange(1, 31))
    assert T.sma(c, 20)["X"].iloc[19] == pytest.approx(np.mean(np.arange(1, 21)))
    assert np.isnan(T.sma(c, 20)["X"].iloc[18])
    e = T.ema(c, 20)["X"]
    alpha = 2 / 21
    manual = [1.0]
    for v in range(2, 31):
        manual.append(alpha * v + (1 - alpha) * manual[-1])
    assert e.iloc[-1] == pytest.approx(manual[-1])


def test_rsi_extremes_and_reference():
    up = frame(np.arange(1, 40))
    assert T.rsi(up)["X"].iloc[-1] == pytest.approx(100.0)
    flat = frame(np.ones(40))
    assert T.rsi(flat)["X"].iloc[-1] == pytest.approx(50.0)
    rng = np.random.default_rng(0)
    prices = 100 + np.cumsum(rng.normal(0, 1, 200))
    d = np.diff(prices)
    # pandas ewm(alpha=1/n, adjust=False) seeds with the first value rather than the SMA; both converge.
    g, l_ = np.clip(d, 0, None), np.clip(-d, 0, None)
    ref = 100 - 100 / (1 + reference_wilder(g, 14) / reference_wilder(l_, 14))
    ours = T.rsi(frame(prices))["X"].to_numpy()[1:]
    assert ours[-1] == pytest.approx(ref[-1], abs=0.5)
    assert ((ours[20:] >= 0) & (ours[20:] <= 100)).all()


def test_macd_components():
    c = frame(100 + np.sin(np.linspace(0, 12, 120)) * 5)
    line, sig, hist = T.macd(c)
    assert (hist - (line - sig)).abs().max().max() < 1e-12
    assert line["X"].iloc[-1] == pytest.approx((T.ema(c, 12) - T.ema(c, 26))["X"].iloc[-1])


def test_atr_constant_range():
    n = 60
    c = frame(np.full(n, 100.0))
    h, lo = c + 1.0, c - 1.0
    assert T.atr(h, lo, c, 14)["X"].iloc[-1] == pytest.approx(2.0)


def test_adx_strong_trend_and_direction():
    n = 120
    c = frame(np.linspace(100, 200, n))
    h, lo = c + 0.5, c - 0.5
    adx, pdi, mdi = T.adx(h, lo, c, 14)
    assert adx["X"].iloc[-1] > 50
    assert pdi["X"].iloc[-1] > mdi["X"].iloc[-1]
    down = frame(np.linspace(200, 100, n))
    _, pdi2, mdi2 = T.adx(down + 0.5, down - 0.5, down, 14)
    assert mdi2["X"].iloc[-1] > pdi2["X"].iloc[-1]


def test_volatility_annualized():
    rng = np.random.default_rng(1)
    r = rng.normal(0, 0.01, 400)
    c = frame(100 * np.cumprod(1 + r))
    v = T.volatility(c, 60)["X"].iloc[-1]
    assert v == pytest.approx(np.std(r[-60:], ddof=1) * np.sqrt(252), rel=1e-6)


def test_breakouts_52w_and_ratios():
    vals = list(np.linspace(100, 110, 300)) + [130.0]
    c = frame(vals)
    panel = T.compute_indicator_panel(c, c * 1.001, c * 0.999, c, frame(np.full(len(vals), 1e6)))
    assert panel["breakout_20d"]["X"].iloc[-1] == 1.0
    assert panel["breakout_60d"]["X"].iloc[-1] == pytest.approx(130 / 110 - 1, rel=1e-3)
    assert panel["dist_52w_high"]["X"].iloc[-1] == pytest.approx(130 / (130 * 1.001) - 1, rel=1e-6)
    assert panel["price_sma200"]["X"].iloc[-1] == pytest.approx(130 / c["X"].iloc[-200:].mean() - 1)
    assert panel["volume_ratio_20d"]["X"].iloc[-1] == pytest.approx(1.0)


def test_max_drawdown_at():
    c = frame([100, 120, 90, 95, 130, 117] + [117] * 250)
    mdd = T.max_drawdown_at(c, c.index[-1], n=256)
    assert mdd["X"] == pytest.approx(90 / 120 - 1)


def test_momentum_offsets_no_lookahead():
    c = frame(np.arange(1, 301, dtype=float))
    m = momentum_panel(c)
    i = 299
    assert m["ret_3m"]["X"].iloc[i] == pytest.approx(c["X"].iloc[i] / c["X"].iloc[i - 63] - 1)
    assert m["mom_12_1"]["X"].iloc[i] == pytest.approx(c["X"].iloc[i - 21] / c["X"].iloc[i - 252] - 1)
    # changing the future does not change today's momentum
    c2 = c.copy()
    c2.iloc[i + 1:] = 0.0
    assert momentum_panel(c2)["ret_6m"]["X"].iloc[i] == m["ret_6m"]["X"].iloc[i]


def test_forward_returns_and_delisting():
    idx = pd.bdate_range("2022-01-03", periods=10)
    c = pd.DataFrame({"A": np.arange(10, 20, dtype=float), "B": [10, 11, 12, 13, np.nan, np.nan, np.nan, np.nan,
                                                                 np.nan, np.nan]}, index=idx)
    fr = forward_returns(c, [idx[0]], 5, delisting_haircut=0.5).set_index("symbol")
    assert fr.loc["A", "fwd_return"] == pytest.approx(15 / 10 - 1)
    assert fr.loc["B", "fwd_return"] == pytest.approx(13 * 0.5 / 10 - 1)  # last close with haircut
    assert fr.loc["A", "label_end_date"] == idx[5]
    assert forward_returns(c, [idx[6]], 5).empty  # window beyond data -> no label, never extrapolated
