"""Theme layer commands (docs/ROADMAP.md, docs/THEMES_SPEC.md §10).

    python -m src.pipeline.themes t0-inventory
"""
from __future__ import annotations

from pathlib import Path

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
             limit: int = typer.Option(None, help="only the first N companies (sample run)"),
             retry_not_found: bool = typer.Option(False, help="re-download filings cached as item1_not_found")
             ) -> None:
    """T2: fetch and cache 10-K Item 1 text for candidates whose subthemes use keywords."""
    from src.themes.tasks import run_t2
    setup_logging()
    ctx = open_context(db, progress_printer)
    _, sec = make_clients(ctx)
    print_json("T2", run_t2(ctx, sec, workers, since, limit, retry_not_found))


@app.command("t2-samples")
def t2_samples(n: int = 10, seed: int = 20260930) -> None:
    """T2 review: n random cached Item 1 extractions (length, first/last 300 characters) + extraction statistics."""
    import gzip
    import json
    import random

    from src.config import PROJECT_ROOT
    from src.themes.edgar_text import CACHE_DIR
    files = sorted(CACHE_DIR.rglob("*.json.gz"))
    recs = []
    for p in files:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            recs.append(json.load(fh))
    ok = [r for r in recs if r.get("status") == "ok"]
    words = [r.get("item1_words", 0) for r in ok]
    md = ["# T2 — 10-K Item 1 çıkarımı: örnekler", "",
          f"Önbellekteki dosya: {len(recs)}; Item 1 bulunan: {len(ok)} (%{100 * len(ok) / max(1, len(recs)):.1f}); "
          f"bulunamayan: {len(recs) - len(ok)}. Kelime sayısı medyanı: "
          f"{sorted(words)[len(words) // 2] if words else 0}.", "",
          "Yöntem: HTML → metin (gizli XBRL başlıkları, script/style atlanır); Item 1 = 'Item 1' başlığından "
          "'Item 1A' (yoksa 'Item 2') başlığına kadar olan en uzun aralık (içindekiler tablosundaki kopyalar elenir).", ""]
    for r in random.Random(seed).sample(ok, min(n, len(ok))):
        text = r.get("item1", "")
        md += [f"## {r.get('cik')} — {r.get('form')} {r.get('accession')} (kabul {r.get('acceptance')})", "",
               f"Kelime: {r.get('item1_words')}, karakter: {len(text)}", "", "**İlk 300:**", "",
               "> " + text[:300].replace("\n", " "), "", "**Son 300:**", "", "> " + text[-300:].replace("\n", " "), ""]
    out = PROJECT_ROOT / "reports" / "themes" / "T2_item1_samples.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print_json("T2 samples", {"files": len(recs), "ok": len(ok), "report": str(out)})


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


@app.command("t5-preregister")
def t5_preregister() -> None:
    """T5: copy config/themes.yaml to research/preregistration/<version>.yaml + SHA256 (commit before t5-research)."""
    from src.themes.config import load_strict
    from src.themes.research.report import preregister
    cfg = load_strict()
    path, sha = preregister(cfg.version)
    print_json("T5 preregistration", {"file": str(path), "sha256": sha, "next": "git add + commit, then t5-research"})


@app.command("t5-research")
def t5_research(db: str = typer.Option(None), run_id: str = typer.Option(None)) -> None:
    """T5: research module §7.1-§7.9 on theme_feature_panel -> reports/themes/<run_id>/factor_explain.md + CSVs."""
    import pandas as pd

    from src.config import PROJECT_ROOT
    from src.data.french import french_monthly
    from src.data.prices import load_prices
    from src.themes.config import load_strict
    from src.themes.panel import load_closes, load_theme_panel, theme_lookahead_audit
    from src.themes.research.report import check_preregistration, write_report
    from src.themes.research.run import mom_consistency, run_research
    from src.themes.scoring import score_panel
    setup_logging()
    cfg = load_strict()
    sha = check_preregistration(cfg.version)
    ctx = open_context(db, progress_printer)
    audit = theme_lookahead_audit(ctx.con)
    if not audit["passed"]:
        console.print(f"[red]look-ahead audit failed: {audit}[/]")
        raise typer.Exit(1)
    fmp, _ = make_clients(ctx)
    load_prices(ctx.con, fmp, ["^VIX"])
    closes = load_closes(ctx.con, ["SPY", "^VIX"])
    panel = load_theme_panel(ctx.con)
    scores = score_panel(panel, cfg)
    run_id = run_id or f"{cfg.version}_{pd.Timestamp.now():%Y%m%d_%H%M}"
    out = PROJECT_ROOT / "reports" / "themes" / run_id
    tables = run_research(panel, scores, cfg, french_monthly(), closes["SPY"], closes.get("^VIX"), out)
    consistency = mom_consistency(ctx.con, PROJECT_ROOT / "docs" / "FACTOR_IC.md")
    el = panel[panel["eligible"] & (panel["rebalance_date"] >= pd.Timestamp(cfg.research.subperiods[0][0]))]
    meta = {"start": el["rebalance_date"].min().date(), "end": el["rebalance_date"].max().date(),
            "dates": el["rebalance_date"].nunique(), "rows": len(el)}
    path = write_report(tables, out, run_id, sha, audit, consistency, meta)
    print_json("T5", {"report": str(path), "consistency": consistency, "audit": audit})


@app.command("t6-backtest")
def t6_backtest(db: str = typer.Option(None), start: str = "2011-06-30",
                tag: str = typer.Option("", help="output suffix, e.g. v1r2 (keeps earlier reports)"),
                rf: bool = typer.Option(True, help="uninvested cash earns the French risk-free rate")) -> None:
    """T6: single fixed-config theme portfolio backtest, §8 success table and the current shortlist."""
    import numpy as np
    import pandas as pd

    from src.config import PROJECT_ROOT, load_config
    from src.data.french import french_monthly
    from src.features.store import load_market_data
    from src.themes.backtest import (
        ThemeBacktester,
        annualized,
        daily_rf,
        equity_period_returns,
        max_drawdown,
        period_returns,
        success_table,
        theme_indices,
    )
    from src.themes.config import load_strict
    from src.themes.membership import members_on
    from src.themes.panel import load_closes, load_theme_panel
    from src.themes.research.report import check_preregistration
    from src.themes.scoring import score_panel
    from src.themes.shortlist import build_shortlist, load_overrides, shortlist_markdown
    setup_logging()
    cfg = load_strict()
    sha = check_preregistration(cfg.version)
    ctx = open_context(db, progress_printer)
    panel = load_theme_panel(ctx.con)
    scores = score_panel(panel, cfg)
    md_ = load_market_data(ctx.con, sorted(panel["symbol"].unique()))
    from src.features.momentum import delisting_haircuts
    haircut = delisting_haircuts(md_.mats["close"], md_.mats["raw_close"], load_config("backtest")["costs"])
    bt = ThemeBacktester(panel, scores, cfg, md_.mats["open"], md_.mats["close"], haircuts=haircut)
    s0 = pd.Timestamp(start)
    rfd = daily_rf(french_monthly(), md_.calendar) if rf else None
    r1, r2 = bt.run(1.0, s0, rfd), bt.run(2.0, s0, rfd)
    dates = [d for d in bt.dates if d >= s0]
    idx = theme_indices(panel, md_.mats["close"], cfg, dates, haircut)
    port, port2 = equity_period_returns(r1.equity, dates), equity_period_returns(r2.equity, dates)
    succ = success_table(port, idx["composite"], port2, cfg.research.subperiods)
    etfs = sorted({b for t in cfg.themes.values() for b in t.benchmarks} | {"QQQ", "SPY"})
    ec = load_closes(ctx.con, etfs).reindex(md_.calendar)
    bench = {e: ec[e].reindex(pd.DatetimeIndex(dates)).pct_change() for e in ec.columns}
    # per-theme sleeves (gross, equal weight of the names held after each rebalance) vs the theme index
    h = r1.holdings
    sleeves = {}
    for t in idx.columns.drop("composite"):
        mem = {d: list(g["symbol"]) for d, g in h[h["theme"] == t].groupby("rebalance_date")}
        sleeves[t] = period_returns(md_.mats["close"], mem, dates, haircut)
    sl = pd.DataFrame(sleeves)
    out = PROJECT_ROOT / "reports" / "themes"
    frame = pd.DataFrame({"portfolio": port, "portfolio_2x_costs": port2}).join(idx, how="outer").join(
        sl.add_prefix("sleeve_gross_"), how="left")
    sfx = f"_{tag}" if tag else ""
    frame.to_csv(out / f"T6_period_returns{sfx}.csv")
    r1.trades.to_csv(out / f"T6_trades{sfx}.csv", index=False)
    c = succ["criteria"]

    def line(name, r):
        r = r.dropna()
        return (f"| {name} | {r.index.min().date() if len(r) else '—'} | {annualized(r):.2%} | "
                f"{r.std() * np.sqrt(12):.2%} | {max_drawdown(r):.2%} |") if len(r) else f"| {name} | — | — | — | — |"
    title_tag = f" — {tag}" if tag else ""
    md = [f"# T6 — Tema portföyü backtest (themes_v1, tek sabit yapılandırma){title_tag}", "",
          f"Ön kayıt SHA256 `{sha}`. Dönem {dates[0].date()} → {dates[-1].date()} ({len(dates)} ay). Jev ağırlığı 0. "
          "Parametre taraması yok; yapılandırma hiçbir parametre tahmin etmediği için tüm dönem örneklem dışıdır ve "
          "ön kayıtlı alt dönemler walk-forward katmanlarının yerini tutar.",
          "Maliyetler: mevcut model (komisyon, kayma, işlem maliyeti, Abdi–Ranaldo yarım spread); delist: son kapanış "
          f"eksi sembol bazlı kesinti (sıkıntılı delist %{load_config('backtest')['costs']['distress_haircut'] * 100:.0f}, "
          "diğerleri yapılandırılmış oran; portföy ve endeks aynı kuralı kullanır). Tema endeksleri maliyetsiz, aylık "
          "yeniden dengelenen eşit ağırlıklıdır.", "",
          "## §8 Başarı ölçütü (ön kayıtlı; CAGR hedefi değil)", "",
          "| Ölçüt | Değer | Sonuç |", "|---|---|---|",
          f"| Seçim katkısı > 0 alt dönemlerin ≥ 2/3'ünde | {c['subperiods_positive']} | {'✔' if c['c1_subperiods'] else '✘'} |",
          f"| Maks. düşüş, tema endeksinden en fazla 5 puan kötü | portföy {c['max_dd_portfolio']:.1%} / endeks "
          f"{c['max_dd_index']:.1%} | {'✔' if c['c2_drawdown'] else '✘'} |",
          f"| 2× maliyette seçim katkısı ≥ 0 | {c['contribution_2x_costs_ann']:+.2%}/yıl | "
          f"{'✔' if c['c3_costs_2x'] else '✘'} |",
          f"| **Sonuç** | seçim katkısı (tüm dönem) {c['contribution_ann']:+.2%}/yıl | "
          f"**{'GEÇTİ' if c['passed'] else 'GEÇMEDİ'}** |", "",
          "## Seçim katkısının istatistiği (aylık, aritmetik)", "",
          f"Aritmetik katkı {c.get('contribution_arith_ann', float('nan')):+.2%}/yıl, takip hatası "
          f"{c.get('tracking_error_ann', float('nan')):.2%}, bilgi oranı {c.get('information_ratio', float('nan')):+.2f}, "
          f"NW t {c.get('contribution_nw_t', float('nan')):+.2f}; gözlenen bilgi oranının %95 güvenle anlamlı olması "
          f"için gereken en kısa süre (MinTRL): {c.get('min_track_record_months', float('nan')):.0f} ay. "
          f"Nakit: {'risksiz faiz (French RF) işler' if rf else 'faiz işlemez'}.", "",
          "## Alt dönemler", "", "| Alt dönem | Ay | Portföy (yıllık) | Tema endeksi (yıllık) | Seçim katkısı |",
          "|---|---|---|---|---|"]
    for r in succ["subperiods"].itertuples():
        md.append(f"| {r.subperiod} | {r.months} | {r.portfolio_ann:.2%} | {r.index_ann:.2%} | "
                  f"{r.selection_contribution_ann:+.2%} |")
    md += ["", "## Karşılaştırma (aylık getirilerden; ETF'ler kendi başlangıç tarihlerinden)", "",
           "| Seri | Başlangıç | Yıllık getiri | Yıllık oynaklık | Maks. düşüş |", "|---|---|---|---|---|",
           line("Portföy (1× maliyet)", port), line("Portföy (2× maliyet)", port2),
           line("Bileşik tema endeksi", idx["composite"])]
    md += [line(f"Tema endeksi: {t}", idx[t]) for t in idx.columns.drop("composite")]
    md += [line(e, r) for e, r in bench.items()]
    md += ["", "## Tema kolları (brüt) vs tema endeksi", "",
           "Geometrik fark oynaklık sürüklenmesinden etkilenir (düşük oynaklıklı kol lehine); asıl ölçü aritmetik "
           "farktır.", "", "| Tema | Kol (geom.) | Endeks (geom.) | Geom. fark | Aritm. fark | t |",
           "|---|---|---|---|---|---|"]
    for t in sl.columns:
        a, b = annualized(sl[t]), annualized(idx[t].reindex(sl[t].dropna().index))
        dd = (sl[t] - idx[t]).dropna()
        tt = dd.mean() / dd.std(ddof=1) * np.sqrt(len(dd)) if len(dd) > 2 else float("nan")
        md.append(f"| {t} | {a:.2%} | {b:.2%} | {a - b:+.2%} | {dd.mean() * 12:+.2%} | {tt:+.2f} |")
    decision = ("Faktör seçimi canlı kullanıma girer (ROADMAP Adım 8-9)." if c["passed"] else
                "Faktör seçimi temayı geçemedi: tema içinde geniş eşit ağırlıklı sepet (veya tema ETF'i) tutulur; "
                "yalnızca nakit ömrü/sulandırma elemeleri korunur, TA zamanlama için kullanılır (ROADMAP Adım 7).")
    md += ["", "## Karar", "", decision, "",
           f"İşlem sayısı: {len(r1.trades)}; dosyalar: `T6_period_returns{sfx}.csv`, `T6_trades{sfx}.csv`."]
    (out / f"T6_backtest{sfx}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    # shortlist for the latest rebalance date (holdings before it = after the previous rebalance)
    last = bt.dates[-1]
    prev = [d for d in bt.dates if d < last][-1]
    held = {r.symbol: r.theme for r in h[h["rebalance_date"] == prev].itertuples()}
    cross = bt.cross[last]
    ev = members_on(membership_frame_full(ctx.con), last).drop_duplicates("symbol").set_index("symbol")
    sl_df = build_shortlist(cross, cfg, held, ev, load_overrides())
    sl_df.to_csv(out / f"shortlist_{last.date()}{sfx}.csv", index=False)
    (out / f"shortlist_{last.date()}{sfx}.md").write_text(shortlist_markdown(sl_df, last, cfg), encoding="utf-8")
    print_json("T6", {"criteria": c, "report": str(out / f"T6_backtest{sfx}.md")})


@app.command("t7-ta-table")
def t7_ta_table(db: str = typer.Option(None), shortlist: str = typer.Option(None, help="shortlist CSV (default: latest)")
                ) -> None:
    """T7: indicator + rule-state table for the BUY/HOLD names of the latest shortlist (run every interval_days)."""
    import pandas as pd

    from src.config import PROJECT_ROOT
    from src.features.store import load_market_data
    from src.themes.config import load_strict
    from src.themes.ta import indicator_table, load_rules, round_trips
    setup_logging()
    cfg = load_strict()
    rules = load_rules(PROJECT_ROOT / cfg.ta_layer.rules_file)
    rep = PROJECT_ROOT / "reports" / "themes"
    path = Path(shortlist) if shortlist else max(rep.glob("shortlist_*.csv"))
    sl = pd.read_csv(path)
    names = sl[sl["signal"].isin(["BUY", "HOLD"])]["symbol"].tolist()
    jpath = PROJECT_ROOT / cfg.ta_layer.journal_file
    entries = {}
    if jpath.exists() and jpath.stat().st_size > 0:
        _, lots = round_trips(pd.read_csv(jpath))
        if not lots.empty:
            entries = lots.groupby("symbol")["date"].min().to_dict()
    ctx = open_context(db, progress_printer)
    md_ = load_market_data(ctx.con, names)
    at = md_.calendar[-1]
    t = indicator_table(md_.mats["high"], md_.mats["low"], md_.mats["close"], names, at, rules, entries)
    t = t.join(sl.set_index("symbol")[["theme", "signal", "score"]], how="left")
    out = rep / "ta"
    out.mkdir(parents=True, exist_ok=True)
    t.to_csv(out / f"ta_{at.date()}.csv")
    cols = ["theme", "signal", "close", "sma50", "sma200", "rsi14", "adx14", "bb_pctb", "golden_cross_50_200",
            "pullback_to_50d", "trailing_stop_atr", "stop_hit"]
    lines = [f"# TA tablosu — {at.date()} ({rules['version']}, {rules['status']})", "",
             f"Kaynak liste: `{path.name}`. TA listeyi değiştirmez; yalnızca zamanlama önerir. Otomatik işlem yok.", "",
             "| Sembol | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for sym, r in t.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(("✔" if v else "") if isinstance(v, bool) else (f"{v:.2f}" if isinstance(v, float) else str(v)))
        lines.append(f"| {sym} | " + " | ".join(vals) + " |")
    (out / f"ta_{at.date()}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print_json("T7 table", {"as_of": str(at.date()), "names": len(t), "file": str(out / f"ta_{at.date()}.md")})


@app.command("t7-ta-eval")
def t7_ta_eval(db: str = typer.Option(None), journal: str = typer.Option(None)) -> None:
    """T7: evaluate the trade journal (base-rate hit rate, profit factor, profit/maxDD, month-start contribution)."""
    import pandas as pd

    from src.config import PROJECT_ROOT, load_config
    from src.features.store import load_market_data
    from src.themes.config import load_strict
    from src.themes.ta import evaluate_journal, evaluation_markdown, load_rules
    setup_logging()
    cfg = load_strict()
    rules = load_rules(PROJECT_ROOT / cfg.ta_layer.rules_file)
    j = pd.read_csv(Path(journal) if journal else PROJECT_ROOT / cfg.ta_layer.journal_file)
    ctx = open_context(db, progress_printer)
    md_ = load_market_data(ctx.con, sorted(j["symbol"].unique()) if len(j) else [])
    ev = evaluate_journal(j, md_.mats["open"], md_.mats["close"], load_config("backtest")["costs"])
    out = PROJECT_ROOT / "reports" / "themes" / "ta"
    out.mkdir(parents=True, exist_ok=True)
    (out / "ta_evaluation.md").write_text(evaluation_markdown(ev, rules["version"]), encoding="utf-8")
    if len(ev.get("table", [])):
        ev["table"].to_csv(out / "ta_evaluation_trades.csv", index=False)
    print_json("T7 eval", {k: v for k, v in ev.items() if k != "table"})


@app.command("search")
def search(db: str = typer.Option(None), trials: int = 500, seed: int = 20261001) -> None:
    """v2 free-search track (user decision 2026-10-01): seeded random search with measured overfitting."""
    import re

    from src.config import PROJECT_ROOT
    from src.themes.config import load_themes_config
    from src.themes.search_run import run_search, write_report
    setup_logging()
    cfg = load_themes_config()
    ctx = open_context(db, progress_printer)
    out = PROJECT_ROOT / "reports" / "themes" / "v2_search"
    res = run_search(ctx.con, cfg, trials, seed, out)
    v1r2 = None
    v1r2_md = PROJECT_ROOT / "reports" / "themes" / "T6_backtest_v1r2.md"
    if v1r2_md.exists():
        txt = v1r2_md.read_text(encoding="utf-8")
        m = re.search(r"Aritmetik katkı ([+-][\d.]+)%/yıl, takip hatası ([\d.]+)%, bilgi oranı ([+-][\d.]+)", txt)
        if m:
            v1r2 = {"contribution_arith_ann": float(m.group(1)) / 100, "tracking_error_ann": float(m.group(2)) / 100,
                    "information_ratio": float(m.group(3))}
    path = write_report(res, v1r2, out)
    ev = res["evaluation"]
    print_json("search", {k: ev[k] for k in ("selected", "design_ir", "holdout_ir", "wf_ir", "trials")}
               | {"pbo": ev["pbo"].get("pbo"), "dsr": ev["dsr_full_sample_best"].get("dsr"),
                  "exact_passed": res["success"]["criteria"]["passed"], "report": str(path)})


@app.command("forward")
def forward(db: str = typer.Option(None), eval_months: int = 36) -> None:
    """Record this month's forward (shadow) targets of the frozen v2 selection and of themes_v1-r2 (top-N)."""
    import json

    import pandas as pd

    from src.config import PROJECT_ROOT
    from src.portfolio.rebalance import theme_targets
    from src.themes import forward as F
    from src.themes.backtest import monthly_signals
    from src.themes.config import load_themes_config
    from src.themes.panel import load_theme_panel
    from src.themes.scoring import score_panel
    from src.themes.search import ScoreInputs, SearchConfig, tilt_targets
    setup_logging()
    cfg = load_themes_config()
    ctx = open_context(db, progress_printer)
    panel = load_theme_panel(ctx.con)
    d = panel["rebalance_date"].max()
    scores = score_panel(panel[panel["rebalance_date"] == d], cfg)
    si = ScoreInputs(panel[panel["rebalance_date"] == d], scores, cfg)
    sel = json.loads((PROJECT_ROOT / "reports" / "themes" / "v2_search" / "selected_config.json").read_text())
    evald = pd.Timestamp.now().normalize() + pd.DateOffset(months=eval_months)
    meta = F.freeze(ctx.con, "v2_selected", sel["config"], f"search {sel['key']}", evald,
                    sel.get("min_track_record_months"))
    c = meta["config"]
    sc = SearchConfig(tuple(sorted(c["group_mult"].items())), c["lam"], c["top_frac"],
                      tuple(sorted(c["budgets"].items())), c["speed"], c["rebalance_months"], c["vol_block"])
    cross = si.df.assign(score=si.scores(c["group_mult"]))
    tv2 = tilt_targets(cross, sc, cfg.portfolio.position_cap)
    info = cross.set_index("symbol")
    n2 = F.record(ctx.con, "v2_selected", d, pd.DataFrame({"symbol": tv2.index, "theme": info.loc[tv2.index, "theme"],
                                                           "weight": tv2.to_numpy(),
                                                           "score": info.loc[tv2.index, "score"].to_numpy()}))
    F.freeze(ctx.con, "v1r2_topn", {"construction": "themes_v1 top-N (pre-registered)"}, "themes_v1", evald)
    prev = ctx.con.execute("SELECT symbol, theme FROM theme_forward_targets WHERE model = 'v1r2_topn' AND "
                           "snapshot_date < ? ORDER BY snapshot_date DESC", [d.date()]).df()
    held = dict(zip(prev["symbol"], prev["theme"], strict=False)) if len(prev) else {}
    c1 = panel[(panel["rebalance_date"] == d) & panel["eligible"]].merge(
        scores[["symbol", "score"] + [x for x in scores.columns if x.startswith("grp_")]], on="symbol").set_index("symbol")
    sigs = monthly_signals(c1, cfg, held)
    keep = {t: [s for s, x in sg.items() if x in ("HOLD", "BUY")] for t, sg in sigs.items()}
    tv1 = theme_targets(keep, cfg.enabled_weights(), {t: th.n_picks for t, th in cfg.themes.items()},
                        cfg.portfolio.position_cap)
    n1 = F.record(ctx.con, "v1r2_topn", d, pd.DataFrame({"symbol": tv1.index, "theme": c1.loc[tv1.index, "theme"],
                                                         "weight": tv1.to_numpy(),
                                                         "score": c1.loc[tv1.index, "score"].to_numpy()}))
    print_json("forward", {"snapshot_date": str(d.date()), "v2_names": n2, "v1r2_names": n1,
                           "v2_frozen_new": meta["new"], "evaluation_date": str(meta["evaluation_date"])})


@app.command("forward-eval")
def forward_eval(db: str = typer.Option(None)) -> None:
    """Evaluate matured forward months of every tracked model against the composite theme index."""
    import pandas as pd

    from src.config import PROJECT_ROOT, load_config
    from src.features.store import load_market_data
    from src.themes import forward as F
    from src.themes.config import load_themes_config
    from src.themes.panel import load_theme_panel
    setup_logging()
    cfg = load_themes_config()
    ctx = open_context(db, progress_printer)
    F.init(ctx.con)
    snaps = ctx.con.execute("SELECT * FROM theme_forward_targets").df()
    meta = ctx.con.execute("SELECT model, source, frozen_at, evaluation_date FROM theme_forward_meta").df()
    panel = load_theme_panel(ctx.con)
    lines = ["# İleri (gölge) takip", "", "Tek temiz örneklem dışı kanıt. Yapılandırmalar donduruldu; aylık hedef "
             "ağırlıklar kaydedilir, olgunlaşan aylar kompozit tema endeksine karşı değerlendirilir.", "",
             "| Model | Kaynak | Donduruldu | Değerlendirme tarihi |", "|---|---|---|---|"]
    lines += [f"| {r.model} | {r.source} | {r.frozen_at} | {r.evaluation_date} |" for r in meta.itertuples()]
    if snaps.empty:
        lines += ["", "Henüz kayıt yok."]
    else:
        snaps["snapshot_date"] = pd.to_datetime(snaps["snapshot_date"])
        md_ = load_market_data(ctx.con, sorted(snaps["symbol"].unique()) + sorted(panel["symbol"].unique()))
        costs = load_config("backtest")["costs"]
        unit = (float(costs["slippage_bps"]) + float(costs["transaction_cost_bps"])) / 1e4
        real = F.realized(snaps, md_.mats["close"], panel[panel["eligible"]], cfg.enabled_weights(), unit)
        s = F.summary(real)
        lines += ["", f"Kayıtlı aylar: {snaps['snapshot_date'].nunique()}; olgunlaşan ay sayısı modele göre aşağıda.",
                  "", "| Model | Olgun ay | Katkı (yıllık) | IR | t |", "|---|---|---|---|---|"]
        lines += [f"| {r.model} | {r.months} | {r.contribution_ann:+.2%} | {r.ir:+.2f} | {r.t:+.2f} |"
                  for r in s.itertuples()]
    out = PROJECT_ROOT / "reports" / "themes" / "forward_tracking.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print_json("forward-eval", {"report": str(out), "snapshots": int(len(snaps))})


def membership_frame_full(con):
    import pandas as pd
    m = con.execute("SELECT symbol, theme, subtheme, valid_from, valid_to, method, hits, matched, filing_accession "
                    "FROM theme_membership").df()
    m["valid_from"], m["valid_to"] = pd.to_datetime(m["valid_from"]), pd.to_datetime(m["valid_to"])
    return m


if __name__ == "__main__":
    app()
