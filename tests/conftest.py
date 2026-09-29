from __future__ import annotations

import copy

import pytest

import src.config as config_mod
from src.data.http import RawCache
from src.jev.client import JevClient
from tests.synthetic import make_world


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    """Tests never use real credentials, the real database or the network."""
    monkeypatch.setenv("FMP_API_KEY", "test-fmp-key")
    monkeypatch.setenv("SEC_USER_AGENT", "jev-factor-investor-tests tests@example.com")
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "test-gateway-key")
    monkeypatch.setenv("JEV_ENABLED", "true")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.duckdb"))
    JevClient.default_transport = None
    yield
    JevClient.default_transport = None


@pytest.fixture
def cache(tmp_path):
    return RawCache(tmp_path / "raw_cache")


@pytest.fixture(scope="session")
def world():
    return make_world()


@pytest.fixture
def small_search(monkeypatch):
    """Shrinks the research grid so end-to-end tests run in seconds (production config is unchanged)."""
    original = config_mod._load_yaml

    def patched(name):
        cfg = copy.deepcopy(original(name))
        if name == "backtest":
            s = cfg["search"]
            s["jev_weights"] = [0.0, 0.2]
            s["random_configs"] = 4
            s["portfolio_sizes"] = [5, 10]
            s["market_caps"] = [100000000, 300000000]
            s["adv_thresholds"] = [1000000, 5000000]
            s["hold_buffers"] = [1.0, 1.5]
            s["cost_multipliers"] = [1.0, 2.0]
            s["defaults"]["portfolio_size"] = 5
            cfg["family_presets"] = {k: v for k, v in cfg["family_presets"].items()
                                     if k in ("literature", "momentum_only", "literature_ic_shrunk")}
        if name == "jev":
            cfg["candidate_pool"]["top_n"] = 8
            cfg["candidate_pool"]["boundary_extra"] = 2
        return cfg

    monkeypatch.setattr(config_mod, "_load_yaml", patched)
    yield
