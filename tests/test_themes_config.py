import pytest
import yaml

from src.themes.config import THEMES_PATH, ThemesConfigError, load_themes_config


def write(tmp_path, mutate):
    cfg = yaml.safe_load(THEMES_PATH.read_text(encoding="utf-8"))
    mutate(cfg)
    p = tmp_path / "themes.yaml"
    p.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return p


def test_repo_config_loads_and_signs_are_parsed():
    c = load_themes_config()
    low_risk = {f.name: f.direction for f in c.factor_groups["low_risk"]}
    assert low_risk == {"idio_vol_60d": -1, "max_ret_21d": -1}
    assert abs(sum(c.enabled_weights().values()) - 1.0) < 1e-12


def test_weights_must_sum_to_one(tmp_path):
    p = write(tmp_path, lambda c: c["themes"]["energy"].update(weight=0.5))
    with pytest.raises(ThemesConfigError, match="sum to 1.0"):
        load_themes_config(p)


def test_disabled_theme_weight_is_redistributed(tmp_path):
    p = write(tmp_path, lambda c: c["themes"]["energy"].update(enabled=False))
    w = load_themes_config(p).enabled_weights()
    assert set(w) == {"robotics", "biotech"} and abs(w["robotics"] - 0.4 / 0.75) < 1e-12


def test_unknown_factor_and_group_rejected(tmp_path):
    p = write(tmp_path, lambda c: c["factor_groups"]["momentum"].append("made_up_factor"))
    with pytest.raises(ThemesConfigError, match="unknown factor"):
        load_themes_config(p)
    p2 = write(tmp_path, lambda c: c["factor_sets"]["pre_profit"].append("no_such_group"))
    with pytest.raises(ThemesConfigError, match="unknown group"):
        load_themes_config(p2)


def test_unknown_fmp_industry_is_an_error_not_skipped():
    c = load_themes_config()
    known = c.all_fmp_industries() - {"Solar"}
    with pytest.raises(ThemesConfigError, match="Solar"):
        load_themes_config(known_fmp_industries=known)


def test_backtest_overrides_and_auto_trade_forbidden(tmp_path):
    p = write(tmp_path, lambda c: c["classification"].update(backtest_manual_overrides=True))
    with pytest.raises(ThemesConfigError, match="never allowed in backtests"):
        load_themes_config(p)
    p2 = write(tmp_path, lambda c: c["ta_layer"].update(auto_trade=True))
    with pytest.raises(ThemesConfigError, match="auto_trade"):
        load_themes_config(p2)


def test_strict_mode_refuses_verify_markers(tmp_path):
    p = tmp_path / "themes.yaml"
    p.write_text(THEMES_PATH.read_text(encoding="utf-8") + "\n# VERIFY\n", encoding="utf-8")
    with pytest.raises(ThemesConfigError, match="VERIFY"):
        load_themes_config(p, strict=True)
