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


def delisting_haircuts(close: pd.DataFrame, traded_close: pd.DataFrame | None, costs_cfg: dict) -> pd.Series:
    """Per-symbol haircut applied to the last price of a security that stopped trading before the data end.

    Distress delistings (last traded price below ``distress_price`` or a fall of more than ``distress_drawdown``
    over the final 126 sessions) get ``distress_haircut``; other delistings (typically mergers) get
    ``delisting_haircut``. Symbols still trading get 0.
    """
    base = float(costs_cfg.get("delisting_haircut", 0.0))
    distress = float(costs_cfg.get("distress_haircut", base))
    min_px = float(costs_cfg.get("distress_price", 0.0))
    max_dd = float(costs_cfg.get("distress_drawdown", 1.0))
    end = close.index[-1]
    out = {}
    for sym in close.columns:
        s = close[sym].dropna()
        if s.empty or s.index[-1] >= end:
            continue
        last = float(traded_close[sym].dropna().iloc[-1]) if traded_close is not None and sym in traded_close \
            else float(s.iloc[-1])
        fall = float(s.iloc[-1] / s.iloc[max(0, len(s) - 127)] - 1.0)
        out[sym] = distress if (last < min_px or fall < -max_dd) else base
    return pd.Series(out, dtype=float)


def relative_strength(stock_ret: pd.Series, bench_ret: float | pd.Series) -> pd.Series:
    """(1 + r_stock) / (1 + r_bench) - 1."""
    return (1.0 + stock_ret) / (1.0 + bench_ret) - 1.0


def forward_returns(close: pd.DataFrame, dates: list[pd.Timestamp], horizon: int,
                    delisting_haircut: float | pd.Series = 0.0) -> pd.DataFrame:
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
        hc = delisting_haircut.reindex(end.index).fillna(0.0) if isinstance(delisting_haircut, pd.Series) \
            else delisting_haircut
        end_val = end.where(~delisted, last_valid * (1.0 - hc))
        r = (end_val / start - 1.0).dropna()
        for sym, val in r.items():
            rows.append((d, sym, float(val), idx[j]))
    return pd.DataFrame(rows, columns=["rebalance_date", "symbol", "fwd_return", "label_end_date"])
