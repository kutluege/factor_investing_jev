import numpy as np
import pandas as pd

from src.db.schema import connect
from src.features.fundamentals import compute_fundamental_features
from src.jev.forward import forward_ic, jev_production_gate


def _seed(con, months: int, informative: bool):
    rng = np.random.default_rng(0)
    syms = [f"S{i}" for i in range(30)]
    dates = pd.bdate_range("2023-01-02", periods=months * 21 + 80)
    drift = {s: rng.normal(0, 0.002) for s in syms}
    rows = []
    for s in syms:
        px = 50 * np.exp(np.cumsum(rng.normal(drift[s], 0.01, len(dates))))
        rows += [(s, d.date(), p, p, p, p, p, 1e6, "t", None) for d, p in zip(dates, px, strict=True)]
    con.executemany("INSERT INTO daily_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    for m in range(months):
        d = dates[m * 21]
        key = f"production:{m:03d}"
        con.execute("INSERT INTO production_runs VALUES (?, 'production', ?, NULL, 'completed', NULL, NULL, NULL, NULL)",
                    [key, d.date()])
        for s in syms:
            jev = drift[s] * 1000 + (0 if informative else rng.normal(0, 50))
            if not informative:
                jev = rng.normal()
            con.execute("INSERT INTO monthly_rankings VALUES (?, ?, 'v', ?, 1, NULL, ?, ?, NULL, 0, '{}', '{}', true, NULL)",
                        [key, d.date(), s, rng.normal(), jev])


def test_gate_requires_matured_forward_months():
    con = connect(":memory:")
    _seed(con, months=5, informative=True)
    g = jev_production_gate(con)
    assert not g["allowed"] and "shadow mode" in g["reason"]


def test_gate_opens_only_for_informative_scores():
    con = connect(":memory:")
    _seed(con, months=14, informative=True)
    ic = forward_ic(con)
    assert len(ic) >= 12 and ic["jev_ic"].mean() > 0.3
    assert jev_production_gate(con)["allowed"]
    con2 = connect(":memory:")
    _seed(con2, months=14, informative=False)
    assert not jev_production_gate(con2)["allowed"]


def test_fscore_counts_signals():
    idx = ["GOOD", "BAD"]
    snap = pd.DataFrame({
        "net_income__ttm": [10.0, -5.0], "net_income__ttm_1y": [5.0, 1.0],
        "operating_cf__ttm": [15.0, -8.0], "operating_cf__ttm_1y": [8.0, 2.0],
        "total_assets": [100.0, 100.0], "total_assets__1y": [100.0, 90.0],
        "long_term_debt": [10.0, 50.0], "long_term_debt__1y": [20.0, 30.0],
        "current_assets": [60.0, 20.0], "current_liabilities": [30.0, 30.0],
        "current_assets__1y": [50.0, 30.0], "current_liabilities__1y": [30.0, 20.0],
        "revenue__ttm": [120.0, 50.0], "revenue__ttm_1y": [100.0, 60.0],
        "gross_profit__ttm": [60.0, 10.0], "gross_profit__ttm_1y": [45.0, 20.0],
        "shares_outstanding": [100.0, 150.0], "shares_outstanding__1y": [100.0, 100.0],
        "equity": [50.0, 20.0], "equity__1y": [45.0, 30.0]}, index=idx)
    f, _ = compute_fundamental_features(snap, pd.Series({"GOOD": 10.0, "BAD": 10.0}), None, pd.Timestamp("2024-01-31"))
    assert f.loc["GOOD", "fscore"] == 9 and f.loc["BAD", "fscore"] == 0
    assert f.loc["BAD", "share_issuance"] > 0 and f.loc["GOOD", "asset_growth"] == 0
