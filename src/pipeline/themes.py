"""Theme layer commands (docs/ROADMAP.md, docs/THEMES_SPEC.md §10).

    python -m src.pipeline.themes t0-inventory
"""
from __future__ import annotations

import typer

from src.pipeline.cli_support import console, print_json, progress_printer, setup_logging
from src.pipeline.common import make_clients, open_context

app = typer.Typer(add_completion=False)


@app.callback()
def _group() -> None:
    """Theme layer tasks (T0-T7)."""


@app.command("t0-inventory")
def t0_inventory(db: str = typer.Option(None), skip_sic: bool = False) -> None:
    """T0: dump FMP sector/industry and EDGAR SIC distributions for the configured exchanges."""
    import pandas as pd

    from src.themes.config import load_themes_config
    from src.themes.inventory import (
        fmp_industry_inventory,
        industry_counts,
        mapping_proposal,
        sic_counts,
        sic_inventory,
        write_outputs,
    )
    setup_logging()
    ctx = open_context(db, progress_printer)
    cfg = load_themes_config()
    fmp, sec = make_clients(ctx)
    known = fmp.available_industries()
    inv = fmp_industry_inventory(fmp, cfg.universe.exchanges)
    counts = industry_counts(inv, known)
    sics = sic_counts(sic_inventory(sec, cfg.universe.exchanges)) if not skip_sic else pd.DataFrame()
    proposal = mapping_proposal(cfg, counts)
    paths = write_outputs(inv, counts, sics, proposal)
    print_json("T0", {"screener_rows": len(inv), "industries": int(counts["industry"].nunique()),
                      "sic_codes": len(sics), "configured_names": len(proposal),
                      "exact_matches": int(proposal["exact_match"].sum()),
                      "outputs": {k: str(v) for k, v in paths.items()}})
    miss = proposal[~proposal["exact_match"]]
    if not miss.empty:
        console.print("[yellow]configured names without an exact FMP match:[/]")
        console.print(miss[["theme", "subtheme", "configured", "closest"]].to_string(index=False))


if __name__ == "__main__":
    app()


THEME_BENCHMARKS_EXTRA = ["QQQ", "SPY"]


@app.command("t1-universe")
def t1_universe(db: str = typer.Option(None), skip_data: bool = False) -> None:
    """T1: NASDAQ+NYSE theme candidate pool; prices/splits/SEC fundamentals for candidates + theme ETFs only."""
    import json

    import pandas as pd

    from src.config import PROJECT_ROOT, load_config
    from src.data.fundamentals_loader import load_fundamentals
    from src.data.prices import load_prices, load_splits
    from src.themes.config import load_strict
    from src.themes.universe import build_candidates, candidate_counts
    setup_logging()
    ctx = open_context(db, progress_printer)
    cfg = load_strict()
    fmp, sec = make_clients(ctx)
    rep = build_candidates(ctx.con, fmp, sec, cfg)
    ctx.step("t1", f"candidates: {rep}")
    counts = candidate_counts(ctx.con)
    cands = [r[0] for r in ctx.con.execute("SELECT symbol FROM theme_candidates").fetchall()]
    etfs = sorted({b for t in cfg.themes.values() for b in t.benchmarks} | set(THEME_BENCHMARKS_EXTRA))
    if not skip_data:
        pr = load_prices(ctx.con, fmp, etfs + cands)
        rep["prices"] = {k: v for k, v in pr.items() if k != "failed"} | {"failed": len(pr.get("failed", {}))}
        have = {r[0] for r in ctx.con.execute("SELECT DISTINCT symbol FROM daily_prices").fetchall()}
        rep["splits"] = load_splits(ctx.con, fmp, [s for s in cands if s in have])
        ciks = [r[0] for r in ctx.con.execute("SELECT DISTINCT cik FROM theme_candidates WHERE cik IS NOT NULL"
                                              ).fetchall()]
        scfg = load_config("data")["sec"]
        rep["fundamentals"] = {k: v for k, v in load_fundamentals(
            ctx.con, sec, ciks, snapshot_min_date=pd.Timestamp(scfg["snapshot_min_date"]),
            workers=int(scfg.get("snapshot_workers", 4))).items() if k != "failed"}
    priced = ctx.con.execute("SELECT count(DISTINCT c.symbol) FROM theme_candidates c JOIN daily_prices p "
                             "USING (symbol)").fetchone()[0]
    rep["candidates_with_prices"] = int(priced)
    md = ["# T1 — Tema aday havuzu (aşama A)", "",
          "Aşama A yalnızca 10-K metni puanlanacak firmaları belirler; üyelik kararı vermez (THEMES_SPEC §3-A).",
          "FMP sanayi ve EDGAR SIC bugünkü değerlerdir (PIT değildir); filtre bilerek geniş tutulmuştur.", "",
          f"- Borsalar: {', '.join(rep['exchanges'])} (NYSE American hariç)",
          f"- Aday firma: **{rep['candidates']}** (aktif {rep['active']}, delist {rep['delisted']}); "
          f"10-K metni gereken: {rep['needs_10k']}; yabancı dosyalayan (20-F/40-F) çıkarılan: "
          f"{rep['excluded_foreign_filers']}; fiyatı olan: {rep['candidates_with_prices']}", "",
          "| Tema | Alt tema | Aday | NASDAQ | NYSE | Delist | Sadece SIC ile |", "|---|---|---|---|---|---|---|"]
    for r in counts.itertuples():
        md.append(f"| {r.theme} | {r.subtheme} | {r.candidates} | {r.nasdaq} | {r.nyse} | {r.delisted} | "
                  f"{r.via_sic_only} |")
    md += ["", "Not: bir firma birden çok alt temanın aday havuzunda olabilir; birincil alt tema T3'te 10-K ile belirlenir.",
           "", f"Veri yükleme özeti: `{json.dumps({k: v for k, v in rep.items() if k in ('prices', 'splits', 'fundamentals')}, default=str)}`"]
    out = PROJECT_ROOT / "reports" / "themes" / "T1_candidates.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print_json("T1", rep)
    console.print(f"wrote {out}")
