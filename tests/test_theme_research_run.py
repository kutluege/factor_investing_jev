"""Theme research run end to end on a synthetic theme panel: CSVs, §7.9 decisions, Turkish report, pre-registration."""
import numpy as np
import pandas as pd
import pytest

from src.themes.config import load_themes_config
from src.themes.research import report as R
from src.themes.research.run import applicable, run_research
from src.themes.scoring import score_panel

CFG = load_themes_config()
FACTORS = sorted({f.name for fs in CFG.factor_groups.values() for f in fs})
SUBS = {"robotics": ["industrial_automation", "surgical_medical"], "biotech": ["biotech_all"],
        "energy": ["oil_gas", "power_utilities"]}
STUDIED = ["mom_12_1", "idio_vol_60d", "cash_runway_years", "gross_profitability", "ear_3d"]


def synthetic_panel(seed=0, n=40) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2011-07-31", "2016-06-30", freq="ME")
    rows = []
    for d in dates:
        for theme, subs in SUBS.items():
            df = pd.DataFrame(rng.normal(size=(n, len(FACTORS))), columns=FACTORS)
            df["symbol"] = [f"{theme[:3]}{i}" for i in range(n)]
            df["theme"] = theme
            df["subtheme"] = [subs[i % len(subs)] for i in range(n)]
            df["stage"] = (["clinical", "commercial"] if theme == "biotech" else ["pre_profit", "profitable"])[0] \
                if False else [("clinical" if i % 4 == 0 else "commercial") if theme == "biotech"
                               else ("pre_profit" if i % 4 == 0 else "profitable") for i in range(n)]
            df["market_cap"] = np.exp(rng.normal(21, 1, n))
            df["beta_252d"] = rng.normal(1, 0.3, n)
            df["size_ln_mcap"] = np.log(df["market_cap"])
            for h in (21, 63, 126):
                y = 0.01 * df["mom_12_1"] * np.sqrt(h / 21) + rng.normal(0, 0.08 * np.sqrt(h / 21), n)
                df[f"label_fwd_{h}"] = y
                df[f"label_fwd_{h}_theme"] = y - y.mean()
            df["eligible"] = True
            df["rebalance_date"] = d
            rows.append(df)
    return pd.concat(rows, ignore_index=True)


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    out = tmp_path_factory.mktemp("research")
    p = synthetic_panel()
    scores = score_panel(p, CFG)
    rng = np.random.default_rng(1)
    months = pd.date_range("2011-01-31", "2018-12-31", freq="ME")
    french = pd.DataFrame(rng.normal(0, 0.03, (len(months), 9)), index=months,
                          columns=["ff_mkt_rf", "ff_smb", "ff_hml", "ff_rf", "ff5_smb", "ff5_hml", "ff_rmw", "ff_cma",
                                   "ff_mom"])
    days = pd.bdate_range("2010-01-01", "2018-12-31")
    spy = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(days)))), index=days)
    vix = pd.Series(rng.uniform(10, 40, len(days)), index=days)
    tables = run_research(p, scores, CFG, french, spy, vix, out, factors=STUDIED)
    path = R.write_report(tables, out, "test_run", "abc123", {"passed": True}, None,
                          {"start": "2011-07-31", "end": "2016-06-30", "dates": 60, "rows": len(p)})
    return {"tables": tables, "out": out, "report": path, "panel": p}


def test_csvs_and_report_written(result):
    for name in ("ic", "sorts", "alphas", "dependent", "fm", "descriptive", "corr", "vif", "persistence",
                 "stability", "decision", "counts", "orth"):
        assert (result["out"] / f"{name}.csv").exists(), name
    text = result["report"].read_text(encoding="utf-8")
    assert "§7.9 Karar tablosu" in text and "Kapsam: havuz" in text and "Fama-MacBeth" in text


def test_planted_factor_works_and_noise_mostly_does_not(result):
    d = result["tables"]["decision"].set_index(["scope", "factor"])
    assert bool(d.loc[("havuz", "mom_12_1"), "calisiyor"])
    noise = d.loc["havuz"].drop(index="mom_12_1")
    assert not noise["calisiyor"].any()


def test_stage_specific_factor_only_on_using_rows(result):
    p = result["panel"]
    m = applicable(p, CFG, "cash_runway_years")
    assert set(p.loc[m, "stage"]) <= {"pre_profit", "clinical"}
    assert applicable(p, CFG, "ear_3d").all()  # candidate outside every set -> all rows


def test_preregistration_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "PREREG_DIR", tmp_path / "prereg")
    src = tmp_path / "themes.yaml"
    src.write_text("version: x\n", encoding="utf-8")
    dst, sha = R.preregister("vtest", src)
    assert R.check_preregistration("vtest", src, require_committed=False) == sha
    src.write_text("version: y\n", encoding="utf-8")  # config edited after pre-registration
    with pytest.raises(R.PreregistrationError):
        R.check_preregistration("vtest", src, require_committed=False)
    with pytest.raises(R.PreregistrationError):
        R.preregister("vtest", src)  # cannot silently overwrite a pre-registered version
