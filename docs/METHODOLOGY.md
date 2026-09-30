# jev-factor-investor — Methodology Summary

A complete description of the stock-selection method built and tested in this project: data, universe,
characteristics (factors), preprocessing and scoring, portfolio construction, costs, the Jev LLM layer, the
validation protocol, what was tested and the results obtained. Written to support an in-depth comparison against
state-of-the-art (SOTA) practice. Companion documents: `docs/RESEARCH.md` (literature basis), `docs/RESULTS.md`
(stored research run), `docs/EXPLORATION.md` (maximum-return track), `docs/FACTOR_IC.md` (characteristic research).

Status (2026-09-30): quant and Jev results complete. Jev results are in §7.1; the second research run (250
configurations, run `bt_20260930_151358_aceb0b`) is summarized in §9.4.

---

## 1. Objective and constraints

| Item | Specification |
|---|---|
| Market | US, NASDAQ-listed common equities |
| Sectors | Technology, Biotechnology/Pharma, Energy, Metals & Mining (sub-industries included) |
| Style | Long-only, no leverage, no shorting |
| Horizon | Medium term — intended holding 3–6 months |
| Review | Monthly (a review is **not** a forced liquidation; hysteresis keeps positions) |
| Capital | USD 10,000 paper portfolio, fractional shares |
| Output | Monthly factor ranking (shortlist for the user's own technical analysis) + BUY / HOLD / WAIT / SELL |
| Technical analysis | Deliberately **excluded** from scoring and exit rules (user applies TA); indicators computed and displayed only |
| Execution | Decision support only; `BrokerAdapter` protocol for a future broker integration |

---

## 2. Data sources and point-in-time (PIT) handling

### 2.1 Sources
| Source | Used for | Notes |
|---|---|---|
| **Financial Modeling Prep (FMP), Starter plan** | Daily OHLCV (split-adjusted `historical-price-eod/full` + `dividend-adjusted`), company screener (sector/industry), profiles (CIK, IPO date, exchange, ETF/fund/ADR flags), splits, `stock-list` / `actively-trading-list` | Verified live: US coverage, 300 calls/min, 20 GB / rolling 30 days; price history available back to **2006** (5,000 rows/request); `delisted-companies` capped at page 0 (402 on page ≥ 1) |
| **SEC EDGAR (data.sec.gov)** | XBRL company facts (every tag with its `filed` date), submissions (SIC), tickers-by-exchange | Free; descriptive User-Agent with contact email required; client limited to ≤ 8 req/s |
| **Vercel AI Gateway → TypeSafe `typesafe-ai/jev`** | Probabilistic structured judgements (boolean / score / choice) | See §7 |

All HTTP responses are stored in a gzip raw-response cache (immutable history cached forever), with retries,
exponential backoff, `Retry-After` handling, request counting and a per-minute rate limiter.

### 2.2 Dataset actually loaded
- Prices: **2,382 symbols**, 2006-10-02 → 2026-09-28 (~5.5M daily rows).
- Security master: **2,348 securities**, of which **797 delisted** (recovered; §3.3).
- SEC facts: **2,104 companies**, ~4.07M fact rows.
- PIT fundamental snapshots: **69,524** (one per company per filing-availability date, from 2009).
- Stock splits: 2,958 (FMP); SEC-share-count inference only as a fallback.
- Feature panel: **227 month-end rebalance dates**, 256k rows, 97.7k eligible rows.
- Research/backtest start: **2011-06-30** (broad XBRL coverage; small filers phase in during 2011).

### 2.3 Point-in-time rules (anti look-ahead)
- **Filing-availability dating:** a fact is usable from `filed + 1 day`, never from its fiscal period end.
  (A Dec-31 period filed Feb-10 is invisible to a Jan-31 rebalance — tested.)
- **Restatements:** for each (metric, period) the value used at date D comes from the most recent filing with
  availability ≤ D.
- **Periods identified by (start, end)**, not by `fy`/`fp` (these describe the filing, not the period).
- **Concept fallback lists** per metric (companies switch XBRL tags).
- **Derived quarters:** Q4 = FY − 9M YTD; YTD cash flows differenced; TTM = FY fact or sum of 4 discrete quarters.
- **Snapshots** built per filing-availability date; the as-of join raises on any snapshot available after the
  rebalance date.
- **Price features** use trailing windows only (tests inject large future moves and assert identical features).
- **Traded vs adjusted price:** the minimum-price filter uses the *traded* price (split-adjusted close × cumulative
  later split ratio). Using split-adjusted closes would have excluded future split winners in earlier years
  (look-ahead). Found and fixed during this project.
- **Market cap** = split-adjusted close × SEC-reported shares converted to adjusted units with post-dated splits.
- **Incremental price loads** chain dividend-adjusted closes from an overlap day; vendor re-basing after splits
  triggers a full reload.
- **Labels** (forward returns 21/63/126 sessions) are used only once matured (`label_end_date ≤ as_of`).
- **Audit:** every research run checks `availability_date ≤ rebalance_date` for all persisted features.

Known PIT limitation: sector/industry classification is a current snapshot, not point-in-time.

---

## 3. Universe

### 3.1 Per-rebalance eligibility (information available at the date only)
1. NASDAQ common equities; exclude ETFs, funds, ADRs.
2. Exclude warrants/units/rights/preferreds/SPAC-type instruments (name patterns) and NASDAQ 5th-letter suffixes
   (W, R, U, P, Z, Q, F, Y on 5-letter symbols).
3. Sector group from FMP sector/industry (SEC SIC fallback).
4. Listed at the date: IPO before, not delisted before, ≥ 252 sessions of history, traded in the last 5 sessions.
5. Traded price ≥ **$3**.
6. Market cap ≥ threshold (grid: $100M, $300M, $500M, $1B; exploration also $10B).
7. **ADV20 = mean(close × volume over 20 sessions)** ≥ threshold (grid: $1M, $5M, $10M, $20M).

Eligible universe at the default thresholds ($300M / $5M): ~137 names (2011) → ~595 (2026).

### 3.2 Benchmarks
QQQ, SPY, sector ETFs (XLK, XBI, XLE, XME), and the **equal-weight eligible universe** (monthly rebalanced, no
costs) — the honest hurdle for a factor model.

### 3.3 Survivorship-bias treatment
- FMP Starter caps the delisted list, but still serves prices and profiles of delisted symbols.
- Delisted companies were recovered as **FMP full symbol list − actively-trading list**; ~5,700 candidates were
  profiled (exchange, sector, CIK, IPO date), yielding **797 delisted NASDAQ common stocks** in the target sectors.
- A security is treated as delisted after its last trading day.
- About 25–30% of each mid-sample year's universe consists of companies later delisted.
- **Distress delisting haircut:** if the last traded price is < $2 or the stock fell > 60% over its final 126
  sessions, the last price is cut by 30% (Shumway 1997; Shumway & Warther 1999); other delistings (mergers) 0%.
  Applied in backtests and in research labels.
- Residual gaps: tickers later reused by another company; companies FMP no longer lists.

---

## 4. Characteristics (factor model v2)

Signals and theme weights were **fixed from the published literature before any backtest results were seen**
(literature review: Jensen–Kelly–Pedersen 2023, Hou–Xue–Zhang 2020, McLean–Pontiff 2016, Chen–Zimmermann 2022,
Chen–Velikov 2023, Novy-Marx–Velikov 2016, and others — see `docs/RESEARCH.md`).

| Theme | Characteristic | Definition | Sign | Ranking scope | Source |
|---|---|---|---|---|---|
| Momentum | `res_mom_12_2` | Sum of residuals t-12..t-2 from a 36-month regression on QQQ and sector-group returns, ÷ their std | + | universe | Blitz, Huij & Martens (2011); Blitz, Hanauer & Vidojevic (2020) |
| | `dist_52w_high` | Price / 252-session high − 1 | + | universe | George & Hwang (2004) |
| | `mom_12_1` | 12-1 month return | + | universe | Jegadeesh & Titman (1993) |
| | `mom_12_7` | 12-7 month return | + | universe | Novy-Marx (2012) |
| | `sector_mom_6m` | Sector-group median 6-month return (energy, mining only) | + | universe | Moskowitz & Grinblatt (1999) |
| Quality | `cop_at` | Operating cash flow (TTM) / total assets (cash-based profitability proxy) | + | sector | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| | `gross_profitability` | Gross profit (TTM) / total assets | + | sector | Novy-Marx (2013) |
| | `fscore` | Piotroski F-score (9 signals, scaled over computable signals, ≥ 6 required; not biotech) | + | sector | Piotroski (2000) |
| Investment | `asset_growth` | Total assets YoY growth | − | sector | Cooper, Gulen & Schill (2008) |
| | `share_issuance` | log(split-adjusted shares / shares one year earlier) | − | sector | Pontiff & Woodgate (2008) |
| | `cash_runway_years` | Cash / annual FCF burn (biotech only) | + | sector | dilution-risk proxy |
| Value | `ebit_ev`, `ocf_ev` | EBIT / EV, operating cash flow / EV (not biotech) | + | sector | Loughran & Wellman (2011) |
| | `book_to_market` | Book equity / market cap | + | sector | Fama & French (1992) |
| | `rd_intensity` | R&D (TTM) / market cap (tech, biotech) | + | sector | Chan, Lakonishok & Sougiannis (2001) |
| | `cash_to_mcap` | Cash + short-term investments / market cap (biotech) | + | sector | — |
| Fundamental momentum | `droe` | Quarterly ROE − ROE four quarters earlier (not biotech) | + | sector | Hou, Mo, Xue & Zhang (2021) |
| | `sue` | (NI_q − NI_{q−4}) / std of the last 8 seasonal changes | + | sector | Foster, Olsen & Shevlin (1984); Novy-Marx (2015) |
| Low risk | `max_ret_21d` | Largest daily return over 21 sessions | − | universe | Bali, Cakici & Whitelaw (2011) |
| | `idio_vol_60d` | Volatility of daily returns net of beta × QQQ (60 sessions) | − | universe | Ang, Hodrick, Xing & Zhang (2006) |
| Growth (zero weight in core presets) | `revenue_yoy`, `gross_profit_growth` | YoY growth off positive bases | + | sector | weak/negative in the literature |

Also computed but **not scored**: SMA/EMA, RSI, MACD, ADX, ATR, volatility, breakouts, seasonality (Heston–Sadka),
the Abdi–Ranaldo spread estimate (used for costs), and legacy v1 ratios (ROIC, ROE, margins, etc.).

Invalid ratios (non-positive denominators) are NaN, never forced; growth is only computed off positive bases.

---

## 5. Preprocessing and scoring

1. **Per-date cross-sectional normalization only** (nothing pooled across dates → no future leakage).
2. **Rank → normal scores**: Φ⁻¹((rank − 0.5)/n), robust to outliers.
3. **Scope:** accounting ratios ranked **within sector group** (group ≥ 8 names, else universe-wide); price signals
   ranked **across the universe** (Ehsani, Harvey & Li 2023: forced sector neutrality hurts long-only).
4. A characteristic is dropped at a date if coverage < 30%; sector applicability rules apply (e.g. no earnings
   ratios for biotech).
5. **Theme score** = mean of available characteristic scores, re-standardized; percentile ranks kept for display.
6. **Composite quant score** = weighted mean of theme scores; missing-theme weight is redistributed (a name needs
   ≥ 50% of total weight present) → robust z.

### 5.1 Theme-weight presets (small interpretable set; no free-form optimisation)
| Preset | Momentum | Quality | Investment | Value | Fund. mom. | Low risk |
|---|---|---|---|---|---|---|
| **literature** (production prior) | 30 | 25 | 20 | 15 | 5 | 5 |
| equal_themes | 1 | 1 | 1 | 1 | 1 | 1 |
| momentum_quality | 40 | 30 | 15 | 5 | 5 | 5 |
| quality_value | 10 | 30 | 20 | 30 | 5 | 5 |
| defensive | 15 | 35 | 25 | 10 | 0 | 15 |
| momentum_only | 1 | – | – | – | – | – |
| literature_factor_momentum | literature weights tilted ±30% toward themes with positive trailing-12-month top-quintile excess return (Ehsani & Linnainmaa 2022); matured 21-day labels only |
| literature_ic_shrunk | IC weights (36-month lookback, matured 126-day labels only) shrunk 50% toward literature weights |

---

## 6. Portfolio construction, signals and costs

### 6.1 Signals (entry/exit hysteresis)
- **BUY** — not owned; rank ≤ N among names passing entry gates (the most volatile 3% are blocked); a slot is free,
  or it ranks in the top N × 0.5 and replaces a holding outside the top N.
- **HOLD** — owned; rank ≤ N × hold_buffer; no exit condition.
- **WAIT** — not owned; rank ≤ 2N but entry criteria unmet (near cutoff, gate failure, portfolio full).
- **SELL** — rank > N × hold_buffer; fundamental deterioration (quality and fundamental-momentum percentiles both
  < 10%); no longer eligible (delisted, illiquid, < $3, below cap threshold); replaced by a stronger candidate.
  A technical-breakdown exit exists but is disabled (TA left to the user).
- Jev, when weighted, only changes the score; hard gates and exits are applied afterwards.

### 6.2 Sizing
- Weighting: equal / score / inverse-volatility / score × inverse-volatility.
- Position cap max(8%, 1.5/N); sector-group cap 45% (relaxed when infeasible).
- Drift band 25%; minimum rebalancing trade $150.
- Optional market-regime overlay: exposure → 50% or 0% when QQQ closes below its 200-day average (Faber 2007).
- One shared module (`src/portfolio/rebalance.py`) is used by both the backtest and the production monthly run.

### 6.3 Execution and costs
- Signals from the close of day D; **trades at the next session's open**.
- Commission $1/trade; slippage 10 bps + **half the Abdi–Ranaldo (2017) estimated bid-ask spread** (capped at
  200 bps); 5 bps fees; delisting haircuts as in §3.3.
- Cost sensitivity multipliers 0×–3×.

---

## 7. Jev (LLM probabilistic decision layer)

- **API:** `POST https://ai-gateway.vercel.sh/v1/evaluate`, model `typesafe-ai/jev`. Schema verified live:
  `boolean` → `probability`; `score` → `criteria` = ordered levels, answer `score` (expected level index),
  `probabilities`, `confidence`; `choice` → `criteria` = {label: description}.
- **One request per (stock, date) state** carrying all questions: momentum persistence (boolean), fundamental
  deterioration (boolean), value trap (boolean), relative outperformance vs sector (boolean), regime fit
  (5-level score). Holdings additionally get thesis-intact / exit-urgency (production only, not scored).
- **States:** compact, bucketed, **anonymized** (no ticker, company or date); all arithmetic done in Python — Jev
  never computes numbers.
- **Durable cache** keyed by hash(model + normalized state + state-schema version + question-schema version);
  results never overwritten; versioned feature-set IDs; bounded concurrency; retries with `Retry-After`;
  resumable checkpointing.
- **Candidate reduction:** union of top 50 + 10 boundary names per static preset on two universes (≈ **29,655**
  unique historical states, 2011–2026). States are built on a fixed reference universe so one evaluation serves
  every backtest configuration (Stage A generation separated from Stage B backtests).
- **Jev score:** weighted combination of question probabilities (negative weights on deterioration and value trap),
  robust-z within the candidate pool; `final = (1 − w)·z_quant + w·z_jev`, w ∈ {0, 5, …, 30%}.
- **Look-ahead caveat:** LLMs memorize and can reconstruct firms/dates even from anonymized inputs
  (Lopez-Lira, Tang & Zhu 2025; Glasserman & Lin 2023; Sarkar & Vafa 2024). Historical Jev backtests are therefore
  an **upper bound only**.
- **Production policy (shadow mode):** Jev scores are stored every month; Jev receives weight only after ≥ 12
  matured forward months show a rank IC beyond the quant score with t ≥ 2 (`config/jev.yaml → production_policy`,
  `src/jev/forward.py`).

---

### 7.1 Jev results (historical; upper bound because of possible LLM look-ahead)

Historical generation: 29,655 unique anonymized states (candidate pools at 183 month-ends, 2011-06 → 2026-08), 0
failures, median latency 0.32 s, 30.0M input tokens, total cost **$1.26**. Feature set `jfs_ab5d5f8fc4f9`.

**Signal test** (Spearman rank IC inside the Jev candidate pools, ~161 names/month; t-stats adjusted for overlapping
labels by √(h/21)):

| Horizon | Jev rank IC | Quant rank IC | Jev residual IC (beyond quant) | Corr(Jev, quant) | Top-quintile Jev excess |
|---|---|---|---|---|---|
| 21d | +0.015 (t≈1.4) | +0.020 (t≈2.0) | +0.006 (t≈0.6) | 0.39 | −1.4% |
| 63d | +0.031 (t≈2.0) | +0.036 (t≈2.1) | +0.017 (t≈1.2) | 0.39 | −2.8% |
| 126d | +0.045 (t≈2.2) | +0.059 (t≈2.4) | +0.026 (t≈1.4) | 0.39 | −2.2% |

**Portfolio test** (honest nested walk-forward, 2014-07 → 2026-09): incumbent/challenger with Jev weight selectable
7.4% CAGR, Sharpe 0.47, max DD −29.9% vs 8.6% / 0.55 / −23.9% quant-only; free selection with Jev 4.0% vs 17.3%
quant-only. The best-on-all-folds comparison (Jev weight 10%: median fold CAGR 13.3%, Sharpe 0.93 vs 11.5% / 0.75)
favours Jev, but that comparison is in-sample over 6× more Jev configurations and is exposed to LLM look-ahead.

**Conclusion:** Jev's judgements add no statistically reliable information beyond the factor score, and do not improve
honest out-of-sample portfolios. Production keeps Jev in shadow mode (weight 0); its scores are recorded monthly so a
clean forward track record accumulates (`src/jev/forward.py`, gate: ≥ 12 matured months, residual IC t ≥ 2).

## 8. Validation protocol

1. **Walk-forward folds:** expanding window, ≥ 36 training months, 12-month test blocks, 1-month embargo, 126-day
   label purge → **12 folds** (first test month 2014-07-31).
2. **Search space:** Stage 1 = 8 presets × Jev weights at defaults; Stage 2 = a **seeded random sample of 160**
   configurations from the full grid (market cap, ADV, N ∈ {5, 10, 15, 20, 25, 30}, weighting, hold buffer ∈
   {1, 1.5, 2, 3, 4}, Jev weight) drawn independently of results; plus one-at-a-time sensitivity (incl. cost
   multipliers). Every configuration persisted (196 in the main run; 208 including exploration).
3. **Objective** (robust-z across candidates): 35% median CAGR, 15% medium-horizon return, 15% Calmar, 10% Sharpe,
   15% median-drawdown quality, 10% worst-fold drawdown quality, minus a turnover penalty; Pareto view reported.
4. **Honest performance estimates:**
   - (a) **Fixed prior** — the pre-specified default, never changed.
   - (b) **Incumbent/challenger** — emulates production: switches only if a diversified challenger (N ≥ 15,
     cap ≥ $300M, multi-theme) beats the incumbent by ≥ 0.25 objective units, wins ≥ 60% of training blocks and
     does not worsen worst drawdown by > 5 pp.
   - (c) **Free per-fold selection** — shown for transparency.
5. **Overfitting controls:** probability of backtest overfitting via CSCV (Bailey, Borwein, López de Prado & Zhu
   2017); deflated Sharpe ratio (Bailey & López de Prado 2014).
6. **Descriptive factor research:** per-characteristic rank IC and top-quintile excess at 21/63/126 days, overall
   and by sub-period — not used for selection.
7. **Reproducibility:** each run stores git commit, data snapshot, full config, seed, fold definitions, metrics,
   diagnostics and equity curves; `tools reproduce <run_id>` re-simulates a stored run.
8. **Diagnostics:** look-ahead audit, survivorship statement, missing fundamentals, small universe/sample,
   single-stock or sector dominance, turnover, micro-cap exposure, cost realism.
9. **Tests:** 84 automated tests — indicators, PIT leakage injections, filing availability, universe membership,
   delisting, accounting, hysteresis, costs, Jev schema/cache/resume/failure, idempotent monthly runs, exact
   reproduction, dashboard rendering.

---

## 9. Results

### 9.1 Characteristic research (2011–2026, $300M / $5M universe; t-stats inflated by overlapping labels)
- **Strongest rank IC (126d):** idiosyncratic volatility (−) 0.13, share issuance (−) 0.11, 52-week-high proximity
  0.10, cash profitability 0.10; investment and quality themes; SUE 0.045.
- **Best top-quintile excess (126d, the long-only statistic):** 12-1 momentum +1.9%, low issuance +1.8%,
  ΔROE +1.4%, momentum theme +1.4%, cash profitability +1.2%.
- **Weak/none:** residual momentum (~0), sector momentum, book-to-market / value theme.
- **Negative:** revenue and gross-profit growth, cash/market cap, R&D intensity (mostly within biotech).

### 9.2 Out-of-sample performance (2014-07 → 2026-09, after costs)
| Strategy | CAGR | Sharpe | Max DD |
|---|---|---|---|
| **Fixed prior (production model)** | **10.5%** | **0.58** | **−30.4%** |
| Incumbent/challenger process | 6.0% | 0.40 | −37.3% |
| Free per-fold selection | −6.8% | −0.17 | −76.1% |
| Equal-weight universe | 13.6% | 0.62 | −47.2% |
| QQQ | 19.3% | 0.95 | −35.1% |
| SPY | 13.9% | 0.86 | −33.7% |

- Fixed prior vs equal-weight universe: beta 0.63, alpha ≈ +1.8%/yr, excess CAGR −3.1%.
- **PBO 56%**: in-sample winners did no better than chance out of sample.
- Free selection repeatedly picked noisy 5-stock portfolios, including pure momentum right before the 2021–22
  speculative-tech crash (−65% in that fold).

### 9.3 Maximum-return exploration (declared after the main results; exploratory)
| Variant | CAGR | Sharpe | Max DD |
|---|---|---|---|
| Large-cap ($10B+) momentum, 10 stocks | 15.1% | 0.67 | −35.4% |
| Large-cap momentum + quality, 15 stocks | 12.1% | 0.68 | −30.4% |
| Momentum, 10 stocks + regime filter | 12.3% | 0.51 | −56.9% |
| Momentum, 20 stocks | 12.2% | 0.51 | −63.7% |
| Equal themes, 20 stocks | 9.9% | 0.62 | −22.5% |
| Broad "anti-junk", 60 stocks | 10.5% | 0.59 | −31.0% |

The regime overlay hurt in every variant (whipsaws 2015–16, 2018, 2022). No honest configuration approached
50%/yr, and none beat QQQ out of sample.

---

### 9.4 Second research run (quant + Jev, 250 configurations)

| Strategy (out of sample 2014-07 → 2026-09) | CAGR | Vol | Sharpe | Max DD |
|---|---|---|---|---|
| Fixed prior (pre-specified) | 10.5% | 20.9% | 0.58 | −30.4% |
| Incumbent/challenger, quant only | 8.6% | 18.2% | 0.55 | −23.9% |
| Free per-fold selection, quant only | 17.3% | 30.2% | 0.68 | −53.7% |
| Incumbent/challenger, Jev selectable | 7.4% | 19.1% | 0.47 | −29.9% |
| Free per-fold selection, Jev selectable | 4.0% | 19.8% | 0.30 | −49.0% |
| EW universe / QQQ / SPY | 13.6% / 19.3% / 13.9% | — | — | −47.2% / −35.1% / −33.7% |

PBO (CSCV, 216 configurations): 62%. Free per-fold selection returned −6.8% in run 1 and +17.3% in run 2 — the only
difference being the seeded random candidate draw (the Jev-weight list changed the random stream) — i.e. its outcome
is noise. The incumbent/challenger process ended on `equal_themes`, 20 stocks, $300M+; it passed every promotion test
except the 3-month cooldown, so the pre-specified model remains the production incumbent until the next review.

## 10. Key conclusions
1. In this universe and period the factor model mainly **reduces risk** (beta ≈ 0.6–0.75; drawdown −30% vs −47%);
   it does not raise raw return above the equal-weight universe and does not beat mega-cap-driven QQQ.
2. **Backtest-driven parameter selection destroyed value**; a pre-specified, literature-based model is the most
   robust choice and is the production model (audited methodology correction recorded in `promotion_decisions`).
3. Concentration, pure momentum and trend overlays raised drawdowns without raising returns.
4. LLM signals cannot be validated on historical data; forward-only validation (shadow mode) is required.

---

## 11. Known limitations
- Sector classification not point-in-time.
- Residual survivorship gaps (reused tickers, companies FMP no longer lists).
- SUE timed on 10-Q/10-K filing dates, which lag earnings releases.
- Some revenue reported only in company-specific XBRL extensions not published by SEC (e.g. APA) → missing.
- ~15 years of PIT fundamentals → 12 folds: indicative, not statistically conclusive.
- Production paper portfolio fills at the rebalance close; distress-delisting haircut is a heuristic.
- No analyst estimates, short interest, options or intraday data.

---

## 12. Checklist for a SOTA comparison

| Area | This project | SOTA / literature reference to compare against |
|---|---|---|
| Signal set | ~20 published characteristics in 6 themes | Jensen–Kelly–Pedersen (153 factors / 13 themes); Chen–Zimmermann open-source library |
| Combination | Fixed theme weights; IC-shrunk and factor-momentum variants | ML composites (Gu–Kelly–Xiu 2020; Freyberger–Neuhierl–Weber 2020); shrinkage (Kozak–Nagel–Santosh 2020) |
| Cost-aware construction | Buffer rule, spread-based costs, drift band, min trade | Jensen–Kelly–Malamud–Pedersen, "Machine Learning and the Implementable Efficient Frontier" |
| Momentum crash control | 200-day regime overlay (hurt) | Daniel–Moskowitz (2016) dynamic scaling; Barroso–Santa-Clara (2015) volatility-managed momentum |
| Validation | Walk-forward with embargo/purge, CSCV PBO, deflated Sharpe | López de Prado purged k-fold / CPCV; Harvey–Liu–Zhu (t > 3) |
| Earnings signals | SUE from filing dates | Announcement-date SUE (8-K timing); analyst revisions (unavailable here) |
| LLM usage | Anonymized structured states; shadow mode + forward gate | Kim–Muhn–Nikolaev (2024); Lopez-Lira–Tang–Zhu (2025) memorization; chronologically consistent models (He et al. 2025) |
| Data / universe | NASDAQ, 4 sectors; delisted recovered via FMP; SEC XBRL PIT | CRSP/Compustat point-in-time with delisting returns (institutional standard) |

---

## 13. Where things live in the code
| Component | Path |
|---|---|
| Config (universe, factors, search, costs, Jev) | `config/*.yaml` |
| Data clients, XBRL PIT normalization | `src/data/` (`fmp.py`, `sec.py`, `xbrl.py`, `fundamentals_loader.py`, `prices.py`, `reference.py`) |
| Characteristics | `src/features/` (`fundamentals.py`, `research_features.py`, `momentum.py`, `technicals.py`, `preprocess.py`, `store.py`) |
| Scoring / model config | `src/model/scoring.py`, `src/model/promotion.py` |
| Portfolio, signals, sizing | `src/portfolio/` |
| Backtest, folds, metrics, research, validation, exploration | `src/backtest/` |
| Jev adapter, state, cache, forward gate | `src/jev/` |
| Pipelines / CLI | `src/pipeline/` (`bootstrap`, `monthly`, `tools`) |
| Dashboard | `app/streamlit_app.py` |
| Tests | `tests/` |
