"""Forward shadow tracking: freeze once, idempotent snapshots, matured-only evaluation."""
import duckdb
import numpy as np
import pandas as pd
import pytest

from src.themes import forward as F


def test_freeze_never_overwrites_and_snapshots_are_idempotent(tmp_path):
    con = duckdb.connect(str(tmp_path / "f.duckdb"))
    a = F.freeze(con, "v2", {"lam": 0.5}, "test", pd.Timestamp("2029-10-01"), 40.0)
    b = F.freeze(con, "v2", {"lam": 9.9}, "test", pd.Timestamp("2030-01-01"))
    assert a["new"] and not b["new"] and b["config"] == {"lam": 0.5}
    t = pd.DataFrame({"symbol": ["A", "B"], "theme": ["x", "x"], "weight": [0.5, 0.5], "score": [1.0, 0.0]})
    F.record(con, "v2", pd.Timestamp("2026-09-30"), t)
    F.record(con, "v2", pd.Timestamp("2026-09-30"), t)
    assert con.execute("SELECT count(*) FROM theme_forward_targets").fetchone()[0] == 2


def test_realized_only_matured_months_and_contribution():
    idx = pd.bdate_range("2026-09-28", periods=40)  # ends 2026-11-20
    close = pd.DataFrame({"A": np.linspace(10, 12, 40), "B": np.full(40, 10.0)}, index=idx)
    d0, d1, d2 = pd.Timestamp("2026-09-30"), pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-30")
    snaps = pd.DataFrame({"snapshot_date": [d0, d1, d2], "model": "v2", "symbol": "A", "theme": "x",
                          "weight": 1.0, "score": 1.0})
    members = pd.DataFrame({"rebalance_date": [d0, d0, d1, d1], "symbol": ["A", "B", "A", "B"], "theme": "x"})
    real = F.realized(snaps, close, members, {"x": 1.0}, unit_cost=0.0)
    assert list(real["snapshot_date"]) == [d0]  # d1 -> d2 not matured (no prices after 2026-11-30 + 1 session)
    a, b = close.index[close.index.searchsorted(d0, "right")], close.index[close.index.searchsorted(d1, "right")]
    r_a = close.loc[b, "A"] / close.loc[a, "A"] - 1
    assert real["contribution"].iloc[0] == pytest.approx(r_a - r_a / 2)
    assert F.summary(real)["months"].iloc[0] == 1
