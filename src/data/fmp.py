"""Financial Modeling Prep stable-API client (https://financialmodelingprep.com/stable/)."""
from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

import httpx

from src.config import get_settings, load_config
from src.data.http import ApiError, BudgetExhausted, CachedHttpClient, PlanRestricted

log = logging.getLogger(__name__)

_BUDGET_MARKERS = ("limit reach", "bandwidth limit", "limit reached")
_PLAN_MARKERS = ("premium", "restricted endpoint", "subscription", "upgrade your plan", "not available under",
                 "special endpoint")


def _error_kind(text: str) -> type[ApiError] | None:
    t = text.lower()
    if any(m in t for m in _BUDGET_MARKERS):
        return BudgetExhausted
    if any(m in t for m in _PLAN_MARKERS):
        return PlanRestricted
    return None


class FmpClient(CachedHttpClient):
    def __init__(self, api_key: str | None = None, calls_today: Callable[[], int] | None = None,
                 request_logger=None, transport: httpx.BaseTransport | None = None, cache=None):
        cfg = load_config("data")["fmp"]
        self.cfg = cfg
        self.api_key = api_key or get_settings().fmp_api_key
        if not self.api_key:
            raise ApiError("fmp", None, "FMP_API_KEY is not set in .env")
        super().__init__("fmp", min_interval=cfg["min_interval_seconds"], max_retries=cfg["max_retries"],
                         request_logger=request_logger, transport=transport, cache=cache)
        self.base = cfg["base_url"].rstrip("/")
        budget = cfg.get("daily_call_budget")
        self.daily_budget = int(budget) if budget is not None else None
        self._calls_today = calls_today or (lambda: 0)
        self._session_calls = 0
        self._budget_base: int | None = None
        self._budget_lock = threading.Lock()
        self.unavailable: dict[str, str] = {}  # endpoint -> reason (plan restriction / budget)

    # --- budget & error handling ---------------------------------------------------------------------------
    def before_live_call(self, endpoint: str) -> None:
        """Atomically reserve one call against the daily budget (safe with concurrent fetch threads)."""
        if self.daily_budget is None:
            return
        with self._budget_lock:
            if self._budget_base is None:
                self._budget_base = self._calls_today()
            used = self._budget_base + self._session_calls
            if used >= self.daily_budget:
                raise BudgetExhausted("fmp", None, f"local daily FMP call budget reached ({used}/{self.daily_budget})")
            self._session_calls += 1

    def classify_error(self, response: httpx.Response) -> ApiError:
        kind = _error_kind(response.text)
        if kind is not None:
            return kind("fmp", response.status_code, response.text[:300], retryable=False)
        return super().classify_error(response)

    def payload_error(self, payload: Any) -> ApiError | None:
        if isinstance(payload, dict) and "Error Message" in payload:
            msg = str(payload["Error Message"])
            kind = _error_kind(msg) or ApiError
            return kind("fmp", 200, msg[:300])
        return None

    def _get(self, path: str, params: dict[str, Any] | None = None, ttl_hours: float | None = 24.0,
             endpoint: str | None = None) -> Any:
        endpoint = endpoint or path
        if endpoint in self.unavailable:
            raise PlanRestricted("fmp", None, f"{endpoint} unavailable: {self.unavailable[endpoint]}")
        query = dict(params or {})
        cache_key = f"fmp:{path}?" + "&".join(f"{k}={query[k]}" for k in sorted(query))
        query["apikey"] = self.api_key
        try:
            return self.get_json(f"{self.base}/{path}", params=query, cache_key=cache_key, ttl_hours=ttl_hours,
                                 endpoint=endpoint)
        except PlanRestricted as exc:
            self.unavailable[endpoint] = str(exc)
            raise

    # --- reference data -----------------------------------------------------------------------------------
    def company_screener(self, **filters: Any) -> list[dict]:
        params = {"limit": 10000, **{k: (str(v).lower() if isinstance(v, bool) else v) for k, v in filters.items()}}
        return self._get("company-screener", params, ttl_hours=self.cfg["ttl_hours"]["reference"]) or []

    def stock_list(self) -> list[dict]:
        return self._get("stock-list", ttl_hours=self.cfg["ttl_hours"]["reference"]) or []

    def actively_trading_list(self) -> list[dict]:
        return self._get("actively-trading-list", ttl_hours=self.cfg["ttl_hours"]["reference"]) or []

    def profile(self, symbol: str, ttl_hours: float | None = None) -> dict | None:
        data = self._get("profile", {"symbol": symbol},
                         ttl_hours=ttl_hours if ttl_hours is not None else self.cfg["ttl_hours"]["reference"])
        return data[0] if isinstance(data, list) and data else None

    def delisted_companies(self, page: int = 0, limit: int = 100) -> list[dict]:
        return self._get("delisted-companies", {"page": page, "limit": limit},
                         ttl_hours=self.cfg["ttl_hours"]["delisted"]) or []

    def splits(self, symbol: str) -> list[dict]:
        return self._get("splits", {"symbol": symbol}, ttl_hours=self.cfg["ttl_hours"]["reference"]) or []

    # --- prices -------------------------------------------------------------------------------------------
    def _price_ttl(self, to: date) -> float | None:
        # A window ending well in the past is immutable (except rare vendor corrections): cache forever.
        return None if to < date.today() - timedelta(days=7) else self.cfg["ttl_hours"]["prices_recent"]

    def historical_prices(self, symbol: str, start: date, end: date) -> list[dict]:
        """Split-adjusted daily OHLCV (FMP 'full' endpoint)."""
        return self._get("historical-price-eod/full",
                         {"symbol": symbol, "from": start.isoformat(), "to": end.isoformat()},
                         ttl_hours=self._price_ttl(end)) or []

    def dividend_adjusted_prices(self, symbol: str, start: date, end: date) -> list[dict]:
        return self._get("historical-price-eod/dividend-adjusted",
                         {"symbol": symbol, "from": start.isoformat(), "to": end.isoformat()},
                         ttl_hours=self._price_ttl(end)) or []
