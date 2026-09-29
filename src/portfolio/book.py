"""Portfolio accounting with fractional shares and explicit transaction costs.

A ``BrokerAdapter`` executes orders; the default ``SimulatedBroker`` fills at a supplied reference price with
adverse slippage. A live broker adapter can implement the same protocol later without touching strategy code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import pandas as pd


@dataclass(frozen=True)
class CostModel:
    commission_per_trade_usd: float = 1.0
    slippage_bps: float = 10.0
    transaction_cost_bps: float = 5.0

    def scaled(self, multiplier: float) -> CostModel:
        return CostModel(self.commission_per_trade_usd * multiplier, self.slippage_bps * multiplier,
                         self.transaction_cost_bps * multiplier)

    @classmethod
    def from_config(cls, cfg: dict, multiplier: float = 1.0) -> CostModel:
        return cls(float(cfg["commission_per_trade_usd"]), float(cfg["slippage_bps"]),
                   float(cfg["transaction_cost_bps"])).scaled(multiplier)


@dataclass
class Position:
    symbol: str
    shares: float
    entry_date: pd.Timestamp
    entry_price: float
    cost_basis: float  # total cash paid including costs


@dataclass(frozen=True)
class Order:
    symbol: str
    side: str          # BUY | SELL
    shares: float
    reason: str


@dataclass(frozen=True)
class Fill:
    symbol: str
    side: str
    shares: float
    price: float       # execution price after slippage
    gross: float       # shares * price
    commission: float
    slippage_cost: float
    transaction_cost: float
    trade_date: pd.Timestamp
    reason: str

    @property
    def total_cost(self) -> float:
        return self.commission + self.transaction_cost


class BrokerAdapter(Protocol):
    def execute(self, order: Order, reference_price: float, trade_date: pd.Timestamp) -> Fill | None: ...


class SimulatedBroker:
    def __init__(self, costs: CostModel):
        self.costs = costs

    def execute(self, order: Order, reference_price: float, trade_date: pd.Timestamp) -> Fill | None:
        if reference_price is None or not reference_price > 0 or order.shares <= 0:
            return None
        slip = self.costs.slippage_bps / 1e4
        price = reference_price * (1 + slip) if order.side == "BUY" else reference_price * (1 - slip)
        gross = order.shares * price
        return Fill(order.symbol, order.side, order.shares, price, gross, self.costs.commission_per_trade_usd,
                    abs(price - reference_price) * order.shares, gross * self.costs.transaction_cost_bps / 1e4,
                    trade_date, order.reason)


@dataclass
class Portfolio:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    fills: list[Fill] = field(default_factory=list)

    def market_value(self, prices: dict[str, float] | pd.Series) -> float:
        mv = 0.0
        for sym, pos in self.positions.items():
            p = prices.get(sym)
            if p is not None and p == p:
                mv += pos.shares * float(p)
            else:
                mv += pos.cost_basis  # unpriced: carried at cost (flagged by callers)
        return mv

    def equity(self, prices: dict[str, float] | pd.Series) -> float:
        return self.cash + self.market_value(prices)

    def weights(self, prices: dict[str, float] | pd.Series) -> dict[str, float]:
        eq = self.equity(prices)
        return {s: (p.shares * float(prices.get(s, 0) or 0)) / eq for s, p in self.positions.items()} if eq > 0 else {}

    def apply(self, fill: Fill) -> None:
        if fill.side == "BUY":
            cash_out = fill.gross + fill.total_cost
            if cash_out > self.cash + 1e-9:
                raise ValueError(f"insufficient cash for {fill.symbol}: need {cash_out:.2f}, have {self.cash:.2f}")
            self.cash -= cash_out
            pos = self.positions.get(fill.symbol)
            if pos is None:
                self.positions[fill.symbol] = Position(fill.symbol, fill.shares, fill.trade_date, fill.price, cash_out)
            else:
                pos.shares += fill.shares
                pos.cost_basis += cash_out
        else:
            pos = self.positions.get(fill.symbol)
            if pos is None or fill.shares > pos.shares + 1e-9:
                raise ValueError(f"cannot sell {fill.shares} {fill.symbol}; holding {pos.shares if pos else 0}")
            frac = fill.shares / pos.shares
            self.cash += fill.gross - fill.total_cost
            pos.cost_basis *= (1 - frac)
            pos.shares -= fill.shares
            if pos.shares <= 1e-9:
                del self.positions[fill.symbol]
        self.fills.append(fill)
