"""Target-weight execution shared by the backtest engine and the production monthly run."""
from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from src.portfolio.book import BrokerAdapter, CostModel, Fill, Order, Portfolio
from src.portfolio.weights import cap_weights, target_weights

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


# --- theme portfolio (THEMES_SPEC §8) --------------------------------------------------------------------------------

def select_theme(ranked: pd.DataFrame, held: set[str], n_picks: int, hold_buffer: float, max_subtheme_share: float,
                 blocked: set[str], n_wait: int = 5) -> dict[str, str]:
    """Signals for one theme on one date. ``ranked``: index symbol, columns score and subtheme (eligible members).

    Held names ranked within ``hold_buffer x n_picks`` stay (HOLD); open slots are filled in score order (BUY),
    skipping names in the entry block (top volatility) and names whose subtheme already holds
    ceil(``max_subtheme_share`` x n_picks) of the picks (only when >= 2 subthemes are ranked). Held names outside the buffer or no longer ranked are SELL; the next
    ``n_wait`` best names not selected are WAIT."""
    r = ranked.dropna(subset=["score"]).sort_values("score", ascending=False)
    rank = {s: i + 1 for i, s in enumerate(r.index)}
    # the cap needs at least two subthemes to be meaningful (a single-subtheme theme such as biotech_all would
    # otherwise be limited to half its picks); ceil keeps n_picks reachable with two subthemes (7 -> 4 + 3)
    capped = r["subtheme"].nunique() >= 2
    max_per_sub = max(1, int(np.ceil(max_subtheme_share * n_picks))) if capped else n_picks
    signals: dict[str, str] = {}
    keep = [s for s in r.index if s in held and rank[s] <= hold_buffer * n_picks][:n_picks]
    for s in keep:
        signals[s] = "HOLD"
    per_sub = r.loc[keep, "subtheme"].value_counts().to_dict()
    for s in r.index:
        if len([x for x in signals.values() if x in ("HOLD", "BUY")]) >= n_picks:
            break
        if s in signals or s in blocked:
            continue
        sub = r.at[s, "subtheme"]
        if per_sub.get(sub, 0) >= max_per_sub:
            continue
        signals[s] = "BUY"
        per_sub[sub] = per_sub.get(sub, 0) + 1
    for s in held:
        signals.setdefault(s, "SELL")
    waits = [s for s in r.index if s not in signals][:n_wait]
    for s in waits:
        signals[s] = "WAIT"
    return signals


def theme_targets(picks: dict[str, list[str]], theme_weights: dict[str, float], n_picks: dict[str, int],
                  cap: float) -> pd.Series:
    """Equal weight theme_weight / n_picks per pick, capped; unfilled slots stay in cash."""
    w = {}
    for t, syms in picks.items():
        each = min(cap, theme_weights[t] / max(1, n_picks[t]))
        for s in syms:
            w[s] = w.get(s, 0.0) + each
    return pd.Series(w, dtype=float)


def theme_tilt_weights(score: pd.Series, budget: float, lam: float, top_frac: float, cap: float,
                       blocked: set[str] | frozenset = frozenset()) -> pd.Series:
    """Score-tilted holding of one theme (v2 construction; Grinold-Kahn style tilt around the theme index).

    Eligible members (index of ``score``) start from equal weight, the theme index weight. Names in the top
    ``top_frac`` by score are kept (all when 1.0); weights are proportional to max(0, 1 + lam * z) with z the
    score (robust z, NaN = neutral 0); ``blocked`` names are dropped (entry block); the result is scaled to
    ``budget`` with a single-name ``cap`` (fraction of total capital). lam = 0 and top_frac = 1 replicate the
    equal-weight theme index, so the whole budget is always invested when the theme has members."""
    z = score.astype(float).fillna(0.0)
    z = z[~z.index.isin(list(blocked))]
    if z.empty or budget <= 0:
        return pd.Series(dtype=float)
    n_keep = max(1, int(np.ceil(top_frac * len(z))))
    z = z.sort_values(ascending=False).iloc[:n_keep]
    raw = (1.0 + lam * z).clip(lower=0.0)
    if raw.sum() <= 0:
        raw = pd.Series(1.0, index=z.index)
    w = cap_weights(raw[raw > 0], min(1.0, cap / budget))
    return (w * budget).astype(float)


def partial_rebalance(current: pd.Series, target: pd.Series, speed: float) -> pd.Series:
    """Move ``speed`` of the way from current to target weights (THEMES_SPEC §11 partial trading); names that
    leave the target are sold completely (no lingering positions outside the theme membership)."""
    if speed >= 1.0 or current.empty:
        return target
    names = target.index.union(current.index)
    cur, tgt = current.reindex(names, fill_value=0.0), target.reindex(names, fill_value=0.0)
    out = cur + speed * (tgt - cur)
    out[~names.isin(target.index)] = 0.0
    return out[out > 1e-9]


def present_budgets(budgets: dict[str, float], present: set[str]) -> dict[str, float]:
    """Theme budgets re-normalized over the themes that have eligible members on the date, so a theme without
    members (e.g. quantum in 2011) does not leave its budget in cash (v2; the benchmark composite re-weights the
    same way)."""
    live = {t: w for t, w in budgets.items() if t in present and w > 0}
    tot = sum(live.values())
    return {t: w / tot * sum(budgets.values()) for t, w in live.items()} if tot > 0 else {}


def cap_total_weight(target: pd.Series, cap: float) -> pd.Series:
    """Multi-theme holdings (v2): a stock held through several themes is capped at ``cap`` of capital in total;
    the excess is redistributed pro rata to the other names (total invested weight unchanged when feasible)."""
    target = target[target > 0]
    total = float(target.sum())
    if target.empty or (target <= cap + 1e-12).all():
        return target
    return cap_weights(target / total, cap / total) * total
