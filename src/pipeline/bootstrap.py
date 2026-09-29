"""First-time historical initialization: data -> features -> historical Jev (Stage A) -> research (Stage B).

    python -m src.pipeline.bootstrap                      # full run (resumable; respects the FMP daily budget)
    python -m src.pipeline.bootstrap --max-symbols 40     # reduced universe
    python -m src.pipeline.bootstrap --skip-data          # reuse stored data
    python -m src.pipeline.bootstrap --skip-jev           # quant-only
"""
from __future__ import annotations

import typer

from src.features.store import build_features
from src.pipeline.cli_support import console, print_json, progress_printer, setup_logging
from src.pipeline.common import (
    make_clients,
    open_context,
    update_fundamentals,
    update_prices,
    update_reference,
    verify_configuration,
)
from src.pipeline.research_run import generate_historical_jev, run_research

app = typer.Typer(add_completion=False)


def bootstrap(db: str | None = None, max_symbols: int | None = None, symbols: list[str] | None = None,
              skip_data: bool = False, skip_jev: bool = False, jev_max_new: int | None = None,
              max_configs: int | None = None, sensitivity: bool = True, progress=progress_printer,
              clients=None) -> dict:
    ctx = open_context(db, progress)
    verify_configuration(ctx)
    if not skip_data:
        fmp, sec = clients or make_clients(ctx)
        update_reference(ctx, fmp, sec)
        update_prices(ctx, fmp, symbols=symbols, max_symbols=max_symbols)
        update_fundamentals(ctx, sec, symbols=None)
    n_prices = ctx.con.execute("SELECT count(DISTINCT symbol) FROM daily_prices").fetchone()[0]
    if n_prices == 0:
        reason = (ctx.report.get("prices") or {}).get("stopped_reason") or "no price data stored"
        ctx.report["status"] = "blocked"
        ctx.report["blocked_reason"] = (f"No daily prices are stored, so features and backtests cannot run. "
                                        f"FMP: {str(reason)[:200]}. Re-run bootstrap when FMP is reachable; "
                                        "stored SEC data and caches are reused.")
        ctx.step("blocked", ctx.report["blocked_reason"])
        return ctx.report
    ctx.step("features", "building point-in-time features for all rebalance dates")
    panel = build_features(ctx.con)
    ctx.report["features"] = {"rebalance_dates": int(panel["rebalance_date"].nunique()),
                              "rows": int(len(panel)), "eligible_rows": int(panel["base_eligible"].sum())}
    ctx.step("features", str(ctx.report["features"]))
    if not skip_jev:
        generate_historical_jev(ctx, max_new=jev_max_new)
    run_research(ctx, max_configs=max_configs, sensitivity=sensitivity, use_jev=not skip_jev)
    return ctx.report


@app.command()
def main(db: str = typer.Option(None, help="DuckDB path (default from config/data.yaml)"),
         max_symbols: int = typer.Option(None, help="limit securities whose prices are loaded this run"),
         symbol: list[str] = typer.Option(None, "--symbol", help="explicit symbols to load (repeatable)"),
         skip_data: bool = typer.Option(False, help="do not call FMP/SEC; use stored data"),
         skip_jev: bool = typer.Option(False, help="quant-only research"),
         jev_max_new: int = typer.Option(None, help="cap new Jev evaluations this run (resume later)"),
         max_configs: int = typer.Option(None, help="cap Stage-2 random configurations"),
         no_sensitivity: bool = typer.Option(False, help="skip one-at-a-time sensitivity analysis"),
         verbose: bool = False) -> None:
    setup_logging(verbose)
    report = bootstrap(db, max_symbols, symbol or None, skip_data, skip_jev, jev_max_new, max_configs,
                       not no_sensitivity)
    print_json("bootstrap report", report)
    if report.get("status") == "blocked":
        console.print(f"[yellow]bootstrap blocked[/]: {report['blocked_reason']}")
        raise typer.Exit(2)
    console.print("[green]bootstrap finished[/]")


if __name__ == "__main__":
    app()
