"""BUY / HOLD / WAIT / SELL decisions with entry/exit hysteresis and hard risk gates.

Jev only influences ``final_score`` (and therefore rank). Hard gates and exit rules are applied afterwards and
cannot be overridden by Jev.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.portfolio.book import Position

BUY, HOLD, WAIT, SELL = "BUY", "HOLD", "WAIT", "SELL"


@dataclass
class Decision:
    symbol: str
    signal: str
    reasons: list[str] = field(default_factory=list)
    rank: int | None = None
    replaced: str | None = None


@dataclass(frozen=True)
class SignalRules:
    portfolio_size: int
    hold_buffer: float
    wait_rank_multiple: float = 2.0
    replace_rank_fraction: float = 0.5
    min_holding_days_for_rank_exit: int = 0
    max_vol60_percentile: float | None = 0.95
    require_above_sma200: bool = False
    min_jev_confidence: float | None = None
    technical_breakdown: bool = True
    breakdown_pct: float = 0.10
    fundamental_deterioration_pct: float | None = 0.10

    @property
    def hold_rank_limit(self) -> float:
        return self.portfolio_size * self.hold_buffer

    @classmethod
    def from_config(cls, portfolio_cfg: dict, portfolio_size: int, hold_buffer: float) -> SignalRules:
        g, x = portfolio_cfg["entry_gates"], portfolio_cfg["exit_rules"]
        return cls(portfolio_size=portfolio_size, hold_buffer=hold_buffer,
                   wait_rank_multiple=float(portfolio_cfg["wait_rank_multiple"]),
                   replace_rank_fraction=float(portfolio_cfg["replace_rank_fraction"]),
                   min_holding_days_for_rank_exit=int(portfolio_cfg["min_holding_days_for_rank_exit"]),
                   max_vol60_percentile=g.get("max_vol60_percentile"),
                   require_above_sma200=bool(g.get("require_above_sma200", False)),
                   min_jev_confidence=g.get("min_jev_confidence"),
                   technical_breakdown=bool(x.get("technical_breakdown", True)),
                   breakdown_pct=float(x.get("breakdown_pct", 0.10)),
                   fundamental_deterioration_pct=x.get("fundamental_deterioration_pct"))


def _technical_breakdown(r: pd.Series, rules: SignalRules) -> bool:
    ps, ss = r.get("price_sma200"), r.get("sma50_sma200")
    return bool(rules.technical_breakdown and pd.notna(ps) and pd.notna(ss)
                and ps < -rules.breakdown_pct and ss < 0)


def _fundamental_deterioration(r: pd.Series, rules: SignalRules) -> bool:
    t = rules.fundamental_deterioration_pct
    fm, q = r.get("pct_fundamental_momentum"), r.get("pct_quality")
    return bool(t is not None and pd.notna(fm) and pd.notna(q) and fm < t and q < t)


def entry_gate_failures(r: pd.Series, rules: SignalRules) -> list[str]:
    fails = []
    vp = r.get("vol60_pct")
    if rules.max_vol60_percentile is not None and pd.notna(vp) and vp > rules.max_vol60_percentile:
        fails.append("gate:excessive_volatility")
    if rules.require_above_sma200 and not (pd.notna(r.get("price_sma200")) and r["price_sma200"] > 0):
        fails.append("gate:no_technical_confirmation")
    if _technical_breakdown(r, rules):
        fails.append("gate:technical_breakdown")
    if rules.min_jev_confidence is not None and pd.notna(r.get("jev_confidence")) \
            and r["jev_confidence"] < rules.min_jev_confidence:
        fails.append("gate:insufficient_jev_confidence")
    return fails


def decide(ranking: pd.DataFrame, holdings: dict[str, Position], as_of: pd.Timestamp, rules: SignalRules,
           exclusion_reasons: dict[str, str] | None = None, holding_days: dict[str, int] | None = None) -> list[Decision]:
    """``ranking``: eligible names indexed by symbol with columns rank, final_score, vol60_pct, price_sma200,
    sma50_sma200, pct_quality, pct_fundamental_momentum, (optional) jev_confidence."""
    N = rules.portfolio_size
    out: dict[str, Decision] = {}
    holding_days = holding_days or {}
    exclusion_reasons = exclusion_reasons or {}

    # 1) existing holdings: hard exits first, then hysteresis on rank
    holds: list[str] = []
    for sym in holdings:
        if sym not in ranking.index:
            reason = exclusion_reasons.get(sym, "not in eligible universe")
            out[sym] = Decision(sym, SELL, [f"exit:no_longer_eligible ({reason})"])
            continue
        r = ranking.loc[sym]
        rank = int(r["rank"])
        reasons = []
        if _technical_breakdown(r, rules):
            reasons.append("exit:technical_breakdown")
        if _fundamental_deterioration(r, rules):
            reasons.append("exit:fundamental_deterioration")
        if rank > rules.hold_rank_limit and holding_days.get(sym, 10**6) >= rules.min_holding_days_for_rank_exit:
            reasons.append(f"exit:rank_deterioration (rank {rank} > hold limit {rules.hold_rank_limit:g})")
        if reasons:
            out[sym] = Decision(sym, SELL, reasons, rank)
        else:
            out[sym] = Decision(sym, HOLD, [f"hold:rank {rank} within hold limit {rules.hold_rank_limit:g}"], rank)
            holds.append(sym)

    # 2) portfolio shrink (e.g. portfolio size reduced): sell the worst-ranked holds beyond N
    if len(holds) > N:
        for sym in sorted(holds, key=lambda s: out[s].rank)[N:]:
            out[sym] = Decision(sym, SELL, ["exit:portfolio_size_reduction"], out[sym].rank)
        holds = sorted(holds, key=lambda s: out[s].rank)[:N]

    # 3) entry candidates in rank order
    candidates = ranking[~ranking.index.isin(list(holdings))].sort_values("rank")
    slots = N - len(holds)
    strong_waiting: list[str] = []
    gated_above = 0  # gated names ranked above do not consume entry positions
    for sym, r in candidates.iterrows():
        rank = int(r["rank"])
        if rank > N * rules.wait_rank_multiple:
            break
        fails = entry_gate_failures(r, rules)
        if fails:
            gated_above += 1
        entry_rank = rank - gated_above if not fails else rank
        if entry_rank <= N and not fails:
            if slots > 0:
                note = f" ({gated_above} higher-ranked name(s) blocked by entry gates)" if entry_rank < rank else ""
                out[sym] = Decision(sym, BUY, [f"entry:rank {rank} <= {N}{note}"], rank)
                slots -= 1
            else:
                out[sym] = Decision(sym, WAIT, [f"wait:rank {rank} qualifies but portfolio is full"], rank)
                if rank <= N * rules.replace_rank_fraction:
                    strong_waiting.append(sym)
        elif rank <= N:
            out[sym] = Decision(sym, WAIT, fails, rank)
        else:
            out[sym] = Decision(sym, WAIT, [f"wait:near cutoff (rank {rank}, entry requires <= {N})"] + fails, rank)

    # 4) replacement: a strong waiting candidate displaces the weakest hold that is outside the top N
    weak = sorted([s for s in holds if out[s].rank is not None and out[s].rank > N], key=lambda s: -out[s].rank)
    for cand in strong_waiting:
        if not weak:
            break
        victim = weak.pop(0)
        out[victim] = Decision(victim, SELL, [f"exit:replaced_by_better_candidate ({cand}, rank {out[cand].rank})"],
                               out[victim].rank, replaced=cand)
        out[cand] = Decision(cand, BUY, [f"entry:rank {out[cand].rank} replaces {victim} (rank {out[victim].rank})"],
                             out[cand].rank)
    return list(out.values())


def change_conditions(signal: str, rank: int | None, rules: SignalRules, gates: list[str]) -> list[str]:
    """Deterministic statements of what would change the current state."""
    N, lim = rules.portfolio_size, rules.hold_rank_limit
    if signal in (HOLD, BUY):
        c = [f"SELL if rank falls below {lim:g}",
             f"SELL if price drops more than {rules.breakdown_pct:.0%} below its 200-day average while the 50-day "
             "average is below the 200-day average"]
        if rules.fundamental_deterioration_pct is not None:
            c.append(f"SELL if both quality and fundamental-momentum percentiles fall below "
                     f"{rules.fundamental_deterioration_pct:.0%}")
        c.append(f"SELL if a non-owned stock ranks in the top {int(N * rules.replace_rank_fraction)} while this one "
                 f"ranks outside the top {N}")
        return c
    if signal == WAIT:
        c = [f"BUY if rank improves to {N} or better and all entry gates pass"] if rank is None or rank > N else \
            [f"BUY when a portfolio slot opens or it reaches the top {int(N * rules.replace_rank_fraction)}"]
        c += [f"clear gate '{g.split(':', 1)[1]}'" for g in gates if g.startswith("gate:")]
        return c
    if signal == SELL:
        return [f"re-entry requires rank {N} or better and passing entry gates"]
    return []
