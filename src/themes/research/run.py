"""Theme research run (THEMES_SPEC §7): per scope (theme, subtheme with n >= 15, pooled) and factor, all §7.1-§7.8
analyses, the §7.9 decision rule, CSVs and a Turkish report ``reports/themes/<run_id>/factor_explain.md``.

Descriptive only: nothing here changes factor sets or weights (§7.9, CLAUDE.md §3). Factors are analysed on the rows
whose stage actually uses them (e.g. quality only for profitable firms); candidate factors outside every set
(the earnings_event group) are analysed on all rows. Targets: theme-index-adjusted forward returns
(``label_fwd_<h>_theme``); Fama-MacBeth also reports raw forward returns.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.themes.config import ThemesConfig
from src.themes.research import analyses as A
from src.themes.research.stats import nw_mean

log = logging.getLogger(__name__)

# §7.8 "why it should work": mechanism (risk / behavioural / limits to arbitrage) and source
WHY = {
    "mom_12_1": ("davranışsal (yetersiz tepki) + risk", "Jegadeesh & Titman (1993); Carhart (1997)"),
    "dist_52w_high": ("davranışsal (çıpalama)", "George & Hwang (2004)"),
    "idio_vol_60d": ("sınırlı arbitraj / piyango tercihi (−)", "Ang, Hodrick, Xing & Zhang (2006)"),
    "max_ret_21d": ("piyango tercihi (−)", "Bali, Cakici & Whitelaw (2011)"),
    "share_issuance": ("piyasa zamanlaması (−)", "Pontiff & Woodgate (2008); Daniel & Titman (2006)"),
    "asset_growth": ("aşırı yatırım / q-teorisi (−)", "Cooper, Gulen & Schill (2008); Hou, Xue & Zhang (2015)"),
    "capex_at": ("yatırım faktörü (−)", "Titman, Wei & Xie (2004); Fama & French (2015) CMA"),
    "gross_profitability": ("risk/kalite", "Novy-Marx (2013)"),
    "cop_at": ("kalite (tahakkuksuz kârlılık)", "Ball, Gerakos, Linnainmaa & Nikolaev (2016)"),
    "ebit_ev": ("değer (risk + davranışsal)", "Loughran & Wellman (2011)"),
    "ocf_ev": ("değer (nakit akışı)", "Lakonishok, Shleifer & Vishny (1994)"),
    "sue": ("davranışsal (kazanç sonrası sürüklenme)", "Bernard & Thomas (1989)"),
    "droe": ("temel momentum", "Hou, Xue & Zhang (2015) q-faktör ROE"),
    "profitable_growth": ("kalite + büyüme", "Mohanram (2005) GSCORE ruhunda"),
    "cash_runway_years": ("finansal kısıt / seyreltme riski", "Hadlock & Pierce (2010) — tema uyarlaması"),
    "net_debt_ebitda": ("kaldıraç / sıkıntı riski (−)", "Campbell, Hilscher & Szilagyi (2008)"),
    "oil_beta_trend": ("emtia risk primi + trend", "Moskowitz, Ooi & Pedersen (2012) — tema uyarlaması"),
    "ear_3d": ("davranışsal (duyuru getirisi sürüklenmesi)", "Chan, Jegadeesh & Lakonishok (1996)"),
    "sue_announce": ("davranışsal (PEAD, duyuru tarihli)", "Bernard & Thomas (1989); Livnat & Mendenhall (2006)"),
}


def factor_directions(cfg: ThemesConfig) -> dict[str, int]:
    return {f.name: f.direction for fs in cfg.factor_groups.values() for f in fs}


def group_of(cfg: ThemesConfig) -> dict[str, str]:
    return {f.name: g for g, fs in cfg.factor_groups.items() for f in fs}


def in_set_groups(cfg: ThemesConfig) -> set[str]:
    used = {g for gs in cfg.factor_sets.values() for g in gs}
    for m in cfg.theme_factor_map.values():
        for extra in (m.get("subtheme_extra") or {}).values():
            used |= set(extra)
    return used


def applicable(panel: pd.DataFrame, cfg: ThemesConfig, factor: str) -> pd.Series:
    """Rows whose stage (and subtheme) use the factor's group; candidates outside every set -> all rows."""
    g = group_of(cfg)[factor]
    if g not in in_set_groups(cfg):
        return pd.Series(True, index=panel.index)
    cache: dict[tuple, bool] = {}

    def uses(t, s, sub):
        k = (t, s, sub)
        if k not in cache:
            try:
                cache[k] = g in cfg.factor_groups_for(t, s, sub)
            except KeyError:
                cache[k] = False
        return cache[k]
    return pd.Series([uses(t, s, sub) for t, s, sub in zip(panel["theme"], panel["stage"], panel["subtheme"],
                                                              strict=True)], index=panel.index)


def scopes(panel: pd.DataFrame, cfg: ThemesConfig) -> list[tuple[str, str, pd.DataFrame]]:
    out = [("havuz", "pooled", panel)]
    min_n = cfg.research.min_names_per_date
    for t in cfg.themes:
        p = panel[panel["theme"] == t]
        if p.empty:
            continue
        out.append((t, "theme", p))
        for sub, ps in p.groupby("subtheme"):
            if ps.groupby("rebalance_date").size().median() >= min_n:
                out.append((f"{t}/{sub}", "subtheme", ps))
    return out


def analyse_scope(name: str, kind: str, p: pd.DataFrame, cfg: ThemesConfig, factors: list[str], french: pd.DataFrame,
                  regimes: dict[str, pd.Series]) -> dict:
    r = cfg.research
    wins = tuple(r.winsorize)
    min_n = r.min_names_per_date
    dirs = factor_directions(cfg)
    res = {"ic": [], "sorts": [], "alphas": [], "dependent": [], "fm": [], "stability": [], "orth": []}
    present = [f for f in factors if f in p and p[f].notna().mean() > 0.05]
    res["descriptive"] = A.descriptive(p, present, wins).assign(scope=name)
    pear, spear, comb = A.correlations(p, present, wins)
    res["corr"] = comb
    res["redundant"] = A.redundant_pairs(pear, spear, r.corr_redundancy_threshold).assign(scope=name)
    vif_f = [f for f in present if p[f].notna().mean() >= 0.5]
    res["vif"] = A.vif(p, vif_f).rename("vif").to_frame().assign(scope=name)
    res["persistence"] = A.persistence(p, present, r.persistence_lags_months, min_n).assign(scope=name)
    sub_masks = A.subperiod_masks(pd.DatetimeIndex(sorted(p["rebalance_date"].unique())), r.subperiods)
    for f in present:
        q = p[applicable(p, cfg, f)].copy()
        q["sig"] = q[f] * dirs.get(f, 1)
        q["resid"] = A.orthogonal_residuals(q, "sig")
        for h in r.horizons:
            lab = f"label_fwd_{h}_theme"
            ic = A.rank_ic_series(q, "sig", lab, min_n)
            if ic.empty:
                continue
            s = A.ic_summary(ic, h)
            res["ic"].append({"scope": name, "kind": kind, "factor": f, "horizon": h, **s})
            ts = A.sort_portfolios(q, "sig", lab, min_n, r.sort_portfolios.n_if_ge_50, r.sort_portfolios.n_if_lt_50)
            res["sorts"].append({"scope": name, "factor": f, "horizon": h, **A.sort_summary(ts, h)})
            if h == 21:  # alphas need raw (not theme-adjusted) monthly returns
                raw = A.sort_portfolios(q, "sig", f"label_fwd_{h}", min_n, r.sort_portfolios.n_if_ge_50,
                                        r.sort_portfolios.n_if_lt_50)
                al = A.alphas(raw, french, r.alpha_models)
                if not al.empty:
                    res["alphas"].append(al.assign(scope=name, factor=f))
            dep = A.dependent_sort(q, "sig", lab, "score", min_n)
            if not dep.empty:
                s2 = nw_mean(dep["avg_diff"], max(1, h // 21))
                res["dependent"].append({"scope": name, "factor": f, "horizon": h, "avg_diff": s2["mean"],
                                         "nw_t": s2["t"], "months": s2["n"]})
            for v in r.fm_variants:
                for target in (lab, f"label_fwd_{h}"):
                    fm = A.fama_macbeth(q, ["sig"], target, list(r.fm_controls), v, wins, min_n)
                    sm = A.fm_summary(fm, ["sig"], h, v)
                    if not sm.empty:
                        res["fm"].append(sm.assign(scope=name, factor=f, horizon=h, variant=v,
                                                   target="tema_arındırılmış" if target == lab else "ham"))
            buckets = {**sub_masks, **regimes}
            res["stability"].append({"scope": name, "factor": f, "horizon": h,
                                     **{k: v for k, v in A.bucket_means(ic, buckets).items()}})
            # §7.2 orthogonalization: IC of the part of the factor not explained by the score and subtheme
            oic = A.rank_ic_series(q, "resid", lab, min_n)
            if not oic.empty:
                res["orth"].append({"scope": name, "factor": f, "horizon": h, **A.ic_summary(oic, h)})
    # all-factor Fama-MacBeth on factors with >= 50% coverage (complete rows), main variant, theme-adjusted target
    allf = [f for f in present if p[f].notna().mean() >= 0.5]
    if allf:
        q = p.copy()
        cols = []
        for f in allf:
            q[f"sig_{f}"] = q[f] * dirs.get(f, 1)
            cols.append(f"sig_{f}")
        for h in r.horizons:
            fm = A.fama_macbeth(q, cols, f"label_fwd_{h}_theme", list(r.fm_controls), "ols_rank_normal", wins, min_n)
            sm = A.fm_summary(fm, cols, h, "ols_rank_normal")
            if not sm.empty:
                res["fm"].append(sm.assign(scope=name, factor=sm["factor"].str[4:], horizon=h,
                                           variant="ols_rank_normal_all", target="tema_arındırılmış"))
    return res


def decision(ic: pd.DataFrame, fm: pd.DataFrame, stab: pd.DataFrame, dep: pd.DataFrame, subperiods: list[list[str]],
             horizon: int = 126) -> pd.DataFrame:
    """§7.9 rule per (scope, factor): 126-session IC > 0 and NW t >= 2; FM coefficient (main variant) same sign;
    IC > 0 in >= 2/3 of subperiods; dependent-sort average difference > 0."""
    rows = []
    keys = [f"{a}..{b}" for a, b in subperiods]
    icx = ic[ic["horizon"] == horizon].set_index(["scope", "factor"])
    fmx = fm[(fm["horizon"] == horizon) & (fm["variant"] == "ols_rank_normal") &
             (fm["target"] == "tema_arındırılmış")].set_index(["scope", "factor"]) if not fm.empty else pd.DataFrame()
    stx = stab[stab["horizon"] == horizon].set_index(["scope", "factor"]) if not stab.empty else pd.DataFrame()
    dpx = dep[dep["horizon"] == horizon].set_index(["scope", "factor"]) if not dep.empty else pd.DataFrame()
    for key, row in icx.iterrows():
        c1 = bool(row["ic_mean"] > 0 and row["ic_nw_t"] >= 2)
        c2 = bool(key in fmx.index and np.sign(fmx.loc[key, "coef"]) == np.sign(row["ic_mean"]))
        sub = [stx.loc[key, k] for k in keys if key in stx.index and k in stx.columns and pd.notna(stx.loc[key, k])]
        c3 = bool(sub) and (sum(v > 0 for v in sub) >= int(np.ceil(2 * len(sub) / 3)))
        c4 = bool(key in dpx.index and dpx.loc[key, "avg_diff"] > 0)
        rows.append({"scope": key[0], "factor": key[1], "ic_126": row["ic_mean"], "ic_126_nw_t": row["ic_nw_t"],
                     "ic_pozitif_t2": c1, "fm_ayni_isaret": c2, "altdonem_2_3": c3, "bagimli_siralama_pozitif": c4,
                     "calisiyor": c1 and c2 and c3 and c4})
    return pd.DataFrame(rows)


def run_research(panel: pd.DataFrame, scores: pd.DataFrame, cfg: ThemesConfig, french: pd.DataFrame,
                 market_close: pd.Series, vix_close: pd.Series | None, out_dir: Path,
                 factors: list[str] | None = None) -> dict:
    start = pd.Timestamp(cfg.research.subperiods[0][0])
    p = panel[panel["eligible"] & (panel["rebalance_date"] >= start)]
    p = p.merge(scores[["rebalance_date", "symbol", "score"]], on=["rebalance_date", "symbol"], how="left")
    factors = factors or sorted(factor_directions(cfg))
    dates = pd.DatetimeIndex(sorted(p["rebalance_date"].unique()))
    regimes = A.regime_masks(dates, market_close, vix_close)
    agg: dict[str, list] = {}
    for name, kind, sp in scopes(p, cfg):
        log.info("research scope %s (%d rows)", name, len(sp))
        r = analyse_scope(name, kind, sp, cfg, factors, french, regimes)
        for k, v in r.items():
            if k == "corr":
                agg.setdefault("corr", []).append(v.assign(scope=name))
            elif isinstance(v, list):
                agg.setdefault(k, []).extend(v)
            else:
                agg.setdefault(k, []).append(v)
    tables = {}
    for k, v in agg.items():
        if not v:
            tables[k] = pd.DataFrame()
            continue
        if isinstance(v[0], dict):
            tables[k] = pd.DataFrame(v)
        else:
            tables[k] = pd.concat([x.reset_index().rename(columns={"index": "factor"}) if k in
                                   ("descriptive", "vif", "persistence", "corr") else x for x in v], ignore_index=True)
    tables["decision"] = decision(tables["ic"], tables.get("fm", pd.DataFrame()), tables["stability"],
                                  tables.get("dependent", pd.DataFrame()), cfg.research.subperiods)
    counts = p.groupby(["rebalance_date", "theme"]).size().unstack(fill_value=0)
    tables["counts"] = counts.reset_index()
    out_dir.mkdir(parents=True, exist_ok=True)
    for k, df in tables.items():
        df.to_csv(out_dir / f"{k}.csv", index=False)
    return tables


def mom_consistency(con, doc_path: Path, tolerance: float = 0.003) -> dict:
    """T5 check: this module's rank IC on the existing NASDAQ panel reproduces docs/FACTOR_IC.md for mom_12_1
    (21 sessions, market cap >= $300M, ADV20 >= $5M, from 2011-06-30, >= 30 names per month)."""
    import re

    from src.features.store import load_labels, load_panel
    from src.themes.research.stats import plain_t
    panel = load_panel(con)
    lab = load_labels(con, 21)[["rebalance_date", "symbol", "fwd_return"]]
    p = panel[panel["base_eligible"] & (panel["market_cap"] >= 300e6) & (panel["adv20"] >= 5e6) &
              (panel["rebalance_date"] >= pd.Timestamp("2011-06-30"))]
    p = p.merge(lab, on=["rebalance_date", "symbol"], how="inner")
    ic = A.rank_ic_series(p, "mom_12_1", "fwd_return", 30)
    m = re.search(r"\| mom_12_1 \| momentum \| (-?[\d.]+) \| (-?[\d.]+) \|", doc_path.read_text(encoding="utf-8"))
    doc_ic, doc_t = (float(m.group(1)), float(m.group(2))) if m else (np.nan, np.nan)
    diff = float(ic.mean() - doc_ic)
    return {"ic": float(ic.mean()), "t": plain_t(ic), "months": len(ic), "doc_ic": doc_ic, "doc_t": doc_t,
            "diff": diff, "ok": bool(abs(diff) <= tolerance)}
