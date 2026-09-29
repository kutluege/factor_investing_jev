"""Console output helpers shared by the CLI entry points."""
from __future__ import annotations

import json
import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s",
                        handlers=[RichHandler(console=console, show_path=False, rich_tracebacks=True)], force=True)
    for noisy in ("httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def progress_printer(step: str, msg: str) -> None:
    console.print(f"[bold cyan]{step:>14}[/] {msg}")


def print_json(title: str, obj) -> None:
    console.rule(title)
    console.print_json(json.dumps(obj, default=str))
