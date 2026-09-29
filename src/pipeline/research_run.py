"""Historical Jev generation (Stage A) and research/backtest runs (Stage B) with full persistence."""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import numpy as np
import pandas as pd

from src.backtest.diagnostics import run_diagnostics
from src.backtest.engine import Backtester, JevFeatures
from src.backtest.folds import walk_forward_folds
from src.backtest.metrics import information_coefficients, performance, quantile_spreads
from src.backtest.research import Researcher, summarize_folds
from src.backtest.validation import deflated_sharpe, ew_universe_benchmark, monthly_returns_matrix, pbo_cscv
from src.config import all_configs, load_config
from src.db.repo import utcnow
from src.db.schema import upsert_df
from src.features.store import load_labels, load_market_data, load_panel
from src.jev.candidates import (
    build_tasks,
    candidate_definition,
    candidate_symbols,
    jev_feature_frame,
    persist_candidate_set,
)
from src.jev.client import JevClient
from src.jev.store import decisions_frame, ensure_feature_set, feature_set_id, generate, question_set
from src.model.promotion import current_incumbent, record_versions, register_model
from src.model.scoring import FAMILIES, ScoreCache, default_config, family_preset, quant_scores
from src.pipeline.common import Context, data_snapshot, git_commit

log = logging.getLogger(__name__)


def generate_historical_jev(ctx: Context, dates: list[pd.Timestamp] | None = None, max_new: int | None = None,
                            max_concurrency: int | None = None) -> dict:
    """Stage A: evaluate every historical candidate state that is not already cached."""
    if not ctx.settings.jev_available:
        out = {"status": "unavailable", "reason": ctx.report.get("verify", {}).get("jev", "Jev unavailable")}
        ctx.report["jev_history"] = out
        return out
    panel = load_panel(ctx.con, dates)
    if panel.empty:
        return {"status": "skipped", "reason": "no feature panel"}
    cache = ScoreCache(panel)
    md = load_market_data(ctx.con)
    industries = dict(ctx.con.execute("SELECT symbol, coalesce(industry, sic_description) FROM securities").fetchall())
    definition = candidate_definition()
    qset = question_set("candidate")
    client = JevClient()
    fsid = ensure_feature_set(ctx.con, client.model, qset)
    tasks = []
    for d in cache.dates:
        syms = candidate_symbols(cache, d, definition=definition)
        persist_candidate_set(ctx.con, d, fsid, syms, definition)
        tasks.extend(build_tasks(cache, md.bench.get("QQQ"), d, syms, industries))

    def progress(s):
        done = s.completed + s.failed
        if done % 25 == 0 or done == s.pending:
            ctx.step("jev_history", f"{done}/{s.pending} new evaluations (cached {s.cached}, failed {s.failed})")

    stats = generate(ctx.con, tasks, "candidate", client, max_concurrency, progress, max_new=max_new)
    out = {"status": "ok", "jev_feature_set_id": fsid, **stats.summary()}
    ctx.report["jev_history"] = out
    ctx.step("jev_history", f"states={stats.unique_states} cached={stats.cached} new={stats.completed} "
                            f"failed={stats.failed}")
    return out


def _series_rows(run_id: str, name: str, s: pd.Series) -> pd.DataFrame:
    s = s.dropna()
    return pd.DataFrame({"run_id": run_id, "series": name, "date": pd.to_datetime(s.index).date, "equity": s.values})


def _json(obj: Any) -> str:
    def default(v):
        if isinstance(v, (pd.Timestamp,)):
            return str(v.date())
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        if isinstance(v, (set, tuple)):
            return list(v)
        return str(v)
    return json.dumps(obj, default=default)


def factor_research(cache: ScoreCache, labels: dict[int, pd.DataFrame]) -> dict:
    """Cross-sectional IC / rank IC and quintile spreads of family scores and a balanced composite."""
    d = default_config()
    rows = []
    for dt in cache.dates:
        cs = cache.cross_section(dt, *d.universe_key)
        if cs.frame.empty:
            continue
        f = cs.family_z.copy()
        f["composite_literature"] = quant_scores(cs, {k: float(family_preset("literature").get(k, 0))
                                                      for k in FAMILIES})
        f["rebalance_date"] = dt
        rows.append(f.reset_index().rename(columns={"index": "symbol"}))
    if not rows:
        return {}
    scores = pd.concat(rows, ignore_index=True)
    cols = FAMILIES + ["composite_literature"]
    out = {}
    for h, lab in labels.items():
        ic = information_coefficients(scores, lab[["rebalance_date", "symbol", "fwd_return"]], cols)
        if ic.empty:
            continue
        g = ic.groupby("score")
        out[f"h{h}"] = {
            "mean_ic": g["ic"].mean().round(4).to_dict(), "mean_rank_ic": g["rank_ic"].mean().round(4).to_dict(),
            "rank_ic_t": (g["rank_ic"].mean() / (g["rank_ic"].std() / np.sqrt(g["rank_ic"].count()))).round(2).to_dict(),
            "dates": int(ic["rebalance_date"].nunique()),
        }
        spreads = quantile_spreads(scores, lab[["rebalance_date", "symbol", "fwd_return"]], "composite_literature")
        if not spreads.empty:
            out[f"h{h}"]["composite_quintile_mean"] = spreads.drop(columns=["rebalance_date"]).mean().round(4).to_dict()
    return out


def overfitting_report(researcher, rr, folds) -> dict:
    """PBO (CSCV) across all tested configurations and deflated Sharpe of the honest walk-forward curves."""
    if not folds:
        return {"reason": "no folds"}
    oos_start = folds[0].test_start
    trials = {m: r.equity for m, r in researcher.results.items() if researcher.stage.get(m) in ("stage1", "stage2")}
    M = monthly_returns_matrix(trials, oos_start)
    out: dict = {"pbo": pbo_cscv(M) if not M.empty else {"pbo": None, "reason": "no overlapping months"}}
    if not M.empty:
        trial_sr = (M.mean() / M.std(ddof=1)).to_numpy()
        for key, n in rr.nested.items():
            if "result" in n:
                mr = n["result"].equity.resample("ME").last().pct_change().dropna()
                out[f"deflated_sharpe_{key}"] = deflated_sharpe(mr, trial_sr)
    return out


def run_research(ctx: Context, max_configs: int | None = None, sensitivity: bool = True, use_jev: bool = True,
                 kind: str = "research") -> dict:
    cfgs = all_configs()
    bt_cfg = cfgs["backtest"]
    panel = load_panel(ctx.con)
    if panel.empty:
        raise RuntimeError("No feature panel. Run the data and feature steps first.")
    cache = ScoreCache(panel)
    md = load_market_data(ctx.con)
    labels = {h: load_labels(ctx.con, h) for h in load_config("factors")["horizons"]}
    jev_feats, fsid = None, None
    jev_ok = False
    if use_jev and ctx.settings.jev_enabled:
        fsid = feature_set_id(ctx.settings.jev_model, question_set("candidate"))
        dec = decisions_frame(ctx.con, fsid)
        if not dec.empty:
            jev_feats = JevFeatures(jev_feature_frame(dec), fsid)
            jev_ok = True
    bt = Backtester(cache, md.mats["open"], md.mats["close"], labels, jev_feats,
                    initial_capital=ctx.settings.initial_capital_usd)
    wf = bt_cfg["walk_forward"]
    start = pd.Timestamp(bt_cfg["start_date"]) if bt_cfg.get("start_date") else None
    research_dates = [d for d in cache.dates if start is None or d >= start]
    folds = walk_forward_folds(research_dates, md.calendar[-1], wf["min_train_months"], wf["test_months"],
                               wf["embargo_months"], wf["purge_label_days"])
    bench = {k: v for k, v in md.bench.items()}
    d = default_config()
    ew = ew_universe_benchmark(cache, md.mats["close"], d.min_market_cap, d.min_adv20,
                               ctx.settings.initial_capital_usd, start)
    if not ew.empty:
        bench["EW_universe"] = ew
    ctx.step("research", f"{len(cache.dates)} rebalance dates, {len(folds)} folds, Jev features: "
                         f"{'yes (' + fsid + ')' if jev_ok else 'no'}")
    researcher = Researcher(bt, folds, bench, jev_available=jev_ok, max_configs=max_configs)
    inc = current_incumbent(ctx.con)
    rr = researcher.run_all(sensitivity=sensitivity)
    inc_id = None
    if inc is not None:
        inc_id = researcher.evaluate(inc["config"], "incumbent")
    summary = researcher.summary()
    validation = overfitting_report(researcher, rr, folds)
    best_id = rr.best_id
    best_cfg = rr.configs[best_id]
    best_res = bt.run(best_cfg, record_rankings=True)
    best_metrics = performance(best_res.equity, bench, best_res.trades)
    diag = run_diagnostics(ctx.con, best_res, best_metrics, panel, len(folds))
    run_id = "bt_" + pd.Timestamp.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]

    # --- persistence ----------------------------------------------------------------------------------------
    for mid, c in researcher.configs.items():
        register_model(ctx.con, c, f"tested in {run_id} ({researcher.stage[mid]})")
    nested_out = {}
    for key, n in rr.nested.items():
        nested_out[key] = {k: v for k, v in n.items() if k not in ("result", "fold_metrics")}
    research_metrics = factor_research(cache, labels)
    ctx.con.execute("INSERT INTO backtest_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        run_id, kind, utcnow(), git_commit(), _json(data_snapshot(ctx.con)), _json(cfgs), fsid if jev_ok else None,
        int(bt_cfg["search"]["seed"]), _json([f.to_dict() for f in folds]),
        _json({"best_model_id": best_id, "best_config": best_cfg.to_dict(), "best_full_period": best_metrics,
               "best_oos_summary": summary.loc[best_id].to_dict(), "nested_walk_forward": nested_out,
               "ablation": rr.ablation, "stability": rr.stability, "factor_research": research_metrics,
               "validation": validation,
               "sensitivity": rr.sensitivity.to_dict("records") if not rr.sensitivity.empty else [],
               "nested_fold_metrics": {k: v.get("fold_metrics") for k, v in rr.nested.items()},
               "costs": bt_cfg["costs"], "jev": {"used": jev_ok, "feature_set_id": fsid,
                                                  "model_requested": ctx.settings.jev_model,
                                                  "resolved_version": "unknown (not exposed by Vercel AI Gateway)"},
               "n_configs": len(researcher.configs), "backtest_stats": best_res.stats}),
        _json(diag), "completed", None])
    mres = summary.reset_index()[["model_id", "stage", "objective"]].copy()
    mres["run_id"] = run_id
    mres["objective"] = mres["objective"].replace([np.inf, -np.inf], np.nan)
    mres["summary"] = [_json(summary.loc[m].to_dict()) for m in mres["model_id"]]
    upsert_df(ctx.con, "backtest_model_results", mres[["run_id", "model_id", "stage", "objective", "summary"]],
              ["run_id", "model_id"])
    frows = []
    for mid, fm in researcher.fm.items():
        for m in fm:
            f = folds[m["fold_id"]]
            frows.append({"run_id": run_id, "model_id": mid, "fold_id": f.fold_id, "train_start": f.train_start.date(),
                          "train_end": f.train_end.date(), "test_start": f.test_start.date(),
                          "test_end": f.test_end.date(), "metrics": _json(m)})
    if frows:
        upsert_df(ctx.con, "backtest_fold_results", pd.DataFrame(frows), ["run_id", "model_id", "fold_id"])
    eq = [_series_rows(run_id, "best_model", best_res.equity)]
    for key, n in rr.nested.items():
        if "result" in n:
            eq.append(_series_rows(run_id, f"walk_forward_{key}", n["result"].equity))
    if inc_id:
        eq.append(_series_rows(run_id, "incumbent", researcher.results[inc_id].equity))
    start = best_res.equity.index[0]
    for name, b in bench.items():
        b = b[b.index >= start].dropna()
        if len(b):
            eq.append(_series_rows(run_id, f"bench_{name}", b / b.iloc[0] * ctx.settings.initial_capital_usd))
    upsert_df(ctx.con, "backtest_equity", pd.concat(eq, ignore_index=True), ["run_id", "series", "date"])
    if not best_res.trades.empty:
        t = best_res.trades.copy()
        t["txn_id"] = [f"{run_id}:{i}" for i in range(len(t))]
        t["portfolio_id"] = f"bt:{run_id}:best"
        t["run_key"] = run_id
        t = t.rename(columns={"gross": "gross_amount"})
        t["status"] = "backtest"
        t["created_at"] = utcnow()
        for c in ("rebalance_date", "trade_date"):
            t[c] = pd.to_datetime(t[c]).dt.date
        upsert_df(ctx.con, "portfolio_transactions", t[["txn_id", "portfolio_id", "run_key", "rebalance_date",
                                                        "trade_date", "symbol", "side", "shares", "price",
                                                        "gross_amount", "commission", "slippage_cost",
                                                        "transaction_cost", "reason", "status", "created_at"]],
                  ["txn_id"])
    # --- incumbent / challenger ------------------------------------------------------------------------------
    def stats_for(mid):
        row = summary.loc[mid]
        return {"objective": float(row["objective"]) if np.isfinite(row["objective"]) else None,
                "fold_returns": summarize_folds(researcher.fm[mid]).get("fold_total_returns"),
                "worst_fold_max_drawdown": row.get("worst_fold_max_drawdown"),
                "median_cagr": row.get("median_cagr")}
    promo = record_versions(ctx.con, best_cfg, stats_for(best_id), stats_for(inc_id) if inc_id else None, run_id,
                            cache.dates[-1])
    out = {"run_id": run_id, "best_model_id": best_id, "best_config": best_cfg.to_dict(),
           "configs_tested": len(researcher.configs), "folds": len(folds), "jev_used": jev_ok,
           "best_full_period": {k: best_metrics.get(k) for k in ("cagr", "max_drawdown", "sharpe", "total_return",
                                                                 "turnover_annual")},
           "nested": {k: {"cagr": v.get("metrics", {}).get("cagr"), "max_drawdown": v.get("metrics", {}).get("max_drawdown"),
                          "sharpe": v.get("metrics", {}).get("sharpe")} for k, v in rr.nested.items()},
           "promotion": {k: promo[k] for k in ("role", "promote", "reason")},
           "diagnostic_flags": [f["code"] for f in diag["flags"]]}
    ctx.report["research"] = out
    ctx.step("research", f"run {run_id}: best {best_id} ({best_cfg.preset}), promotion: {promo['reason']}")
    return out


def reproduce_run(ctx: Context, run_id: str) -> dict:
    """Re-simulate a stored run's best configuration on the stored data and compare equity curves."""
    row = ctx.con.execute("SELECT config, metrics, jev_feature_set_id FROM backtest_runs WHERE run_id = ?",
                          [run_id]).fetchone()
    if row is None:
        raise KeyError(run_id)
    stored_cfg, metrics = json.loads(row[0]), json.loads(row[1])
    current = all_configs()
    cfg_dict = dict(metrics["best_config"])
    cfg_dict.pop("family_weights", None)
    from src.model.scoring import ModelConfig
    cfg = ModelConfig(**cfg_dict)
    panel = load_panel(ctx.con)
    cache = ScoreCache(panel, stored_cfg["factors"])
    md = load_market_data(ctx.con)
    jev = None
    if row[2]:
        jev = JevFeatures(jev_feature_frame(decisions_frame(ctx.con, row[2])), row[2])
    bt = Backtester(cache, md.mats["open"], md.mats["close"],
                    {h: load_labels(ctx.con, h) for h in stored_cfg["factors"]["horizons"]}, jev,
                    initial_capital=float(stored_cfg["backtest"]["initial_capital_usd"]),
                    bt_config=stored_cfg["backtest"], jev_config=stored_cfg["jev"])
    res = bt.run(cfg)
    stored = ctx.con.execute("SELECT date, equity FROM backtest_equity WHERE run_id = ? AND series = 'best_model' "
                             "ORDER BY date", [run_id]).df()
    stored_s = pd.Series(stored["equity"].values, index=pd.to_datetime(stored["date"]))
    j = pd.concat([stored_s, res.equity], axis=1, join="inner").dropna()
    max_diff = float((j.iloc[:, 0] - j.iloc[:, 1]).abs().max()) if len(j) else None
    return {"run_id": run_id, "config_changed_since_run": stored_cfg != current, "points_compared": len(j),
            "max_abs_equity_difference": max_diff, "reproduced": max_diff is not None and max_diff < 1e-6}
