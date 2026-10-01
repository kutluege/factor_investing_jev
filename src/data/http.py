"""HTTP client with raw-response disk cache, request counting, rate limiting, retries and backoff."""
from __future__ import annotations

import gzip
import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from src.config import PROJECT_ROOT, load_config

log = logging.getLogger(__name__)


class ApiError(RuntimeError):
    def __init__(self, provider: str, status: int | None, message: str, retryable: bool = False):
        super().__init__(f"{provider} HTTP {status}: {message}")
        self.provider = provider
        self.status = status
        self.retryable = retryable


class BudgetExhausted(ApiError):
    """Local daily call budget or provider bandwidth/plan limit reached; retrying today is pointless."""


class PlanRestricted(ApiError):
    """Endpoint not available under the configured plan."""


@dataclass
class RequestStats:
    live_calls: int = 0
    cache_hits: int = 0
    errors: int = 0
    retries: int = 0
    by_endpoint: dict[str, int] = field(default_factory=dict)


class RawCache:
    """Content-addressed gzip JSON cache on disk. Immutable payloads use ttl=None (never expire)."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, provider: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()
        return self.root / provider / digest[:2] / f"{digest}.json.gz"

    def get(self, provider: str, key: str, ttl_hours: float | None) -> Any | None:
        p = self._path(provider, key)
        if not p.exists():
            return None
        if ttl_hours is not None and (time.time() - p.stat().st_mtime) > ttl_hours * 3600:
            return None
        try:
            with gzip.open(p, "rt", encoding="utf-8") as fh:
                return json.load(fh)["payload"]
        except (OSError, ValueError, KeyError):
            return None

    def put(self, provider: str, key: str, payload: Any) -> None:
        p = self._path(provider, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        with gzip.open(tmp, "wt", encoding="utf-8") as fh:
            json.dump({"key": key, "stored_at": datetime.now(UTC).isoformat(), "payload": payload}, fh)
        tmp.replace(p)


class RateLimiter:
    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self) -> None:
        with self._lock:
            delta = time.monotonic() - self._last
            if delta < self.min_interval:
                time.sleep(self.min_interval - delta)
            self._last = time.monotonic()


class CachedHttpClient:
    """Shared machinery for FMP and SEC clients."""

    def __init__(self, provider: str, headers: dict[str, str] | None = None, min_interval: float = 0.0,
                 max_retries: int = 4, timeout: float = 60.0, cache: RawCache | None = None,
                 request_logger=None, transport: httpx.BaseTransport | None = None):
        self.provider = provider
        self.max_retries = max_retries
        self.limiter = RateLimiter(min_interval)
        cache_dir = PROJECT_ROOT / load_config("data")["raw_cache_dir"]
        self.cache = cache or RawCache(cache_dir)
        self.stats = RequestStats()
        self.request_logger = request_logger  # callable(provider, endpoint, status, from_cache, latency, error)
        self._client = httpx.Client(headers=headers or {}, timeout=timeout, transport=transport,
                                    follow_redirects=True)

    def close(self) -> None:
        self._client.close()

    def _log(self, endpoint: str, status: int | None, from_cache: bool, latency_ms: float, error: str | None):
        if self.request_logger:
            try:
                self.request_logger(self.provider, endpoint, status, from_cache, latency_ms, error)
            except Exception:  # logging must never break data loading
                log.debug("request logger failed", exc_info=True)

    def classify_error(self, response: httpx.Response) -> ApiError:
        retryable = response.status_code in (429, 500, 502, 503, 504, 529)
        return ApiError(self.provider, response.status_code, response.text[:300], retryable=retryable)

    def before_live_call(self, endpoint: str) -> None:
        """Hook for budget enforcement."""

    def get_json(self, url: str, params: dict[str, Any] | None = None, cache_key: str | None = None,
                 ttl_hours: float | None = 24.0, endpoint: str | None = None, use_cache: bool = True) -> Any:
        params = params or {}
        endpoint = endpoint or url
        key = cache_key or f"{url}?{json.dumps(params, sort_keys=True)}"
        if use_cache:
            cached = self.cache.get(self.provider, key, ttl_hours)
            if cached is not None:
                self.stats.cache_hits += 1
                self._log(endpoint, None, True, 0.0, None)
                return cached

        self.before_live_call(endpoint)
        attempt = 0
        while True:
            self.limiter.wait()
            started = time.perf_counter()
            try:
                resp = self._client.get(url, params=params)
            except (httpx.TransportError, httpx.DecodingError) as exc:  # corrupt gzip bodies are transient too
                latency = (time.perf_counter() - started) * 1000
                self.stats.errors += 1
                self._log(endpoint, None, False, latency, type(exc).__name__)
                if attempt >= self.max_retries:
                    raise ApiError(self.provider, None, f"transport error: {exc}", retryable=True) from exc
                attempt += 1
                self.stats.retries += 1
                time.sleep(min(60, 2 ** attempt))
                continue
            latency = (time.perf_counter() - started) * 1000
            self.stats.live_calls += 1
            self.stats.by_endpoint[endpoint] = self.stats.by_endpoint.get(endpoint, 0) + 1
            if resp.status_code == 200:
                try:
                    payload = resp.json()
                except ValueError as exc:
                    self._log(endpoint, resp.status_code, False, latency, "invalid json")
                    raise ApiError(self.provider, 200, "response was not JSON") from exc
                err = self.payload_error(payload)
                if err is not None:
                    self._log(endpoint, resp.status_code, False, latency, str(err))
                    raise err
                self._log(endpoint, 200, False, latency, None)
                self.cache.put(self.provider, key, payload)
                return payload
            error = self.classify_error(resp)
            self.stats.errors += 1
            self._log(endpoint, resp.status_code, False, latency, str(error)[:200])
            if not error.retryable or attempt >= self.max_retries:
                raise error
            attempt += 1
            self.stats.retries += 1
            retry_after = resp.headers.get("retry-after")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else min(60, 2 ** attempt)
            log.warning("%s %s -> %s, retry %d in %.1fs", self.provider, endpoint, resp.status_code, attempt, delay)
            time.sleep(delay)

    def payload_error(self, payload: Any) -> ApiError | None:
        return None

    def get_text(self, url: str, endpoint: str | None = None) -> str:
        """Uncached text download with the same rate limit, retries and request logging as get_json."""
        endpoint = endpoint or url
        attempt = 0
        while True:
            self.limiter.wait()
            started = time.perf_counter()
            try:
                resp = self._client.get(url)
            except (httpx.TransportError, httpx.DecodingError) as exc:  # corrupt gzip bodies are transient too
                self._log(endpoint, None, False, (time.perf_counter() - started) * 1000, type(exc).__name__)
                if attempt >= self.max_retries:
                    raise ApiError(self.provider, None, f"transport error: {exc}", retryable=True) from exc
                attempt += 1
                time.sleep(min(60, 2 ** attempt))
                continue
            latency = (time.perf_counter() - started) * 1000
            self.stats.live_calls += 1
            if resp.status_code == 200:
                self._log(endpoint, 200, False, latency, None)
                raw = resp.content
                try:  # many older EDGAR documents are Windows-1252 without a charset declaration
                    return raw.decode("utf-8")
                except UnicodeDecodeError:
                    return raw.decode("cp1252", errors="replace")
            error = self.classify_error(resp)
            self._log(endpoint, resp.status_code, False, latency, str(error)[:200])
            if not error.retryable or attempt >= self.max_retries:
                raise error
            attempt += 1
            retry_after = resp.headers.get("retry-after")
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else min(60, 2 ** attempt))
