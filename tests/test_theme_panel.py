"""Theme feature panel on the synthetic market: schema, PIT membership, labels, and a truncation leakage test."""
import numpy as np
import pandas as pd
import pytest

from src.data.fmp import FmpClient
from src.data.fundamentals_loader import load_fundamentals
from src.data.http import RawCache
from src.data.prices import load_prices, load_splits
from src.data.sec import SecClient
from src.pipeline.common import open_context
from src.themes import membership as mem_mod
from src.themes import universe as uni_mod
from src.themes.config import load_themes_config
from src.themes.panel import build_theme_panel
from tests.synthetic import fmp_transport, make_world, sec_transport

THEME_OF = {"Technology": ("robotics", "industrial_automation"), "Biotech": ("biotech", "biotech_all"),
            "Energy": ("energy", "oil_gas")}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    mp = pytest.MonkeyPatch()
    tmp = tmp_path_factory.mktemp("theme_panel")
    mp.setenv("FMP_API_KEY", "test")
    mp.setenv("SEC_USER_AGENT", "tests tests@example.com")
    mp.setenv("DATABASE_PATH", str(tmp / "t.duckdb"))
    world = make_world(n_per_group=8, years=4)
    cache = RawCache(tmp / "raw")
    fmp = FmpClient(transport=fmp_transport(world), cache=cache)
    sec = SecClient(transport=sec_transport(world), cache=cache)
    ctx = open_context()
    con = ctx.con
    stocks = [c for c in world.companies if c.group in THEME_OF]
    load_prices(con, fmp, [c.symbol for c in stocks] + ["QQQ", "SPY", "XBI", "XLE"], workers=1)
    load_splits(con, fmp, [c.symbol for c in stocks])
    load_fundamentals(con, sec, [str(c.cik).zfill(10) for c in stocks], workers=1)
    # oil series (Brent) correlated with the energy names is not part of the synthetic FMP world: insert directly
    cal = world.calendar
    rng = np.random.default_rng(11)
    oil = 80 * np.exp(np.cumsum(rng.normal(0, 0.02, len(cal))))
    con.register("_oil", pd.DataFrame({"symbol": "BZUSD", "date": cal.date, "open": oil, "high": oil, "low": oil,
                                       "close": oil, "adj_close": oil, "volume": 0.0, "source": "test",
                                       "loaded_at": pd.Timestamp("2026-01-01")}))
    con.execute("INSERT INTO daily_prices SELECT * FROM _oil")
    con.execute(uni_mod.DDL)
    con.execute(mem_mod.DDL)
    half = cal[len(cal) // 2]
    for i, c in enumerate(stocks):
        theme, sub = THEME_OF[c.group]
        cik = str(c.cik).zfill(10)
        con.execute("INSERT INTO theme_candidates (symbol, cik, exchange, is_active, source) VALUES (?, ?, 'NASDAQ', "
                    "true, 'test')", [c.symbol, cik])
        # the first robotics name only becomes a member half-way through the sample (PIT membership)
        start = half if (i == 0) else cal[0]
        con.execute("INSERT INTO theme_membership (cik, symbol, theme, subtheme, valid_from, valid_to, hits, density, "
                    "filing_accession, method) VALUES (?, ?, ?, ?, ?, ?, 5, 1.0, ?, 'test')",
                    [cik, c.symbol, theme, sub, start.date(), (cal[-1] + pd.Timedelta(days=30)).date(), f"acc{i}"])
    cfg = load_themes_config()
    cfg.universe.min_market_cap = 1e6
    cfg.universe.min_adv20 = 1e3
    cfg.universe.min_price = 1.0
    cfg.research.horizons = [21, 63]
    dates = list(pd.Series(cal, index=cal).groupby([cal.year, cal.month]).max())[14:-1]
    panel = build_theme_panel(con, cfg, dates=[pd.Timestamp(d) for d in dates])
    yield {"con": con, "cfg": cfg, "panel": panel, "dates": dates, "world": world, "half": half, "stocks": stocks}
    con.close()
    mp.undo()


def test_panel_columns_and_persisted(built):
    p = built["panel"]
    for c in ("mom_12_1", "idio_vol_60d", "capex_at", "net_debt_ebitda", "profitable_growth", "stage", "beta_252d",
              "size_ln_mcap", "oil_beta_trend", "label_fwd_21", "label_fwd_21_theme", "eligible", "theme", "subtheme"):
        assert c in p.columns, c
    n = built["con"].execute("SELECT count(*) FROM theme_feature_panel").fetchone()[0]
    assert n == len(p)


def test_membership_is_point_in_time(built):
    p, first = built["panel"], built["stocks"][0].symbol
    rows = p[p["symbol"] == first]
    assert not rows.empty and (rows["rebalance_date"] >= built["half"]).all()


def test_oil_beta_only_for_oil_gas(built):
    p = built["panel"]
    assert p.loc[p["subtheme"] != "oil_gas", "oil_beta_trend"].isna().all()
    assert p.loc[p["subtheme"] == "oil_gas", "oil_beta_trend"].notna().any()


def test_theme_adjusted_label_is_demeaned(built):
    p = built["panel"]
    e = p[p["eligible"] & p["label_fwd_21"].notna()]
    means = e.groupby(["rebalance_date", "theme"])["label_fwd_21_theme"].mean()
    assert means.abs().max() < 1e-9


def test_theme_panel_leakage_truncation(built):
    """Rows for an early date must not change when all data after that date are removed."""
    con, cfg, dates = built["con"], built["cfg"], built["dates"]
    d = pd.Timestamp(dates[len(dates) // 2])
    full = built["panel"]
    con.execute("CREATE TABLE dp_backup AS SELECT * FROM daily_prices")
    try:
        con.execute("DELETE FROM daily_prices WHERE date > ?", [d.date()])
        trunc = build_theme_panel(con, cfg, dates=[d], persist=False)
    finally:
        con.execute("DELETE FROM daily_prices")
        con.execute("INSERT INTO daily_prices SELECT * FROM dp_backup")
        con.execute("DROP TABLE dp_backup")
    feat = [c for c in trunc.columns if not c.startswith("label_") and c not in ("exclusion_reason",)
            and pd.api.types.is_numeric_dtype(trunc[c])]
    a = full[full["rebalance_date"] == d].set_index("symbol")[feat].sort_index()
    b = trunc.set_index("symbol")[feat].sort_index()
    pd.testing.assert_frame_equal(a, b, check_dtype=False, atol=1e-10, rtol=1e-8)


def test_theme_lookahead_audit_passes_and_detects(built):
    from src.themes.panel import theme_lookahead_audit
    con = built["con"]
    assert theme_lookahead_audit(con)["passed"]
    con.execute("CREATE TABLE tp_backup AS SELECT * FROM theme_feature_panel")
    try:
        con.execute("UPDATE theme_feature_panel SET membership_valid_from = rebalance_date + INTERVAL 5 DAY "
                    "WHERE symbol = (SELECT min(symbol) FROM theme_feature_panel)")
        assert not theme_lookahead_audit(con)["passed"]
    finally:
        con.execute("DELETE FROM theme_feature_panel")
        con.execute("INSERT INTO theme_feature_panel SELECT * FROM tp_backup")
        con.execute("DROP TABLE tp_backup")


def test_duplicate_listing_rule_keeps_most_liquid():
    import pandas as pd
    p = pd.DataFrame({"rebalance_date": pd.Timestamp("2026-09-30"), "theme": "ai", "cik": ["1", "1", "2"],
                      "symbol": ["MSTR", "STRC", "NVDA"], "adv20": [5e9, 2e7, 9e9], "eligible": True,
                      "exclusion_reason": None})
    dup = p[p["eligible"] & p["cik"].notna()].sort_values("adv20", ascending=False).duplicated(
        ["rebalance_date", "theme", "cik"])
    assert list(p.loc[dup[dup].index, "symbol"]) == ["STRC"]
