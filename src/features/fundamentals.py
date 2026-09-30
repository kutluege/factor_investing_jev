"""Fundamental factor features from PIT SEC snapshots and PIT market capitalization.

Every output row carries ``observation_period_end`` (latest fiscal period used) and ``availability_date`` (first
date the underlying filing could be used), and is produced only from snapshots with snapshot_date <= rebalance.
Invalid ratios (non-positive denominators where the ratio would be meaningless) are set to NaN, not forced.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.prices import split_factor_after

FUNDAMENTAL_FEATURES = [
    "earnings_yield", "fcf_yield", "ebit_ev", "sales_ev", "book_to_market", "cash_to_mcap",
    "roic", "roe", "roa", "gross_profitability", "operating_margin", "fcf_margin", "cash_conversion",
    "debt_to_assets", "net_debt_to_assets", "interest_coverage", "cash_runway_years", "rd_intensity",
    "revenue_yoy", "revenue_cagr_2y", "eps_growth", "ebitda_growth", "fcf_growth", "gross_profit_growth",
    "revenue_growth_accel", "operating_margin_chg", "roic_chg", "fcf_margin_chg", "eps_accel", "leverage_chg",
    "share_dilution_yoy",
    # literature additions (see src/features/research_features.py docstring / docs/RESEARCH.md)
    "cop_at", "ocf_ev", "asset_growth", "share_issuance", "droe", "sue", "fscore", "accruals",
    # themes_v1 (THEMES_SPEC §4, §5.2): stage inputs and new characteristics
    "ocf_ttm", "revenue_ttm", "capex_at", "net_debt_ebitda",
]


def _sue(qhist) -> float:
    """Standardized unexpected earnings: (NI_q - NI_{q-4}) / std of the last 8 seasonal changes."""
    if not isinstance(qhist, (list, tuple)) or len(qhist) < 12:
        return np.nan
    v = [np.nan if x is None else float(x) for x in qhist]
    changes = [v[k] - v[k + 4] for k in range(8)]
    ch = np.array([c for c in changes if not np.isnan(c)])
    if np.isnan(changes[0]) or len(ch) < 6:
        return np.nan
    sd = ch.std(ddof=1)
    return float(np.clip(changes[0] / sd, -10, 10)) if sd > 0 else np.nan


def _col(df: pd.DataFrame, name: str) -> pd.Series:
    return df[name] if name in df else pd.Series(np.nan, index=df.index)


def _div(a: pd.Series, b: pd.Series, require_positive: bool = True) -> pd.Series:
    b = b.astype(float)
    ok = b > 0 if require_positive else b != 0
    return (a.astype(float) / b.where(ok)).replace([np.inf, -np.inf], np.nan)


def _growth(cur: pd.Series, prev: pd.Series, clip: float = 5.0) -> pd.Series:
    """Growth only where the base is positive (growth off a negative base is not meaningful)."""
    return (_div(cur, prev) - 1.0).clip(-1.0, clip)


def _tax_rate(df: pd.DataFrame) -> pd.Series:
    rate = _div(_col(df, "income_tax__ttm"), _col(df, "pretax_income__ttm"))
    return rate.clip(0.0, 0.35).fillna(0.21)


def asof_join_snapshots(snapshots: pd.DataFrame, cik_by_symbol: dict[str, str], date: pd.Timestamp,
                        symbols: list[str]) -> pd.DataFrame:
    """Latest snapshot per symbol with snapshot_date <= date. Hard assertion guards against future filings."""
    if snapshots is None or snapshots.empty:
        return pd.DataFrame(index=pd.Index(symbols, name="symbol"))
    s = snapshots[snapshots["snapshot_date"] <= date]
    s = s.sort_values("snapshot_date").groupby("cik").tail(1).set_index("cik")
    rows = {}
    for sym in symbols:
        cik = cik_by_symbol.get(sym)
        if cik is not None and cik in s.index:
            rows[sym] = s.loc[cik]
    out = pd.DataFrame.from_dict(rows, orient="index")
    out.index.name = "symbol"
    if not out.empty:
        assert (out["availability_date"] <= date).all(), "PIT violation: filing available after rebalance date"
    return out


def compute_fundamental_features(snap: pd.DataFrame, price: pd.Series, splits: pd.DataFrame | None,
                                 date: pd.Timestamp) -> tuple[pd.DataFrame, pd.Series]:
    """Features for one rebalance date. ``price``: split-adjusted close at the date, indexed by symbol.

    Returns (features, market_cap). Market cap = adjusted price x reported shares converted to adjusted units
    using splits that occurred after the share-count date.
    """
    df = snap.reindex(price.index)
    shares = _col(df, "shares_outstanding")
    fallback = _col(df, "diluted_shares")
    shares_end = _col(df, "shares_outstanding__end")
    adj = pd.Series(1.0, index=df.index)
    split_syms = set(df.index) & set(splits["symbol"]) if splits is not None and not splits.empty else set()
    if split_syms:
        for sym in split_syms:
            ref = shares_end.get(sym)
            ref = pd.Timestamp(ref) if pd.notna(ref) else df["period_end"].get(sym) if "period_end" in df else None
            if ref is not None and pd.notna(ref):
                adj[sym] = split_factor_after(splits, sym, pd.Timestamp(ref))
    shares_adj = shares.fillna(fallback) * adj
    mcap = (price * shares_adj).where(shares_adj > 0)

    cash = _col(df, "cash").fillna(0) + _col(df, "short_term_investments").fillna(0)
    debt = _col(df, "long_term_debt").fillna(0) + _col(df, "short_term_debt").fillna(0)
    debt_1y = _col(df, "long_term_debt__1y").fillna(0) + _col(df, "short_term_debt__1y").fillna(0)
    ev = mcap + debt - cash
    assets, assets_1y = _col(df, "total_assets"), _col(df, "total_assets__1y")
    equity, equity_1y = _col(df, "equity"), _col(df, "equity__1y")
    rev, rev_1y, rev_2y = _col(df, "revenue__ttm"), _col(df, "revenue__ttm_1y"), _col(df, "revenue__ttm_2y")
    gp = _col(df, "gross_profit__ttm").fillna(rev - _col(df, "cost_of_revenue__ttm"))
    gp_1y = _col(df, "gross_profit__ttm_1y").fillna(rev_1y - _col(df, "cost_of_revenue__ttm_1y"))
    ebit, ebit_1y = _col(df, "operating_income__ttm"), _col(df, "operating_income__ttm_1y")
    ni, ni_1y = _col(df, "net_income__ttm"), _col(df, "net_income__ttm_1y")
    ocf, ocf_1y = _col(df, "operating_cf__ttm"), _col(df, "operating_cf__ttm_1y")
    capex, capex_1y = _col(df, "capex__ttm").fillna(0), _col(df, "capex__ttm_1y").fillna(0)
    fcf, fcf_1y = ocf - capex, ocf_1y - capex_1y
    dep, dep_1y = _col(df, "depreciation__ttm"), _col(df, "depreciation__ttm_1y")
    dil, dil_1y = _col(df, "diluted_shares"), _col(df, "diluted_shares__1y")
    tax = _tax_rate(df)

    f = pd.DataFrame(index=df.index)
    f["earnings_yield"] = _div(ni, mcap)
    f["fcf_yield"] = _div(fcf, mcap)
    f["ebit_ev"] = _div(ebit, ev)
    f["sales_ev"] = _div(rev, ev)
    f["book_to_market"] = _div(equity, mcap)
    f["cash_to_mcap"] = _div(cash, mcap)

    invested = equity + debt - cash
    invested_1y = equity_1y + debt_1y - (_col(df, "cash__1y").fillna(0) + _col(df, "short_term_investments__1y").fillna(0))
    f["roic"] = _div(ebit * (1 - tax), invested).clip(-2, 2)
    roic_1y = _div(ebit_1y * (1 - tax), invested_1y).clip(-2, 2)
    avg_eq = (equity + equity_1y.fillna(equity)) / 2
    avg_assets = (assets + assets_1y.fillna(assets)) / 2
    f["roe"] = _div(ni, avg_eq).clip(-3, 3)
    f["roa"] = _div(ni, avg_assets).clip(-2, 2)
    f["gross_profitability"] = _div(gp, assets)
    f["operating_margin"] = _div(ebit, rev).clip(-5, 1)
    f["fcf_margin"] = _div(fcf, rev).clip(-5, 1)
    f["cash_conversion"] = _div(ocf, ni).clip(-5, 5)          # only meaningful when earnings are positive
    f["debt_to_assets"] = _div(debt, assets)
    f["net_debt_to_assets"] = _div(debt - cash, assets)
    f["interest_coverage"] = _div(ebit, _col(df, "interest_expense__ttm")).clip(-50, 100)
    burn = (-fcf).where(fcf < 0)
    f["cash_runway_years"] = _div(cash, burn).clip(0, 10).where(fcf < 0, 10.0).where(cash.notna() & fcf.notna())
    f["rd_intensity"] = _div(_col(df, "rd_expense__ttm"), mcap).clip(0, 2)

    f["revenue_yoy"] = _growth(rev, rev_1y)
    f["revenue_cagr_2y"] = (np.sqrt(_div(rev, rev_2y)) - 1.0).clip(-1, 3)
    eps, eps_1y = _div(ni, dil), _div(ni_1y, dil_1y)
    f["eps_growth"] = _growth(eps, eps_1y)
    f["ebitda_growth"] = _growth(ebit + dep.fillna(0), ebit_1y + dep_1y.fillna(0))
    f["fcf_growth"] = _growth(fcf, fcf_1y)
    f["gross_profit_growth"] = _growth(gp, gp_1y)

    rq, rq1, rp, rp1 = (_col(df, f"revenue__{k}") for k in ("q", "q_1y", "q_prev", "q_prev_1y"))
    f["revenue_growth_accel"] = (_growth(rq, rq1) - _growth(rp, rp1)).clip(-3, 3)
    f["operating_margin_chg"] = (f["operating_margin"] - _div(ebit_1y, rev_1y).clip(-5, 1)).clip(-2, 2)
    f["roic_chg"] = (f["roic"] - roic_1y).clip(-2, 2)
    f["fcf_margin_chg"] = (f["fcf_margin"] - _div(fcf_1y, rev_1y).clip(-5, 1)).clip(-2, 2)
    nq, nq1, np_, np1 = (_col(df, f"net_income__{k}") for k in ("q", "q_1y", "q_prev", "q_prev_1y"))
    f["eps_accel"] = (_growth(nq, nq1) - _growth(np_, np1)).clip(-3, 3)
    f["leverage_chg"] = (f["debt_to_assets"] - _div(debt_1y, assets_1y)).clip(-1, 1)
    so_1y = _col(df, "shares_outstanding__1y")
    split_1y = pd.Series(1.0, index=df.index)
    if split_syms:
        for sym in split_syms:
            ref = shares_end.get(sym)
            if pd.notna(ref):
                split_1y[sym] = split_factor_after(splits, sym, pd.Timestamp(ref) - pd.Timedelta(days=365)) / \
                    split_factor_after(splits, sym, pd.Timestamp(ref))
    f["share_dilution_yoy"] = (_div(shares, so_1y * split_1y) - 1.0).clip(-0.5, 3)

    # --- literature additions ---------------------------------------------------------------------------
    # Ball et al. (2016) cash-based operating profitability, cash-flow-statement proxy: OCF / total assets
    f["cop_at"] = _div(ocf, assets).clip(-2, 2)
    f["ocf_ev"] = _div(ocf, ev)
    f["asset_growth"] = (_div(assets, assets_1y) - 1.0).clip(-0.9, 5)            # Cooper-Gulen-Schill [-]
    ratio = _div(shares, so_1y * split_1y)
    f["share_issuance"] = np.log(ratio.where(ratio > 0)).clip(-1, 2)                # Pontiff-Woodgate [-]
    roe_q = _div(_col(df, "net_income__q"), equity)
    roe_q_1y = _div(_col(df, "net_income__q_1y"), equity_1y)
    f["droe"] = (roe_q - roe_q_1y).clip(-1, 1)                                      # Hou et al. (2021) [+]
    f["sue"] = _col(df, "net_income__qhist").map(_sue) if "net_income__qhist" in df else np.nan
    f["accruals"] = _div(ni - ocf, avg_assets).clip(-2, 2)                          # Sloan (1996) [-]
    # Piotroski (2000) F-score: nine binary signals from the latest filing vs one year earlier
    roa_now, roa_1y = _div(ni, assets), _div(ni_1y, assets_1y)
    cur_ratio = _div(_col(df, "current_assets"), _col(df, "current_liabilities"))
    cur_ratio_1y = _div(_col(df, "current_assets__1y"), _col(df, "current_liabilities__1y"))
    gm, gm_1y = _div(gp, rev), _div(gp_1y, rev_1y)
    turn, turn_1y = _div(rev, assets), _div(rev_1y, assets_1y)
    lev, lev_1y = _div(_col(df, "long_term_debt"), assets), _div(_col(df, "long_term_debt__1y"), assets_1y)
    signals = pd.DataFrame({
        "roa_pos": roa_now > 0, "cfo_pos": ocf > 0, "droa_pos": roa_now > roa_1y, "accrual": ocf > ni,
        "lev_down": lev.fillna(0) <= lev_1y.fillna(0), "liquidity_up": cur_ratio > cur_ratio_1y,
        "no_issuance": ratio <= 1.005, "margin_up": gm > gm_1y, "turnover_up": turn > turn_1y})
    known = pd.DataFrame({"roa_pos": roa_now.notna(), "cfo_pos": ocf.notna(), "droa_pos": roa_1y.notna() & roa_now.notna(),
                          "accrual": ocf.notna() & ni.notna(), "lev_down": assets.notna(),
                          "liquidity_up": cur_ratio.notna() & cur_ratio_1y.notna(), "no_issuance": ratio.notna(),
                          "margin_up": gm.notna() & gm_1y.notna(), "turnover_up": turn.notna() & turn_1y.notna()})
    n_known = known.sum(axis=1)
    # scale to 0..9 over the signals that can be computed; require at least 6 of 9
    f["fscore"] = ((signals & known).sum(axis=1) / n_known.replace(0, np.nan) * 9).where(n_known >= 6)

    # --- themes_v1 additions ------------------------------------------------------------------------------------
    f["ocf_ttm"] = ocf                      # stage flag input: pre_profit when <= 0
    f["revenue_ttm"] = rev                  # biotech clinical/commercial threshold input
    f["capex_at"] = _div(_col(df, "capex__ttm"), assets).clip(0, 2)            # investment (-)
    ebitda = ebit + dep.fillna(0)
    f["net_debt_ebitda"] = _div(debt - cash, ebitda).clip(-20, 50)             # leverage (-); EBITDA <= 0 -> NaN
    return f.replace([np.inf, -np.inf], np.nan), mcap


def fundamental_meta(snap: pd.DataFrame, index: pd.Index) -> pd.DataFrame:
    s = snap.reindex(index)
    return pd.DataFrame({"observation_period_end": s.get("period_end"),
                         "availability_date": s.get("availability_date")}, index=index)
