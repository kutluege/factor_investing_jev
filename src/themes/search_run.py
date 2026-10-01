"""Run the themes v2 search end to end and write ``reports/themes/v2_search/`` (Turkish report + CSVs)."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from src.config import load_config
from src.data.french import french_monthly
from src.features.momentum import delisting_haircuts
from src.features.store import load_market_data
from src.themes.backtest import (
    ThemeBacktester,
    annualized,
    contribution_stats,
    daily_rf,
    equity_period_returns,
    max_drawdown,
    success_table,
    theme_indices,
)
from src.themes.config import ThemesConfig
from src.themes.panel import load_theme_panel
from src.themes.scoring import score_panel
from src.themes.search import (
    PeriodData,
    ScoreInputs,
    SearchConfig,
    evaluate_search,
    information_ratio,
    sample_configs,
    simulate,
)

log = logging.getLogger(__name__)

START = pd.Timestamp("2011-06-30")
DESIGN_END = pd.Timestamp("2020-12-31")
FIRST_WF_YEAR = 2016


def _trial_metrics(sim: pd.DataFrame, design_end: pd.Timestamp) -> dict:
    d = sim.index <= design_end
    net = sim["net"]
    return {"ir_full": information_ratio(sim["contribution"]), "ir_design": information_ratio(sim.loc[d, "contribution"]),
            "ir_holdout": information_ratio(sim.loc[~d, "contribution"]),
            "contribution_ann": float(sim["contribution"].mean() * 12), "net_ann": annualized(net),
            "sharpe_net": float(net.mean() / net.std(ddof=1) * np.sqrt(12)), "max_dd": max_drawdown(net),
            "turnover_ann": float(sim["turnover"].mean() * 12), "cost_ann": float(sim["cost"].mean() * 12),
            "invested_avg": float(sim["invested"].mean()), "names_avg": float(sim["names"].mean())}


def run_search(con: duckdb.DuckDBPyConnection, cfg: ThemesConfig, n_trials: int, seed: int, out_dir: Path) -> dict:
    panel = load_theme_panel(con)
    base_scores = score_panel(panel, cfg)
    si = ScoreInputs(panel, base_scores, cfg)
    md = load_market_data(con, sorted(panel["symbol"].unique()))
    costs = load_config("backtest")["costs"]
    haircut = delisting_haircuts(md.mats["close"], md.mats["raw_close"], costs)
    french = french_monthly()
    rfd = daily_rf(french, md.calendar)
    dates = [d for d in sorted(panel["rebalance_date"].unique()) if d >= START]
    pdata = PeriodData(md.mats["close"], dates, haircut, rfd, panel[panel["eligible"]], cfg, costs)
    themes = [t for t, th in cfg.themes.items() if th.enabled]
    configs = sample_configs(si.groups, themes, cfg.enabled_weights(), n_trials, seed)
    contrib, nets, rows = {}, {}, []
    for i, c in enumerate(configs):
        sim = simulate(c, si, pdata, cfg.portfolio.position_cap)
        contrib[c.key], nets[c.key] = sim["contribution"], sim["net"]
        rows.append({"key": c.key, **_trial_metrics(sim, DESIGN_END), "config": json.dumps(c.as_dict())})
        if (i + 1) % 50 == 0:
            log.info("search: %d/%d trials", i + 1, len(configs))
    C = pd.DataFrame(contrib).dropna(how="all")
    trials = pd.DataFrame(rows)
    ev = evaluate_search(C.dropna(), DESIGN_END, START, FIRST_WF_YEAR)
    chosen = next(c for c in configs if c.key == ev["selected"])

    # exact validation of the selected configuration (execution at next open, full cost model, RF on cash)
    sc = si.df[["rebalance_date", "symbol"]].assign(score=si.scores(dict(chosen.group_mult)))
    bt = ThemeBacktester(panel, sc, cfg, md.mats["open"], md.mats["close"], haircuts=haircut)
    ex1, ex2 = bt.run(1.0, START, rfd, tilt=chosen), bt.run(2.0, START, rfd, tilt=chosen)
    rdates = [d for d in bt.dates if d >= START]
    idx = theme_indices(panel, md.mats["close"], cfg, rdates, haircut)
    p1, p2 = equity_period_returns(ex1.equity, rdates), equity_period_returns(ex2.equity, rdates)
    succ = success_table(p1, idx["composite"], p2, cfg.research.subperiods)
    exact_contrib = (p1 - idx["composite"].reindex(p1.index)).dropna()
    hold_stats = contribution_stats(exact_contrib[exact_contrib.index > DESIGN_END])

    out_dir.mkdir(parents=True, exist_ok=True)
    trials.to_csv(out_dir / "trials.csv", index=False)
    C.to_csv(out_dir / "contribution_matrix.csv")
    pd.DataFrame({"exact_1x": p1, "exact_2x": p2, "composite_index": idx["composite"]}).to_csv(
        out_dir / "selected_exact_returns.csv")
    con.execute("CREATE OR REPLACE TABLE theme_search_trials AS SELECT * FROM trials")
    (out_dir / "selected_config.json").write_text(json.dumps(
        {"key": chosen.key, "config": chosen.as_dict(), "selected_on": f"{START.date()}..{DESIGN_END.date()}",
         "min_track_record_months": hold_stats.get("min_track_record_months")}, indent=2, default=str),
        encoding="utf-8")
    return {"trials": trials, "evaluation": ev, "chosen": chosen, "success": succ, "holdout_exact": hold_stats,
            "exact_1x": p1, "exact_2x": p2, "index": idx, "n_trials": len(configs), "dates": rdates,
            "trades": len(ex1.trades)}


def _cfg_lines(c: SearchConfig) -> list[str]:
    d = c.as_dict()
    gm = ", ".join(f"{k} ×{v:g}" for k, v in d["group_mult"].items())
    bd = ", ".join(f"{k} %{v * 100:.0f}" for k, v in d["budgets"].items())
    return [f"- Grup ağırlık çarpanları: {gm}", f"- Tilt gücü λ = {c.lam:g}; tutulan üst dilim = %{c.top_frac * 100:.0f}",
            f"- Tema bütçeleri: {bd}", f"- Yeniden dengeleme: her {c.rebalance_months} ayda bir, hız {c.speed:g}",
            f"- Oynaklık bloğu: en oynak %{c.vol_block * 100:.0f}"]


def write_report(res: dict, v1r2: dict | None, out_dir: Path) -> Path:
    ev, tr, s = res["evaluation"], res["trials"], res["success"]["criteria"]
    pbo = ev["pbo"].get("pbo")
    dsr = ev["dsr_full_sample_best"].get("dsr")
    md = ["# themes v2 — serbest arama, ölçülen aşırı uyum", "",
          "**Durum: ARAMA İZİ (örneklem içi).** Kullanıcı kararıyla (2026-10-01) CLAUDE.md §3 bu iz için geçersiz "
          "kılındı; themes_v1 kaydı dondurulmuştur. Faktör listesi değişmedi; grup ağırlıkları, tilt kurulumu, tema "
          "bütçeleri, yeniden dengeleme hızı/sıklığı ve oynaklık bloğu arandı. Ölçüt: kompozit tema endeksine karşı "
          "net seçim katkısının bilgi oranı (IR).", "",
          "## Aşırı uyum ölçümü (asıl sonuç)", "",
          "| Ölçü | Değer | Yorum |", "|---|---|---|",
          f"| Deneme sayısı | {res['n_trials']} | hepsi `trials.csv` içinde |",
          f"| Tasarım penceresi (2011-07→2020-12) IR, seçilen | {ev['design_ir']:+.2f} | seçim burada yapıldı (iyimser) |",
          f"| **Tutma dönemi (2021-01→) IR, seçilen** | **{ev['holdout_ir']:+.2f}** | seçimde hiç kullanılmadı |",
          f"| Tutma dönemi katkı (aritm., yıllık) | {ev['holdout_contribution_ann']:+.2%} | {ev['holdout_months']} ay |",
          f"| Seçilenin tutma dönemindeki yüzdelik sırası | %{ev['holdout_percentile_of_selected'] * 100:.0f} | "
          "%50 = tesadüf |",
          f"| İç içe walk-forward IR (yıllık yeniden seçim) | {ev['wf_ir']:+.2f} | gerçekçi tahmin, "
          f"{ev['wf_months']} ay |",
          f"| İç içe walk-forward katkı (yıllık) | {ev['wf_contribution_ann']:+.2%} | |",
          f"| PBO (CSCV, tüm denemeler) | {pbo if pbo is None else f'{pbo:.0%}'} | > %50: seçim kalıcı değil |",
          f"| Deflated Sharpe (tam örneklem en iyisi) | {dsr if dsr is None else f'{dsr:.2f}'} | < 0,95: anlamlı değil |",
          "", "## Seçilen yapılandırma (tasarım penceresinde en yüksek IR)", ""]
    md += _cfg_lines(res["chosen"])
    md += ["", "## Seçilenin tam (exact) backtest'i — sonraki açılışta işlem, tüm maliyet modeli, nakit RF", "",
           "| Ölçü | Değer |", "|---|---|",
           f"| §8 ölçütü (alt dönem, düşüş, 2× maliyet) | {s['subperiods_positive']}, "
           f"{'✔' if s['c2_drawdown'] else '✘'}, {'✔' if s['c3_costs_2x'] else '✘'} → "
           f"**{'GEÇTİ' if s['passed'] else 'GEÇMEDİ'}** |",
           f"| Seçim katkısı (aritm., tüm dönem) | {s.get('contribution_arith_ann', float('nan')):+.2%}/yıl, "
           f"NW t {s.get('contribution_nw_t', float('nan')):+.2f} |",
           f"| Takip hatası / IR | {s.get('tracking_error_ann', float('nan')):.2%} / "
           f"{s.get('information_ratio', float('nan')):+.2f} |",
           f"| 2× maliyette katkı (geom.) | {s['contribution_2x_costs_ann']:+.2%}/yıl |",
           f"| Maks. düşüş portföy / endeks | {s['max_dd_portfolio']:.1%} / {s['max_dd_index']:.1%} |",
           f"| Tutma dönemi (exact) katkı / IR | {res['holdout_exact'].get('contribution_arith_ann', float('nan')):+.2%} / "
           f"{res['holdout_exact'].get('information_ratio', float('nan')):+.2f} |",
           f"| Portföy yıllık getiri / endeks | {annualized(res['exact_1x']):.2%} / "
           f"{annualized(res['index']['composite'].reindex(res['exact_1x'].index)):.2%} |",
           f"| İşlem sayısı | {res['trades']} |", ""]
    if v1r2:
        md += ["## Karşılaştırma: themes_v1-r2 (veri düzeltmeli v1, ilk-N)", "",
               f"Aritmetik katkı {v1r2.get('contribution_arith_ann', float('nan')):+.2%}/yıl, IR "
               f"{v1r2.get('information_ratio', float('nan')):+.2f}, takip hatası "
               f"{v1r2.get('tracking_error_ann', float('nan')):.2%} (bkz. `T6_backtest_v1r2.md`).", ""]
    q = tr["ir_design"].quantile([0.1, 0.5, 0.9])
    qh = tr["ir_holdout"].quantile([0.1, 0.5, 0.9])
    md += ["## Deneme dağılımı", "",
           f"Tasarım IR yüzdelikleri (10/50/90): {q.iloc[0]:+.2f} / {q.iloc[1]:+.2f} / {q.iloc[2]:+.2f}; tutma dönemi: "
           f"{qh.iloc[0]:+.2f} / {qh.iloc[1]:+.2f} / {qh.iloc[2]:+.2f}. Tasarım ve tutma IR'ı arasındaki sıra "
           f"korelasyonu: {tr['ir_design'].corr(tr['ir_holdout'], method='spearman'):+.2f} (yakın 0 → tasarımda iyi "
           "görünen, sonra iyi kalmıyor).", "",
           "## Yorum kuralları", "",
           "- Tek temiz örneklem dışı kanıt ileri (gölge) takiptir (`themes forward`).",
           "- Tasarım IR'ı seçim yanlılığı içerir; karar için tutma dönemi, walk-forward, PBO ve DSR birlikte okunur.",
           "- Bu iz CLAUDE.md §3'ün kullanıcı tarafından geçersiz kılınmasıyla yürütülmüştür (`docs/CHANGELOG_THEMES.md`)."]
    path = out_dir / "v2_search.md"
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return path
