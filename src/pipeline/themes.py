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


if __name__ == "__main__":
    app()
