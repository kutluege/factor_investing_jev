"""Monthly production analysis (identical to the dashboard's RUN MONTHLY ANALYSIS button).

    python -m src.pipeline.monthly
    python -m src.pipeline.monthly --no-update-data
"""
from __future__ import annotations

import typer

from src.pipeline.cli_support import console, print_json, progress_printer, setup_logging
from src.pipeline.common import open_context
from src.pipeline.monthly_run import PORTFOLIO_ID, run_monthly

app = typer.Typer(add_completion=False)


@app.command()
def main(db: str = typer.Option(None, help="DuckDB path"),
         portfolio: str = typer.Option(PORTFOLIO_ID, help="portfolio id"),
         update_data: bool = typer.Option(True, help="refresh FMP/SEC data before analysis"),
         max_price_symbols: int = typer.Option(None, help="limit price updates this run"),
         verbose: bool = False) -> None:
    setup_logging(verbose)
    ctx = open_context(db, progress_printer)
    try:
        result = run_monthly(ctx, portfolio, update_data=update_data, max_price_symbols=max_price_symbols)
    except RuntimeError as exc:  # e.g. no price data yet; nothing was committed
        console.print(f"[red]monthly analysis not possible[/]: {exc}")
        raise typer.Exit(2) from exc
    print_json(f"monthly analysis: {result['status']}", result)
    console.print(f"[green]{result['status']}[/] {result['run_key']}")


if __name__ == "__main__":
    app()
