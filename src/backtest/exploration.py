"""Exploratory strategy evaluation (maximum-return track).

Strategies are declared in config/backtest.yaml -> exploration. They were declared AFTER the main research results
were seen, so they are labelled exploratory and their deflated Sharpe counts every configuration ever tested.
Every strategy runs through the same engine, costs and out-of-sample window as the main research.
"""
from __future__ import annotations

import json
import uuid

import pandas as pd

from src.backtest.engine import Backtester
from src.backtest.metrics import performance
from src.backtest.validation import deflated_sharpe, ew_universe_benchmark
from src.config import all_configs, load_config
from src.db.repo import utcnow
from src.db.schema import upsert_df
from src.features.store import load_labels, load_market_data, load_panel
from src.model.scoring import ModelConfig, ScoreCache, default_config
from src.pipeline.common import Context, data_snapshot, git_commit


def run_exploration(ctx: Context) -> dict:
    cfgs = all_configs()
    ex = cfgs["backtest"]["exploration"]
    panel = load_panel(ctx.con)
    cache = ScoreCache(panel)
    md = load_market_data(ctx.con)
    labels = {h: load_labels(ctx.con, h) for h in cfgs["factors"]["horizons"]}
    bt = Backtester(cache, md.mats["open"], md.mats["close"], labels, None, ctx.settings.initial_capital_usd,
                    raw_close_px=md.mats["raw_close"], market_close=md.bench.get("QQQ"))
    oos_start = pd.Timestamp(ex["oos_start"])
    d = default_config()
    bench = dict(md.bench)
    bench["EW_universe"] = ew_universe_benchmark(cache, md.mats["close"], d.min_market_cap, d.min_adv20,
                                                 ctx.settings.initial_capital_usd, oos_start)
    base = {"min_adv20": d.min_adv20, "weighting": "equal", "jev_weight": 0.0, "cost_multiplier": 1.0,
            "regime_filter": "none"}
    prior_trials = int(ctx.con.execute("SELECT count(*) FROM factor_models").fetchone()[0])
    results, equities = [], {}
    for spec in ex["strategies"]:
        c = ModelConfig(**{**base, **{k: v for k, v in spec.items() if k != "name"}})
        res = bt.run(c, start=oos_start)
        m = performance(res.equity, bench, res.trades)
        equities[spec["name"]] = res.equity
        results.append({"name": spec["name"], "config": c.to_dict(), "model_id": c.model_id, "metrics": m})
        ctx.step("explore", f"{spec['name']}: CAGR {m['cagr']:.1%} maxDD {m['max_drawdown']:.1%} Sharpe {m['sharpe']:.2f}")
    mret = pd.DataFrame({k: v.resample("ME").last().pct_change() for k, v in equities.items()}).dropna()
    trial_sr = (mret.mean() / mret.std(ddof=1)).to_numpy()
    n_trials = prior_trials + len(results)
    # expected max Sharpe of n_trials uses the dispersion of the exploratory trials as the variance estimate
    import numpy as np
    for r in results:
        r["deflated_sharpe"] = deflated_sharpe(mret[r["name"]], np.resize(trial_sr, max(n_trials, 2)))
    run_id = "ex_" + pd.Timestamp.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    ctx.con.execute("INSERT INTO backtest_runs VALUES (?, 'exploration', ?, ?, ?, ?, NULL, ?, NULL, ?, NULL, 'completed', ?)",
                    [run_id, utcnow(), git_commit(), json.dumps(data_snapshot(ctx.con), default=str),
                     json.dumps(cfgs, default=str), int(cfgs["backtest"]["search"]["seed"]),
                     json.dumps({"strategies": results, "oos_start": str(oos_start.date()), "n_trials_total": n_trials},
                                default=str),
                     "exploratory: declared after main research results"])
    rows = [pd.DataFrame({"run_id": run_id, "series": k, "date": v.index.date, "equity": v.values})
            for k, v in equities.items()]
    for name in ("EW_universe", "QQQ", "SPY"):
        b = bench.get(name)
        if b is not None:
            b = b[b.index >= oos_start].dropna()
            rows.append(pd.DataFrame({"run_id": run_id, "series": f"bench_{name}", "date": b.index.date,
                                      "equity": (b / b.iloc[0] * ctx.settings.initial_capital_usd).values}))
    upsert_df(ctx.con, "backtest_equity", pd.concat(rows, ignore_index=True), ["run_id", "series", "date"])
    return {"run_id": run_id, "results": results, "n_trials_total": n_trials}


def to_markdown(out: dict) -> str:
    def p(v):
        return "—" if v is None else f"{v * 100:.1f}%"
    lines = ["# Maximum-return exploration", "",
             f"Run `{out['run_id']}`. Out-of-sample window from {load_config('backtest')['exploration']['oos_start']}. "
             "Strategies were declared after the main research results were seen (exploratory). Same engine, costs "
             f"and data as the main research. Deflated Sharpe counts all {out['n_trials_total']} configurations tested.",
             "", "| Strategy | CAGR | Volatility | Sharpe | Max DD | Worst month | vs QQQ CAGR | vs EW CAGR | Turnover/yr | "
             "Deflated Sharpe |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["results"]:
        m = r["metrics"]
        q, e = m.get("bench_QQQ", {}), m.get("bench_EW_universe", {})
        ds = r.get("deflated_sharpe", {}).get("dsr")
        lines.append(f"| {r['name']} | {p(m['cagr'])} | {p(m['annual_volatility'])} | {m['sharpe']:.2f} | "
                     f"{p(m['max_drawdown'])} | {p(m.get('worst_month'))} | {p(q.get('excess_cagr'))} | "
                     f"{p(e.get('excess_cagr'))} | {m.get('turnover_annual', 0):.1f} | {p(ds)} |")
    first = out["results"][0]["metrics"]
    for name in ("QQQ", "SPY", "EW_universe"):
        b = first.get(f"bench_{name}")
        if b:
            lines.append(f"| Benchmark {name} | {p(b['cagr'])} | — | — | {p(b['max_drawdown'])} | — | — | — | — | — |")
    lines += ["", "Configurations:", ""]
    for r in out["results"]:
        c = {k: v for k, v in r["config"].items() if k != "family_weights"}
        lines.append(f"- **{r['name']}**: `{json.dumps(c)}`")
    return "\n".join(lines) + "\n"
