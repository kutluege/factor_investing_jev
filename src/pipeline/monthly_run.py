"""Production monthly analysis: the single code path behind `python -m src.pipeline.monthly` and the dashboard button.

Idempotency: one production run per (portfolio, calendar month of the rebalance date). A completed run is never
re-executed or overwritten; pressing the button again returns the stored result. All decisions, signals and
portfolio accounting for a run are written in one database transaction.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.backtest.engine import Backtester, JevFeatures
from src.config import PROJECT_ROOT, load_config
from src.db.repo import utcnow
from src.explain.explainer import explain, feature_contributions
from src.features.store import (
    build_features,
    default_rebalance_dates,
    load_labels,
    load_market_data,
    load_panel,
)
from src.jev.candidates import (
    build_tasks,
    candidate_definition,
    candidate_symbols,
    jev_feature_frame,
    persist_candidate_set,
    reference_universe,
)
from src.jev.client import JevClient, JevError
from src.jev.state import build_state, regime_context
from src.jev.store import JevTask, decisions_frame, ensure_feature_set, feature_set_id, generate, question_set
from src.model.promotion import current_incumbent
from src.model.scoring import FAMILIES, ModelConfig, ScoreCache, default_config
from src.pipeline.common import (
    Context,
    make_clients,
    update_fundamentals,
    update_prices,
    update_reference,
    verify_configuration,
)
from src.portfolio.book import CostModel, Order, Portfolio, Position, SimulatedBroker
from src.portfolio.signals import BUY, HOLD, SELL, WAIT, SignalRules, decide
from src.portfolio.weights import target_weights

log = logging.getLogger(__name__)
PORTFOLIO_ID = "production"


def run_key_for(portfolio_id: str, rebalance_date: pd.Timestamp) -> str:
    return f"{portfolio_id}:{rebalance_date:%Y-%m}"


def existing_run(con, run_key: str) -> dict | None:
    row = con.execute("SELECT status, rebalance_date, summary FROM production_runs WHERE run_key = ?", [run_key]).fetchone()
    if row is None:
        return None
    return {"status": row[0], "rebalance_date": row[1], "summary": json.loads(row[2]) if row[2] else None}


def load_portfolio(con, portfolio_id: str, initial_capital: float) -> tuple[Portfolio, pd.Timestamp | None]:
    last = con.execute("SELECT max(as_of_date) FROM portfolio_cash WHERE portfolio_id = ?", [portfolio_id]).fetchone()[0]
    if last is None:
        return Portfolio(cash=initial_capital), None
    cash = con.execute("SELECT cash FROM portfolio_cash WHERE portfolio_id = ? AND as_of_date = ?",
                       [portfolio_id, last]).fetchone()[0]
    pos = con.execute("SELECT symbol, shares, entry_date, entry_price, cost_basis FROM portfolio_positions "
                      "WHERE portfolio_id = ? AND as_of_date = ?", [portfolio_id, last]).fetchall()
    return Portfolio(cash=float(cash), positions={
        s: Position(s, float(sh), pd.Timestamp(ed), float(ep), float(cb)) for s, sh, ed, ep, cb in pos}), pd.Timestamp(last)


def previous_ranks(con, portfolio_id: str, before: pd.Timestamp) -> tuple[dict[str, int], dict[str, str]]:
    row = con.execute("SELECT run_key FROM production_runs WHERE portfolio_id = ? AND status = 'completed' "
                      "AND rebalance_date < ? ORDER BY rebalance_date DESC LIMIT 1", [portfolio_id, before.date()]).fetchone()
    if row is None:
        return {}, {}
    ranks = dict(con.execute("SELECT symbol, rank FROM monthly_rankings WHERE run_key = ?", [row[0]]).fetchall())
    sigs = dict(con.execute("SELECT symbol, signal FROM signal_history WHERE run_key = ?", [row[0]]).fetchall())
    return ranks, sigs


def run_monthly(ctx: Context, portfolio_id: str = PORTFOLIO_ID, update_data: bool = True,
                max_price_symbols: int | None = None, clients=None) -> dict:
    con, s = ctx.con, ctx.settings
    verify = verify_configuration(ctx)
    steps = {"verify": verify}
    if update_data:
        fmp, sec = clients or make_clients(ctx)
        steps["reference"] = update_reference(ctx, fmp, sec)
        steps["prices"] = update_prices(ctx, fmp, max_symbols=max_price_symbols)
        steps["fundamentals"] = update_fundamentals(ctx, sec)
    md = load_market_data(con)
    rebalance_date = md.calendar[-1]
    run_key = run_key_for(portfolio_id, rebalance_date)
    prev = existing_run(con, run_key)
    if prev is not None and prev["status"] == "completed":
        ctx.step("idempotency", f"run {run_key} already completed on {prev['rebalance_date']}; returning stored result")
        return {"status": "already_completed", "run_key": run_key, "summary": prev["summary"]}
    con.execute("INSERT INTO production_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (run_key) DO UPDATE SET "
                "status = excluded.status, started_at = excluded.started_at",
                [run_key, portfolio_id, rebalance_date.date(), None, "running", utcnow(), None, None, None])

    # 4-6) universe, factors, technical indicators for the live date and the prior month-end
    hist_dates = default_rebalance_dates(md, load_config("universe")["min_history_days"])
    dates = sorted(set(hist_dates[-1:] + [rebalance_date]))
    ctx.step("features", f"building features for {[str(d.date()) for d in dates]}")
    build_features(con, dates=dates, md=md, persist=True)
    panel = load_panel(con)
    cache = ScoreCache(panel)

    # 7) incumbent model
    inc = current_incumbent(con)
    cfg: ModelConfig = inc["config"] if inc else default_config()
    model_version = inc["version_id"] if inc else "default-unvalidated"
    ctx.step("model", f"model {model_version}: preset={cfg.preset} N={cfg.portfolio_size} jev_weight={cfg.jev_weight}")
    port, _ = load_portfolio(con, portfolio_id, s.initial_capital_usd)
    holdings = list(port.positions)

    # 8-10) quant ranking, Jev candidates, final ranking
    labels = load_labels(con, 126)  # only the dynamic IC preset uses labels; may be empty
    jev_status = verify["jev"]
    jev_info: dict = {"status": jev_status}
    jev_by_symbol: dict[str, dict] = {}
    holding_review: dict[str, dict] = {}
    fsid = None
    client = None
    if s.jev_available:
        try:
            client = JevClient()
            qset = question_set("candidate")
            fsid = ensure_feature_set(con, client.model, qset)
            definition = candidate_definition()
            # the incumbent's own pool is contained in the union definition; holdings are always added
            syms = candidate_symbols(cache, rebalance_date, extra=holdings, definition=definition)
            persist_candidate_set(con, rebalance_date, fsid, syms, definition)
            industries = dict(con.execute("SELECT symbol, coalesce(industry, sic_description) FROM securities").fetchall())
            tasks = build_tasks(cache, md.bench.get("QQQ"), rebalance_date, syms, industries)
            stats = generate(con, tasks, "candidate", client)
            jev_info.update({"feature_set_id": fsid, **stats.summary()})
            dec = decisions_frame(con, fsid, [rebalance_date])
            jf = jev_feature_frame(dec)
            jev_feats = JevFeatures(jf, fsid)
            for r in dec.itertuples():
                jev_by_symbol[r.symbol] = {"answers": r.answers, "decision_id": r.decision_id}
        except JevError as exc:
            jev_info.update({"status": f"failed: {exc}"})
            jev_feats = None
    else:
        jev_feats = None
    bt = Backtester(cache, md.mats["open"], md.mats["close"], labels, jev_feats, s.initial_capital_usd)
    effective_cfg = cfg if jev_feats is not None else cfg.replace(jev_weight=0.0)
    if cfg.jev_weight > 0 and jev_feats is None:
        jev_info["note"] = "incumbent uses Jev but Jev is unavailable: ranked quant-only (jev_weight=0) this month"
    ranking, cs = bt.rank_at(effective_cfg, rebalance_date, holdings)
    if ranking.empty:
        raise RuntimeError("Empty eligible universe at the rebalance date; check data coverage.")

    # 11-12) reconcile and emit signals
    rules = SignalRules.from_config(load_config("backtest")["portfolio"], cfg.portfolio_size, cfg.hold_buffer)
    held_days = {sym: int((rebalance_date - p.entry_date).days) for sym, p in port.positions.items()}
    excl = dict(con.execute("SELECT symbol, exclusion_reason FROM rebalance_universe WHERE rebalance_date = ?",
                            [rebalance_date.date()]).fetchall())
    decisions = decide(ranking, port.positions, rebalance_date, rules, exclusion_reasons=excl, holding_days=held_days)
    prev_rank, prev_sig = previous_ranks(con, portfolio_id, rebalance_date)

    # holding review (production only, portfolio-aware state; informational)
    if client is not None and holdings and jev_feats is not None:
        try:
            ref = cache.cross_section(rebalance_date, *reference_universe())
            regime = regime_context(md.bench.get("QQQ"), ref.frame, rebalance_date)
            htasks = []
            closes = md.mats["close"].loc[rebalance_date]
            for sym, p in port.positions.items():
                if sym not in ref.frame.index:
                    continue
                pstate = {"holding_days": len(md.calendar[(md.calendar > p.entry_date) & (md.calendar <= rebalance_date)]),
                          "entry_return": (float(closes.get(sym)) / p.entry_price - 1) if closes.get(sym) == closes.get(sym) else None,
                          "rank": int(ranking.loc[sym, "rank"]) if sym in ranking.index else "unranked",
                          "previous_rank": prev_rank.get(sym, "n/a"), "previous_signal": prev_sig.get(sym, "n/a")}
                htasks.append(JevTask(sym, rebalance_date, build_state(ref.frame.loc[sym], ref.family_pct.loc[sym], regime,
                                                                       portfolio=pstate)))
            generate(con, htasks, "holding", client)
            hq = question_set("holding")
            for r in decisions_frame(con, feature_set_id(client.model, hq), [rebalance_date]).itertuples():
                holding_review[r.symbol] = r.answers
        except JevError as exc:
            jev_info["holding_review"] = f"failed: {exc}"

    # 13) explanations
    fam_w = bt.family_weights(effective_cfg, rebalance_date)
    contrib = feature_contributions(cs.frame, fam_w)
    names = dict(con.execute("SELECT symbol, name FROM securities").fetchall())
    closes = md.mats["raw_close"].loc[rebalance_date] if rebalance_date in md.mats["raw_close"].index else pd.Series(dtype=float)
    signal_rows, expl = [], {}
    for dcs in decisions:
        sym = dcs.symbol
        rr = ranking.loc[sym] if sym in ranking.index else None
        pos = port.positions.get(sym)
        e = explain(sym, names.get(sym), dcs.signal, dcs.reasons, rr, prev_rank.get(sym), contrib,
                    cs.frame.loc[sym] if sym in cs.frame.index else None, jev_by_symbol.get(sym),
                    {"entry_date": pos.entry_date, "entry_price": pos.entry_price} if pos else None,
                    float(closes.get(sym)) if closes.get(sym) == closes.get(sym) else None, rules, rebalance_date)
        if sym in holding_review:
            e["jev_holding_review"] = holding_review[sym]
        expl[sym] = e
        signal_rows.append((run_key, portfolio_id, rebalance_date.date(), sym, dcs.signal, json.dumps(dcs.reasons),
                            json.dumps(e, default=str), dcs.rank, prev_rank.get(sym),
                            float(rr["final_score"]) if rr is not None else None, model_version, utcnow()))

    # 14) paper-portfolio accounting at the rebalance close (reference price) with explicit costs
    bt_cfg = load_config("backtest")
    broker = SimulatedBroker(CostModel.from_config(bt_cfg["costs"]))
    fills = []
    px = {sym: float(closes.get(sym)) for sym in closes.index if closes.get(sym) == closes.get(sym)}
    for dcs in decisions:
        if dcs.signal == SELL and dcs.symbol in port.positions and dcs.symbol in px:
            f = broker.execute(Order(dcs.symbol, "SELL", port.positions[dcs.symbol].shares, dcs.reasons[0]),
                               px[dcs.symbol], rebalance_date)
            if f:
                port.apply(f)
                fills.append(f)
    keep = [d.symbol for d in decisions if d.signal in (HOLD, BUY)]
    tw = target_weights(keep, cfg.weighting, ranking["final_score"], ranking["vol_60d"],
                        float(bt_cfg["portfolio"]["max_position_weight"]))
    equity = port.cash + sum(p.shares * px.get(sym, p.entry_price) for sym, p in port.positions.items())
    costs = broker.costs
    buys = [(sym, equity * float(tw[sym])) for sym in keep if sym not in port.positions and sym in px]
    need = sum(v for _, v in buys)
    budget = port.cash - costs.commission_per_trade_usd * len(buys)
    scale = min(1.0, budget / (need * (1 + costs.slippage_bps / 1e4) * (1 + costs.transaction_cost_bps / 1e4))) if need else 0
    for sym, val in buys:
        if val * scale < 1:
            continue
        f = broker.execute(Order(sym, "BUY", val * scale / px[sym], "entry"), px[sym], rebalance_date)
        if f and f.gross + f.total_cost <= port.cash + 1e-9:
            port.apply(f)
            fills.append(f)

    counts = {k: sum(1 for d in decisions if d.signal == k) for k in (BUY, HOLD, WAIT, SELL)}
    summary = {"run_key": run_key, "rebalance_date": str(rebalance_date.date()), "model_version": model_version,
               "model_config": cfg.to_dict(), "signals": counts, "universe_size": int(len(cs.frame)),
               "jev": jev_info, "transactions": len(fills),
               "equity_after": port.cash + sum(p.shares * px.get(sym, p.entry_price) for sym, p in port.positions.items()),
               "cash_after": port.cash, "costs": bt_cfg["costs"],
               "note": None if inc else "No incumbent model yet (run bootstrap): using the default, unvalidated configuration."}

    # persist everything atomically
    con.execute("BEGIN TRANSACTION")
    try:
        rank_rows = ranking.head(max(150, cfg.portfolio_size * 4)).reset_index().rename(columns={"index": "symbol"})
        for r in rank_rows.itertuples():
            con.execute("INSERT INTO monthly_rankings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
                run_key, rebalance_date.date(), model_version, r.symbol, int(r.rank), prev_rank.get(r.symbol),
                _f(r.quant_score), _f(r.jev_raw), _f(r.jev_confidence), _f(r.final_score),
                json.dumps({f: _f(getattr(r, f"z_{f}")) for f in FAMILIES}),
                json.dumps({f: _f(getattr(r, f"pct_{f}")) for f in FAMILIES}), bool(r.in_pool), utcnow()])
        con.executemany("INSERT INTO signal_history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", signal_rows)
        for i, f in enumerate(fills):
            con.execute("INSERT INTO portfolio_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
                f"{run_key}:{i}", portfolio_id, run_key, rebalance_date.date(), rebalance_date.date(), f.symbol, f.side,
                f.shares, f.price, f.gross, f.commission, f.slippage_cost, f.transaction_cost, f.reason,
                "simulated_fill_at_close", utcnow()])
        for sym, p in port.positions.items():
            con.execute("INSERT INTO portfolio_positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
                portfolio_id, rebalance_date.date(), sym, p.shares, p.entry_date.date(), p.entry_price, p.cost_basis,
                px.get(sym), p.shares * px.get(sym, p.entry_price), run_key])
        con.execute("INSERT INTO portfolio_cash VALUES (?, ?, ?, ?, ?)",
                    [portfolio_id, rebalance_date.date(), port.cash, summary["equity_after"], run_key])
        con.execute("UPDATE production_runs SET status = 'completed', finished_at = ?, model_version_id = ?, steps = ?, "
                    "summary = ? WHERE run_key = ?", [utcnow(), model_version, json.dumps(steps, default=str),
                                                      json.dumps(summary, default=str), run_key])
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.execute("UPDATE production_runs SET status = 'failed' WHERE run_key = ?", [run_key])
        raise

    # 15) report
    report_path = write_report(summary, expl)
    summary["report_path"] = str(report_path)
    ctx.step("report", f"{counts} -> {report_path}")
    return {"status": "completed", "run_key": run_key, "summary": summary}


def _f(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) or np.isinf(f) else f


def write_report(summary: dict, explanations: dict) -> Path:
    out_dir = PROJECT_ROOT / "data" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{summary['run_key'].replace(':', '_')}.md"
    lines = [f"# Monthly analysis {summary['rebalance_date']}", "",
             f"Model version: `{summary['model_version']}`  ", f"Universe size: {summary['universe_size']}  ",
             f"Signals: {summary['signals']}  ", f"Jev: {summary['jev'].get('status')}  ",
             f"Costs assumed: {summary['costs']}", ""]
    if summary.get("note"):
        lines += [f"> {summary['note']}", ""]
    for sig in (SELL, BUY, HOLD, WAIT):
        rows = [e for e in explanations.values() if e["signal"] == sig]
        if not rows:
            continue
        lines += [f"## {sig}", ""]
        for e in sorted(rows, key=lambda x: x.get("rank") or 10**6):
            lines.append(f"- {e['summary']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
