"""Utility commands.

    python -m src.pipeline.tools jev-check          # one live Jev evaluation through Vercel AI Gateway
    python -m src.pipeline.tools status             # data coverage, API usage, Jev observability, runs
    python -m src.pipeline.tools backtest           # research run on stored data (no API calls)
    python -m src.pipeline.tools reproduce RUN_ID   # re-simulate a stored run and compare equity
    python -m src.pipeline.tools jev-history        # Stage A only (resumable)
    python -m src.pipeline.tools load-data          # refresh reference data, prices, SEC facts, features
"""
from __future__ import annotations

import typer

from src.db.repo import RequestLog
from src.features.store import build_features
from src.jev.client import JevClient, JevError
from src.jev.store import observability
from src.pipeline.cli_support import console, print_json, progress_printer, setup_logging
from src.pipeline.common import (
    data_snapshot,
    make_clients,
    open_context,
    update_fundamentals,
    update_prices,
    update_reference,
    verify_configuration,
)
from src.pipeline.research_run import generate_historical_jev, reproduce_run, run_research

app = typer.Typer(add_completion=False)


@app.command("jev-check")
def jev_check() -> None:
    setup_logging()
    try:
        client = JevClient()
        res = client.evaluate(
            "context: connectivity check\nfactor_percentiles: price momentum 85, value 30\ntechnicals: price above "
            "200-day average", {"ok": {"type": "boolean", "instructions": "Is the stated price momentum strong?"}})
    except JevError as exc:
        console.print(f"[red]Jev NOT connected[/]: {exc}")
        raise typer.Exit(1) from exc
    print_json("Jev connected", {"model": res.model_returned, "answers": res.answers, "usage": res.usage,
                                 "latency_ms": round(res.latency_ms), "generation_id": res.provider_request_id})


@app.command()
def status(db: str = typer.Option(None)) -> None:
    setup_logging()
    ctx = open_context(db, progress_printer)
    verify_configuration(ctx)
    print_json("data snapshot", data_snapshot(ctx.con))
    print_json("API requests", RequestLog(ctx.con).summary().head(20).to_dict("records"))
    print_json("Jev observability", observability(ctx.con))
    runs = ctx.con.execute("SELECT run_id, kind, created_at, status FROM backtest_runs ORDER BY created_at DESC "
                           "LIMIT 5").df()
    print_json("recent backtest runs", runs.to_dict("records"))


@app.command()
def backtest(db: str = typer.Option(None), max_configs: int = typer.Option(None),
             no_sensitivity: bool = False, skip_jev: bool = False) -> None:
    setup_logging()
    ctx = open_context(db, progress_printer)
    verify_configuration(ctx)
    print_json("research", run_research(ctx, max_configs=max_configs, sensitivity=not no_sensitivity,
                                        use_jev=not skip_jev))


@app.command("load-data")
def load_data(db: str = typer.Option(None), force_reference: bool = typer.Option(
                  False, help="rebuild the security master (incl. delisted discovery) even if it is fresh"),
              features: bool = typer.Option(True, help="rebuild the point-in-time feature panel afterwards")) -> None:
    """Refresh reference data, prices, splits and SEC fundamentals (resumable; cached payloads are reused)."""
    setup_logging()
    ctx = open_context(db, progress_printer)
    verify_configuration(ctx)
    fmp, sec = make_clients(ctx)
    update_reference(ctx, fmp, sec, force=force_reference)
    update_prices(ctx, fmp)
    update_fundamentals(ctx, sec)
    if features:
        panel = build_features(ctx.con)
        ctx.report["features"] = {"rebalance_dates": int(panel["rebalance_date"].nunique()), "rows": int(len(panel)),
                                  "eligible_rows": int(panel["base_eligible"].sum())}
    print_json("load-data report", {k: v for k, v in ctx.report.items() if k != "verify"})
    print_json("data snapshot", data_snapshot(ctx.con))


@app.command("build-features")
def build_features_cmd(db: str = typer.Option(None)) -> None:
    """Rebuild the point-in-time feature panel and labels for all rebalance dates (no API calls)."""
    import time
    setup_logging()
    ctx = open_context(db, progress_printer)
    t0 = time.time()
    panel = build_features(ctx.con)
    print_json("features", {"rebalance_dates": int(panel["rebalance_date"].nunique()), "rows": int(len(panel)),
                            "eligible_rows": int(panel["base_eligible"].sum()),
                            "exclusions": panel["exclusion_reason"].value_counts().to_dict(),
                            "seconds": round(time.time() - t0)})


@app.command("repair-adjusted")
def repair_adjusted_cmd(db: str = typer.Option(None)) -> None:
    """Repair vendor breaks in stored dividend-adjusted closes (logged in price_repairs; idempotent)."""
    from src.data.prices import repair_adjusted
    setup_logging()
    ctx = open_context(db, progress_printer)
    print_json("repair-adjusted", repair_adjusted(ctx.con))


@app.command("factor-ic")
def factor_ic(db: str = typer.Option(None)) -> None:
    """Descriptive characteristic research (rank IC, top-quintile excess) -> docs/FACTOR_IC.md."""
    import pandas as pd

    from src.backtest.factor_analysis import by_subperiod, characteristic_ic, to_markdown
    from src.config import PROJECT_ROOT, load_config
    from src.features.store import load_labels, load_panel
    from src.model.scoring import ScoreCache, default_config
    setup_logging()
    ctx = open_context(db, progress_printer)
    cache = ScoreCache(load_panel(ctx.con))
    labels = {h: load_labels(ctx.con, h) for h in load_config("factors")["horizons"]}
    d = default_config()
    start = pd.Timestamp(load_config("backtest")["start_date"])
    full = characteristic_ic(cache, labels, d.min_market_cap, d.min_adv20, start)
    subs = by_subperiod(cache, labels, d.min_market_cap, d.min_adv20,
                        ["2011-06-30", "2016-01-01", "2021-01-01", "2026-12-31"])
    md = ["# Characteristic research (descriptive)", "",
          f"Universe: market cap >= ${d.min_market_cap / 1e6:.0f}M, ADV20 >= ${d.min_adv20 / 1e6:.0f}M, "
          f"rebalances from {start.date()}. Rank IC = Spearman correlation with the forward return; top-quintile "
          "excess = mean forward return of the best 20% minus the eligible-universe mean (the long-only relevant "
          "statistic). Signals were fixed from the literature beforehand; this table is not used to select them.", ""]
    for h in sorted(full["horizon"].unique()):
        md += [f"## Horizon {h} sessions (2011–2026)", "", to_markdown(full, h), ""]
    md += ["## Sub-period stability (126-session horizon)", ""]
    for name, df in subs.items():
        md += [f"### {name}", "", to_markdown(df, 126), ""]
    path = PROJECT_ROOT / "docs" / "FACTOR_IC.md"
    path.write_text("\n".join(md), encoding="utf-8")
    full.to_csv(PROJECT_ROOT / "data" / "logs" / "factor_ic.csv", index=False)
    console.print(f"wrote {path}")


@app.command()
def explore(db: str = typer.Option(None)) -> None:
    """Maximum-return exploration (config/backtest.yaml -> exploration) -> docs/EXPLORATION.md."""
    from src.backtest.exploration import run_exploration, to_markdown
    from src.config import PROJECT_ROOT
    setup_logging()
    ctx = open_context(db, progress_printer)
    out = run_exploration(ctx)
    path = PROJECT_ROOT / "docs" / "EXPLORATION.md"
    path.write_text(to_markdown(out), encoding="utf-8")
    console.print(f"wrote {path}")


@app.command("set-incumbent")
def set_incumbent(model_id: str, reason: str = typer.Option(..., help="why (stored in the audit trail)"),
                  db: str = typer.Option(None)) -> None:
    """Append a new incumbent version for a stored model (audited; earlier versions are never modified)."""
    import json
    import uuid

    import pandas as pd

    from src.db.repo import utcnow
    setup_logging()
    ctx = open_context(db, progress_printer)
    if ctx.con.execute("SELECT count(*) FROM factor_models WHERE model_id = ?", [model_id]).fetchone()[0] == 0:
        console.print(f"[red]unknown model {model_id}[/]")
        raise typer.Exit(1)
    prev = ctx.con.execute("SELECT version_id FROM model_versions WHERE role = 'incumbent' ORDER BY created_at DESC "
                           "LIMIT 1").fetchone()
    vid = "v_" + uuid.uuid4().hex[:12]
    today = pd.Timestamp.today().normalize()
    ctx.con.execute("INSERT INTO model_versions VALUES (?, ?, 'incumbent', ?, NULL, NULL, ?, ?)",
                    [vid, model_id, today.date(), json.dumps({"manual": True, "reason": reason}), utcnow()])
    ctx.con.execute("INSERT INTO promotion_decisions VALUES (?, ?, ?, ?, true, ?, ?, ?)",
                    ["p_" + uuid.uuid4().hex[:12], today.date(), prev[0] if prev else None, vid,
                     json.dumps({"manual_override": True}), json.dumps({"reason": reason}), utcnow()])
    console.print(f"[green]incumbent set[/]: {model_id} as version {vid}")


@app.command()
def report(run_id: str = typer.Argument(None), db: str = typer.Option(None)) -> None:
    """Write docs/RESULTS.md for a stored research run (latest by default)."""
    from src.pipeline.report import write
    setup_logging()
    ctx = open_context(db, progress_printer)
    console.print(f"wrote {write(ctx.con, run_id)}")


@app.command()
def reproduce(run_id: str, db: str = typer.Option(None)) -> None:
    setup_logging()
    ctx = open_context(db, progress_printer)
    print_json("reproduction", reproduce_run(ctx, run_id))


@app.command("jev-history")
def jev_history(db: str = typer.Option(None), max_new: int = typer.Option(None),
                concurrency: int = typer.Option(None)) -> None:
    setup_logging()
    ctx = open_context(db, progress_printer)
    verify_configuration(ctx)
    print_json("Jev Stage A", generate_historical_jev(ctx, max_new=max_new, max_concurrency=concurrency))


if __name__ == "__main__":
    app()
