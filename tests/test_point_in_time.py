"""Leakage tests: each one tries to smuggle future information into a rebalance decision."""
import numpy as np
import pandas as pd
import pytest

from src.backtest.folds import purge_labels, walk_forward_folds
from src.data.xbrl import (
    add_priority,
    asof_snapshot,
    parse_company_facts,
    pit_filter,
    snapshot,
    snapshots_by_filing,
)
from src.features.fundamentals import asof_join_snapshots
from src.features.price_features import price_features_at
from src.features.technicals import adjusted_ohlc
from src.model.scoring import ic_family_weights


def facts_payload(entries):
    return {"cik": 1, "facts": {"us-gaap": {"Revenues": {"units": {"USD": entries}}}}}


def rev(start, end, val, filed, accn, form="10-Q"):
    return {"start": start, "end": end, "val": val, "filed": filed, "accn": accn, "fy": 2023, "fp": "Q", "form": form}


def test_filing_after_rebalance_is_invisible():
    """Period ending Dec 31, filed Feb 10: must NOT be visible to a Jan 31 rebalance."""
    facts = add_priority(parse_company_facts(facts_payload([
        rev("2023-07-01", "2023-09-30", 100.0, "2023-11-01", "a1"),
        rev("2023-01-01", "2023-12-31", 460.0, "2024-02-10", "a2", "10-K"),
    ])))
    jan = pit_filter(facts, pd.Timestamp("2024-01-31"))
    assert set(jan["period_end"]) == {pd.Timestamp("2023-09-30")}
    feb = pit_filter(facts, pd.Timestamp("2024-02-11"))  # available the session after filing
    assert pd.Timestamp("2023-12-31") in set(feb["period_end"])
    assert pit_filter(facts, pd.Timestamp("2024-02-10")).period_end.max() == pd.Timestamp("2023-09-30")


def test_restatement_only_visible_after_its_filing():
    facts = add_priority(parse_company_facts(facts_payload([
        rev("2023-01-01", "2023-03-31", 100.0, "2023-05-01", "orig"),
        rev("2023-01-01", "2023-03-31", 80.0, "2023-08-01", "restated"),
    ])))
    assert pit_filter(facts, pd.Timestamp("2023-06-30")).iloc[0]["value"] == 100.0
    assert pit_filter(facts, pd.Timestamp("2023-08-02")).iloc[0]["value"] == 80.0


def test_q4_derived_from_annual_minus_ytd_and_ttm():
    e = [rev("2023-01-01", "2023-03-31", 10, "2023-05-01", "q1"),
         rev("2023-01-01", "2023-06-30", 22, "2023-08-01", "h1"),
         rev("2023-01-01", "2023-09-30", 36, "2023-11-01", "9m"),
         rev("2023-01-01", "2023-12-31", 52, "2024-02-10", "fy", "10-K")]
    facts = add_priority(parse_company_facts(facts_payload(e)))
    s = snapshot(facts, pd.Timestamp("2024-03-01"))
    assert s["revenue__ttm"] == 52
    assert s["revenue__q"] == pytest.approx(16)   # Q4 = FY - 9M
    s_before = snapshot(facts, pd.Timestamp("2024-01-31"))
    assert s_before["revenue__end"] == pd.Timestamp("2023-09-30")


def test_asof_join_rejects_future_snapshots():
    snaps = pd.DataFrame({"cik": ["0001", "0001"], "snapshot_date": pd.to_datetime(["2023-11-02", "2024-02-11"]),
                          "availability_date": pd.to_datetime(["2023-11-02", "2024-02-11"]),
                          "period_end": pd.to_datetime(["2023-09-30", "2023-12-31"]), "revenue__ttm": [1.0, 2.0]})
    out = asof_join_snapshots(snaps, {"AAA": "0001"}, pd.Timestamp("2024-01-31"), ["AAA"])
    assert out.loc["AAA", "revenue__ttm"] == 1.0
    tampered = snaps.copy()
    tampered.loc[0, "availability_date"] = pd.Timestamp("2024-03-01")  # corrupt: available after rebalance
    with pytest.raises(AssertionError, match="PIT violation"):
        asof_join_snapshots(tampered, {"AAA": "0001"}, pd.Timestamp("2024-01-31"), ["AAA"])


def test_snapshots_only_change_on_filing_dates():
    e = [rev("2023-01-01", "2023-03-31", 10, "2023-05-01", "q1"), rev("2023-04-01", "2023-06-30", 12, "2023-08-01", "q2")]
    snaps = snapshots_by_filing(add_priority(parse_company_facts(facts_payload(e))))
    assert list(snaps["snapshot_date"]) == [pd.Timestamp("2023-05-02"), pd.Timestamp("2023-08-02")]
    assert asof_snapshot(snaps, pd.Timestamp("2023-07-31"))["revenue__q"] == 10


def _synthetic_prices(n=400, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    rows = []
    for s in ("AAA", "BBB", "QQQ"):
        c = 50 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
        for d, v in zip(idx, c, strict=True):
            rows.append({"symbol": s, "date": d, "open": v, "high": v * 1.01, "low": v * 0.99, "close": v,
                         "adj_close": v, "volume": 1e6})
    return pd.DataFrame(rows), idx


def test_price_features_ignore_future_prices():
    prices, idx = _synthetic_prices()
    d = idx[300]
    mats = adjusted_ohlc(prices)
    bench = mats["close"].pop("QQQ")
    mats = {k: v.drop(columns=["QQQ"], errors="ignore") for k, v in mats.items()}
    base = price_features_at(mats, bench, [d], {"AAA": "technology", "BBB": "technology"})
    tampered = {k: v.copy() for k, v in mats.items()}
    for v in tampered.values():
        v.loc[v.index > d] = v.loc[v.index > d] * 10  # inject a massive future move
    bench2 = bench.copy()
    bench2[bench2.index > d] *= 10
    after = price_features_at(tampered, bench2, [d], {"AAA": "technology", "BBB": "technology"})
    pd.testing.assert_frame_equal(base.drop(columns=["price_date"]), after.drop(columns=["price_date"]))


def test_ic_weights_ignore_unmatured_labels():
    dates = list(pd.date_range("2021-01-31", periods=20, freq="ME"))
    rng = np.random.default_rng(1)
    hist, labels = [], []
    for d in dates:
        fz = pd.DataFrame({f: rng.normal(size=50) for f in ("value", "quality", "growth", "fundamental_momentum",
                                                             "price_momentum", "technical_trend", "risk")},
                          index=[f"S{i}" for i in range(50)])
        hist.append((d, fz))
        # labels perfectly predicted by momentum -- but they mature 6 months later
        labels.append(pd.DataFrame({"rebalance_date": d, "symbol": fz.index, "fwd_return": fz["price_momentum"],
                                    "label_end_date": d + pd.DateOffset(months=6)}))
    lab = pd.concat(labels)
    as_of = dates[8]
    w = ic_family_weights(hist, lab, as_of, 126, 24, 2)
    usable = lab[lab["label_end_date"] <= as_of]["rebalance_date"].nunique()
    assert usable == 3
    assert w["price_momentum"] == max(w.values())
    # tamper: make an unmatured label contradict momentum -> weights must be unchanged
    lab2 = lab.copy()
    mask = lab2["label_end_date"] > as_of
    lab2.loc[mask, "fwd_return"] = -lab2.loc[mask, "fwd_return"]
    assert ic_family_weights(hist, lab2, as_of, 126, 24, 2) == w


def test_walk_forward_folds_embargo_and_purge():
    dates = list(pd.date_range("2020-01-31", periods=48, freq="ME"))
    folds = walk_forward_folds(dates, dates[-1] + pd.Timedelta(days=20), 18, 6, 1, 126)
    assert len(folds) >= 4
    for f in folds:
        assert f.train_end < f.test_start
        assert len(f.embargo_dates) == 1 and f.train_end < f.embargo_dates[0] < f.test_start
    labels = pd.DataFrame({"rebalance_date": dates, "symbol": "A", "fwd_return": 0.0,
                           "label_end_date": [d + pd.DateOffset(months=6) for d in dates]})
    kept = purge_labels(labels, folds[0])
    assert (kept["label_end_date"] < folds[0].test_start).all()
    assert len(kept) < (labels["rebalance_date"] <= folds[0].train_end).sum()  # overlapping labels were purged
