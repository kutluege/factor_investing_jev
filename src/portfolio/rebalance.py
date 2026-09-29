"""Target-weight execution shared by the backtest engine and the production monthly run."""
from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.portfolio.book import BrokerAdapter, CostModel, Fill, Order, Portfolio
from src.portfolio.weights import target_weights

REGIME_EXPOSURE = {"none": 1.0, "half": 0.5, "cash": 0.0}


def regime_exposure(regime_filter: str, market_close: pd.Series | None, d: pd.Timestamp, window: int = 200) -> float:
    """Equity exposure implied by the market-regime overlay on date d (data up to d only).

    Risk-off when the market (QQQ) closes below its trailing 200-session average (Faber 2007; trend-following
    overlays reduce momentum-crash risk, Daniel & Moskowitz 2016).
    """
    if regime_filter in (None, "none") or market_close is None:
        return 1.0
    m = market_close.loc[:d].dropna()
    if len(m) < window:
        return 1.0
    risk_off = float(m.iloc[-1]) < float(m.tail(window).mean())
    return REGIME_EXPOSURE[regime_filter] if risk_off else 1.0


def position_cap(portfolio_cfg: dict, portfolio_size: int) -> float:
    """Effective single-name cap: the configured cap, but never below 1.5 / N (keeps small N feasible)."""
    return max(float(portfolio_cfg["max_position_weight"]), 1.5 / max(1, portfolio_size))


def plan_targets(keep: list[str], weighting: str, ranking: pd.DataFrame, portfolio_cfg: dict,
                 portfolio_size: int) -> pd.Series:
    return target_weights(keep, weighting, ranking["final_score"], ranking["vol_60d"],
                          position_cap(portfolio_cfg, portfolio_size),
                          ranking["sector_group"] if "sector_group" in ranking else None,
                          portfolio_cfg.get("max_sector_weight"))


def execute_targets(port: Portfolio, targets: pd.Series, prices: dict[str, float], broker: BrokerAdapter,
                    costs: CostModel, extra_bps: Callable[[str], float], drift_band: float, min_trade_usd: float,
                    trade_date: pd.Timestamp, on_fill: Callable[[Fill], None],
                    on_new_position: Callable[[str], None] | None = None) -> None:
    """Trim/top-up kept positions outside the drift band and open new positions, scaling buys to cash."""
    equity = port.cash + sum(p.shares * float(prices.get(s) or p.entry_price) for s, p in port.positions.items())
    buys: list[tuple[str, float, float]] = []
    for sym, w in targets.items():
        px = prices.get(sym)
        if px is None or px != px or px <= 0:
            continue
        target_val = equity * float(w)
        cur_val = port.positions[sym].shares * px if sym in port.positions else 0.0
        if sym in port.positions and abs(cur_val - target_val) <= drift_band * target_val:
            continue
        delta = target_val - cur_val
        if sym in port.positions and abs(delta) < min_trade_usd:
            continue
        if delta < 0:
            f = broker.execute(Order(sym, "SELL", min(-delta / px, port.positions[sym].shares),
                                     "rebalance:trim to target"), px, trade_date, extra_bps(sym))
            if f:
                port.apply(f)
                on_fill(f)
        elif delta > 0:
            buys.append((sym, delta, px))
    if not buys:
        return
    tc = costs.transaction_cost_bps / 1e4
    worst_slip = max((costs.slippage_bps + extra_bps(s)) / 1e4 for s, _, _ in buys)
    need = sum(d for _, d, _ in buys)
    budget = port.cash - costs.commission_per_trade_usd * len(buys)
    scale = min(1.0, budget / (need * (1 + worst_slip) * (1 + tc))) if need > 0 else 0.0
    for sym, delta, px in buys:
        notional = delta * max(scale, 0.0)
        if notional < 1.0:  # dust
            continue
        new = sym not in port.positions
        f = broker.execute(Order(sym, "BUY", notional / px, "entry" if new else "rebalance:top up"), px, trade_date,
                           extra_bps(sym))
        if f and f.gross + f.total_cost <= port.cash + 1e-9:
            port.apply(f)
            on_fill(f)
            if new and on_new_position:
                on_new_position(sym)


def spread_cost_fn(costs_cfg: dict, spread: pd.Series, cost_multiplier: float = 1.0) -> Callable[[str], float]:
    """Half the estimated bid-ask spread in bps, capped and scaled; 0 when the spread model is disabled."""
    cap = float(costs_cfg.get("max_spread_cost_bps", 200))
    enabled = bool(costs_cfg.get("spread_cost"))

    def f(sym: str) -> float:
        if not enabled:
            return 0.0
        s = spread.get(sym) if spread is not None else None
        if s is None or s != s:
            return 0.0
        return min(cap, 0.5 * float(s) * 1e4) * cost_multiplier
    return f
