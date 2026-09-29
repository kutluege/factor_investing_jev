"""SEC EDGAR client (data.sec.gov). No key required; a descriptive User-Agent with contact email is mandatory."""
from __future__ import annotations

import httpx

from src.config import get_settings, load_config
from src.data.http import ApiError, CachedHttpClient


def cik10(cik: int | str) -> str:
    return str(int(cik)).zfill(10)


class SecClient(CachedHttpClient):
    def __init__(self, user_agent: str | None = None, request_logger=None,
                 transport: httpx.BaseTransport | None = None, cache=None):
        cfg = load_config("data")["sec"]
        self.cfg = cfg
        ua = user_agent or get_settings().sec_user_agent
        if not ua or "@" not in ua:
            raise ApiError("sec", None, "SEC_USER_AGENT must be set in .env as 'app-name contact@email'")
        super().__init__("sec", headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"},
                         min_interval=1.0 / float(cfg["max_requests_per_second"]),
                         max_retries=cfg["max_retries"], request_logger=request_logger, transport=transport,
                         cache=cache)
        self.base = cfg["base_url"].rstrip("/")
        self.www = cfg["www_url"].rstrip("/")

    def payload_error(self, payload):
        return None

    def classify_error(self, response: httpx.Response) -> ApiError:
        if response.status_code == 403 and "Undeclared Automated Tool" in response.text:
            return ApiError("sec", 403, "SEC rejected the User-Agent; set SEC_USER_AGENT with a contact email")
        if response.status_code == 404:
            return ApiError("sec", 404, "not found")
        return super().classify_error(response)

    def company_tickers_exchange(self) -> list[dict]:
        data = self.get_json(f"{self.www}/files/company_tickers_exchange.json",
                             ttl_hours=self.cfg["ttl_hours"]["tickers"], endpoint="company_tickers_exchange")
        fields = data["fields"]
        return [dict(zip(fields, row, strict=False)) for row in data["data"]]

    def submissions(self, cik: int | str) -> dict:
        return self.get_json(f"{self.base}/submissions/CIK{cik10(cik)}.json",
                             ttl_hours=self.cfg["ttl_hours"]["submissions"], endpoint="submissions")

    def company_facts(self, cik: int | str) -> dict:
        return self.get_json(f"{self.base}/api/xbrl/companyfacts/CIK{cik10(cik)}.json",
                             ttl_hours=self.cfg["ttl_hours"]["companyfacts"], endpoint="companyfacts")
