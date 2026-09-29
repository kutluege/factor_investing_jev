"""Utility commands.

    python -m src.pipeline.tools jev-check          # one live Jev evaluation through Vercel AI Gateway
    python -m src.pipeline.tools status             # data coverage, API usage, Jev observability, runs
    python -m src.pipeline.tools backtest           # research run on stored data (no API calls)
    python -m src.pipeline.tools reproduce RUN_ID   # re-simulate a stored run and compare equity
    python -m src.pipeline.tools jev-history        # Stage A only (resumable)
"""
from __future__ import annotations

import typer

from src.db.repo import RequestLog
from src.jev.client import JevClient, JevError
from src.jev.store import observability
from src.pipeline.cli_support import console, print_json, progress_printer, setup_logging
from src.pipeline.common import data_snapshot, open_context, verify_configuration
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
