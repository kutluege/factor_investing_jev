"""End-to-end: bootstrap -> research -> monthly run (twice) -> reproduction, on the synthetic market."""
import copy
import json

import pandas as pd
import pytest

import src.config as config_mod
from src.backtest.diagnostics import lookahead_audit
from src.data.fmp import FmpClient
from src.data.http import RawCache
from src.data.sec import SecClient
from src.jev.client import JevClient
from src.pipeline.bootstrap import bootstrap
from src.pipeline.common import open_context
from src.pipeline.monthly_run import run_monthly
from src.pipeline.research_run import reproduce_run
from tests.synthetic import fmp_transport, jev_transport, make_world, sec_transport


def _small(original):
    def patched(name):
        cfg = copy.deepcopy(original(name))
        if name == "backtest":
            s = cfg["search"]
            s.update(jev_weights=[0.0, 0.2], random_configs=3, portfolio_sizes=[5, 10],
                     market_caps=[100000000, 300000000], adv_thresholds=[1000000, 5000000], hold_buffers=[1.0, 1.5],
                     cost_multipliers=[1.0, 2.0])
            s["defaults"].update(portfolio_size=5, min_market_cap=100000000, min_adv20=1000000)
            cfg["family_presets"] = {k: v for k, v in cfg["family_presets"].items()
                                     if k in ("balanced", "momentum_trend", "ic_weighted_126")}
        if name == "jev":
            cfg["candidate_pool"].update(top_n=6, boundary_extra=2)
        return cfg
    return patched


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    mp = pytest.MonkeyPatch()
    tmp = tmp_path_factory.mktemp("e2e")
    mp.setenv("FMP_API_KEY", "test")
    mp.setenv("SEC_USER_AGENT", "tests tests@example.com")
    mp.setenv("AI_GATEWAY_API_KEY", "test")
    mp.setenv("JEV_ENABLED", "true")
    mp.setenv("DATABASE_PATH", str(tmp / "e2e.duckdb"))
    mp.setattr(config_mod, "_load_yaml", _small(config_mod._load_yaml))
    world = make_world(n_per_group=10)
    jev_calls: list = []
    transport = jev_transport(jev_calls)
    JevClient.default_transport = transport
    cache = RawCache(tmp / "raw")
    clients = (FmpClient(transport=fmp_transport(world), cache=cache),
               SecClient(transport=sec_transport(world), cache=cache))
    report = bootstrap(max_configs=3, sensitivity=False, clients=clients, progress=lambda s, m: None)
    yield {"world": world, "report": report, "clients": clients, "jev_calls": jev_calls, "tmp": tmp,
           "db": str(tmp / "e2e.duckdb"), "transport": transport, "patched_yaml": config_mod._load_yaml}
    JevClient.default_transport = None
    mp.undo()


@pytest.fixture
def e2e(env, monkeypatch):
    """Per-test view of the module database (the autouse fixture isolates env vars per test)."""
    monkeypatch.setenv("DATABASE_PATH", env["db"])
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "test")
    monkeypatch.setattr(config_mod, "_load_yaml", env["patched_yaml"])
    JevClient.default_transport = env["transport"]
    return env


def test_bootstrap_builds_point_in_time_database(e2e):
    ctx = open_context()
    con = ctx.con
    secs = con.execute("SELECT symbol, is_active, sector_group FROM securities").df()
    assert "ETFX" not in set(secs["symbol"])                      # ETFs excluded
    delisted = e2e["world"].companies[3].symbol
    assert not secs.set_index("symbol").loc[delisted, "is_active"]  # delisted names kept for survivorship
    assert set(secs["sector_group"]) == {"technology", "biotechnology", "energy", "metals_mining"}
    assert lookahead_audit(con)["passed"]
    bad = con.execute("SELECT count(*) FROM factor_values WHERE availability_date > rebalance_date").fetchone()[0]
    assert bad == 0


def test_universe_membership_respects_listing_dates(e2e):
    con = open_context().con
    w = e2e["world"]
    ipo, gone = w.companies[5], w.companies[3]
    u = con.execute("SELECT rebalance_date, symbol, base_eligible, exclusion_reason FROM rebalance_universe").df()
    u["rebalance_date"] = pd.to_datetime(u["rebalance_date"])
    ipo_rows = u[u["symbol"] == ipo.symbol]
    assert not ipo_rows[ipo_rows["rebalance_date"] < ipo.start + pd.DateOffset(years=1)]["base_eligible"].any()
    gone_after = u[(u["symbol"] == gone.symbol) & (u["rebalance_date"] > gone.end)]
    assert gone_after.empty or not gone_after["base_eligible"].any()


def test_split_does_not_break_market_cap(e2e):
    con = open_context().con
    sym = e2e["world"].companies[7].symbol
    mc = con.execute("SELECT rebalance_date, market_cap FROM rebalance_universe WHERE symbol = ? ORDER BY 1",
                     [sym]).df().dropna()
    ratio = (mc["market_cap"] / mc["market_cap"].shift(1)).dropna()
    assert ratio.max() < 1.6 and ratio.min() > 0.6   # no 2x jump at the 2:1 split


def test_research_run_persisted_with_reproducibility_metadata(e2e):
    con = open_context().con
    run = con.execute("SELECT run_id, git_commit, data_snapshot, config, folds, metrics, jev_feature_set_id "
                      "FROM backtest_runs").fetchone()
    assert run is not None
    metrics = json.loads(run[5])
    assert json.loads(run[3])["backtest"]["costs"]["slippage_bps"] > 0     # costs recorded explicitly
    assert len(json.loads(run[4])) >= 2                                   # fold definitions stored
    assert "quant_only" in metrics["nested_walk_forward"] and "quant_plus_jev" in metrics["nested_walk_forward"]
    assert metrics["jev"]["resolved_version"].startswith("unknown")
    assert run[6] is not None                                              # Jev feature set recorded
    n_models = con.execute("SELECT count(*) FROM factor_models").fetchone()[0]
    assert n_models == metrics["n_configs"]
    inc = con.execute("SELECT count(*) FROM model_versions WHERE role = 'incumbent'").fetchone()[0]
    assert inc == 1


def test_historical_jev_not_regenerated_by_second_research(e2e):
    from src.pipeline.research_run import generate_historical_jev
    before = len(e2e["jev_calls"])
    ctx = open_context()
    out = generate_historical_jev(ctx)
    assert out["completed_this_run"] == 0 and len(e2e["jev_calls"]) == before


def test_monthly_run_idempotent_and_complete(e2e):
    ctx = open_context()
    first = run_monthly(ctx, clients=e2e["clients"])
    assert first["status"] == "completed"
    s = first["summary"]
    assert sum(s["signals"].values()) > 0 and s["signals"]["BUY"] > 0
    con = ctx.con
    n_txn = con.execute("SELECT count(*) FROM portfolio_transactions WHERE portfolio_id='production'").fetchone()[0]
    n_sig = con.execute("SELECT count(*) FROM signal_history").fetchone()[0]
    expl = json.loads(con.execute("SELECT explanation FROM signal_history LIMIT 1").fetchone()[0])
    for key in ("ticker", "signal", "rank", "final_score", "strongest_positive_drivers", "change_conditions"):
        assert key in expl
    second = run_monthly(open_context(), clients=e2e["clients"])
    assert second["status"] == "already_completed"
    assert con.execute("SELECT count(*) FROM portfolio_transactions WHERE portfolio_id='production'").fetchone()[0] == n_txn
    assert con.execute("SELECT count(*) FROM signal_history").fetchone()[0] == n_sig


def test_backtest_reproduces_exactly(e2e):
    ctx = open_context()
    run_id = ctx.con.execute("SELECT run_id FROM backtest_runs ORDER BY created_at LIMIT 1").fetchone()[0]
    rep = reproduce_run(ctx, run_id)
    assert rep["reproduced"], rep
