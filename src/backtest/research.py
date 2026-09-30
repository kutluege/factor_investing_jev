"""Restricted model search, robust objective, Pareto front, stability, sensitivity and nested walk-forward."""
from __future__ import annotations

import logging
import random
import time
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.backtest.engine import Backtester, BacktestResult
from src.backtest.folds import Fold
from src.backtest.metrics import performance, segment
from src.config import load_config
from src.features.preprocess import robust_z
from src.model.scoring import FAMILIES, ModelConfig, default_config, family_preset

log = logging.getLogger(__name__)

OBJECTIVE_COMPONENTS = ["median_cagr", "medium_horizon_return", "median_calmar", "median_sharpe",
                        "median_drawdown_quality", "worst_drawdown_quality"]


def fold_metrics(equity: pd.Series, trades: pd.DataFrame, folds: list[Fold], bench=None) -> list[dict]:
    out = []
    for f in folds:
        seg = segment(equity, f.test_start, f.test_end)
        if len(seg) < 10:
            out.append({"fold_id": f.fold_id, "error": "insufficient data"})
            continue
        tr = trades[(trades["rebalance_date"] >= f.test_start) & (trades["rebalance_date"] < f.test_end)] \
            if trades is not None and not trades.empty else None
        m = performance(seg, bench, tr)
        m["fold_id"] = f.fold_id
        out.append(m)
    return out


def summarize_folds(fm: list[dict]) -> dict:
    ok = [m for m in fm if "error" not in m]
    if not ok:
        return {"folds": 0}

    def med(key):
        vals = [m[key] for m in ok if m.get(key) is not None]
        return float(np.median(vals)) if vals else None

    mdds = [m["max_drawdown"] for m in ok if m.get("max_drawdown") is not None]
    r3, r6 = med("rolling_3m_median"), med("rolling_6m_median")
    total = [m["total_return"] for m in ok if m.get("total_return") is not None]
    return {
        "folds": len(ok),
        "median_cagr": med("cagr"),
        "median_3m_return": r3,
        "median_6m_return": r6 if r6 is not None else (float(np.median(total)) if total else None),
        "medium_horizon_return": np.nanmean([x for x in (r3, r6) if x is not None]) if (r3 or r6) else None,
        "median_sharpe": med("sharpe"),
        "median_sortino": med("sortino"),
        "median_calmar": med("calmar"),
        "median_max_drawdown": float(np.median(mdds)) if mdds else None,
        "worst_fold_max_drawdown": float(min(mdds)) if mdds else None,
        "median_drawdown_quality": float(np.median(mdds)) if mdds else None,   # closer to 0 is better
        "worst_drawdown_quality": float(min(mdds)) if mdds else None,
        "turnover": med("turnover_annual"),
        "fold_total_returns": total,
    }


def objective_scores(summaries: pd.DataFrame, weights: dict[str, float], turnover_penalty: float,
                     min_folds: int) -> pd.Series:
    """Robust-z each component across candidate configurations, then combine."""
    s = summaries.copy()
    score = pd.Series(0.0, index=s.index)
    for comp, w in weights.items():
        col = s[comp].astype(float) if comp in s else pd.Series(np.nan, index=s.index)
        z = robust_z(col, clip=3.0).fillna(-3.0)  # missing component = worst
        score += float(w) * z
    if "turnover" in s:
        score -= turnover_penalty * robust_z(s["turnover"].astype(float), clip=3.0).fillna(0.0)
    return score.where(s["folds"] >= min_folds, -np.inf)


def pareto_front(df: pd.DataFrame, maximize: list[str], minimize: list[str]) -> pd.Series:
    vals = df[maximize + minimize].astype(float).copy()
    for c in minimize:
        vals[c] = -vals[c]
    arr = vals.fillna(-np.inf).to_numpy()
    n = len(arr)
    efficient = np.ones(n, dtype=bool)
    for i in range(n):
        if not efficient[i]:
            continue
        dominated = np.all(arr >= arr[i], axis=1) & np.any(arr > arr[i], axis=1)
        if dominated.any():
            efficient[i] = False
    return pd.Series(efficient, index=df.index)


@dataclass
class ResearchResult:
    configs: dict[str, ModelConfig]
    results: dict[str, BacktestResult]
    fold_metrics: dict[str, list[dict]]
    summary: pd.DataFrame
    folds: list[Fold]
    best_id: str
    nested: dict = field(default_factory=dict)
    stability: dict = field(default_factory=dict)
    sensitivity: pd.DataFrame = field(default_factory=pd.DataFrame)
    ablation: dict = field(default_factory=dict)


class Researcher:
    def __init__(self, backtester: Backtester, folds: list[Fold], bench: dict[str, pd.Series], jev_available: bool,
                 max_configs: int | None = None):
        self.bt = backtester
        self.folds = folds
        self.bench = bench
        self.cfg = load_config("backtest")
        self.jev_available = jev_available
        self.max_configs = max_configs
        self.configs: dict[str, ModelConfig] = {}
        self.results: dict[str, BacktestResult] = {}
        self.fm: dict[str, list[dict]] = {}
        self.stage: dict[str, str] = {}

    def evaluate(self, cfg: ModelConfig, stage: str) -> str:
        mid = cfg.model_id
        if mid in self.results:
            return mid
        t0 = time.perf_counter()
        res = self.bt.run(cfg)
        # keep only what the analyses need (equity curve + trades); per-day holdings/signal frames of hundreds of
        # configurations would otherwise dominate memory. The selected model is re-run in full afterwards.
        res.signals = pd.DataFrame()
        res.holdings = pd.DataFrame()
        res.rankings = pd.DataFrame()
        if not res.trades.empty:
            res.trades = res.trades[["rebalance_date", "gross", "commission", "transaction_cost", "slippage_cost"]]
        self.configs[mid], self.results[mid] = cfg, res
        log.info("research: %s %d configs done (%s %s N=%d w=%s buf=%s jev=%s) %.1fs", stage, len(self.results),
                 cfg.preset, int(cfg.min_market_cap / 1e6), cfg.portfolio_size, cfg.weighting, cfg.hold_buffer,
                 cfg.jev_weight, time.perf_counter() - t0)
        self.fm[mid] = fold_metrics(res.equity, res.trades, self.folds)
        self.stage[mid] = stage
        return mid

    def _jev_weights(self) -> list[float]:
        return list(self.cfg["search"]["jev_weights"]) if self.jev_available else [0.0]

    def stage1(self) -> list[str]:
        ids = []
        for preset in self.cfg["family_presets"]:
            for w in self._jev_weights():
                ids.append(self.evaluate(default_config(preset=preset, jev_weight=float(w)), "stage1"))
        return ids

    def stage2(self) -> list[str]:
        """Seeded random sample of the full restricted grid. Independent of results, so nested selection over
        stage1+stage2 candidates is not contaminated by full-sample performance."""
        s = self.cfg["search"]
        rng = random.Random(int(s["seed"]))
        grid = dict(preset=list(self.cfg["family_presets"]), min_market_cap=s["market_caps"],
                    min_adv20=s["adv_thresholds"], portfolio_size=s["portfolio_sizes"], weighting=s["weightings"],
                    hold_buffer=s["hold_buffers"], jev_weight=self._jev_weights())
        n = int(s["random_configs"]) if self.max_configs is None else min(int(s["random_configs"]), self.max_configs)
        ids, seen, attempts = [], set(self.results), 0
        while len(ids) < n and attempts < n * 20:
            attempts += 1
            c = ModelConfig(preset=rng.choice(grid["preset"]), min_market_cap=float(rng.choice(grid["min_market_cap"])),
                            min_adv20=float(rng.choice(grid["min_adv20"])),
                            portfolio_size=int(rng.choice(grid["portfolio_size"])), weighting=rng.choice(grid["weighting"]),
                            hold_buffer=float(rng.choice(grid["hold_buffer"])),
                            jev_weight=float(rng.choice(grid["jev_weight"])))
            if c.model_id in seen:
                continue
            seen.add(c.model_id)
            ids.append(self.evaluate(c, "stage2"))
        return ids

    def summary(self) -> pd.DataFrame:
        rows = []
        for mid, fm in self.fm.items():
            c = self.configs[mid]
            full = performance(self.results[mid].equity, self.bench, self.results[mid].trades)
            rows.append({"model_id": mid, "stage": self.stage[mid], **{k: v for k, v in c.to_dict().items()
                                                                       if k != "family_weights"},
                         **summarize_folds(fm), "full_cagr": full.get("cagr"), "full_max_drawdown": full.get("max_drawdown"),
                         "full_sharpe": full.get("sharpe")})
        df = pd.DataFrame(rows).set_index("model_id")
        for col in ("folds", "median_cagr", "worst_fold_max_drawdown", "turnover", "median_sharpe",
                    "median_max_drawdown", *OBJECTIVE_COMPONENTS):
            if col not in df:
                df[col] = np.nan if col != "folds" else 0
        df["folds"] = df["folds"].fillna(0)
        o = self.cfg["objective"]
        df["objective"] = objective_scores(df, o["weights"], float(o["turnover_penalty"]),
                                           int(o["min_folds_for_selection"]))
        df["pareto"] = pareto_front(df, ["median_cagr", "worst_fold_max_drawdown"], ["turnover"])
        return df.sort_values("objective", ascending=False)

    # --- robustness analyses ------------------------------------------------------------------------------
    def stability(self, summary: pd.DataFrame, top_frac: float = 0.1) -> dict:
        valid = summary[np.isfinite(summary["objective"])]
        k = max(5, int(len(valid) * top_frac))
        top = valid.head(k)
        fam_incl = Counter()
        for mid in top.index:
            preset = family_preset(self.configs[mid].preset)
            if preset.get("dynamic"):
                fam_incl["(dynamic IC weights)"] += 1
                continue
            for f in FAMILIES:
                if float(preset.get(f, 0)) > 0:
                    fam_incl[f] += 1
        params = {p: top[p].value_counts(normalize=True).round(3).to_dict()
                  for p in ("preset", "portfolio_size", "min_market_cap", "min_adv20", "weighting", "hold_buffer",
                            "jev_weight")}
        return {"top_k": k, "family_inclusion_share": {f: round(v / k, 3) for f, v in fam_incl.items()},
                "parameter_frequency": params,
                "objective_spread_top_k": float(top["objective"].max() - top["objective"].min()) if k > 1 else 0.0}

    def sensitivity(self, best: ModelConfig) -> pd.DataFrame:
        s = self.cfg["search"]
        variants = []
        for field_name, values in (("min_market_cap", s["market_caps"]), ("min_adv20", s["adv_thresholds"]),
                                   ("portfolio_size", s["portfolio_sizes"]), ("weighting", s["weightings"]),
                                   ("hold_buffer", s["hold_buffers"]), ("jev_weight", self._jev_weights()),
                                   ("cost_multiplier", s["cost_multipliers"]), ("preset", list(self.cfg["family_presets"]))):
            for v in values:
                v = type(getattr(best, field_name))(v)
                variants.append((field_name, v, best.replace(**{field_name: v})))
        rows = []
        for field_name, v, c in variants:
            mid = self.evaluate(c, "sensitivity")
            sm = summarize_folds(self.fm[mid])
            rows.append({"parameter": field_name, "value": v, "model_id": mid, "is_best": c == best,
                         "median_cagr": sm.get("median_cagr"), "median_sharpe": sm.get("median_sharpe"),
                         "worst_fold_max_drawdown": sm.get("worst_fold_max_drawdown"), "turnover": sm.get("turnover")})
        return pd.DataFrame(rows)

    # --- honest nested walk-forward -----------------------------------------------------------------------
    def select_in_train(self, candidate_ids: list[str], fold: Fold) -> str | None:
        """Choose a configuration using only performance inside the training window (6-month blocks)."""
        blocks, start = [], fold.train_start
        while True:
            end = start + pd.DateOffset(months=6)
            if end > fold.train_end + pd.DateOffset(months=1):
                break
            blocks.append((start, end))
            start = end
        if len(blocks) < 2:
            return None
        rows = {}
        for mid in candidate_ids:
            eq = self.results[mid].equity
            fm = []
            for i, (a, b) in enumerate(blocks):
                seg = segment(eq, a, min(b, fold.train_end + pd.DateOffset(days=31)))
                if len(seg) >= 10:
                    m = performance(seg)
                    m["fold_id"] = i
                    fm.append(m)
            rows[mid] = summarize_folds(fm)
        df = pd.DataFrame(rows).T
        o = self.cfg["objective"]
        score = objective_scores(df, o["weights"], float(o["turnover_penalty"]), 2)
        return score.idxmax() if np.isfinite(score.max()) else None

    def train_block_summaries(self, candidate_ids: list[str], fold: Fold) -> tuple[pd.DataFrame, dict]:
        """Per-candidate summaries over 6-month blocks inside the training window (and per-block returns)."""
        blocks, start = [], fold.train_start
        while True:
            end = start + pd.DateOffset(months=6)
            if end > fold.train_end + pd.DateOffset(months=1):
                break
            blocks.append((start, end))
            start = end
        rows, block_returns = {}, {}
        for mid in candidate_ids:
            eq = self.results[mid].equity
            fm = []
            for i, (a, b) in enumerate(blocks):
                seg = segment(eq, a, min(b, fold.train_end + pd.DateOffset(days=31)))
                if len(seg) >= 10:
                    m = performance(seg)
                    m["fold_id"] = i
                    fm.append(m)
            rows[mid] = summarize_folds(fm)
            block_returns[mid] = [m.get("total_return") for m in fm]
        return pd.DataFrame(rows).T, block_returns

    def robust_candidates(self, ids: list[str]) -> list[str]:
        """Pre-specified diversification rules for candidates eligible for selection (not results-based)."""
        s = self.cfg["search"]
        min_n = int(s.get("min_portfolio_size_for_selection", 1))
        min_cap = float(s.get("min_market_cap_for_selection", 0))
        excluded = set(s.get("selection_excluded_presets", []))
        return [m for m in ids if self.configs[m].portfolio_size >= min_n and self.configs[m].min_market_cap >= min_cap
                and self.configs[m].preset not in excluded]

    def nested_promotion(self, candidate_ids: list[str], prior: ModelConfig, label: str) -> dict:
        """Emulates the production incumbent/challenger process out of sample.

        Starts from the pre-specified prior configuration. At each fold the best training-window candidate
        replaces the incumbent only if it passes the same promotion rules used in production (objective margin,
        block win rate, worst-drawdown guard). Otherwise the incumbent is kept.
        """
        prior_id = self.evaluate(prior, "prior")
        pol = self.cfg["promotion"]
        o = self.cfg["objective"]
        incumbent = prior_id
        schedule, picks = [], []
        ids = list(dict.fromkeys(candidate_ids + [prior_id]))
        for f in self.folds:
            df, blocks = self.train_block_summaries(ids, f)
            if df.empty or df["folds"].max() < 2:
                schedule.append((f.test_start, self.configs[incumbent]))
                picks.append({"fold_id": f.fold_id, "test_start": str(f.test_start.date()), "model_id": incumbent,
                              "preset": self.configs[incumbent].preset, "promoted": False, "reason": "insufficient history"})
                continue
            score = objective_scores(df, o["weights"], float(o["turnover_penalty"]), 2)
            challenger = score.idxmax()
            reason, promoted = "incumbent retained", False
            if challenger != incumbent:
                d_obj = float(score[challenger] - score[incumbent])
                cr, ir = blocks[challenger], blocks[incumbent]
                n = min(len(cr), len(ir))
                win = sum(1 for x, y in zip(cr[-n:], ir[-n:], strict=False) if x is not None and y is not None and x > y) / n \
                    if n else 0.0
                cdd = df.loc[challenger, "worst_fold_max_drawdown"]
                idd = df.loc[incumbent, "worst_fold_max_drawdown"]
                dd_ok = cdd is not None and idd is not None and (idd - cdd) <= float(pol["max_worst_dd_deterioration"])
                if d_obj >= float(pol["min_objective_improvement"]) and win >= float(pol["min_fold_win_rate"]) and dd_ok:
                    incumbent, promoted, reason = challenger, True, f"promoted (objective +{d_obj:.2f}, win {win:.0%})"
                else:
                    reason = f"retained (challenger objective +{d_obj:.2f}, win {win:.0%}, dd_ok={dd_ok})"
            schedule.append((f.test_start, self.configs[incumbent]))
            c = self.configs[incumbent]
            picks.append({"fold_id": f.fold_id, "test_start": str(f.test_start.date()), "model_id": incumbent,
                          "preset": c.preset, "portfolio_size": c.portfolio_size, "min_market_cap": c.min_market_cap,
                          "promoted": promoted, "reason": reason, "jev_weight": c.jev_weight})
        res = self.bt.run(schedule[0][1], start=schedule[0][0], schedule=schedule)
        fm = fold_metrics(res.equity, res.trades, [f for f in self.folds if f.test_start >= schedule[0][0]], self.bench)
        return {"label": label, "picks": picks, "result": res, "final_model_id": incumbent,
                "metrics": performance(res.equity, self.bench, res.trades), "fold_summary": summarize_folds(fm),
                "fold_metrics": fm}

    def fixed_strategy(self, cfg: ModelConfig, label: str) -> dict:
        """A configuration specified before seeing results, held throughout the out-of-sample period."""
        mid = self.evaluate(cfg, "prior")
        start = self.folds[0].test_start
        res = self.bt.run(cfg, start=start)
        fm = fold_metrics(res.equity, res.trades, self.folds, self.bench)
        return {"label": label, "picks": [{"test_start": str(start.date()), "model_id": mid, "preset": cfg.preset}],
                "result": res, "final_model_id": mid, "metrics": performance(res.equity, self.bench, res.trades),
                "fold_summary": summarize_folds(fm), "fold_metrics": fm}

    def nested_walk_forward(self, candidate_ids: list[str], label: str) -> dict:
        schedule, picks = [], []
        for f in self.folds:
            mid = self.select_in_train(candidate_ids, f)
            if mid is None:
                continue
            schedule.append((f.test_start, self.configs[mid]))
            picks.append({"fold_id": f.fold_id, "test_start": str(f.test_start.date()), "model_id": mid,
                          "preset": self.configs[mid].preset, "jev_weight": self.configs[mid].jev_weight})
        if not schedule:
            return {"label": label, "error": "no fold had enough training history for selection"}
        res = self.bt.run(schedule[0][1], start=schedule[0][0], schedule=schedule)
        fm = fold_metrics(res.equity, res.trades, [f for f in self.folds if f.test_start >= schedule[0][0]], self.bench)
        return {"label": label, "picks": picks, "result": res,
                "metrics": performance(res.equity, self.bench, res.trades), "fold_summary": summarize_folds(fm),
                "fold_metrics": fm}

    def run_all(self, sensitivity: bool = True) -> ResearchResult:
        log.info("research: stage 1 (presets x Jev weights)")
        self.stage1()
        log.info("research: stage 2 (seeded random sample)")
        self.stage2()
        candidates = list(self.results)
        summ = self.summary()
        best_id = summ.index[0]
        best = self.configs[best_id]
        sens = self.sensitivity(best) if sensitivity else pd.DataFrame()
        summ = self.summary()  # include sensitivity variants in the table (not in nested candidates)
        prior = default_config()
        quant_only = [m for m in candidates if self.configs[m].jev_weight == 0]
        robust_q = self.robust_candidates(quant_only)
        nested = {
            "fixed_prior": self.fixed_strategy(prior, "Fixed prior (pre-specified default, no selection)"),
            "promotion_quant_only": self.nested_promotion(robust_q, prior,
                                                          "Incumbent/challenger, quant only (production process)"),
            "free_selection_quant_only": self.nested_walk_forward(quant_only, "Free per-fold selection, quant only"),
        }
        if self.jev_available:
            robust_all = self.robust_candidates(candidates)
            nested["promotion_with_jev"] = self.nested_promotion(
                robust_all, prior, "Incumbent/challenger, Jev weight selectable (upper bound: LLM look-ahead)")
            nested["free_selection_with_jev"] = self.nested_walk_forward(
                candidates, "Free per-fold selection, Jev weight selectable")
        ablation = {}
        if self.jev_available:
            q_best = summ[summ["jev_weight"] == 0]
            j_best = summ[summ["jev_weight"] > 0]
            ablation = {
                "best_quant_only": q_best.iloc[0][["median_cagr", "median_sharpe", "worst_fold_max_drawdown",
                                                   "objective"]].to_dict() if len(q_best) else None,
                "best_with_jev": j_best.iloc[0][["median_cagr", "median_sharpe", "worst_fold_max_drawdown", "objective",
                                                 "jev_weight"]].to_dict() if len(j_best) else None,
            }
        return ResearchResult(self.configs, self.results, self.fm, summ, self.folds, best_id, nested,
                              self.stability(summ[summ["stage"] != "sensitivity"]), sens, ablation)
