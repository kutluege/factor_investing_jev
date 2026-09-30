"""T4b: announcement timing, FMP EPS matching, ear_3d / sue_announce + leakage-injection tests."""
import numpy as np
import pandas as pd
import pytest

from src.features.earnings_events import (
    announcement_events,
    ear_3d_at,
    earnings_features_at,
    event_session,
    sue_announce_at,
)
from src.themes.earnings import earnings_8k

SESSIONS = pd.bdate_range("2010-01-01", "2026-12-31")


def test_event_session_rules():
    assert event_session(pd.Timestamp("2024-02-01 07:32"), SESSIONS) == pd.Timestamp("2024-02-01")  # pre-open
    assert event_session(pd.Timestamp("2024-02-01 16:12"), SESSIONS) == pd.Timestamp("2024-02-02")  # after close
    assert event_session(pd.Timestamp("2024-02-02 16:05"), SESSIONS) == pd.Timestamp("2024-02-05")  # Fri -> Mon
    assert event_session(pd.Timestamp("2024-02-03 09:00"), SESSIONS) == pd.Timestamp("2024-02-05")  # Saturday


def test_announcement_events_dedup_and_matching():
    k8 = pd.DataFrame({"accession": ["a", "a_amend", "b"],
                       "acceptance": pd.to_datetime(["2024-02-01 16:12", "2024-02-03 10:00", "2024-05-02 07:00"])})
    fmp = pd.DataFrame({"date": pd.to_datetime(["2024-02-01", "2024-08-01"]), "epsActual": [1.1, 2.2]})
    ev = announcement_events(k8, fmp, SESSIONS)
    assert list(ev["accession"]) == ["a", "b"]                      # 8-K/A two days later = same announcement
    assert ev.loc[0, "t0"] == pd.Timestamp("2024-02-02")
    assert ev.loc[0, "available_from"] == pd.Timestamp("2024-02-05")
    assert ev.loc[0, "eps"] == 1.1 and np.isnan(ev.loc[1, "eps"])  # FMP 2024-08-01 is > 3 days from 2024-05-02


def _quarterly(n=16, start="2020-02-03", eps=None) -> pd.DataFrame:
    acc = pd.date_range(start, periods=n, freq="91D") + pd.Timedelta(hours=16, minutes=5)
    k8 = pd.DataFrame({"accession": [f"q{i}" for i in range(n)], "acceptance": acc})
    eps = eps if eps is not None else [0.1 * i + (0.3 if i % 4 == 0 else 0.0) + 0.05 * np.sin(i) for i in range(n)]
    fmp = pd.DataFrame({"date": acc.normalize(), "epsActual": eps})
    return announcement_events(k8, fmp, SESSIONS)


def test_sue_announce_matches_definition():
    ev = _quarterly()
    at = ev["available_from"].iloc[-1]
    e = list(ev["eps"])[::-1][:12]
    ch = np.array([e[k] - e[k + 4] for k in range(8)])
    assert sue_announce_at(ev, at) == pytest.approx(ch[0] / ch.std(ddof=1))
    # the last event is not usable one session earlier
    assert sue_announce_at(ev, at - pd.offsets.BDay(1)) != pytest.approx(sue_announce_at(ev, at))


def test_sue_announce_leakage_injection():
    ev = _quarterly(16)
    at = ev["available_from"].iloc[11]
    base = sue_announce_at(ev, at)
    tampered = ev.copy()
    tampered.loc[12:, "eps"] = 999.0          # announcements after ``at``
    assert sue_announce_at(tampered, at) == pytest.approx(base)
    assert not np.isnan(base)


def _prices(t0: pd.Timestamp, jump: float = 0.05):
    idx = pd.bdate_range(t0 - pd.Timedelta(days=60), t0 + pd.Timedelta(days=60))
    rng = np.random.default_rng(1)
    b = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    s = b.copy()
    s.loc[t0] += jump
    return s, b


def test_ear_3d_value_and_window_completion():
    ev = announcement_events(pd.DataFrame({"accession": ["x"], "acceptance": [pd.Timestamp("2024-02-01 16:12")]}),
                             pd.DataFrame(columns=["date", "epsActual"]), SESSIONS)
    t0 = ev["t0"].iloc[0]
    s, b = _prices(t0)
    assert ear_3d_at(ev, s, b, t0 + pd.offsets.BDay(1)) == pytest.approx(0.05)
    assert np.isnan(ear_3d_at(ev, s, b, t0))                           # t0+1 not yet observed
    assert np.isnan(ear_3d_at(ev, s, b, t0 + pd.Timedelta(days=95)))  # older than 90 days


def test_ear_3d_leakage_injection():
    ev = announcement_events(pd.DataFrame({"accession": ["x"], "acceptance": [pd.Timestamp("2024-02-01 16:12")]}),
                             pd.DataFrame(columns=["date", "epsActual"]), SESSIONS)
    t0 = ev["t0"].iloc[0]
    s, b = _prices(t0)
    at = t0 + pd.offsets.BDay(3)
    base = ear_3d_at(ev, s, b, at)
    s2, b2 = s.copy(), b.copy()
    s2.loc[s2.index > at] = 0.5
    b2.loc[b2.index > at] = -0.5
    future = pd.concat([ev, ev.assign(accession="y", t0=at + pd.offsets.BDay(2),
                                      available_from=at + pd.offsets.BDay(3))], ignore_index=True)
    assert ear_3d_at(future, s2, b2, at) == pytest.approx(base)
    rets = pd.DataFrame({"X": s, "XBI": b})
    f = earnings_features_at({"X": ev}, rets, pd.Series({"X": "XBI"}), at)
    assert f.loc["X", "ear_3d"] == pytest.approx(base)


class _FakeSec:
    base = "https://data.sec.gov"
    cfg = {"ttl_hours": {"submissions": 1}}

    def submissions(self, cik):
        return {"filings": {"recent": {
            "form": ["8-K", "8-K", "10-Q", "8-K/A"],
            "items": ["2.02,9.01", "5.02", "", "2.02"],
            "accessionNumber": ["a1", "a2", "a3", "a4"],
            "acceptanceDateTime": ["2024-02-01T21:12:25.000Z", "2024-02-05T15:00:00.000Z",
                                   "2024-02-06T15:00:00.000Z", "2024-02-02T14:00:00.000Z"]}, }, "files": []}

    def get_json(self, *a, **k):
        raise AssertionError("no paged files expected")


def test_earnings_8k_filters_item_202_and_converts_utc():
    k = earnings_8k(_FakeSec(), "1")
    assert list(k["accession"]) == ["a1", "a4"]
    assert k.loc[0, "acceptance"] == pd.Timestamp("2024-02-01 16:12:25")
