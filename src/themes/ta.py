"""TA layer (THEMES_SPEC §9, T7): indicator table for the monthly shortlist and the trade-journal evaluation.

TA never changes the shortlist; it only proposes timing for BUY/HOLD names, using pre-written rules
(``research/ta/rules.yaml``, not optimized). No automatic trading (``ta_layer.auto_trade`` must be false).

Evaluation (lecture criteria): each round trip is compared with buying the same shares at the month-start
rebalance price (first session open of the entry month) and selling at the same exit, costs included; the hit rate
is compared with the base rate of holding the same stock for the same number of sessions from random days; profit
factor, profit / max drawdown, average win / average loss; mean TA contribution with a 95% CI after >= 50 trades.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.features.technicals import adx, atr, ema, macd, rsi, sma

MIN_TRADES_FOR_CI = 50
BASE_RATE_SAMPLES = 200


def load_rules(path: Path) -> dict:
    rules = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not rules or "rules" not in rules or "version" not in rules:
        raise ValueError(f"{path}: expected 'version' and 'rules'")
    return rules


def bollinger(close: pd.DataFrame, n: int = 20, k: float = 2.0) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mid = close.rolling(n, min_periods=n).mean()
    sd = close.rolling(n, min_periods=n).std(ddof=0)
    return mid + k * sd, mid, mid - k * sd


def indicator_table(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame, symbols: list[str], at: pd.Timestamp,
                    rules: dict, entries: dict[str, pd.Timestamp] | None = None) -> pd.DataFrame:
    """One row per symbol with indicators and rule states on ``at`` (data up to ``at`` only)."""
    syms = [s for s in symbols if s in close]
    h, lo, c = high.loc[:at, syms], low.loc[:at, syms], close.loc[:at, syms]
    r = rules["rules"]
    gc, pb, ts = r["golden_cross_50_200"]["params"], r["pullback_to_50d"]["params"], r["trailing_stop_atr"]["params"]
    s_fast, s_slow = sma(c, gc["fast"]), sma(c, gc["slow"])
    s50, s200 = sma(c, pb["anchor"]), sma(c, pb["trend"])
    a = atr(h, lo, c, ts["atr_period"])
    m_line, m_sig, _ = macd(c)
    adx14, _, _ = adx(h, lo, c, 14)
    bu, bm, bl = bollinger(c)
    above = (s_fast > s_slow).astype(float).where(s_fast.notna() & s_slow.notna())
    cross_up = (above.diff() > 0).rolling(gc["lookback_sessions"], min_periods=1).max()
    last = c.iloc[-1]
    rows = {}
    for s in syms:
        entry = (entries or {}).get(s)
        since = c[s].loc[entry:] if entry is not None else c[s].tail(22)
        stop = float(since.max() - ts["multiple"] * a[s].iloc[-1]) if since.notna().any() else np.nan
        uptrend = bool(last[s] > s200[s].iloc[-1] and s50[s].iloc[-1] > s200[s].iloc[-1])
        rows[s] = {
            "close": last[s], "sma50": s50[s].iloc[-1], "sma200": s200[s].iloc[-1], "ema20": ema(c[[s]], 20)[s].iloc[-1],
            "rsi14": rsi(c[[s]], 14)[s].iloc[-1], "macd": m_line[s].iloc[-1], "macd_signal": m_sig[s].iloc[-1],
            "adx14": adx14[s].iloc[-1], "atr14": a[s].iloc[-1], "bb_upper": bu[s].iloc[-1], "bb_lower": bl[s].iloc[-1],
            "bb_pctb": (last[s] - bl[s].iloc[-1]) / (bu[s].iloc[-1] - bl[s].iloc[-1])
            if bu[s].iloc[-1] != bl[s].iloc[-1] else np.nan,
            "breakout_20d": bool(last[s] > c[s].shift(1).tail(20).max()),
            "golden_cross_50_200": bool(cross_up[s].iloc[-1] == 1 and last[s] > s_slow[s].iloc[-1]),
            "pullback_to_50d": bool(uptrend and abs(last[s] / s50[s].iloc[-1] - 1) <= pb["band_pct"]),
            "trailing_stop_atr": stop, "stop_hit": bool(entry is not None and last[s] < stop),
        }
    out = pd.DataFrame.from_dict(rows, orient="index")
    out.index.name = "symbol"
    out.attrs["as_of"] = at
    out.attrs["rules_version"] = rules["version"]
    return out


# --- journal evaluation ------------------------------------------------------------------------------------------------

def round_trips(journal: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """FIFO-match BUY and SELL rows per symbol. Returns (closed round trips, open lots)."""
    j = journal.copy()
    j["date"] = pd.to_datetime(j["date"])
    j["action"] = j["action"].str.upper()
    j = j.sort_values(["date"], kind="stable")
    trips, open_rows = [], []
    for sym, g in j.groupby("symbol", sort=False):
        lots: list[dict] = []
        for r in g.itertuples():
            if r.action == "BUY":
                lots.append({"date": r.date, "price": float(r.price), "shares": float(r.shares), "rule_id": r.rule_id})
                continue
            if r.action != "SELL":
                continue
            left = float(r.shares)
            while left > 1e-9 and lots:
                lot = lots[0]
                q = min(left, lot["shares"])
                trips.append({"symbol": sym, "entry_date": lot["date"], "entry_price": lot["price"],
                              "exit_date": r.date, "exit_price": float(r.price), "shares": q,
                              "rule_id": lot["rule_id"], "exit_rule": r.rule_id})
                lot["shares"] -= q
                left -= q
                if lot["shares"] <= 1e-9:
                    lots.pop(0)
        open_rows += [{"symbol": sym, **lot} for lot in lots]
    return pd.DataFrame(trips), pd.DataFrame(open_rows)


def side_cost(costs_cfg: dict, notional: float) -> float:
    bps = (float(costs_cfg["slippage_bps"]) + float(costs_cfg["transaction_cost_bps"])) / 1e4
    return notional * bps + float(costs_cfg["commission_per_trade_usd"])


def net_return(entry: float, exit_: float, shares: float, costs_cfg: dict) -> tuple[float, float]:
    """(net P&L in USD, net return) including both sides' costs."""
    buy, sell = entry * shares, exit_ * shares
    pnl = sell - buy - side_cost(costs_cfg, buy) - side_cost(costs_cfg, sell)
    return pnl, pnl / buy


def month_start_price(open_px: pd.Series, d: pd.Timestamp) -> float:
    """Open of the first session of d's month (the monthly rebalance execution price)."""
    s = open_px.dropna()
    m = s[(s.index.year == d.year) & (s.index.month == d.month)]
    return float(m.iloc[0]) if len(m) else np.nan


def base_rate(close: pd.Series, sessions: int, rng: np.random.Generator, costs_cfg: dict,
              n: int = BASE_RATE_SAMPLES) -> float:
    """Share of positive net returns from holding ``sessions`` sessions starting on random days."""
    c = close.dropna()
    if len(c) <= sessions + 1:
        return np.nan
    starts = rng.integers(0, len(c) - sessions, size=n)
    wins = [net_return(c.iloc[i], c.iloc[i + sessions], 100.0, costs_cfg)[0] > 0 for i in starts]
    return float(np.mean(wins))


def evaluate_journal(journal: pd.DataFrame, open_px: pd.DataFrame, close_px: pd.DataFrame, costs_cfg: dict,
                     seed: int = 7) -> dict:
    trips, opens = round_trips(journal)
    if trips.empty:
        return {"trades": 0, "open_lots": len(opens), "table": trips}
    rng = np.random.default_rng(seed)
    rows = []
    for t in trips.itertuples():
        pnl, ret = net_return(t.entry_price, t.exit_price, t.shares, costs_cfg)
        ms = month_start_price(open_px[t.symbol], t.entry_date) if t.symbol in open_px else np.nan
        _, bench = net_return(ms, t.exit_price, t.shares, costs_cfg) if ms == ms else (np.nan, np.nan)
        cal = close_px.index
        held = int(((cal > t.entry_date) & (cal <= t.exit_date)).sum())
        br = base_rate(close_px[t.symbol], max(1, held), rng, costs_cfg) if t.symbol in close_px else np.nan
        rows.append({**t._asdict(), "pnl": pnl, "net_return": ret, "month_start_price": ms,
                     "month_start_return": bench, "ta_contribution": ret - bench if bench == bench else np.nan,
                     "sessions_held": held, "base_rate": br})
    df = pd.DataFrame(rows).drop(columns=["Index"])
    wins, losses = df.loc[df["pnl"] > 0, "pnl"], df.loc[df["pnl"] <= 0, "pnl"]
    curve = df.sort_values("exit_date")["pnl"].cumsum()
    max_dd = float((curve - curve.cummax().clip(lower=0)).min())
    contrib = df["ta_contribution"].dropna()
    out = {
        "trades": len(df), "open_lots": len(opens), "hit_rate": float((df["pnl"] > 0).mean()),
        "base_rate": float(df["base_rate"].mean()),
        "profit_factor": float(wins.sum() / -losses.sum()) if losses.sum() < 0 else np.inf,
        "total_pnl": float(df["pnl"].sum()), "max_drawdown_usd": max_dd,
        "profit_to_max_dd": float(df["pnl"].sum() / -max_dd) if max_dd < 0 else np.inf,
        "avg_win_to_avg_loss": float(wins.mean() / -losses.mean()) if len(wins) and len(losses) else np.nan,
        "ta_contribution_mean": float(contrib.mean()) if len(contrib) else np.nan,
        "table": df,
    }
    if len(contrib) >= MIN_TRADES_FOR_CI:
        half = 1.96 * contrib.std(ddof=1) / np.sqrt(len(contrib))
        out["ta_contribution_ci95"] = (out["ta_contribution_mean"] - half, out["ta_contribution_mean"] + half)
    return out


def evaluation_markdown(ev: dict, rules_version: str) -> str:
    md = [f"# TA işlem günlüğü değerlendirmesi ({rules_version})", ""]
    if not ev["trades"]:
        return "\n".join(md + ["Kapanmış işlem yok.", f"Açık lot: {ev['open_lots']}"]) + "\n"
    verdict = "kural taban oranın ALTINDA (kötü)" if ev["hit_rate"] < ev["base_rate"] else "taban oranın üzerinde"
    md += ["| Ölçüt | Değer |", "|---|---|",
           f"| Kapanmış işlem | {ev['trades']} (açık lot {ev['open_lots']}) |",
           f"| İsabet oranı | {ev['hit_rate']:.1%} |",
           f"| Taban oran (aynı hisse, aynı süre, rastgele gün) | {ev['base_rate']:.1%} → {verdict} |",
           f"| Kâr faktörü (brüt kâr / brüt zarar) | {ev['profit_factor']:.2f} |",
           f"| Toplam net K/Z | {ev['total_pnl']:,.0f} USD |",
           f"| Kâr / maks. düşüş | {ev['profit_to_max_dd']:.2f} |",
           f"| Ort. kazanç / ort. kayıp | {ev['avg_win_to_avg_loss']:.2f} |",
           f"| TA katkısı (ay başı girişine göre, ort.) | {ev['ta_contribution_mean']:+.2%} |"]
    if "ta_contribution_ci95" in ev:
        lo, hi = ev["ta_contribution_ci95"]
        md.append(f"| TA katkısı %95 güven aralığı | [{lo:+.2%}, {hi:+.2%}] |")
    else:
        md.append(f"| TA katkısı güven aralığı | yetersiz örnek (n < {MIN_TRADES_FOR_CI}) |")
    md += ["", "Maliyetler dahildir (kayma + işlem maliyeti + komisyon, iki yön). İsabet oranı tek başına anlamsızdır; "
           "taban oranla karşılaştırılır (%56 isabet, taban %60 ise kural kötüdür).", ""]
    t = ev["table"]
    md += ["| Sembol | Giriş | Çıkış | Kural | Net getiri | Ay başı getirisi | TA katkısı | Taban oran |",
           "|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        md.append(f"| {r.symbol} | {r.entry_date.date()} @ {r.entry_price:.2f} | {r.exit_date.date()} @ "
                  f"{r.exit_price:.2f} | {r.rule_id} | {r.net_return:+.2%} | {r.month_start_return:+.2%} | "
                  f"{r.ta_contribution:+.2%} | {r.base_rate:.0%} |")
    return "\n".join(md) + "\n"
