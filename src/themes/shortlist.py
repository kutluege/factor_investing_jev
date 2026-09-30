"""Monthly theme shortlist (THEMES_SPEC §8): signals for the latest rebalance date, group contributions, stage,
WAIT reserve list and 10-K evidence. Manual include/exclude overrides exist ONLY here (live list), never in
backtests (``classification.backtest_manual_overrides: false``); every override is written into the output.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from src.config import PROJECT_ROOT
from src.portfolio.rebalance import select_theme
from src.themes.backtest import entry_block
from src.themes.config import ThemesConfig

OVERRIDES_FILE = PROJECT_ROOT / "research" / "themes" / "live_overrides.yaml"


def load_overrides(path: Path = OVERRIDES_FILE) -> dict[str, set[str]]:
    """Optional file: {include: [SYM, ...], exclude: [SYM, ...]}."""
    if not path.exists():
        return {"include": set(), "exclude": set()}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {k: {str(s).strip() for s in raw.get(k) or []} for k in ("include", "exclude")}


def build_shortlist(cross: pd.DataFrame, cfg: ThemesConfig, held: dict[str, str], evidence: pd.DataFrame,
                    overrides: dict[str, set[str]] | None = None) -> pd.DataFrame:
    """``cross``: eligible scored members on the latest date (index symbol; theme, subtheme, stage, score, grp_*).
    ``held``: current holdings symbol -> theme. ``evidence``: symbol -> method, hits, matched, filing_accession."""
    ov = overrides or {"include": set(), "exclude": set()}
    blocked = entry_block(cross, cfg.portfolio.entry_block_top_vol_pct)
    rows = []
    for t, th in cfg.themes.items():
        if not th.enabled:
            continue
        ranked = cross[(cross["theme"] == t) & ~cross.index.isin(ov["exclude"])][["score", "subtheme"]]
        held_t = {s for s, ht in held.items() if ht == t}
        sig = select_theme(ranked, held_t, th.n_picks, cfg.portfolio.hold_buffer,
                           cfg.portfolio.max_share_per_subtheme, blocked)
        for s in ov["exclude"] & set(cross.index[cross["theme"] == t]):
            sig[s] = "SELL" if s in held_t else "EXCLUDED"
        for s in ov["include"] & set(cross.index[cross["theme"] == t]):
            if sig.get(s) not in ("BUY", "HOLD"):
                sig[s] = "BUY"
        order = ranked["score"].rank(ascending=False, method="first")
        for s, x in sig.items():
            r = cross.loc[s] if s in cross.index else pd.Series(dtype=object)
            row = {"theme": t, "symbol": s, "signal": x, "rank_in_theme": order.get(s),
                   "subtheme": r.get("subtheme"), "stage": r.get("stage"), "score": r.get("score"),
                   "entry_blocked_top_vol": s in blocked,
                   "override": "include" if s in ov["include"] else "exclude" if s in ov["exclude"] else ""}
            for g in [c for c in cross.columns if c.startswith("grp_")]:
                row[g] = r.get(g)
            if s in evidence.index:
                e = evidence.loc[s]
                row.update({"evidence_method": e.get("method"), "evidence_hits": e.get("hits"),
                            "evidence_keywords": e.get("matched"), "evidence_10k": e.get("filing_accession")})
            rows.append(row)
    order = {"BUY": 0, "HOLD": 1, "WAIT": 2, "SELL": 3, "EXCLUDED": 4}
    df = pd.DataFrame(rows)
    return df.sort_values(["theme", "signal", "rank_in_theme"], key=lambda c: c.map(order) if c.name == "signal"
                          else c).reset_index(drop=True)


def shortlist_markdown(df: pd.DataFrame, date: pd.Timestamp, cfg: ThemesConfig) -> str:
    md = [f"# Tema seçim listesi — {date.date()}", "",
          f"Yapılandırma: `{cfg.version}` (sabit, ön kayıtlı). Jev ağırlığı 0. TA katmanı listeyi değiştirmez, yalnızca "
          "zamanlama içindir; otomatik işlem yok.", "",
          "Sinyaller: BUY = yeni giriş, HOLD = tut (histerezis), SELL = çık, WAIT = yedek liste. "
          "Manuel override'lar yalnızca bu canlı listede uygulanır.", ""]
    grp = [c for c in df.columns if c.startswith("grp_")]
    for t, g in df.groupby("theme", sort=False):
        w = cfg.enabled_weights()[t]
        md += [f"## {t} (bütçe %{w * 100:.0f}, {cfg.themes[t].n_picks} seçim)", "",
               "| Sinyal | Sembol | Alt tema | Aşama | Skor | " + " | ".join(c[4:] for c in grp) +
               " | 10-K kanıtı |", "|---|---|---|---|---|" + "---|" * len(grp) + "---|"]
        for r in g.itertuples():
            ev = getattr(r, "evidence_keywords", "") or getattr(r, "evidence_method", "") or ""
            flag = " ⚠vol" if r.entry_blocked_top_vol else ""
            flag += f" ({r.override})" if r.override else ""
            vals = " | ".join("—" if pd.isna(getattr(r, c)) else f"{getattr(r, c):+.2f}" for c in grp)
            score = "—" if pd.isna(r.score) else f"{r.score:+.2f}"
            md.append(f"| {r.signal}{flag} | {r.symbol} | {r.subtheme} | {r.stage} | {score} | {vals} | "
                      f"{str(ev)[:80]} |")
        md.append("")
    return "\n".join(md) + "\n"
