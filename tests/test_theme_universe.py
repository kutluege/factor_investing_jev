import yaml

from src.themes.config import THEMES_PATH, load_themes_config
from src.themes.universe import allowed_exchanges, is_foreign_filer, stage_a_matches


def cfg_with(tmp_path, mutate=None):
    c = yaml.safe_load(THEMES_PATH.read_text(encoding="utf-8"))
    if mutate:
        mutate(c)
    p = tmp_path / "themes.yaml"
    p.write_text(yaml.safe_dump(c, sort_keys=False), encoding="utf-8")
    return load_themes_config(p)


def test_exchange_filter_excludes_nyse_american_by_default(tmp_path):
    assert allowed_exchanges(load_themes_config()) == {"NASDAQ", "NYSE"}
    c = cfg_with(tmp_path, lambda c: c["universe"].update(include_nyse_american=True))
    assert "AMEX" in allowed_exchanges(c)
    c2 = cfg_with(tmp_path, lambda c: c["universe"].update(exchanges=["NASDAQ"]))
    assert allowed_exchanges(c2) == {"NASDAQ"}


def test_stage_a_matches_by_industry_or_sic():
    cfg = load_themes_config()
    m = stage_a_matches("Biotechnology", None, cfg)
    assert [(x["theme"], x["subtheme"], x["via"], x["needs_10k"]) for x in m] == [
        ("biotech", "biotech_all", "industry", False)]
    by_sic = stage_a_matches("Something Else", 3841, cfg)
    assert {(x["theme"], x["subtheme"]) for x in by_sic} == {("robotics", "surgical_medical")}
    # an industry listed under several subthemes yields every candidate subtheme (membership is decided later)
    multi = {(x["theme"], x["subtheme"]) for x in stage_a_matches("Electrical Equipment & Parts", None, cfg)}
    assert {("robotics", "industrial_automation"), ("robotics", "components"), ("energy", "grid_equipment")} <= multi
    assert stage_a_matches("Banks - Regional", 6022, cfg) == []


def test_disabled_theme_is_not_a_candidate(tmp_path):
    c = cfg_with(tmp_path, lambda c: c["themes"]["biotech"].update(enabled=False))
    assert stage_a_matches("Biotechnology", 2834, c) == []


def test_foreign_filer_uses_latest_annual_report():
    sub = lambda forms: {"filings": {"recent": {"form": forms}}}  # noqa: E731
    assert is_foreign_filer(sub(["6-K", "20-F", "10-K"]))
    assert not is_foreign_filer(sub(["10-Q", "10-K", "20-F"]))  # switched to domestic filing
    assert is_foreign_filer(sub(["40-F"]))
    assert not is_foreign_filer(sub(["8-K"]))


def test_build_candidates_handles_screener_exchange_columns(tmp_path):
    """The FMP screener returns both 'exchange' (full name) and 'exchangeShortName' (code)."""
    import httpx
    import pandas as pd

    from src.data.fmp import FmpClient
    from src.data.http import RawCache
    from src.data.sec import SecClient
    from src.db.schema import connect
    from src.themes.universe import build_candidates

    def fmp_handler(req):
        return httpx.Response(200, json=[])

    def sec_handler(req):
        if req.url.path.endswith("company_tickers_exchange.json"):
            return httpx.Response(200, json={"fields": ["cik", "name", "ticker", "exchange"],
                                             "data": [[1, "Robo Inc", "ROBO", "NYSE"], [2, "Amex Co", "AMXX", "NYSE"]]})
        return httpx.Response(200, json={"sic": "3569", "filings": {"recent": {"form": ["10-K"]}}})
    cache = RawCache(tmp_path / "raw")
    fmp = FmpClient(api_key="k", transport=httpx.MockTransport(fmp_handler), cache=cache)
    sec = SecClient(user_agent="t t@e.com", transport=httpx.MockTransport(sec_handler), cache=cache)
    inv = pd.DataFrame([
        {"symbol": "ROBO", "companyName": "Robo Inc", "exchange": "New York Stock Exchange",
         "exchangeShortName": "NYSE", "country": "US", "sector": "Industrials", "industry": "Industrial - Machinery"},
        {"symbol": "AMXX", "companyName": "Amex Co", "exchange": "NYSE American", "exchangeShortName": "AMEX",
         "country": "US", "sector": "Industrials", "industry": "Industrial - Machinery"}])
    con = connect(":memory:")
    rep = build_candidates(con, fmp, sec, load_themes_config(), inventory=inv)
    got = con.execute("SELECT symbol, exchange, sic FROM theme_candidates").fetchall()
    assert got == [("ROBO", "NYSE", 3569)] and rep["candidates"] == 1  # NYSE American excluded
