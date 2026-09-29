"""Settings (from .env) and research configuration (from config/*.yaml)."""
from __future__ import annotations

import hashlib
import json
from functools import cache
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    fmp_api_key: str | None = None
    ai_gateway_api_key: str | None = None
    sec_user_agent: str | None = None
    initial_capital_usd: float = 10_000.0
    jev_enabled: bool = True
    jev_model: str = "typesafe-ai/jev"
    jev_max_concurrency: int = 5
    database_path: str | None = None  # overrides config/data.yaml when set

    @property
    def jev_available(self) -> bool:
        return bool(self.jev_enabled and self.ai_gateway_api_key)

    def credential_report(self) -> dict[str, str]:
        """Human-readable credential status; never includes secret values."""
        return {
            "FMP_API_KEY": "set" if self.fmp_api_key else "MISSING",
            "SEC_USER_AGENT": "set" if self.sec_user_agent and "@" in self.sec_user_agent
            else ("set but has no contact email" if self.sec_user_agent else "MISSING"),
            "AI_GATEWAY_API_KEY": "set" if self.ai_gateway_api_key else "MISSING (Jev unavailable)",
            "JEV_ENABLED": str(self.jev_enabled),
        }


def get_settings() -> Settings:
    return Settings()


@cache
def _load_yaml(name: str) -> dict[str, Any]:
    with open(CONFIG_DIR / f"{name}.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(name: str) -> dict[str, Any]:
    """Return a deep copy so callers can mutate freely."""
    return json.loads(json.dumps(_load_yaml(name)))


def all_configs() -> dict[str, Any]:
    return {n: load_config(n) for n in ("universe", "factors", "backtest", "jev", "data")}


def stable_hash(obj: Any, length: int = 16) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def database_path(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    path = settings.database_path or load_config("data")["database_path"]
    p = Path(path)
    return p if p.is_absolute() else PROJECT_ROOT / p
