"""Small persistence helpers shared by loaders and pipelines."""
from __future__ import annotations

from datetime import UTC, date, datetime

import duckdb
import pandas as pd


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class RequestLog:
    """Persists every external request (live or cached) for request counting and budget enforcement."""

    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def __call__(self, provider: str, endpoint: str, status: int | None, from_cache: bool, latency_ms: float,
                 error: str | None) -> None:
        self.con.execute("INSERT INTO api_requests VALUES (?, ?, ?, ?, ?, ?, ?)",
                         [utcnow(), provider, endpoint, status, from_cache, latency_ms, error])

    def live_calls_today(self, provider: str) -> int:
        start = datetime.combine(date.today(), datetime.min.time())
        row = self.con.execute(
            "SELECT count(*) FROM api_requests WHERE provider = ? AND NOT from_cache AND ts >= ? "
            "AND (status_code IS NOT NULL)", [provider, start]).fetchone()
        return int(row[0])

    def summary(self) -> pd.DataFrame:
        return self.con.execute(
            "SELECT provider, CAST(ts AS DATE) AS day, sum(CASE WHEN from_cache THEN 0 ELSE 1 END) AS live_calls, "
            "sum(CASE WHEN from_cache THEN 1 ELSE 0 END) AS cache_hits, "
            "sum(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) AS errors "
            "FROM api_requests GROUP BY 1, 2 ORDER BY 2 DESC, 1").df()


def set_status(con: duckdb.DuckDBPyConnection, item: str, key: str, status: str, detail: str = "") -> None:
    con.execute(
        "INSERT INTO data_load_status VALUES (?, ?, ?, ?, ?) ON CONFLICT (item, key) DO UPDATE SET "
        "status = excluded.status, detail = excluded.detail, updated_at = excluded.updated_at",
        [item, key, status, detail[:500], utcnow()])


def get_status(con: duckdb.DuckDBPyConnection, item: str) -> dict[str, str]:
    rows = con.execute("SELECT key, status FROM data_load_status WHERE item = ?", [item]).fetchall()
    return dict(rows)
