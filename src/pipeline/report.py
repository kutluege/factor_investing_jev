"""Render a stored research run as a Markdown report (docs/RESULTS.md)."""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from src.config import PROJECT_ROOT


def _pct(v, nd=1) -> str:
    return "—" if v is None or v != v else f"{v * 100:.{nd}f}%"


def _num(v, nd=2) -> str:
    return "—" if v is None or v != v else f"{v:.{nd}f}"


def _metrics_row(label: str, m: dict) -> str:
    return (f"| {label} | {_pct(m.get('cagr'))} | {_pct(m.get('annual_volatility'))} | {_num(m.get('sharpe'))} | "
            f"{_pct(m.get('max_drawdown'))} | {_num(m.get('calmar'))} | {_pct(m.get('monthly_win_rate'), 0)} | "
            f"{_num(m.get('turnover_annual'), 1)} |")


def render(con: duckdb.DuckDBPyConnection, run_id: str | None = None) -> str:
    if run_id is None:
        row = con.execute("SELECT run_id FROM backtest_runs WHERE status='completed' ORDER BY created_at DESC LIMIT 1"
                          ).fetchone()
        if row is None:
            raise RuntimeError("no completed backtest runs")
        run_id = row[0]
    created, commit, snap, cfg, folds, metrics, diag, fsid = con.execute(
        "SELECT created_at, git_commit, data_snapshot, config, folds, metrics, diagnostics, jev_feature_set_id "
        "FROM backtest_runs WHERE run_id = ?", [run_id]).fetchone()
    m, d, snap, folds = json.loads(metrics), json.loads(diag), json.loads(snap), json.loads(folds)
    best = m["best_full_period"]
    eq = con.execute("SELECT series, date, equity FROM backtest_equity WHERE run_id = ?", [run_id]).df()
    lines = [f"# Research results — run `{run_id}`", "",
             f"Generated from the stored run (created {created}, git `{(commit or 'n/a')[:10]}`). "
             f"Data: {snap['prices']['symbols']} symbols with prices {snap['prices']['first']} → {snap['prices']['last']}, "
             f"{snap['facts']['companies']} companies with SEC facts, {snap['securities']['inactive']} delisted securities "
             f"in the master. Configurations tested: {m.get('n_configs')}. Walk-forward folds: {len(folds)}.", ""]

    # --- honest out-of-sample ---------------------------------------------------------------------------------
    lines += ["## 1. Honest out-of-sample performance (nested walk-forward)", "",
              "Each fold's configuration was chosen using only training-window performance, then traded in the test "
              "window (switching costs included). This is the performance estimate to rely on.", "",
              "| Strategy | CAGR | Volatility | Sharpe | Max DD | Calmar | Win months | Turnover/yr |",
              "|---|---|---|---|---|---|---|---|"]
    for key, n in m.get("nested_walk_forward", {}).items():
        met = n.get("metrics") or {}
        if met:
            lines.append(_metrics_row(n.get("label", key), met))
    nw = m.get("nested_walk_forward", {})
    main_key = "promotion_quant_only" if "promotion_quant_only" in nw else next(iter(nw), None)
    wf = (nw.get(main_key) or {}).get("metrics") or {}
    for bname in ("EW_universe", "QQQ", "SPY"):
        b = wf.get(f"bench_{bname}")
        if b:
            lines.append(f"| Benchmark {bname} (same period) | {_pct(b.get('cagr'))} | — | — | {_pct(b.get('max_drawdown'))} "
                         f"| — | — | — |")
    lines.append("")
    for key, n in m.get("nested_walk_forward", {}).items():
        met = n.get("metrics") or {}
        for bname in ("EW_universe", "QQQ", "SPY"):
            b = met.get(f"bench_{bname}")
            if b:
                lines.append(f"- {n.get('label', key)} vs {bname}: excess CAGR {_pct(b.get('excess_cagr'))}, beta "
                             f"{_num(b.get('beta'))}, alpha {_pct(b.get('alpha_annual'))}, information ratio "
                             f"{_num(b.get('information_ratio'))}, tracking error {_pct(b.get('tracking_error'))}")
    picks = (nw.get(main_key) or {}).get("picks", [])
    if picks:
        lines += ["", f"Model held per test fold ({(nw.get(main_key) or {}).get('label', main_key)}):", "",
                  "| Test start | Preset | N | Min market cap | Decision |", "|---|---|---|---|---|"]
        for p in picks:
            cap = p.get("min_market_cap")
            lines.append(f"| {p['test_start']} | {p['preset']} | {p.get('portfolio_size', '—')} | "
                         f"{'—' if cap is None else f'${cap / 1e6:,.0f}M'} | {p.get('reason', '')} |")

    # --- overfitting ------------------------------------------------------------------------------------------
    v = m.get("validation", {})
    lines += ["", "## 2. Overfitting controls", ""]
    pbo = v.get("pbo") or {}
    lines.append(f"- Probability of backtest overfitting (CSCV, {pbo.get('configs', '—')} configurations, "
                 f"{pbo.get('months', '—')} months): **{_pct(pbo.get('pbo'), 0)}** (< 50% means in-sample winners "
                 "tend to stay above median out of sample).")
    for k, ds in v.items():
        if k.startswith("deflated_sharpe_") and isinstance(ds, dict) and ds.get("dsr") is not None:
            lines.append(f"- Deflated Sharpe ratio, {k.replace('deflated_sharpe_', '')}: **{_pct(ds['dsr'], 0)}** "
                         f"probability the true Sharpe exceeds the best of {ds['trials']} random trials "
                         f"(annualized Sharpe {_num(ds['annualized_sharpe'])}).")

    # --- selected configuration -------------------------------------------------------------------------------
    cfgb = m["best_config"]
    lines += ["", "## 3. Configuration selected on all folds (the production challenger)", "",
              f"`{json.dumps({k: v for k, v in cfgb.items() if k != 'family_weights'})}`", "",
              f"Theme weights: `{json.dumps(cfgb.get('family_weights'))}`", "",
              "Full-period simulation of this configuration (in-sample for the selection itself; see §1 for the "
              "honest estimate):", "",
              "| Strategy | CAGR | Volatility | Sharpe | Max DD | Calmar | Win months | Turnover/yr |",
              "|---|---|---|---|---|---|---|---|", _metrics_row("Selected configuration", best)]
    for bname in ("EW_universe", "QQQ", "SPY"):
        b = best.get(f"bench_{bname}")
        if b:
            lines.append(f"| {bname} | {_pct(b.get('cagr'))} | — | — | {_pct(b.get('max_drawdown'))} | — | — | — |")
    oos = m.get("best_oos_summary", {})
    lines += ["", f"Across walk-forward test folds: median CAGR {_pct(oos.get('median_cagr'))}, median Sharpe "
              f"{_num(oos.get('median_sharpe'))}, worst-fold max drawdown {_pct(oos.get('worst_fold_max_drawdown'))}."]

    # --- factor research ----------------------------------------------------------------------------------------
    fr = m.get("factor_research", {})
    if fr:
        lines += ["", "## 4. Factor research (cross-sectional rank IC of theme scores)", "",
                  "| Theme | " + " | ".join(f"rank IC {h}" for h in fr) + " | " + " | ".join(f"t {h}" for h in fr) + " |",
                  "|---|" + "---|" * (2 * len(fr))]
        themes = sorted(next(iter(fr.values()))["mean_rank_ic"])
        for t in themes:
            lines.append(f"| {t} | " + " | ".join(_num(fr[h]["mean_rank_ic"].get(t), 3) for h in fr) + " | "
                         + " | ".join(_num(fr[h]["rank_ic_t"].get(t), 1) for h in fr) + " |")

    # --- stability / sensitivity / Jev ----------------------------------------------------------------------------
    st = m.get("stability", {})
    if st:
        lines += ["", "## 5. Stability of the top configurations", "",
                  f"Top {st.get('top_k')} configurations. Theme inclusion share: `{json.dumps(st.get('family_inclusion_share'))}`",
                  "", f"Parameter frequency: `{json.dumps(st.get('parameter_frequency'))}`"]
    sens = pd.DataFrame(m.get("sensitivity", []))
    if not sens.empty:
        lines += ["", "## 6. Sensitivity (one parameter at a time around the selected configuration)", "",
                  "| Parameter | Value | Median fold CAGR | Median Sharpe | Worst-fold DD | Turnover |", "|---|---|---|---|---|---|"]
        for r in sens.itertuples():
            lines.append(f"| {r.parameter} | {r.value} | {_pct(r.median_cagr)} | {_num(r.median_sharpe)} | "
                         f"{_pct(r.worst_fold_max_drawdown)} | {_num(r.turnover, 1)} |")
    jev = m.get("jev", {})
    lines += ["", "## 7. Jev", "",
              f"Jev features used: {jev.get('used')} (feature set `{fsid}`; requested `{jev.get('model_requested')}`, "
              f"resolved version {jev.get('resolved_version')}).", ""]
    if m.get("ablation"):
        lines.append(f"Ablation (fold medians): `{json.dumps(m['ablation'], default=str)}`")
    lines.append("Historical Jev results are an upper bound (LLM look-ahead); production uses Jev only after forward "
                 "validation (see docs/RESEARCH.md §5).")

    # --- diagnostics ----------------------------------------------------------------------------------------------
    lines += ["", "## 8. Diagnostics", ""]
    for f in d.get("flags", []):
        lines.append(f"- **{f['severity']}** `{f['code']}`: {f['message']}")
    lines.append(f"- Look-ahead audit: {d.get('lookahead_audit')}")
    lines += ["", f"Costs assumed: `{json.dumps(m.get('costs'))}`", ""]
    if not eq.empty:
        last = eq.sort_values("date").groupby("series").tail(1)
        lines.append("Ending equity by series ($10,000 start): " + ", ".join(
            f"{r.series} ${r.equity:,.0f}" for r in last.itertuples()))
    return "\n".join(lines) + "\n"


def write(con: duckdb.DuckDBPyConnection, run_id: str | None = None, path: Path | None = None) -> Path:
    path = path or PROJECT_ROOT / "docs" / "RESULTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(con, run_id), encoding="utf-8")
    return path
