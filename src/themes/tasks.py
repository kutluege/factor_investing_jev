"""Task drivers for T2 (10-K Item 1), T3 (membership) and T3r (automated review). Called from src.pipeline.themes."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from src.config import PROJECT_ROOT
from src.db.schema import upsert_df
from src.pipeline.common import Context
from src.themes.config import ThemesConfig
from src.themes.edgar_text import fetch_item1, list_annual_filings, load_item1
from src.themes.membership import DDL, evidence_sentences, members_on, membership_rows
from src.themes.review import auto_label, stratified_sample


def sessions(con) -> pd.DatetimeIndex:
    d = con.execute("SELECT date FROM daily_prices WHERE symbol = 'QQQ' ORDER BY date").df()
    return pd.DatetimeIndex(pd.to_datetime(d["date"]))


def run_t2(ctx: Context, sec, workers: int = 6, since: str = "2009-01-01", limit: int | None = None,
           retry_not_found: bool = False) -> dict:
    ciks = [r[0] for r in ctx.con.execute("SELECT DISTINCT cik FROM theme_candidates WHERE needs_10k "
                                          "AND cik IS NOT NULL ORDER BY cik").fetchall()]
    if limit:
        ciks = ciks[:limit]
    filings, list_failed = [], 0
    for i, cik in enumerate(ciks):
        try:
            filings += list_annual_filings(sec, cik, since=since)
        except Exception:  # noqa: BLE001 - listing failures are counted, not fatal
            list_failed += 1
        if (i + 1) % 200 == 0:
            ctx.step("t2", f"listed filings for {i + 1}/{len(ciks)} companies ({len(filings)} 10-Ks)")
    stats = {"companies": len(ciks), "listing_failed": list_failed, "filings": len(filings), "ok": 0,
             "item1_not_found": 0, "fetch_failed": 0}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(fetch_item1, sec, f, retry_not_found=retry_not_found) for f in filings]
        for i, fut in enumerate(as_completed(futs), 1):
            st = fut.result()["status"]
            key = "ok" if st == "ok" else "item1_not_found" if st == "item1_not_found" else "fetch_failed"
            stats[key] += 1
            if i % 500 == 0:
                ctx.step("t2", f"{i}/{len(filings)} filings: {stats}")
    return stats


def run_t3(ctx: Context, sec, cfg: ThemesConfig) -> dict:
    sess = sessions(ctx.con)
    cands = ctx.con.execute("SELECT symbol, cik, name, fmp_industry, sic, stage_a FROM theme_candidates "
                            "WHERE cik IS NOT NULL").df()
    ctx.con.execute(DDL)
    rows, missing_text, text_cache = [], 0, {}
    for i, c in enumerate(cands.itertuples()):
        try:
            fl = list_annual_filings(sec, c.cik)
        except Exception:  # noqa: BLE001
            continue
        needs = any(m["needs_10k"] for m in json.loads(c.stage_a))
        recs = []
        for f in fl:
            rec = load_item1(f) if needs else None
            if needs and rec is None:
                missing_text += 1
            rec = rec or {"status": "not_fetched", "item1": "", "item1_words": 0}
            recs.append({"accession": f.accession, "acceptance": f.acceptance, "status": rec.get("status"),
                         "item1": rec.get("item1", ""), "item1_words": rec.get("item1_words", 0)})
        new = membership_rows(c.symbol, c.cik, json.loads(c.stage_a), recs, cfg, sess)
        for r in new:
            if r["method"] == "keywords":
                text_cache[(c.symbol, r["filing_accession"])] = next(x["item1"] for x in recs
                                                                     if x["accession"] == r["filing_accession"])
        rows += new
        if (i + 1) % 500 == 0:
            ctx.step("t3", f"{i + 1}/{len(cands)} companies, {len(rows)} membership rows")
    df = pd.DataFrame(rows)
    ctx.con.execute("DELETE FROM theme_membership")
    upsert_df(ctx.con, "theme_membership", df, ["symbol", "filing_accession"])
    out_dir = PROJECT_ROOT / "research" / "themes"
    me = pd.date_range("2011-06-30", sess[-1], freq="ME")
    counts = pd.DataFrame([{"date": d.date(), **{f"{t}/{s}": n for (t, s), n in
                                                  members_on(df, d).groupby(["theme", "subtheme"]).size().items()}}
                           for d in me]).fillna(0)
    counts.to_csv(out_dir / "theme_date_counts.csv", index=False)
    cur = members_on(df, sess[-1])
    info = cands.set_index("symbol")
    review = []
    for r in cur.itertuples():
        kws = cfg.themes[r.theme].subthemes[r.subtheme].keywords
        text = text_cache.get((r.symbol, r.filing_accession), "")
        review.append({"symbol": r.symbol, "name": info.loc[r.symbol, "name"], "theme": r.theme,
                       "subtheme": r.subtheme, "method": r.method, "hits": r.hits, "density": round(r.density, 2),
                       "matched_keywords": r.matched, "fmp_industry": info.loc[r.symbol, "fmp_industry"],
                       "sic": info.loc[r.symbol, "sic"], "evidence": " | ".join(evidence_sentences(text, kws)),
                       "filing": r.filing_accession, "label": ""})
    rv = pd.DataFrame(review).sort_values(["theme", "subtheme", "symbol"])
    rv.to_csv(PROJECT_ROOT / cfg.classification.review_file, index=False)
    by_date_theme = counts.set_index("date")
    small = {c: int((by_date_theme[c] < cfg.research.min_names_per_date).sum()) for c in by_date_theme.columns}
    return {"membership_rows": len(df), "companies": int(df["symbol"].nunique()) if len(df) else 0,
            "current_members": len(cur),
            "current_by_subtheme": {f"{t}/{s}": int(n) for (t, s), n in cur.groupby(["theme", "subtheme"]).size().items()},
            "filings_without_cached_text": missing_text, "months_below_min_names": small}


def run_t3r(ctx: Context, fmp, cfg: ThemesConfig, n: int = 120) -> dict:
    from src.data.reference import profiles_parallel
    rv = pd.read_csv(PROJECT_ROOT / cfg.classification.review_file)
    sample = stratified_sample(rv, n)
    prof = profiles_parallel(fmp, sample["symbol"].tolist(), ttl_hours=fmp.cfg["ttl_hours"]["reference"])
    labels = [auto_label(r.subtheme, (prof.get(r.symbol) or {}).get("description"),
                         (prof.get(r.symbol) or {}).get("industry")) for r in sample.itertuples()]
    sample = sample.assign(label=[x[0] for x in labels], label_evidence=[x[1] for x in labels])
    sample.to_csv(PROJECT_ROOT / "research" / "themes" / "membership_review_labeled.csv", index=False)
    judged = sample[sample["label"] != "unknown"]
    acc = float((judged["label"] == "correct").mean()) if len(judged) else float("nan")
    by = judged.groupby("subtheme")["label"].apply(lambda s: round(float((s == "correct").mean()), 3)).to_dict()
    wrong = judged[judged["label"] == "wrong"][["symbol", "name", "subtheme", "fmp_industry", "matched_keywords"]]
    return {"sampled": len(sample), "judged": len(judged), "accuracy": round(acc, 4), "by_subtheme": by,
            "passes_85pct": bool(acc >= 0.85), "wrong_examples": wrong.head(25).to_dict("records")}
