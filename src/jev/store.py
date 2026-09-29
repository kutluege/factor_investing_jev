"""Durable Jev cache, feature-set versioning and resumable bounded-concurrency generation (Stage A)."""
from __future__ import annotations

import asyncio
import json
import logging
import statistics
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import duckdb
import pandas as pd

from src.config import get_settings, load_config, stable_hash
from src.db.repo import utcnow
from src.jev.client import JevClient, JevError, JevResult
from src.jev.state import cache_key, state_hash

log = logging.getLogger(__name__)
PROVIDER = "vercel-ai-gateway"
UNKNOWN_VERSION = "unknown (not exposed by Vercel AI Gateway)"


@dataclass(frozen=True)
class QuestionSet:
    purpose: str                    # "candidate" | "holding"
    questions: dict[str, dict]
    state_schema_version: str
    question_schema_version: str    # configured version + content hash (editing text creates a new version)


def question_set(purpose: str = "candidate") -> QuestionSet:
    cfg = load_config("jev")
    if purpose == "candidate":
        qs, sv, qv = cfg["questions"], cfg["state_schema_version"], cfg["question_schema_version"]
    else:
        qs, sv, qv = cfg["holding_questions"], cfg["holding_state_schema_version"], cfg["holding_question_schema_version"]
    return QuestionSet(purpose, qs, sv, f"{qv}:{stable_hash(qs, 8)}")


def feature_set_id(model: str, qset: QuestionSet, resolved_model: str | None = None) -> str:
    tag = load_config("jev").get("feature_set_tag", "v1")
    return "jfs_" + stable_hash([model, resolved_model or "unknown", qset.state_schema_version,
                                 qset.question_schema_version, qset.purpose, tag], 12)


def ensure_feature_set(con: duckdb.DuckDBPyConnection, model: str, qset: QuestionSet,
                       window: tuple[pd.Timestamp, pd.Timestamp] | None = None) -> str:
    fsid = feature_set_id(model, qset)
    exists = con.execute("SELECT window_start, window_end FROM jev_feature_sets WHERE jev_feature_set_id = ?",
                         [fsid]).fetchone()
    if exists is None:
        con.execute("INSERT INTO jev_feature_sets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [fsid, PROVIDER, model, UNKNOWN_VERSION, qset.state_schema_version, qset.question_schema_version,
                     json.dumps(qset.questions), utcnow(),
                     window[0].date() if window else None, window[1].date() if window else None,
                     f"purpose={qset.purpose}"])
    elif window is not None:
        # widening the covered window is metadata only; decisions themselves are never modified
        ws, we = exists
        new_ws = min(filter(None, [ws, window[0].date()]))
        new_we = max(filter(None, [we, window[1].date()]))
        con.execute("UPDATE jev_feature_sets SET window_start = ?, window_end = ? WHERE jev_feature_set_id = ?",
                    [new_ws, new_we, fsid])
    return fsid


def cached_decision(con: duckdb.DuckDBPyConnection, key: str) -> dict | None:
    row = con.execute(
        "SELECT decision_id, answers_payload, confidence_payload FROM jev_decisions WHERE cache_key = ? "
        "AND status = 'ok' ORDER BY created_at LIMIT 1", [key]).fetchone()
    if row is None:
        return None
    return {"decision_id": row[0], "answers": json.loads(row[1]), "confidence": json.loads(row[2] or "{}")}


@dataclass
class JevTask:
    symbol: str
    rebalance_date: pd.Timestamp
    state: str


@dataclass
class GenerationStats:
    total_states: int = 0
    unique_states: int = 0
    cached: int = 0
    pending: int = 0
    completed: int = 0
    failed: int = 0
    retries: int = 0
    http_requests: int = 0
    latencies: list[float] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    market_cost_usd: float = 0.0
    errors: dict[str, int] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        lat = self.latencies
        return {
            "total_states": self.total_states, "unique_states": self.unique_states, "cached": self.cached,
            "pending_before_run": self.pending, "completed_this_run": self.completed, "failed": self.failed,
            "retries": self.retries, "http_requests": self.http_requests,
            "latency_ms_median": round(statistics.median(lat), 1) if lat else None,
            "latency_ms_p95": round(sorted(lat)[int(0.95 * (len(lat) - 1))], 1) if lat else None,
            "input_tokens": self.input_tokens, "output_tokens": self.output_tokens,
            "cost_usd": round(self.cost_usd, 6), "market_cost_usd": round(self.market_cost_usd, 6),
            "errors": self.errors,
        }


def _insert_decision(con, *, decision_id, key, fsid, task: JevTask, purpose, model, qset: QuestionSet,
                     result: JevResult | None, error: JevError | None) -> None:
    now = utcnow()
    if result is not None:
        vals = [decision_id, key, fsid, task.symbol, task.rebalance_date.date(), purpose, PROVIDER, model,
                result.model_returned, UNKNOWN_VERSION, qset.state_schema_version, qset.question_schema_version,
                state_hash(task.state), task.state, json.dumps(qset.questions), json.dumps(result.answers),
                json.dumps(result.probabilities), json.dumps(result.confidence), json.dumps(result.usage),
                result.usage.get("inputTokens"), result.usage.get("outputTokens"), result.cost_usd,
                result.market_cost_usd, result.latency_ms, result.provider_request_id, now, "ok",
                result.retry_count, None, None]
    else:
        vals = [decision_id, key, fsid, task.symbol, task.rebalance_date.date(), purpose, PROVIDER, model, None,
                UNKNOWN_VERSION, qset.state_schema_version, qset.question_schema_version, state_hash(task.state),
                task.state, json.dumps(qset.questions), None, None, None, None, None, None, None, None, None, None,
                now, "failed", getattr(error, "retry_count", 0), error.kind if error else "unknown",
                str(error)[:500] if error else None]
    con.execute("INSERT INTO jev_decisions VALUES (" + ", ".join(["?"] * 30) + ")", vals)


def _index(con, fsid, task: JevTask, purpose, key) -> None:
    con.execute("INSERT INTO jev_state_index VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
                [fsid, task.symbol, task.rebalance_date.date(), purpose, key, state_hash(task.state), utcnow()])


def generate(con: duckdb.DuckDBPyConnection, tasks: list[JevTask], purpose: str = "candidate",
             client: JevClient | None = None, max_concurrency: int | None = None,
             progress: Callable[[GenerationStats], None] | None = None, max_new: int | None = None) -> GenerationStats:
    """Evaluate every task not already cached. Safe to interrupt: each result is persisted on completion,
    so a restart only sends the remaining states. Existing successful decisions are never re-requested."""
    settings = get_settings()
    qset = question_set(purpose)
    model = client.model if client else settings.jev_model
    stats = GenerationStats(total_states=len(tasks))
    if tasks:
        dates = [t.rebalance_date for t in tasks]
        fsid = ensure_feature_set(con, model, qset, (min(dates), max(dates)))
    else:
        return stats
    pending: dict[str, list[JevTask]] = {}
    for t in tasks:
        key = cache_key(model, t.state, qset.state_schema_version, qset.question_schema_version)
        _index(con, fsid, t, purpose, key)
        pending.setdefault(key, []).append(t)
    stats.unique_states = len(pending)
    todo = []
    for key, group in pending.items():
        if cached_decision(con, key) is not None:
            stats.cached += 1
        else:
            todo.append((key, group[0]))
    stats.pending = len(todo)
    if max_new is not None:
        todo = todo[:max_new]
    if not todo:
        return stats
    client = client or JevClient()
    limit = max(1, int(max_concurrency or settings.jev_max_concurrency))

    async def run() -> None:
        sem = asyncio.Semaphore(limit)
        async with client.async_client() as http:
            async def one(key: str, task: JevTask) -> None:
                async with sem:
                    before = client.http_requests
                    try:
                        res = await client.aevaluate(http, task.state, qset.questions)
                        _insert_decision(con, decision_id=str(uuid.uuid4()), key=key, fsid=fsid, task=task,
                                         purpose=purpose, model=model, qset=qset, result=res, error=None)
                        stats.completed += 1
                        stats.retries += res.retry_count
                        stats.latencies.append(res.latency_ms)
                        stats.input_tokens += int(res.usage.get("inputTokens") or 0)
                        stats.output_tokens += int(res.usage.get("outputTokens") or 0)
                        stats.cost_usd += res.cost_usd or 0.0
                        stats.market_cost_usd += res.market_cost_usd or 0.0
                    except JevError as exc:
                        _insert_decision(con, decision_id=str(uuid.uuid4()), key=key, fsid=fsid, task=task,
                                         purpose=purpose, model=model, qset=qset, result=None, error=exc)
                        stats.failed += 1
                        stats.retries += getattr(exc, "retry_count", 0)
                        stats.errors[exc.kind] = stats.errors.get(exc.kind, 0) + 1
                        if exc.kind in ("authentication_error", "quota_exceeded", "forbidden"):
                            raise
                    finally:
                        stats.http_requests += client.http_requests - before
                        if progress:
                            progress(stats)
            await asyncio.gather(*(one(k, t) for k, t in todo))

    try:
        asyncio.run(run())
    except JevError as exc:
        log.error("Jev generation stopped: %s", exc)
        stats.errors["stopped"] = 1
    return stats


def decisions_frame(con: duckdb.DuckDBPyConnection, fsid: str, dates: list | None = None) -> pd.DataFrame:
    """Successful decisions joined to (symbol, rebalance_date) for one feature set."""
    q = """
        SELECT i.symbol, i.rebalance_date, d.decision_id, d.answers_payload, d.confidence_payload
        FROM jev_state_index i
        JOIN (SELECT cache_key, arg_min(decision_id, created_at) AS decision_id,
                     arg_min(answers_payload, created_at) AS answers_payload,
                     arg_min(confidence_payload, created_at) AS confidence_payload
              FROM jev_decisions WHERE status = 'ok' GROUP BY cache_key) d ON d.cache_key = i.cache_key
        WHERE i.jev_feature_set_id = ?
    """
    params: list[Any] = [fsid]
    if dates is not None:
        q += " AND i.rebalance_date IN (SELECT unnest(?))"
        params.append([pd.Timestamp(x).date() for x in dates])
    df = con.execute(q, params).df()
    if df.empty:
        return df
    df["rebalance_date"] = pd.to_datetime(df["rebalance_date"])
    df["answers"] = df["answers_payload"].map(json.loads)
    df["confidence"] = df["confidence_payload"].map(lambda s: json.loads(s) if s else {})
    return df.drop(columns=["answers_payload", "confidence_payload"])


def observability(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    r = con.execute("""
        SELECT count(*) FILTER (WHERE status='ok'), count(*) FILTER (WHERE status='failed'),
               count(DISTINCT cache_key) FILTER (WHERE status='ok'), sum(retry_count),
               median(latency_ms), quantile_cont(latency_ms, 0.95), sum(input_tokens), sum(output_tokens),
               sum(cost_usd), sum(market_cost_usd)
        FROM jev_decisions""").fetchone()
    idx = con.execute("SELECT count(*), count(DISTINCT cache_key) FROM jev_state_index").fetchone()
    missing = con.execute("""SELECT count(DISTINCT i.cache_key) FROM jev_state_index i
        WHERE NOT EXISTS (SELECT 1 FROM jev_decisions d WHERE d.cache_key = i.cache_key AND d.status='ok')""").fetchone()
    return {"indexed_states": idx[0], "unique_states": idx[1], "cached_evaluations": r[2],
            "pending_evaluations": missing[0], "ok_requests": r[0], "failed_requests": r[1], "retries": r[3],
            "latency_ms_median": r[4], "latency_ms_p95": r[5], "input_tokens": r[6], "output_tokens": r[7],
            "cost_usd": r[8], "market_cost_usd": r[9]}
