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


@app.command("t2-item1")
def t2_item1(db: str = typer.Option(None), workers: int = 6, since: str = "2009-01-01",
             limit: int = typer.Option(None, help="only the first N companies (sample run)")) -> None:
    """T2: fetch and cache 10-K Item 1 text for candidates whose subthemes use keywords."""
    from src.themes.tasks import run_t2
    setup_logging()
    ctx = open_context(db, progress_printer)
    _, sec = make_clients(ctx)
    print_json("T2", run_t2(ctx, sec, workers, since, limit))


@app.command("t3-membership")
def t3_membership(db: str = typer.Option(None)) -> None:
    """T3: point-in-time theme membership, review CSV and theme-date firm counts."""
    from src.themes.config import load_strict
    from src.themes.tasks import run_t3
    setup_logging()
    ctx = open_context(db, progress_printer)
    _, sec = make_clients(ctx)
    print_json("T3", run_t3(ctx, sec, load_strict()))


@app.command("t3r-review")
def t3r_review(db: str = typer.Option(None), n: int = 120) -> None:
    """T3r (Gate 2): label a stratified sample of current members with FMP profile descriptions."""
    from src.themes.config import load_strict
    from src.themes.tasks import run_t3r
    setup_logging()
    ctx = open_context(db, progress_printer)
    fmp, _ = make_clients(ctx)
    print_json("T3r", run_t3r(ctx, fmp, load_strict(), n))


@app.command("t4b-verify")
def t4b_verify(n: int = 20, seed: int = 20260930) -> None:
    """T4b: FMP earnings dates vs 8-K Item 2.02 acceptance dates on n random firm-quarters (US theme industries)."""
    import pandas as pd

    from src.config import PROJECT_ROOT
    from src.data.fmp import FmpClient
    from src.data.sec import SecClient
    from src.themes.config import load_strict
    from src.themes.earnings import AGREEMENT_THRESHOLD, compare_sample
    setup_logging()
    cfg = load_strict()
    inv = pd.read_csv(PROJECT_ROOT / "research" / "themes" / "fmp_screener_inventory.csv")
    inv = inv[inv["industry"].isin(cfg.all_fmp_industries()) & (inv["country"] == "US")]
    sec = SecClient()
    tick = pd.DataFrame(sec.company_tickers_exchange())[["ticker", "cik"]].drop_duplicates("ticker")
    pool = inv.merge(tick, left_on="symbol", right_on="ticker")[["symbol", "cik"]]
    res = compare_sample(FmpClient(), sec, pool, n=n, seed=seed)
    out = PROJECT_ROOT / "research" / "themes" / "T4b_earnings_dates_sample.csv"
    res.to_csv(out, index=False)
    same = float(res["agree_same_day"].mean())
    print_json("T4b", {"pool": len(pool), "sample": len(res), "same_day": same,
                       "within_1_day": float(res["agree_within_1"].mean()),
                       "decision": "fmp_dates" if same >= AGREEMENT_THRESHOLD else "8k_dates", "csv": str(out)})


@app.command("t4b-events")
def t4b_events(db: str = typer.Option(None), workers: int = 4) -> None:
    """T4b: announcement events (8-K Item 2.02 timing + FMP realized EPS) for all theme candidates."""
    from src.themes.earnings import build_earnings_events
    from src.themes.tasks import sessions
    setup_logging()
    ctx = open_context(db, progress_printer)
    fmp, sec = make_clients(ctx)
    cands = ctx.con.execute("SELECT symbol, cik FROM theme_candidates WHERE cik IS NOT NULL").df()
    print_json("T4b events", build_earnings_events(ctx.con, fmp, sec, cands, sessions(ctx.con), workers))


@app.command("t4-panel")
def t4_panel(db: str = typer.Option(None)) -> None:
    """T4: build theme_feature_panel (PIT members x month-ends) and write a coverage report."""
    from src.config import PROJECT_ROOT
    from src.data.prices import load_prices
    from src.features.theme_features import OIL_SYMBOL
    from src.themes.config import KNOWN_FACTORS, load_strict
    from src.themes.earnings import load_events
    from src.themes.panel import build_theme_panel
    setup_logging()
    ctx = open_context(db, progress_printer)
    cfg = load_strict()
    fmp, _ = make_clients(ctx)
    load_prices(ctx.con, fmp, [OIL_SYMBOL])
    has_ev = ctx.con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'earnings_events'"
                             ).fetchone()[0]
    events = load_events(ctx.con) if has_ev else None
    panel = build_theme_panel(ctx.con, cfg, events=events)
    el = panel[panel["eligible"]]
    counts = el.groupby(["rebalance_date", "theme"]).size().unstack(fill_value=0)
    minimum = cfg.research.min_names_per_date
    md = ["# T4 — Tema özellik paneli (`theme_feature_panel`)", "",
          f"Satır: {len(panel)}, uygun (eligible): {len(el)}, tarih: {panel['rebalance_date'].nunique()} "
          f"({panel['rebalance_date'].min().date()} → {panel['rebalance_date'].max().date()}).", "",
          "## Tema başına uygun firma sayısı (aylık)", "", "| Tema | Ortalama | Min | Maks | n<15 olan ay |",
          "|---|---|---|---|---|"]
    for t in counts.columns:
        s = counts[t]
        md.append(f"| {t} | {s.mean():.1f} | {s.min()} | {s.max()} | {(s < minimum).sum()} |")
    md += ["", "## Faktör kapsamı (uygun satırlarda dolu oran)", "", "| Faktör | " + " | ".join(counts.columns) + " |",
           "|---|" + "---|" * len(counts.columns)]
    for f in sorted(KNOWN_FACTORS):
        if f in el:
            cov = el.groupby("theme")[f].apply(lambda s: s.notna().mean())
            md.append(f"| `{f}` | " + " | ".join(f"{cov.get(t, 0):.0%}" for t in counts.columns) + " |")
    md += ["", "## Aşama dağılımı (uygun satırlar)", "", "| Tema | Aşama | Satır |", "|---|---|---|"]
    md += [f"| {t} | {s} | {n} |" for (t, s), n in el.groupby(["theme", "stage"]).size().items()]
    md += ["", "Etiketler (`label_fwd_<h>`, `label_fwd_<h>_theme`) yalnızca araştırma hedefidir; skorlama okumaz."]
    out = PROJECT_ROOT / "reports" / "themes" / "T4_panel.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print_json("T4 panel", {"rows": len(panel), "eligible": len(el), "events": bool(events)})
    console.print(f"wrote {out}")


@app.command("t5a-french")
def t5a_french() -> None:
    """T5a: download/cache Kenneth French FF3, FF5, MOM, RF (monthly) and report coverage."""
    from src.config import PROJECT_ROOT
    from src.data.french import CACHE_DIR, FILES, coverage, french_monthly
    setup_logging()
    df = french_monthly()
    cov = coverage(df)
    md = ["# T5a — Kenneth French veri kütüphanesi", "",
          f"Kaynak: {', '.join(f for f, _ in FILES.values())} (aylık tablo; yüzde → ondalık; ay sonu indeks).",
          f"Önbellek: `{CACHE_DIR.relative_to(PROJECT_ROOT).as_posix()}/` (30 gün; ağ yoksa eski önbellek ya da elle "
          "indirilen zip kullanılır).", "",
          "| Seri | Başlangıç | Bitiş | Ay |", "|---|---|---|---|"]
    md += [f"| `{c}` | {r.start} | {r.end} | {r.months} |" for c, r in cov.iterrows()]
    md += ["", "Adlandırma: dış kıyas faktörleri `ff_`/`ff5_` önekli; `mimic_` yalnızca projenin kendi faktör-taklit "
           "portföyleri, `fmp_` yalnızca FMP alanları içindir.",
           "Kontroller (`src/features/theme_features.py`): `beta_252d` = SPY'a karşı günlük CAPM betası (son 252 seans, "
           "en az 200 gözlem); `size_ln_mcap` = ln(piyasa değeri, USD).",
           "Hizalama: portföy getirileri ay içindeki son işlem gününde damgalanır ve `to_month_end` ile takvim ay sonuna "
           "taşınır (test: `tests/test_french.py`)."]
    out = PROJECT_ROOT / "reports" / "themes" / "T5a_french.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print_json("T5a", {k: {kk: str(vv) for kk, vv in v.items()} for k, v in cov.T.to_dict().items()})
    console.print(f"wrote {out}")


if __name__ == "__main__":
    app()
