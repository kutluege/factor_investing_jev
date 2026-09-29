"""Price-momentum features. Offsets are in trading sessions; skip-month variants exclude the latest ~21 sessions."""
from __future__ import annotations

import pandas as pd

HORIZONS = {"ret_1m": 21, "ret_3m": 63, "ret_6m": 126, "ret_9m": 189, "ret_12m": 252}
SKIP = 21


def momentum_panel(close: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Momentum frames; value at t uses closes at t and earlier only."""
    out = {name: close / close.shift(n) - 1.0 for name, n in HORIZONS.items()}
    lagged = close.shift(SKIP)
    out["mom_3_1"] = lagged / close.shift(63) - 1.0
    out["mom_6_1"] = lagged / close.shift(126) - 1.0
    out["mom_12_1"] = lagged / close.shift(252) - 1.0
    return out


def relative_strength(stock_ret: pd.Series, bench_ret: float | pd.Series) -> pd.Series:
    """(1 + r_stock) / (1 + r_bench) - 1."""
    return (1.0 + stock_ret) / (1.0 + bench_ret) - 1.0


def forward_returns(close: pd.DataFrame, dates: list[pd.Timestamp], horizon: int,
                    delisting_haircut: float = 0.0) -> pd.DataFrame:
    """Forward total return from the close on each rebalance date over ``horizon`` sessions.

    For research labels only (IC, targets). A security that stops trading inside the window is valued at its last
    available close (minus ``delisting_haircut``). Returns columns: rebalance_date, symbol, fwd_return,
    label_end_date. Labels whose window extends beyond the data are omitted (never extrapolated).
    """
    idx = close.index
    rows = []
    for d in dates:
        if d not in idx:
            continue
        i = idx.get_loc(d)
        j = i + horizon
        if j >= len(idx):
            continue
        start = close.iloc[i]
        window = close.iloc[i:j + 1]
        end = window.iloc[-1]
        last_valid = window.ffill().iloc[-1]
        delisted = end.isna() & last_valid.notna()
        end_val = end.where(~delisted, last_valid * (1.0 - delisting_haircut))
        r = (end_val / start - 1.0).dropna()
        for sym, val in r.items():
            rows.append((d, sym, float(val), idx[j]))
    return pd.DataFrame(rows, columns=["rebalance_date", "symbol", "fwd_return", "label_end_date"])
