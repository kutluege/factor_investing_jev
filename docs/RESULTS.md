# Research results — run `bt_20260929_180053_0d655e`

Generated from the stored run (created 2026-09-29 15:01:00.660796, git `2ea3b5316a`). Data: 2382 symbols with prices 2006-10-02 → 2026-09-28, 2104 companies with SEC facts, 797 delisted securities in the master. Configurations tested: 196. Walk-forward folds: 12.

## 1. Honest out-of-sample performance (nested walk-forward)

Each fold's configuration was chosen using only training-window performance, then traded in the test window (switching costs included). This is the performance estimate to rely on.

| Strategy | CAGR | Volatility | Sharpe | Max DD | Calmar | Win months | Turnover/yr |
|---|---|---|---|---|---|---|---|
| Fixed prior (pre-specified default, no selection) | 10.5% | 20.9% | 0.58 | -30.4% | 0.35 | 58% | 2.0 |
| Incumbent/challenger, quant only (production process) | 6.0% | 18.8% | 0.40 | -37.3% | 0.16 | 56% | 1.5 |
| Free per-fold selection, quant only | -6.8% | 23.8% | -0.17 | -76.1% | -0.09 | 53% | 3.7 |
| Benchmark EW_universe (same period) | 13.6% | — | — | -47.2% | — | — | — |
| Benchmark QQQ (same period) | 19.3% | — | — | -35.1% | — | — | — |
| Benchmark SPY (same period) | 13.9% | — | — | -33.7% | — | — | — |

- Fixed prior (pre-specified default, no selection) vs EW_universe: excess CAGR -3.1%, beta 0.63, alpha 1.8%, information ratio -0.27, tracking error 15.8%
- Fixed prior (pre-specified default, no selection) vs QQQ: excess CAGR -8.8%, beta 0.74, alpha -2.5%, information ratio -0.53, tracking error 14.7%
- Fixed prior (pre-specified default, no selection) vs SPY: excess CAGR -3.4%, beta 0.94, alpha -1.5%, information ratio -0.18, tracking error 13.1%
- Incumbent/challenger, quant only (production process) vs EW_universe: excess CAGR -7.7%, beta 0.55, alpha -1.5%, information ratio -0.54, tracking error 16.6%
- Incumbent/challenger, quant only (production process) vs QQQ: excess CAGR -13.3%, beta 0.68, alpha -6.1%, information ratio -0.93, tracking error 13.3%
- Incumbent/challenger, quant only (production process) vs SPY: excess CAGR -7.9%, beta 0.90, alpha -5.5%, information ratio -0.66, tracking error 10.6%
- Free per-fold selection, quant only vs EW_universe: excess CAGR -20.4%, beta 0.62, alpha -14.4%, information ratio -1.04, tracking error 19.7%
- Free per-fold selection, quant only vs QQQ: excess CAGR -26.0%, beta 0.75, alpha -19.1%, information ratio -1.31, tracking error 18.4%
- Free per-fold selection, quant only vs SPY: excess CAGR -20.6%, beta 0.95, alpha -17.9%, information ratio -1.08, tracking error 17.3%

Model held per test fold (Incumbent/challenger, quant only (production process)):

| Test start | Preset | N | Min market cap | Decision |
|---|---|---|---|---|
| 2014-07-31 | quality_value | 30 | $300M | promoted (objective +2.37, win 100%) |
| 2015-08-31 | quality_value | 30 | $300M | incumbent retained |
| 2016-09-30 | quality_value | 30 | $300M | retained (challenger objective +1.06, win 50%, dd_ok=True) |
| 2017-10-31 | quality_value | 30 | $300M | retained (challenger objective +1.84, win 58%, dd_ok=True) |
| 2018-11-30 | quality_value | 30 | $300M | retained (challenger objective +1.56, win 57%, dd_ok=True) |
| 2019-12-31 | defensive | 25 | $500M | promoted (objective +1.54, win 62%) |
| 2021-01-29 | defensive | 25 | $500M | retained (challenger objective +0.17, win 42%, dd_ok=True) |
| 2022-02-28 | defensive | 25 | $500M | retained (challenger objective +0.43, win 24%, dd_ok=True) |
| 2023-03-31 | defensive | 25 | $500M | retained (challenger objective +0.28, win 22%, dd_ok=True) |
| 2024-04-30 | defensive | 25 | $500M | retained (challenger objective +0.65, win 36%, dd_ok=True) |
| 2025-05-30 | defensive | 25 | $500M | retained (challenger objective +0.56, win 22%, dd_ok=True) |
| 2026-06-30 | defensive | 25 | $500M | retained (challenger objective +0.66, win 24%, dd_ok=True) |

## 2. Overfitting controls

- Probability of backtest overfitting (CSCV, 168 configurations, 146 months): **56%** (< 50% means in-sample winners tend to stay above median out of sample).
- Deflated Sharpe ratio, fixed_prior: **83%** probability the true Sharpe exceeds the best of 168 random trials (annualized Sharpe 0.65).
- Deflated Sharpe ratio, promotion_quant_only: **60%** probability the true Sharpe exceeds the best of 168 random trials (annualized Sharpe 0.45).
- Deflated Sharpe ratio, free_selection_quant_only: **2%** probability the true Sharpe exceeds the best of 168 random trials (annualized Sharpe -0.19).

## 3. Configuration selected on all folds (the production challenger)

`{"preset": "defensive", "min_market_cap": 500000000.0, "min_adv20": 20000000.0, "portfolio_size": 25, "weighting": "inverse_vol", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`

Theme weights: `{"momentum": 15, "quality": 35, "investment": 25, "value": 10, "fundamental_momentum": 0, "low_risk": 15}`

Full-period simulation of this configuration (in-sample for the selection itself; see §1 for the honest estimate):

| Strategy | CAGR | Volatility | Sharpe | Max DD | Calmar | Win months | Turnover/yr |
|---|---|---|---|---|---|---|---|
| Selected configuration | 14.0% | 17.8% | 0.83 | -26.3% | 0.53 | 63% | 1.2 |
| EW_universe | 13.7% | — | — | -47.2% | — | — | — |
| QQQ | 19.3% | — | — | -35.1% | — | — | — |
| SPY | 14.2% | — | — | -33.7% | — | — | — |

Across walk-forward test folds: median CAGR 12.0%, median Sharpe 0.81, worst-fold max drawdown -26.3%.

## 4. Factor research (cross-sectional rank IC of theme scores)

| Theme | rank IC h21 | rank IC h63 | rank IC h126 | t h21 | t h63 | t h126 |
|---|---|---|---|---|---|---|
| composite_literature | 0.043 | 0.070 | 0.090 | 4.0 | 7.0 | 9.7 |
| fundamental_momentum | 0.014 | 0.024 | 0.025 | 2.2 | 4.2 | 4.7 |
| growth | -0.013 | -0.017 | -0.040 | -1.6 | -2.2 | -5.1 |
| investment | 0.034 | 0.046 | 0.068 | 3.6 | 4.9 | 7.4 |
| low_risk | 0.044 | 0.081 | 0.118 | 3.5 | 6.9 | 10.5 |
| momentum | 0.023 | 0.043 | 0.049 | 2.4 | 4.9 | 5.8 |
| quality | 0.035 | 0.049 | 0.060 | 3.9 | 5.5 | 7.4 |
| value | 0.006 | 0.002 | 0.004 | 0.7 | 0.3 | 0.5 |

## 5. Stability of the top configurations

Top 16 configurations. Theme inclusion share: `{"momentum": 0.875, "quality": 0.562, "investment": 0.562, "value": 0.562, "low_risk": 0.562, "fundamental_momentum": 0.062, "(dynamic IC weights)": 0.125}`

Parameter frequency: `{"preset": {"defensive": 0.5, "momentum_only": 0.312, "equal_themes": 0.062, "literature_ic_shrunk": 0.062, "literature_factor_momentum": 0.062}, "portfolio_size": {"25": 0.312, "15": 0.25, "20": 0.188, "5": 0.125, "30": 0.125}, "min_market_cap": {"500000000.0": 0.312, "100000000.0": 0.25, "300000000.0": 0.25, "1000000000.0": 0.188}, "min_adv20": {"10000000.0": 0.438, "20000000.0": 0.25, "5000000.0": 0.188, "1000000.0": 0.125}, "weighting": {"inverse_vol": 0.5, "score": 0.25, "equal": 0.188, "score_inverse_vol": 0.062}, "hold_buffer": {"3.0": 0.375, "4.0": 0.375, "1.5": 0.125, "2.0": 0.062, "1.0": 0.062}, "jev_weight": {"0.0": 1.0}}`

## 6. Sensitivity (one parameter at a time around the selected configuration)

| Parameter | Value | Median fold CAGR | Median Sharpe | Worst-fold DD | Turnover |
|---|---|---|---|---|---|
| min_market_cap | 100000000.0 | 12.3% | 0.75 | -30.1% | 2.1 |
| min_market_cap | 300000000.0 | 10.4% | 0.73 | -32.2% | 2.2 |
| min_market_cap | 500000000.0 | 11.6% | 0.75 | -31.3% | 2.1 |
| min_market_cap | 1000000000.0 | 13.4% | 0.92 | -28.6% | 2.1 |
| min_adv20 | 1000000.0 | 5.9% | 0.48 | -30.8% | 2.2 |
| min_adv20 | 5000000.0 | 9.5% | 0.74 | -29.8% | 2.1 |
| min_adv20 | 10000000.0 | 9.6% | 0.63 | -28.7% | 2.2 |
| min_adv20 | 20000000.0 | 13.4% | 0.92 | -28.6% | 2.1 |
| portfolio_size | 5 | 9.1% | 0.53 | -25.9% | 3.3 |
| portfolio_size | 10 | 9.6% | 0.63 | -28.6% | 2.8 |
| portfolio_size | 15 | 8.0% | 0.56 | -26.0% | 2.2 |
| portfolio_size | 20 | 13.4% | 0.92 | -28.6% | 2.1 |
| portfolio_size | 25 | 14.0% | 0.82 | -26.8% | 1.9 |
| portfolio_size | 30 | 11.6% | 0.73 | -28.3% | 1.6 |
| weighting | equal | 12.0% | 0.69 | -29.9% | 2.0 |
| weighting | score | 11.5% | 0.67 | -28.8% | 2.4 |
| weighting | inverse_vol | 13.4% | 0.92 | -28.6% | 2.1 |
| weighting | score_inverse_vol | 12.1% | 0.81 | -28.1% | 2.3 |
| hold_buffer | 1.0 | 8.5% | 0.62 | -32.4% | 3.5 |
| hold_buffer | 1.5 | 13.4% | 0.92 | -28.6% | 2.1 |
| hold_buffer | 2.0 | 14.5% | 0.89 | -29.4% | 1.5 |
| hold_buffer | 3.0 | 13.0% | 0.82 | -28.7% | 1.3 |
| hold_buffer | 4.0 | 13.5% | 0.85 | -28.4% | 1.4 |
| jev_weight | 0.0 | 13.4% | 0.92 | -28.6% | 2.1 |
| cost_multiplier | 0.0 | 15.1% | 1.03 | -28.4% | 2.0 |
| cost_multiplier | 1.0 | 13.4% | 0.92 | -28.6% | 2.1 |
| cost_multiplier | 2.0 | 11.4% | 0.81 | -29.6% | 2.1 |
| cost_multiplier | 3.0 | 9.5% | 0.69 | -29.8% | 2.1 |
| preset | literature | 7.7% | 0.48 | -28.8% | 2.5 |
| preset | equal_themes | 7.8% | 0.63 | -23.3% | 2.8 |
| preset | momentum_quality | 11.1% | 0.61 | -30.2% | 2.6 |
| preset | quality_value | 4.1% | 0.31 | -28.1% | 1.7 |
| preset | defensive | 13.4% | 0.92 | -28.6% | 2.1 |
| preset | momentum_only | 8.0% | 0.45 | -39.3% | 4.9 |
| preset | literature_factor_momentum | 5.6% | 0.34 | -30.3% | 2.9 |
| preset | literature_ic_shrunk | 5.6% | 0.61 | -25.0% | 2.8 |

## 7. Jev

Jev features used: False (feature set `None`; requested `typesafe-ai/jev`, resolved version unknown (not exposed by Vercel AI Gateway)).

Historical Jev results are an upper bound (LLM look-ahead); production uses Jev only after forward validation (see docs/RESEARCH.md §5).

## 8. Diagnostics

- **warning** `survivorship`: Partially mitigated: delisted securities are included where the data source provided them, but coverage of historical delistings is incomplete.
- Look-ahead audit: {'future_factor_values': 0, 'future_technical_values': 0, 'future_snapshots': 0, 'passed': True}

Costs assumed: `{"commission_per_trade_usd": 1.0, "slippage_bps": 10, "spread_cost": true, "max_spread_cost_bps": 200, "transaction_cost_bps": 5, "delisting_haircut": 0.0, "distress_haircut": 0.3, "distress_price": 2.0, "distress_drawdown": 0.6}`

Ending equity by series ($10,000 start): incumbent $56,512, best_model $73,727, bench_QQQ $147,247, bench_XLE $27,760, bench_XBI $66,785, bench_XLK $184,389, bench_SPY $75,735, bench_XME $18,678, walk_forward_promotion_quant_only $20,242, walk_forward_free_selection_quant_only $4,274, bench_EW_universe $70,769, walk_forward_fixed_prior $33,662
