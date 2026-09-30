"""T5a: Kenneth French parsing, month-end alignment, cache use; beta_252d / size controls (+ leakage)."""
import io
import zipfile

import numpy as np
import pandas as pd
import pytest

from src.data.french import fetch_zip, parse_monthly, to_month_end
from src.features.theme_features import beta_252d_at, size_ln_mcap

CSV = ("This file was created using the 202608 CRSP database.\r\n\r\n"
       ",Mkt-RF,SMB,HML,RF\r\n"
       "202001,  -0.11,  -3.10,  -6.25,   0.13\r\n"
       "202002,  -8.13,   1.05,  -3.80,   0.12\r\n"
       "202003, -13.39,  -4.94, -13.88,   0.12\r\n"
       "\r\n Annual Factors: January-December \r\n,Mkt-RF,SMB,HML,RF\r\n  2020,  23.66,  13.18, -46.56,   0.45\r\n")


def _zip(text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("F-F_Research_Data_Factors.csv", text)
    return buf.getvalue()


def test_parse_monthly_month_end_and_decimals():
    df = parse_monthly(_zip(CSV))
    assert list(df.index) == list(pd.to_datetime(["2020-01-31", "2020-02-29", "2020-03-31"]))
    assert df.loc["2020-03-31", "Mkt-RF"] == pytest.approx(-0.1339)
    assert len(df) == 3  # annual table not included


def test_to_month_end_alignment():
    s = pd.Series([0.01, 0.02], index=pd.to_datetime(["2020-02-28", "2020-03-31"]))  # last trading days
    assert list(to_month_end(s).index) == list(pd.to_datetime(["2020-02-29", "2020-03-31"]))
    with pytest.raises(ValueError):
        to_month_end(pd.Series([1.0, 2.0], index=pd.to_datetime(["2020-02-03", "2020-02-28"])))


def test_fetch_zip_uses_cache_without_network(tmp_path):
    (tmp_path / "x.zip").write_bytes(b"cached")

    class NoNet:
        def get(self, *a, **k):
            raise AssertionError("network used")

    assert fetch_zip("x.zip", tmp_path, client=NoNet()) == b"cached"


def _world(n=400, seed=5):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2022-01-03", periods=n)
    rm = rng.normal(0, 0.01, n)
    mk = lambda r: pd.Series(100 * np.cumprod(1 + r), index=idx)  # noqa: E731
    close = pd.DataFrame({"HI": mk(1.5 * rm + rng.normal(0, 0.003, n)), "LO": mk(0.5 * rm + rng.normal(0, 0.003, n))})
    return close, mk(rm)


def test_beta_252d_recovers_beta_and_min_obs():
    close, spy = _world()
    b = beta_252d_at(close, spy, close.index[-1])
    assert b["HI"] == pytest.approx(1.5, abs=0.1) and b["LO"] == pytest.approx(0.5, abs=0.1)
    short = close.copy()
    short.iloc[:-150, 0] = np.nan  # only ~150 observations for HI
    assert "HI" not in beta_252d_at(short, spy, close.index[-1]).index


def test_beta_252d_leakage_injection():
    close, spy = _world()
    at = close.index[300]
    base = beta_252d_at(close, spy, at)
    c2, s2 = close.copy(), spy.copy()
    c2.loc[c2.index > at] *= 3
    s2.loc[s2.index > at] *= 0.2
    pd.testing.assert_series_equal(base, beta_252d_at(c2, s2, at))


def test_size_ln_mcap():
    s = size_ln_mcap(pd.Series({"A": np.e ** 20, "B": 0.0, "C": np.nan}))
    assert s["A"] == pytest.approx(20) and np.isnan(s["B"]) and np.isnan(s["C"])
