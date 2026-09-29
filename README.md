# jev-factor-investor

A local research and decision-support application for **medium-term (3–6 month), long-only investing in NASDAQ
common stocks** in Technology, Biotechnology, Energy and Metals & Mining. Every month it produces a **factor-based
ranking** (the shortlist you then check with your own technical analysis) and **BUY / HOLD / WAIT / SELL** signals for
a USD 10,000 paper portfolio (fractional shares), backed by a fully persisted, reproducible walk-forward research
record.

The model (v2) combines literature-grounded, point-in-time characteristics — residual and 12-1 momentum, 52-week-high
proximity, cash-based and gross profitability, F-score, asset growth, net share issuance, value, ΔROE / earnings
surprise and low-risk (MAX, idiosyncratic volatility) — see [`docs/RESEARCH.md`](docs/RESEARCH.md) for definitions
and sources and [`docs/RESULTS.md`](docs/RESULTS.md) for the latest backtest. **Technical-analysis indicators are
deliberately not part of the model** (they are computed and shown in the dashboard for your own analysis).
**TypeSafe AI Jev** (via Vercel AI Gateway) runs in *shadow mode*: its judgements are recorded every month and it only
receives weight after a validated forward track record.

> Decision support only. No orders are sent anywhere. The portfolio layer exposes a `BrokerAdapter` protocol so a
> broker integration can be added later without touching strategy code.

---

## Architecture

```
config/*.yaml            research parameters (universe, factors, search spaces, costs, objective, Jev questions)
src/
  config.py              .env settings + YAML loading
  db/schema.py           DuckDB schema (append-oriented; decisions are versioned, never overwritten)
  data/
    http.py              cached HTTP client: raw-response disk cache, retries/backoff, Retry-After, request log
    fmp.py               Financial Modeling Prep (stable API): reference data, EOD prices, splits, delistings
    sec.py               SEC EDGAR (data.sec.gov): tickers/exchange, submissions (SIC), company facts
    xbrl.py              XBRL normalization with filing-availability semantics, derived quarters, TTM
    fundamentals_loader  facts -> financial_facts -> PIT snapshots (one per filing-availability date)
    reference.py         security master (active + delisted, sector group classification)
    prices.py            incremental price loads (adjusted-price chaining, split re-base detection)
  features/
    technicals.py        SMA/EMA/RSI/MACD/ADX/ATR/volatility/breakouts/... (pure pandas, no TA-Lib)
    momentum.py          1-12m returns, 3-1/6-1/12-1, forward labels (63/126 sessions)
    fundamentals.py      value / quality / growth / fundamental-momentum features (biotech-aware)
    preprocess.py        per-date winsorized robust z (median/MAD), sector-relative, percentiles, families
    store.py             builds + persists universe, factor_values, technical_values, forward_returns
  model/scoring.py       ModelConfig, family scores, quant composite, IC-weighted preset, Quant+Jev combination
  model/promotion.py     incumbent / challenger management
  jev/
    client.py            Vercel AI Gateway /v1/evaluate adapter (typed answers, validation, retries)
    state.py             compact anonymized point-in-time state text + hashing
    store.py             durable cache, feature sets, resumable bounded-concurrency generation
    candidates.py        candidate reduction + state construction on a fixed reference universe
  portfolio/             fractional-share book + costs, BUY/HOLD/WAIT/SELL with hysteresis, weighting
  backtest/              engine, walk-forward folds, metrics, research search/objective/Pareto, diagnostics
  explain/explainer.py   deterministic, traceable explanations
  pipeline/              bootstrap, monthly (shared by CLI + dashboard), tools
app/streamlit_app.py     dashboard with the RUN MONTHLY ANALYSIS button
tests/                   unit, leakage, pipeline and dashboard tests (synthetic data lives only here)
```

The dashboard button and `python -m src.pipeline.monthly` call the **same function**
(`src.pipeline.monthly_run.run_monthly`).

---

## Setup (Windows)

1. Install [uv](https://docs.astral.sh/uv/) (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. In the project folder:
   ```powershell
   uv python install 3.12
   uv sync
   copy .env.example .env      # then edit .env
   ```
3. Fill in `.env`:

| Variable | Purpose |
|---|---|
| `FMP_API_KEY` | Financial Modeling Prep key — **Starter plan or higher** (the free plan limits prices to ~87 symbols and has no screener) |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway key (Vercel dashboard → AI Gateway → API Keys). A credit card must be on file for the gateway to serve requests. |
| `SEC_USER_AGENT` | `"app-name your@email"` — SEC requires a descriptive User-Agent with a contact email |
| `INITIAL_CAPITAL_USD` | default 10000 |
| `JEV_ENABLED` | `true`/`false` |
| `JEV_MODEL` | `typesafe-ai/jev` |
| `JEV_MAX_CONCURRENCY` | bounded concurrency for Jev requests (default 5) |

`.env` is git-ignored. Never commit it. If `AI_GATEWAY_API_KEY` is missing the application runs **quant-only** and
reports Jev as unavailable; it never fabricates Jev outputs.

Check Jev connectivity: `uv run python -m src.pipeline.tools jev-check`

### How SEC access works
SEC EDGAR endpoints need no key. Every request sends `SEC_USER_AGENT`, requests are spaced to ≤ 8/s (SEC's limit
is 10/s), and responses are cached on disk (`data/raw_cache`). The app uses `company_tickers_exchange.json`
(NASDAQ tickers + CIK), `submissions/CIK##########.json` (SIC code) and `api/xbrl/companyfacts/CIK##########.json`
(all XBRL facts, each with its `filed` date).

### FMP plan (Starter, verified 2026-09-29)
Starter serves US prices (split- and dividend-adjusted) back to ~2006 (5,000 rows per request), the screener,
profiles and splits, at 300 calls/min and 20 GB per rolling 30 days. The client stays below the rate limit
(`config/data.yaml → fmp.min_interval_seconds`), fetches with a few threads, caches immutable payloads forever and loads
prices incrementally. Only page 0 of `delisted-companies` is available on Starter, so delisted companies are recovered
another way (see *Survivorship*). For the free plan set `fmp.daily_call_budget: 240`.

---

## Running

```powershell
# first-time historical initialization + research (resumable)
uv run python -m src.pipeline.bootstrap
uv run python -m src.pipeline.bootstrap --max-symbols 60         # reduced universe
uv run python -m src.pipeline.bootstrap --skip-data              # research on stored data only
uv run python -m src.pipeline.bootstrap --skip-jev               # quant-only

# monthly production analysis (same code as the dashboard button)
uv run python -m src.pipeline.monthly

# dashboard
uv run streamlit run app/streamlit_app.py

# utilities
uv run python -m src.pipeline.tools load-data                    # refresh reference data, prices, SEC facts, features
uv run python -m src.pipeline.tools report                       # write docs/RESULTS.md for the latest research run
uv run python -m src.pipeline.tools status
uv run python -m src.pipeline.tools backtest --max-configs 50     # research on stored data, no API calls
uv run python -m src.pipeline.tools jev-history --max-new 500     # Stage A only, resumable
uv run python -m src.pipeline.tools reproduce <RUN_ID>           # re-simulate a stored run
uv run pytest                                                     # test suite
```

---

## Methodology

### Universe (per rebalance, using only information available on that date)
NASDAQ common equities → ETFs/funds and warrants/units/rights/preferreds excluded → sector groups from FMP
sector/industry (SEC SIC fallback) → security must have been listed (IPO before, not delisted before the date, ≥ 252
sessions of history, traded within the last 5 sessions) → market cap ≥ threshold (100M/300M/500M/1B tested) →
**ADV20 = mean(close × volume over the previous 20 sessions)** ≥ threshold (1M/5M/10M/20M tested).
Market cap = split-adjusted close × SEC-reported shares converted to adjusted units with post-dated splits.

### Factors (v2)
Themes: **Momentum, Quality, Investment, Value, Fundamental Momentum, Low Risk** (plus Growth, weight 0 in the core
presets) — `config/factors.yaml`, definitions and sources in `docs/RESEARCH.md`. Invalid ratios (non-positive
denominators) are NaN, never forced. **Biotechnology** uses cash/market cap, cash runway, R&D/market cap, issuance,
asset growth, gross profitability, momentum and low risk — earnings-based ratios and F-score are excluded for the group.
Each date is normalized independently with rank → normal scores; accounting ratios are ranked within sector group,
price signals across the universe. Missing themes are handled explicitly (weight redistributed; a name needs ≥ 50% of
the weight present).

### Horizon
Research labels are **21-, 63- and 126-session** forward returns. The monthly review is only the decision frequency;
positions are held while they satisfy the hold rules (hysteresis), not liquidated monthly.

### Model search (restricted, interpretable)
Stage 1: theme-weight presets (literature, equal themes, momentum-quality, quality-value, defensive, momentum-only,
factor-momentum tilt, IC weights shrunk toward the literature weights) × Jev weights {0,5,…,30%} at default
parameters. Stage 2: a **seeded random sample** of the full grid (market cap, ADV, size {5,10,15,20,25,30}, weighting
{equal, score, inverse-vol, score×inverse-vol}, hold buffer {1,1.5,2,3,4}, Jev weight) that does not depend on results. Every configuration is persisted in
`factor_models`. One-at-a-time sensitivity around the best configuration (including cost multipliers 0–3×).

### Walk-forward evaluation
Backtests start 2011-06-30 (SEC XBRL coverage). Expanding window: ≥ 36 training months, 12-month test blocks,
1-month embargo; training labels whose 126-session
window ends after the test start are purged. Fold definitions are stored with each run. Two kinds of results are
reported and labelled:
* **per-configuration fold metrics** (median CAGR, 3m/6m returns, Sharpe, Sortino, Calmar, median / worst-fold
  drawdown, turnover) — used for the Pareto view, stability and sensitivity;
* **honest nested walk-forward**: in each fold the configuration is chosen using *only training-window*
  performance and then traded in the test window; the stitched out-of-sample curve (with switching costs) is the
  performance estimate. It is computed twice — **Quant only** and **Quant + Jev** — as the Jev ablation.

Objective (configurable): 35% median CAGR, 15% medium-horizon return, 15% Calmar, 10% Sharpe, 15% median-drawdown
quality, 10% worst-fold-drawdown quality, minus a turnover penalty; each component is robust-z normalized across
candidates. Stability reports factor-family inclusion and parameter frequencies among the top configurations.

### Transaction costs (explicit defaults, shown in every report)
Commission $1.00 per trade, slippage 10 bps (adverse) **plus half the estimated bid-ask spread** (Abdi–Ranaldo
estimator from daily OHLC, capped at 200 bps), transaction cost 5 bps of notional, delisting haircut 0%. Signals use
the close of day D; backtest trades execute at the **next session's open**. Position cap max(8%, 1.5/N), sector-group
cap 45%, minimum rebalancing trade $150. Overfitting controls: equal-weight universe benchmark, probability of
backtest overfitting (CSCV) and deflated Sharpe ratio are reported for every run.

### BUY / HOLD / WAIT / SELL
* **BUY** — not owned, ranks within the top *N* among names passing entry gates (volatility gate etc.), and a slot
  is free (or it ranks in the top *N × 0.5* and replaces a holding that fell outside the top *N*).
* **HOLD** — owned, rank ≤ *N × hold_buffer*, no exit condition.
* **WAIT** — not owned, rank ≤ *2N* but entry criteria not met (near cutoff, gate failure, portfolio full).
* **SELL** — owned and: rank > *N × hold_buffer*, fundamental deterioration (quality and fundamental-momentum
  percentiles < 10%), no longer eligible (delisted / illiquid / below market cap / price < $3), or replaced by a
  stronger candidate. (A technical-breakdown exit exists but is disabled: technical analysis is left to you.)
Jev only influences the final score; hard gates and exit rules are applied afterwards and cannot be overridden.

### Jev integration (Vercel AI Gateway)
`POST https://ai-gateway.vercel.sh/v1/evaluate` with `model: typesafe-ai/jev`. Schemas were verified against the
live API: `boolean` → `probability`; `score` → `criteria` = ordered levels, answer `score` (expected level),
`probabilities`, `confidence`; `choice` → `criteria` = `{label: description}`. One request per
`(ticker, rebalance_date)` state carries all questions (momentum persistence, fundamental deterioration, value trap,
relative outperformance, regime fit). Jev never computes numbers: states contain precomputed, bucketed values.
**States omit ticker, company name and dates by default** (`config/jev.yaml → include_identifiers: false`) because
Jev may know what happened to a named stock after a historical date — including identifiers would leak future
information into backtests.

* **Stage A** (`generate_historical_jev`): candidate states (union of top names per static preset on a fixed
  reference universe) are evaluated once and stored in `jev_decisions`, keyed by
  `hash(model + normalized state + state_schema_version + question_schema_version)`. Bounded concurrency,
  retries with `Retry-After`, checkpointing per result: an interrupted run resumes with only the missing states.
* **Stage B** (backtests) reuses stored probabilities; changing portfolio parameters never re-requests Jev.
* Every decision stores answers, probabilities, confidence, usage, cost, latency, generation id, status and errors.
  Vercel does not expose the underlying Jev release; it is recorded as *unknown* and every run records its
  `jev_feature_set_id`. Editing question text creates a new question-schema version; bump
  `feature_set_tag` for a deliberate full refresh (old decisions are kept).
* **Shadow mode / forward validation:** historical Jev backtests are look-ahead contaminated (LLMs can recall what
  happened after a historical date even from anonymized inputs), so they are reported only as an upper bound. In
  production Jev scores are stored every month and Jev receives weight only after ≥ 12 matured forward months show a
  significant rank IC beyond the quant score (`config/jev.yaml → production_policy`, `src/jev/forward.py`).
* Holdings additionally get a production-only *holding review* (thesis intact, exit urgency) that is shown in
  explanations but not scored, because it cannot be generated consistently for historical backtests.

### Incumbent / challenger
Each research run produces a challenger. It is promoted only if, on the same out-of-sample folds, it beats the
incumbent's objective by ≥ 0.25 robust-z units, wins ≥ 60% of folds, does not worsen worst-fold drawdown by more than
5 percentage points, and ≥ 3 months have passed since the last promotion. Every version and decision is appended to
`model_versions` / `promotion_decisions`; nothing is overwritten.

### Explanations
Generated deterministically from stored factor values and their contributions to the composite (strongest
positive/negative drivers with raw values), ranks, Jev probabilities and the exact rule thresholds that would change
the state. No narrative is invented.

---

## Point-in-time guarantees
* Fundamentals are used from `filed + 1 day` (never period end); a Dec-31 period filed Feb-10 is invisible to a
  Jan-31 rebalance. Restatements become visible only after their own filing date.
* Snapshots are built per filing-availability date; an assertion rejects any snapshot available after the rebalance.
* Price features use trailing windows only (tests inject large future moves and verify identical features).
* Normalization is per cross-section; labels are only used after they mature (IC-weighted preset, purged folds).
* Every persisted feature carries `availability_date` / `observation_period_end`; each run audits
  `availability_date <= rebalance_date` and flags any violation as critical.

## Survivorship bias — limitations (read this)
* Delisted NASDAQ companies are recovered from FMP's full symbol list minus actively traded symbols; each candidate is
  profiled (exchange, sector, CIK, IPO date) and priced from FMP's history, which retains delisted symbols. A stock
  is treated as delisted after its last trading day. Residual gaps remain — tickers later reused by another company
  and companies FMP no longer lists — so no run is claimed to be fully survivorship-safe.
* Delisted securities without a CIK mapping have no SEC fundamentals (they are still scored on price families).
* Sector classification is today's snapshot (FMP / SIC), not point-in-time.
* The free SEC and FMP data do not provide historical index membership; eligibility is reconstructed from listing
  dates, prices, market cap and liquidity.

## Other limitations
* ~15 years of point-in-time fundamentals (2011–2026) give about a dozen walk-forward folds: enough for honest
  out-of-sample estimates, still too short to prove skill statistically (see the deflated Sharpe in RESULTS.md).
* Dividend-adjusted prices are used when FMP provides them; otherwise returns are price-only (flagged in the report).
* Stock splits come from FMP's `splits` endpoint. When it is unavailable they are inferred from clean-ratio jumps in
  SEC as-reported share counts (`stock_splits.source = 'inferred_sec'`); vendor data replaces inferred rows later.
* Some companies report revenue only under company-specific XBRL extensions, which SEC's company-facts API does not
  publish (e.g. APA); those metrics stay missing rather than being approximated.
* Production accounting is a paper portfolio filled at the rebalance close with the configured costs.
