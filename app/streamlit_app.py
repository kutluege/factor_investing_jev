"""jev-factor-investor dashboard.  Launch:  uv run streamlit run app/streamlit_app.py

The RUN MONTHLY ANALYSIS button calls src.pipeline.monthly_run.run_monthly, the same function used by
`python -m src.pipeline.monthly`. Views read the database read-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import database_path, get_settings, load_config  # noqa: E402
from src.db.schema import connect  # noqa: E402
from src.features.technicals import ema, sma  # noqa: E402

st.set_page_config(page_title="jev-factor-investor", layout="wide")
SIGNAL_COLORS = {"BUY": "#1a7f37", "HOLD": "#0969da", "WAIT": "#9a6700", "SELL": "#cf222e"}


def ro() -> duckdb.DuckDBPyConnection | None:
    path = database_path()
    if not path.exists():
        return None
    try:
        return duckdb.connect(str(path), read_only=True)
    except duckdb.IOException:
        st.warning("Database is locked by another process (a CLI run may be in progress). Try again shortly.")
        return None


def q(sql: str, params: list | None = None) -> pd.DataFrame:
    con = ro()
    if con is None:
        return pd.DataFrame()
    try:
        return con.execute(sql, params or []).df()
    except duckdb.CatalogException:
        return pd.DataFrame()
    finally:
        con.close()


def pct(v, nd=1):
    return "—" if v is None or pd.isna(v) else f"{v * 100:.{nd}f}%"


# ------------------------------------------------------------------------------------------------ header ---
settings = get_settings()
st.title("jev-factor-investor")
st.caption("Medium-term (3–6 month) NASDAQ research & ranking — Technology · Biotechnology · Energy · Metals & Mining. "
           "Decision support only: no orders are sent to any broker.")

c1, c2, c3, c4 = st.columns(4)
creds = settings.credential_report()
c1.metric("FMP", creds["FMP_API_KEY"])
c2.metric("SEC User-Agent", creds["SEC_USER_AGENT"])
c3.metric("Jev (Vercel AI Gateway)", "available" if settings.jev_available else "unavailable")
last_run = q("SELECT run_key, rebalance_date, status, finished_at, summary FROM production_runs "
             "ORDER BY started_at DESC LIMIT 1")
c4.metric("Last monthly run", "—" if last_run.empty else f"{last_run.iloc[0]['rebalance_date']} ({last_run.iloc[0]['status']})")

left, right = st.columns([1, 2])
with left:
    run = st.button("RUN MONTHLY ANALYSIS", type="primary", width="stretch")
    update_data = st.checkbox("Refresh FMP/SEC data first", value=True)
with right:
    st.markdown("Runs: verify credentials → update market & SEC data → build the point-in-time universe → factors & "
                "technicals → incumbent model → quant ranking → Jev on the candidate set → final ranking → "
                "reconcile holdings → BUY/HOLD/WAIT/SELL → persist → paper-portfolio accounting → report. "
                "Idempotent per rebalance month: a second press returns the stored result.")

if run:
    from src.pipeline.common import Context
    from src.pipeline.monthly_run import run_monthly
    with st.status("Running monthly analysis…", expanded=True) as status:
        con = connect(database_path())
        ctx = Context(con=con, settings=settings, progress=lambda s, m: status.write(f"**{s}** — {m}"))
        try:
            result = run_monthly(ctx, update_data=update_data)
            status.update(label=f"Monthly analysis: {result['status']} ({result['run_key']})", state="complete")
            st.json(result.get("summary") or {}, expanded=False)
        except Exception as exc:  # surface the failure; nothing partial is committed
            status.update(label=f"Monthly analysis failed: {exc}", state="error")
            st.exception(exc)
        finally:
            con.close()

tabs = st.tabs(["Monthly Factor Ranking", "Current Portfolio", "New Opportunities", "Sells", "Security Detail",
                "Backtest", "Data & Jev"])
latest = q("SELECT run_key, rebalance_date FROM production_runs WHERE status='completed' ORDER BY rebalance_date DESC LIMIT 1")
run_key = None if latest.empty else latest.iloc[0]["run_key"]


def signals_frame(signals: list[str]) -> pd.DataFrame:
    if run_key is None:
        return pd.DataFrame()
    df = q("SELECT symbol, signal, rank, previous_rank, final_score, explanation FROM signal_history "
           "WHERE run_key = ? AND signal IN (SELECT unnest(?)) ORDER BY rank NULLS LAST", [run_key, signals])
    if df.empty:
        return df
    e = df["explanation"].map(json.loads)
    df["company"] = e.map(lambda x: x.get("company"))
    df["reasons"] = e.map(lambda x: "; ".join(x.get("reasons", [])))
    df["summary"] = e.map(lambda x: x.get("summary"))
    df["jev_score"] = e.map(lambda x: x.get("jev_score"))
    df["entry_date"] = e.map(lambda x: x.get("entry_date"))
    df["entry_price"] = e.map(lambda x: x.get("entry_price"))
    df["current_price"] = e.map(lambda x: x.get("current_price"))
    df["unrealized_return"] = e.map(lambda x: x.get("unrealized_return"))
    df["change_conditions"] = e.map(lambda x: " | ".join(x.get("change_conditions", [])))
    return df.drop(columns=["explanation"])


# ---------------------------------------------------------------------------------- monthly factor ranking ---
with tabs[0]:
    if run_key is None:
        st.info("No completed monthly run yet. Press RUN MONTHLY ANALYSIS.")
    else:
        st.subheader(f"Factor ranking for {latest.iloc[0]['rebalance_date']}")
        st.caption("Ranked by the incumbent factor model (literature themes; no technical analysis). Use this list as "
                   "the monthly shortlist for your own technical analysis. Percentiles: 100 = best in the universe.")
        rk = q("""SELECT r.rank, r.symbol, s.name AS company, s.sector_group, s.industry, r.final_score, r.quant_score,
                         r.jev_score, r.previous_rank, r.family_percentiles, sh.signal
                  FROM monthly_rankings r LEFT JOIN securities s USING (symbol)
                  LEFT JOIN signal_history sh ON sh.run_key = r.run_key AND sh.symbol = r.symbol
                  WHERE r.run_key = ? ORDER BY r.rank""", [run_key])
        if not rk.empty:
            fam = pd.json_normalize(rk["family_percentiles"].map(json.loads)).mul(100).round(0)
            fam.columns = [f"{c} pct" for c in fam.columns]
            view = pd.concat([rk.drop(columns=["family_percentiles"]), fam], axis=1)
            view["rank change"] = view["previous_rank"] - view["rank"]
            top_n = st.slider("Show top", 10, min(150, len(view)), min(50, len(view)), step=10)
            groups = st.multiselect("Sector groups", sorted(view["sector_group"].dropna().unique()),
                                    default=sorted(view["sector_group"].dropna().unique()))
            v = view[view["sector_group"].isin(groups)].head(top_n)
            st.dataframe(v, hide_index=True, width="stretch",
                         column_config={"final_score": st.column_config.NumberColumn(format="%.2f"),
                                        "quant_score": st.column_config.NumberColumn(format="%.2f"),
                                        "jev_score": st.column_config.NumberColumn(format="%.2f",
                                                                                   help="shadow mode unless validated")})
            st.download_button("Download ranking (CSV)", v.to_csv(index=False).encode("utf-8"),
                               file_name=f"factor_ranking_{latest.iloc[0]['rebalance_date']}.csv", mime="text/csv")
            summ = json.loads(last_run.iloc[0]["summary"]) if not last_run.empty and last_run.iloc[0]["summary"] else {}
            gate = (summ.get("jev") or {}).get("production_gate")
            if gate:
                st.caption(f"Jev production gate: {'ACTIVE' if gate.get('allowed') else 'shadow mode'} — {gate.get('reason')}")

# -------------------------------------------------------------------------------------- current portfolio ---
with tabs[1]:
    if run_key is None:
        st.info("No completed monthly run yet. Run the bootstrap (`python -m src.pipeline.bootstrap`) and then press "
                "RUN MONTHLY ANALYSIS.")
    else:
        st.subheader(f"Portfolio after {latest.iloc[0]['rebalance_date']}")
        pos = q("SELECT p.symbol, p.shares, p.entry_date, p.entry_price, p.last_price, p.market_value, p.cost_basis "
                "FROM portfolio_positions p WHERE portfolio_id='production' AND run_key = ?", [run_key])
        cash = q("SELECT cash, equity FROM portfolio_cash WHERE portfolio_id='production' AND run_key = ?", [run_key])
        sig = signals_frame(["BUY", "HOLD"])
        if not pos.empty:
            pos = pos.merge(sig[["symbol", "signal", "rank", "previous_rank", "final_score"]], on="symbol", how="left")
            pos["unrealized_pnl"] = pos["market_value"] - pos["cost_basis"]
            pos["unrealized_return"] = pos["last_price"] / pos["entry_price"] - 1
            st.dataframe(pos[["symbol", "signal", "shares", "entry_date", "entry_price", "last_price", "unrealized_pnl",
                              "unrealized_return", "final_score", "rank", "previous_rank"]], hide_index=True,
                         width="stretch",
                         column_config={"unrealized_return": st.column_config.NumberColumn(format="percent"),
                                        "shares": st.column_config.NumberColumn(format="%.4f")})
        if not cash.empty:
            a, b = st.columns(2)
            a.metric("Equity (paper)", f"${cash.iloc[0]['equity']:,.2f}")
            b.metric("Cash", f"${cash.iloc[0]['cash']:,.2f}")
        hist = q("SELECT as_of_date, equity FROM portfolio_cash WHERE portfolio_id='production' ORDER BY as_of_date")
        if len(hist) > 1:
            st.line_chart(hist.set_index("as_of_date"))

# ------------------------------------------------------------------------------------------ opportunities ---
with tabs[2]:
    df = signals_frame(["BUY", "WAIT"])
    if df.empty:
        st.info("No BUY/WAIT signals stored yet.")
    else:
        st.dataframe(df[["symbol", "company", "signal", "rank", "previous_rank", "final_score", "jev_score", "reasons",
                         "change_conditions"]], hide_index=True, width="stretch")

# ------------------------------------------------------------------------------------------------- sells ---
with tabs[3]:
    df = signals_frame(["SELL"])
    if df.empty:
        st.info("No SELL signals in the latest run.")
    else:
        st.dataframe(df[["symbol", "company", "rank", "previous_rank", "entry_date", "entry_price", "current_price",
                         "unrealized_return", "reasons", "summary"]], hide_index=True, width="stretch",
                     column_config={"unrealized_return": st.column_config.NumberColumn(format="percent")})

# ---------------------------------------------------------------------------------------- security detail ---
with tabs[4]:
    syms = q("SELECT DISTINCT symbol FROM signal_history UNION SELECT DISTINCT symbol FROM monthly_rankings "
             "ORDER BY 1")
    if syms.empty:
        syms = q("SELECT symbol FROM securities ORDER BY 1")
    if syms.empty:
        st.info("No securities stored yet.")
    else:
        sym = st.selectbox("Security", syms["symbol"].tolist())
        info = q("SELECT name, sector_group, industry, sic_description, is_active, ipo_date, delisted_date "
                 "FROM securities WHERE symbol = ?", [sym])
        if not info.empty:
            st.caption(" · ".join(str(v) for v in info.iloc[0].values if v is not None and not pd.isna(v)))
        colA, colB = st.columns([2, 1])
        px = q("SELECT date, open, high, low, close, adj_close FROM daily_prices WHERE symbol = ? ORDER BY date", [sym])
        with colA:
            if not px.empty:
                px["date"] = pd.to_datetime(px["date"])
                c = px.set_index("date")[["adj_close"]].rename(columns={"adj_close": sym})
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=c.index, y=c[sym], name="adjusted close", line=dict(width=1.5)))
                for n, fn in (("SMA50", lambda s: sma(s, 50)), ("SMA200", lambda s: sma(s, 200)),
                              ("EMA20", lambda s: ema(s, 20))):
                    fig.add_trace(go.Scatter(x=c.index, y=fn(c)[sym], name=n, line=dict(width=1)))
                fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10), title=f"{sym} price & moving averages")
                st.plotly_chart(fig, width="stretch")
        with colB:
            sh = q("SELECT rebalance_date, signal, rank, previous_rank, final_score FROM signal_history "
                   "WHERE symbol = ? ORDER BY rebalance_date DESC", [sym])
            st.markdown("**BUY/HOLD/WAIT/SELL history**")
            st.dataframe(sh, hide_index=True, width="stretch")
        rk = q("SELECT rebalance_date, rank, quant_score, jev_score, final_score, family_percentiles FROM monthly_rankings "
               "WHERE symbol = ? ORDER BY rebalance_date", [sym])
        if not rk.empty:
            last = json.loads(rk.iloc[-1]["family_percentiles"])
            st.markdown("**Factor breakdown (latest percentiles, higher is better)**")
            fb = pd.DataFrame({"family": list(last), "percentile": [v if v is not None else float("nan") for v in last.values()]})
            st.plotly_chart(go.Figure(go.Bar(x=fb["percentile"], y=fb["family"], orientation="h")).update_layout(
                height=280, margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(range=[0, 1])), width="stretch")
            a, b = st.columns(2)
            a.markdown("**Score history**")
            a.line_chart(rk.set_index("rebalance_date")[["quant_score", "final_score"]])
            b.markdown("**Rank history**")
            b.line_chart(rk.set_index("rebalance_date")[["rank"]])
        tech = q("SELECT indicator, value, rebalance_date FROM technical_values WHERE symbol = ? AND rebalance_date = "
                 "(SELECT max(rebalance_date) FROM technical_values WHERE symbol = ?)", [sym, sym])
        if not tech.empty:
            st.markdown(f"**Technical state ({tech.iloc[0]['rebalance_date']})**")
            st.dataframe(tech.pivot_table(index="indicator", values="value").T, width="stretch")
        jev = q("SELECT i.rebalance_date, i.purpose, d.answers_payload, d.confidence_payload, d.model_requested, "
                "d.resolved_model_version, d.state_payload, d.created_at FROM jev_decisions d JOIN jev_state_index i "
                "ON d.cache_key = i.cache_key WHERE i.symbol = ? AND d.status='ok' ORDER BY i.rebalance_date DESC "
                "LIMIT 6", [sym])
        if not jev.empty:
            st.markdown("**Jev outputs** (probabilities; Jev never computes the numbers in its input state)")
            for r in jev.itertuples():
                with st.expander(f"{r.rebalance_date} · {r.purpose} · {r.model_requested} · resolved: {r.resolved_model_version}"):
                    st.json(json.loads(r.answers_payload))
                    st.code(r.state_payload)
        expl = q("SELECT explanation FROM signal_history WHERE symbol = ? ORDER BY rebalance_date DESC LIMIT 1", [sym])
        if not expl.empty:
            e = json.loads(expl.iloc[0]["explanation"])
            st.markdown("**Explanation (deterministic)**")
            st.write(e.get("summary"))
            a, b = st.columns(2)
            a.markdown("Strongest positive drivers")
            a.dataframe(pd.DataFrame(e.get("strongest_positive_drivers", [])), hide_index=True)
            b.markdown("Strongest negative drivers")
            b.dataframe(pd.DataFrame(e.get("strongest_negative_drivers", [])), hide_index=True)
            st.markdown("Conditions that would change the state: " + "; ".join(e.get("change_conditions", [])))

# ----------------------------------------------------------------------------------------------- backtest ---
with tabs[5]:
    runs = q("SELECT run_id, created_at, kind, git_commit FROM backtest_runs WHERE status='completed' ORDER BY created_at DESC")
    if runs.empty:
        st.info("No backtest runs yet. Run `python -m src.pipeline.bootstrap`.")
    else:
        rid = st.selectbox("Backtest run", runs["run_id"].tolist())
        row = q("SELECT metrics, diagnostics, folds, config, data_snapshot, jev_feature_set_id FROM backtest_runs "
                "WHERE run_id = ?", [rid]).iloc[0]
        m, diag = json.loads(row["metrics"]), json.loads(row["diagnostics"])
        eq = q("SELECT series, date, equity FROM backtest_equity WHERE run_id = ? ORDER BY date", [rid])
        if not eq.empty:
            wide = eq.pivot(index="date", columns="series", values="equity")
            fig = go.Figure([go.Scatter(x=wide.index, y=wide[c], name=c) for c in wide.columns])
            fig.update_layout(height=420, title="Equity curves (walk-forward series are out-of-sample)",
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, width="stretch")
            dd = wide / wide.cummax() - 1
            st.plotly_chart(go.Figure([go.Scatter(x=dd.index, y=dd[c], name=c) for c in dd.columns]).update_layout(
                height=280, title="Drawdown", margin=dict(l=10, r=10, t=40, b=10)), width="stretch")
        best = m["best_full_period"]
        k = st.columns(6)
        for col, (label, key) in zip(k, [("CAGR", "cagr"), ("Max DD", "max_drawdown"), ("Sharpe", "sharpe"),
                                         ("Sortino", "sortino"), ("Calmar", "calmar"), ("Turnover", "turnover_annual")], strict=True):
            v = best.get(key)
            col.metric(label, pct(v) if key in ("cagr", "max_drawdown") else ("—" if v is None else f"{v:.2f}"))
        st.caption(f"Best configuration (selected on all folds — see walk-forward rows for honest OOS): "
                   f"`{json.dumps(m['best_config'])}`  · costs: {m['costs']}")
        st.markdown("**Out-of-sample walk-forward (selection inside each training window)**")
        nested = pd.DataFrame({k2: {"cagr": (v.get("fold_summary") or {}).get("median_cagr"),
                                    "median_sharpe": (v.get("fold_summary") or {}).get("median_sharpe"),
                                    "worst_fold_dd": (v.get("fold_summary") or {}).get("worst_fold_max_drawdown"),
                                    "picks": len(v.get("picks", []))} for k2, v in m["nested_walk_forward"].items()}).T
        st.dataframe(nested, width="stretch")
        st.markdown("**Full metrics & benchmarks (best configuration)**")
        st.json({k2: v for k2, v in best.items()}, expanded=False)
        folds = pd.DataFrame(json.loads(row["folds"]))
        st.markdown("**Fold definitions**")
        st.dataframe(folds, hide_index=True, width="stretch")
        fr = q("SELECT model_id, fold_id, test_start, test_end, metrics FROM backtest_fold_results WHERE run_id = ? "
               "AND model_id = ?", [rid, m["best_model_id"]])
        if not fr.empty:
            fm = pd.json_normalize(fr["metrics"].map(json.loads))
            st.markdown("**Walk-forward fold results (best configuration)**")
            st.dataframe(pd.concat([fr[["fold_id", "test_start", "test_end"]], fm[["total_return", "cagr", "max_drawdown",
                                                                                    "sharpe", "turnover_annual"]]], axis=1),
                         hide_index=True, width="stretch")
        res = q("SELECT model_id, stage, objective, summary FROM backtest_model_results WHERE run_id = ?", [rid])
        if not res.empty:
            sm = pd.json_normalize(res["summary"].map(json.loads))
            sm["model_id"], sm["stage"], sm["objective"] = res["model_id"], res["stage"], res["objective"]
            st.markdown("**Pareto view: median OOS CAGR vs worst-fold drawdown (size = turnover)**")
            fig = go.Figure(go.Scatter(x=sm["worst_fold_max_drawdown"], y=sm["median_cagr"], mode="markers",
                                       marker=dict(size=6 + 4 * sm["turnover"].fillna(0).clip(0, 6),
                                                   color=sm["pareto"].map({True: "#1a7f37", False: "#8c959f"})),
                                       text=sm["preset"] + " · N=" + sm["portfolio_size"].astype(str) + " · jev=" +
                                       sm["jev_weight"].astype(str)))
            fig.update_layout(height=380, xaxis_title="worst-fold max drawdown", yaxis_title="median fold CAGR",
                              margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, width="stretch")
            st.dataframe(sm.sort_values("objective", ascending=False).head(30)[
                ["model_id", "stage", "objective", "preset", "portfolio_size", "min_market_cap", "min_adv20", "weighting",
                 "hold_buffer", "jev_weight", "median_cagr", "median_sharpe", "worst_fold_max_drawdown", "turnover",
                 "pareto"]], hide_index=True, width="stretch")
        a, b = st.columns(2)
        a.markdown("**Factor stability (top configurations)**")
        a.json(m.get("stability", {}), expanded=True)
        b.markdown("**Quant only vs Quant + Jev**")
        b.json(m.get("ablation", {}), expanded=True)
        if m.get("sensitivity"):
            st.markdown("**Parameter sensitivity (one-at-a-time around the best configuration)**")
            st.dataframe(pd.DataFrame(m["sensitivity"]), hide_index=True, width="stretch")
        st.markdown("**Factor research (cross-sectional IC / rank IC)**")
        st.json(m.get("factor_research", {}), expanded=False)
        st.markdown("**Incumbent vs challenger**")
        st.dataframe(q("SELECT as_of_date, incumbent_version_id, challenger_version_id, promoted, evidence "
                       "FROM promotion_decisions ORDER BY created_at DESC"), hide_index=True, width="stretch")
        st.dataframe(q("SELECT version_id, model_id, role, as_of_date, objective, created_at FROM model_versions "
                       "ORDER BY created_at DESC"), hide_index=True, width="stretch")
        st.markdown("**Research diagnostics**")
        for f in diag.get("flags", []):
            (st.error if f["severity"] == "critical" else st.warning if f["severity"] == "warning" else st.info)(
                f"{f['code']}: {f['message']}")
        st.json({"lookahead_audit": diag.get("lookahead_audit"), "survivorship": diag.get("survivorship")}, expanded=False)
        st.caption(f"Jev feature set: {row['jev_feature_set_id'] or 'not used'} · data snapshot: {row['data_snapshot']}")

# ----------------------------------------------------------------------------------------------- data/jev ---
with tabs[6]:
    st.markdown("**Data coverage**")
    st.dataframe(q("SELECT 'securities' AS item, count(*) AS n FROM securities UNION ALL "
                   "SELECT 'delisted securities', count(*) FROM securities WHERE NOT is_active UNION ALL "
                   "SELECT 'symbols with prices', count(DISTINCT symbol) FROM daily_prices UNION ALL "
                   "SELECT 'companies with SEC facts', count(DISTINCT cik) FROM financial_facts UNION ALL "
                   "SELECT 'rebalance dates', count(DISTINCT rebalance_date) FROM rebalance_universe"),
                 hide_index=True)
    st.markdown("**External API usage (live calls vs cache hits)**")
    st.dataframe(q("SELECT provider, CAST(ts AS DATE) AS day, count(*) FILTER (WHERE NOT from_cache) AS live_calls, "
                   "count(*) FILTER (WHERE from_cache) AS cache_hits, count(*) FILTER (WHERE error IS NOT NULL) AS errors "
                   "FROM api_requests GROUP BY 1, 2 ORDER BY 2 DESC, 1 LIMIT 30"), hide_index=True)
    st.markdown("**Jev observability**")
    con = ro()
    if con is not None:
        from src.jev.store import observability
        try:
            st.json(observability(con))
        finally:
            con.close()
    st.dataframe(q("SELECT jev_feature_set_id, model_requested, resolved_model, state_schema_version, "
                   "question_schema_version, window_start, window_end, created_at FROM jev_feature_sets"), hide_index=True)
    st.markdown("**Configured costs** (explicit; never silently zero)")
    st.json(load_config("backtest")["costs"])
