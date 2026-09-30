"""Typed loader and validator for config/themes.yaml (THEMES_SPEC; rules in CLAUDE.md).

Validation is deliberately strict: a research or backtest run must never proceed with an unverified industry name,
an unknown factor, or theme weights that do not sum to one. Naming: the ``fmp_`` prefix refers only to the
Financial Modeling Prep API; factor-mimicking portfolios use ``mimic_``.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from src.config import CONFIG_DIR

THEMES_PATH = CONFIG_DIR / "themes.yaml"

# Characteristics the loader accepts in factor_groups. Existing ones are computed by src/features; the T4/T4b
# additions are implemented in src/features/theme_features.py.
KNOWN_FACTORS = {
    "mom_12_1", "dist_52w_high", "idio_vol_60d", "max_ret_21d", "share_issuance", "asset_growth",
    "gross_profitability", "cop_at", "ebit_ev", "ocf_ev", "sue", "droe", "cash_runway_years",
    "capex_at", "fcf_margin", "profitable_growth", "net_debt_ebitda", "oil_beta_trend",
    "ear_3d", "sue_announce",
}


class ThemesConfigError(ValueError):
    pass


class Universe(BaseModel):
    exchanges: list[str]
    include_nyse_american: bool = False
    include_adr: bool = False
    include_foreign_filers: bool = False
    min_price: float
    min_market_cap: float
    min_adv20: float
    min_history_sessions: int


class Classification(BaseModel):
    text_source: str
    forms: list[str]
    valid_from: str
    valid_until: str
    match: str
    one_theme_per_firm: bool
    primary_subtheme: str
    theme_tie_priority: list[str]
    review_file: str
    live_manual_overrides: bool
    backtest_manual_overrides: bool

    @field_validator("backtest_manual_overrides")
    @classmethod
    def no_backtest_overrides(cls, v: bool) -> bool:
        if v:
            raise ValueError("manual include/exclude overrides are never allowed in backtests (CLAUDE.md §1)")
        return v


class Stage(BaseModel):
    pre_profit_rule: str
    biotech_commercial_revenue_usd: float


class Scoring(BaseModel):
    normalization: str
    price_signal_scope: str
    accounting_signal_scope: str
    group_weights: str
    min_coverage: float
    min_weight_present: float


class Portfolio(BaseModel):
    rebalance: str
    weighting: str
    hold_buffer: float
    max_share_per_subtheme: float
    position_cap: float
    entry_block_top_vol_pct: float
    costs: str


class TALayer(BaseModel):
    interval_days: int
    journal_file: str
    rules_file: str
    auto_trade: bool

    @field_validator("auto_trade")
    @classmethod
    def no_auto_trade(cls, v: bool) -> bool:
        if v:
            raise ValueError("auto_trade must be false: the TA layer only produces tables and a journal")
        return v


class SortPortfolios(BaseModel):
    n_if_ge_50: int
    n_if_lt_50: int


class Research(BaseModel):
    horizons: list[int]
    winsorize: tuple[float, float]
    sort_portfolios: SortPortfolios
    breakpoints: str
    portfolio_weighting: list[str]
    alpha_models: list[str]
    fm_controls: list[str]
    fm_variants: list[str]
    nw_lags: str
    corr_redundancy_threshold: float
    vif_threshold: float
    persistence_lags_months: list[int]
    bivariate_sort: str
    subperiods: list[tuple[str, str]]
    min_names_per_date: int


class Subtheme(BaseModel):
    fmp_industries: list[str] = Field(default_factory=list)
    sic: list[int] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    min_hits: int = 0


class Theme(BaseModel):
    enabled: bool
    weight: float
    n_picks: int
    benchmarks: list[str]
    split: str | None = None
    subthemes: dict[str, Subtheme]


class SignedFactor(BaseModel):
    name: str
    direction: int  # +1 higher is better, -1 lower is better


class ThemesConfig(BaseModel):
    version: str
    universe: Universe
    classification: Classification
    stage: Stage
    scoring: Scoring
    portfolio: Portfolio
    ta_layer: TALayer
    research: Research
    themes: dict[str, Theme]
    factor_groups: dict[str, list[SignedFactor]]
    factor_sets: dict[str, list[str]]
    theme_factor_map: dict[str, dict]

    @field_validator("factor_groups", mode="before")
    @classmethod
    def parse_signed(cls, v: dict) -> dict:
        out = {}
        for group, names in v.items():
            parsed = []
            for n in names:
                n = str(n).strip()
                parsed.append({"name": n[1:], "direction": -1} if n.startswith("-") else {"name": n, "direction": 1})
            out[group] = parsed
        return out

    @model_validator(mode="after")
    def check_references(self) -> ThemesConfig:
        total = sum(t.weight for t in self.themes.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"theme weights must sum to 1.0 (got {total:.4f})")
        for group, factors in self.factor_groups.items():
            for f in factors:
                if f.name not in KNOWN_FACTORS:
                    raise ValueError(f"factor group {group!r}: unknown factor {f.name!r}")
        for fs, groups in self.factor_sets.items():
            for g in groups:
                if g not in self.factor_groups:
                    raise ValueError(f"factor set {fs!r}: unknown group {g!r}")
        for theme, mapping in self.theme_factor_map.items():
            if theme not in self.themes:
                raise ValueError(f"theme_factor_map: unknown theme {theme!r}")
            for stage, target in mapping.items():
                if stage == "subtheme_extra":
                    for sub, groups in target.items():
                        if sub not in self.themes[theme].subthemes:
                            raise ValueError(f"{theme}.subtheme_extra: unknown subtheme {sub!r}")
                        for g in groups:
                            if g not in self.factor_groups:
                                raise ValueError(f"{theme}.subtheme_extra.{sub}: unknown group {g!r}")
                elif target not in self.factor_sets:
                    raise ValueError(f"theme_factor_map.{theme}.{stage}: unknown factor set {target!r}")
        for name in self.classification.theme_tie_priority:
            if name not in self.themes:
                raise ValueError(f"theme_tie_priority: unknown theme {name!r}")
        return self

    # --- helpers -----------------------------------------------------------------------------------------------
    def enabled_weights(self) -> dict[str, float]:
        """Weights of enabled themes, renormalized so they sum to one (disabled themes redistribute pro rata)."""
        en = {k: t.weight for k, t in self.themes.items() if t.enabled}
        tot = sum(en.values())
        if tot <= 0:
            raise ThemesConfigError("no enabled theme")
        return {k: v / tot for k, v in en.items()}

    def all_fmp_industries(self) -> set[str]:
        return {i for t in self.themes.values() for s in t.subthemes.values() for i in s.fmp_industries}

    def factor_groups_for(self, theme: str, stage: str, subtheme: str | None = None) -> list[str]:
        mapping = self.theme_factor_map[theme]
        groups = list(self.factor_sets[mapping[stage]])
        extra = mapping.get("subtheme_extra", {})
        if subtheme and subtheme in extra:
            groups += [g for g in extra[subtheme] if g not in groups]
        return groups


def file_sha256(path: Path = THEMES_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_themes_config(path: Path | None = None, strict: bool = False,
                       known_fmp_industries: set[str] | None = None) -> ThemesConfig:
    """Load and validate. ``strict`` (research/backtest mode) refuses unverified industry names.

    ``known_fmp_industries``: the industry names present in the FMP dump (T0). Any configured name that FMP does
    not know raises an error instead of being skipped silently.
    """
    path = path or THEMES_PATH
    text = path.read_text(encoding="utf-8")
    if strict and "# VERIFY" in text:
        raise ThemesConfigError(f"{path.name} still contains '# VERIFY' markers; run T0 and confirm industry names")
    try:
        cfg = ThemesConfig.model_validate(yaml.safe_load(text))
    except ValueError as exc:
        raise ThemesConfigError(str(exc)) from exc
    if known_fmp_industries is not None:
        missing = sorted(cfg.all_fmp_industries() - set(known_fmp_industries))
        if missing:
            raise ThemesConfigError(f"fmp_industries not found in FMP: {missing}")
    return cfg


def known_fmp_industries_from_dump(path: Path | None = None) -> set[str]:
    """Industry names present in the T0 dump (research/themes/fmp_industries.csv)."""
    import pandas as pd

    from src.config import PROJECT_ROOT
    path = path or PROJECT_ROOT / "research" / "themes" / "fmp_industries.csv"
    return set(pd.read_csv(path)["industry"].dropna())


def load_strict() -> ThemesConfig:
    """Research/backtest mode: no VERIFY markers and every industry verified against the T0 dump."""
    return load_themes_config(strict=True, known_fmp_industries=known_fmp_industries_from_dump())
