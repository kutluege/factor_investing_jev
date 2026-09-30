# Research results — run `bt_20260930_151358_aceb0b`

Generated from the stored run (created 2026-09-30 12:14:08.475900, git `0ff4f7ba0b`). Data: 2382 symbols with prices 2006-10-02 → 2026-09-28, 2104 companies with SEC facts, 797 delisted securities in the master. Configurations tested: 250. Walk-forward folds: 12.

## 1. Honest out-of-sample performance (nested walk-forward)

Each fold's configuration was chosen using only training-window performance, then traded in the test window (switching costs included). This is the performance estimate to rely on.

| Strategy | CAGR | Volatility | Sharpe | Max DD | Calmar | Win months | Turnover/yr |
|---|---|---|---|---|---|---|---|
| Fixed prior (pre-specified default, no selection) | 10.5% | 20.9% | 0.58 | -30.4% | 0.35 | 58% | 2.0 |
| Incumbent/challenger, quant only (production process) | 8.6% | 18.2% | 0.55 | -23.9% | 0.36 | 58% | 2.4 |
| Free per-fold selection, quant only | 17.3% | 30.2% | 0.68 | -53.7% | 0.32 | 53% | 2.9 |
| Incumbent/challenger, Jev weight selectable (upper bound: LLM look-ahead) | 7.4% | 19.1% | 0.47 | -29.9% | 0.25 | 58% | 1.7 |
| Free per-fold selection, Jev weight selectable | 4.0% | 19.8% | 0.30 | -49.0% | 0.08 | 59% | 2.2 |
| Benchmark EW_universe (same period) | 13.6% | — | — | -47.2% | — | — | — |
| Benchmark QQQ (same period) | 19.3% | — | — | -35.1% | — | — | — |
| Benchmark SPY (same period) | 13.9% | — | — | -33.7% | — | — | — |

- Fixed prior (pre-specified default, no selection) vs EW_universe: excess CAGR -3.1%, beta 0.63, alpha 1.8%, information ratio -0.27, tracking error 15.8%
- Fixed prior (pre-specified default, no selection) vs QQQ: excess CAGR -8.8%, beta 0.74, alpha -2.5%, information ratio -0.53, tracking error 14.7%
- Fixed prior (pre-specified default, no selection) vs SPY: excess CAGR -3.4%, beta 0.94, alpha -1.5%, information ratio -0.18, tracking error 13.1%
- Incumbent/challenger, quant only (production process) vs EW_universe: excess CAGR -5.0%, beta 0.52, alpha 1.3%, information ratio -0.38, tracking error 17.2%
- Incumbent/challenger, quant only (production process) vs QQQ: excess CAGR -10.6%, beta 0.64, alpha -2.8%, information ratio -0.70, tracking error 14.3%
- Incumbent/challenger, quant only (production process) vs SPY: excess CAGR -5.3%, beta 0.83, alpha -2.1%, information ratio -0.40, tracking error 11.6%
- Free per-fold selection, quant only vs EW_universe: excess CAGR 3.7%, beta 0.73, alpha 8.5%, information ratio 0.17, tracking error 24.0%
- Free per-fold selection, quant only vs QQQ: excess CAGR -1.9%, beta 0.83, alpha 4.0%, information ratio 0.02, tracking error 24.5%
- Free per-fold selection, quant only vs SPY: excess CAGR 3.5%, beta 1.07, alpha 5.0%, information ratio 0.25, tracking error 23.8%
- Incumbent/challenger, Jev weight selectable (upper bound: LLM look-ahead) vs EW_universe: excess CAGR -6.2%, beta 0.57, alpha -0.4%, information ratio -0.46, tracking error 16.2%
- Incumbent/challenger, Jev weight selectable (upper bound: LLM look-ahead) vs QQQ: excess CAGR -11.9%, beta 0.71, alpha -5.2%, information ratio -0.85, tracking error 13.0%
- Incumbent/challenger, Jev weight selectable (upper bound: LLM look-ahead) vs SPY: excess CAGR -6.5%, beta 0.91, alpha -4.3%, information ratio -0.51, tracking error 10.9%
- Free per-fold selection, Jev weight selectable vs EW_universe: excess CAGR -9.7%, beta 0.57, alpha -3.5%, information ratio -0.62, tracking error 17.1%
- Free per-fold selection, Jev weight selectable vs QQQ: excess CAGR -15.3%, beta 0.70, alpha -8.2%, information ratio -0.99, tracking error 14.3%
- Free per-fold selection, Jev weight selectable vs SPY: excess CAGR -9.9%, beta 0.91, alpha -7.4%, information ratio -0.72, tracking error 12.1%

Model held per test fold (Incumbent/challenger, quant only (production process)):

| Test start | Preset | N | Min market cap | Decision |
|---|---|---|---|---|
| 2014-07-31 | defensive | 20 | $300M | promoted (objective +2.06, win 67%) |
| 2015-08-31 | defensive | 20 | $300M | retained (challenger objective +0.10, win 75%, dd_ok=False) |
| 2016-09-30 | defensive | 20 | $300M | retained (challenger objective +0.93, win 80%, dd_ok=False) |
| 2017-10-31 | defensive | 20 | $300M | promoted (objective +1.19, win 75%) |
| 2018-11-30 | equal_themes | 20 | $300M | promoted (objective +0.51, win 64%) |
| 2019-12-31 | equal_themes | 20 | $300M | incumbent retained |
| 2021-01-29 | equal_themes | 20 | $300M | incumbent retained |
| 2022-02-28 | equal_themes | 20 | $300M | retained (challenger objective +0.71, win 43%, dd_ok=False) |
| 2023-03-31 | equal_themes | 20 | $300M | retained (challenger objective +0.28, win 43%, dd_ok=False) |
| 2024-04-30 | equal_themes | 20 | $300M | retained (challenger objective +0.41, win 44%, dd_ok=False) |
| 2025-05-30 | equal_themes | 20 | $300M | incumbent retained |
| 2026-06-30 | equal_themes | 20 | $300M | retained (challenger objective +0.60, win 55%, dd_ok=False) |

## 2. Overfitting controls

- Probability of backtest overfitting (CSCV, 216 configurations, 146 months): **62%** (< 50% means in-sample winners tend to stay above median out of sample).
- Deflated Sharpe ratio, fixed_prior: **80%** probability the true Sharpe exceeds the best of 216 random trials (annualized Sharpe 0.65).
- Deflated Sharpe ratio, promotion_quant_only: **74%** probability the true Sharpe exceeds the best of 216 random trials (annualized Sharpe 0.60).
- Deflated Sharpe ratio, free_selection_quant_only: **73%** probability the true Sharpe exceeds the best of 216 random trials (annualized Sharpe 0.51).
- Deflated Sharpe ratio, promotion_with_jev: **68%** probability the true Sharpe exceeds the best of 216 random trials (annualized Sharpe 0.55).
- Deflated Sharpe ratio, free_selection_with_jev: **37%** probability the true Sharpe exceeds the best of 216 random trials (annualized Sharpe 0.31).

## 3. Configuration selected on all folds (the production challenger)

`{"preset": "equal_themes", "min_market_cap": 300000000.0, "min_adv20": 5000000.0, "portfolio_size": 20, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`

Theme weights: `{"momentum": 1, "quality": 1, "investment": 1, "value": 1, "fundamental_momentum": 1, "low_risk": 1}`

Full-period simulation of this configuration (in-sample for the selection itself; see §1 for the honest estimate):

| Strategy | CAGR | Volatility | Sharpe | Max DD | Calmar | Win months | Turnover/yr |
|---|---|---|---|---|---|---|---|
| Selected configuration | 12.1% | 18.1% | 0.72 | -21.6% | 0.56 | 60% | 2.2 |
| EW_universe | 13.7% | — | — | -47.2% | — | — | — |
| QQQ | 19.3% | — | — | -35.1% | — | — | — |
| SPY | 14.2% | — | — | -33.7% | — | — | — |

Across walk-forward test folds: median CAGR 9.0%, median Sharpe 0.59, worst-fold max drawdown -21.6%.

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

Top 21 configurations. Theme inclusion share: `{"momentum": 0.762, "quality": 0.524, "investment": 0.524, "value": 0.524, "low_risk": 0.524, "(dynamic IC weights)": 0.238, "fundamental_momentum": 0.095}`

Parameter frequency: `{"preset": {"defensive": 0.429, "momentum_only": 0.238, "literature_ic_shrunk": 0.19, "quality_value": 0.048, "literature_factor_momentum": 0.048, "equal_themes": 0.048}, "portfolio_size": {"20": 0.476, "25": 0.286, "5": 0.19, "30": 0.048}, "min_market_cap": {"300000000.0": 0.476, "1000000000.0": 0.19, "100000000.0": 0.19, "500000000.0": 0.143}, "min_adv20": {"5000000.0": 0.429, "20000000.0": 0.238, "10000000.0": 0.238, "1000000.0": 0.095}, "weighting": {"equal": 0.429, "inverse_vol": 0.238, "score_inverse_vol": 0.238, "score": 0.095}, "hold_buffer": {"4.0": 0.333, "3.0": 0.333, "2.0": 0.19, "1.5": 0.143}, "jev_weight": {"0.25": 0.286, "0.0": 0.19, "0.1": 0.19, "0.15": 0.143, "0.3": 0.095, "0.2": 0.048, "0.05": 0.048}}`

## 6. Sensitivity (one parameter at a time around the selected configuration)

| Parameter | Value | Median fold CAGR | Median Sharpe | Worst-fold DD | Turnover |
|---|---|---|---|---|---|
| min_market_cap | 100000000.0 | 11.9% | 0.71 | -27.6% | 1.3 |
| min_market_cap | 300000000.0 | 12.5% | 0.81 | -28.3% | 1.2 |
| min_market_cap | 500000000.0 | 12.9% | 0.74 | -26.8% | 1.2 |
| min_market_cap | 1000000000.0 | 14.5% | 0.76 | -27.6% | 1.2 |
| min_adv20 | 1000000.0 | 6.1% | 0.50 | -30.9% | 1.3 |
| min_adv20 | 5000000.0 | 11.2% | 0.74 | -30.9% | 1.3 |
| min_adv20 | 10000000.0 | 11.9% | 0.79 | -28.9% | 1.4 |
| min_adv20 | 20000000.0 | 12.5% | 0.81 | -28.3% | 1.2 |
| portfolio_size | 5 | 1.1% | 0.15 | -33.0% | 2.5 |
| portfolio_size | 10 | 4.2% | 0.33 | -27.6% | 1.8 |
| portfolio_size | 15 | 14.0% | 0.89 | -31.6% | 1.3 |
| portfolio_size | 20 | 14.1% | 0.83 | -28.9% | 1.3 |
| portfolio_size | 25 | 12.5% | 0.81 | -28.3% | 1.2 |
| portfolio_size | 30 | 12.5% | 0.72 | -26.8% | 1.1 |
| weighting | equal | 11.6% | 0.74 | -29.5% | 1.1 |
| weighting | score | 12.8% | 0.69 | -29.1% | 1.7 |
| weighting | inverse_vol | 12.5% | 0.81 | -28.3% | 1.2 |
| weighting | score_inverse_vol | 12.0% | 0.75 | -27.7% | 1.7 |
| hold_buffer | 1.0 | 10.9% | 0.70 | -28.5% | 3.4 |
| hold_buffer | 1.5 | 12.2% | 0.66 | -27.8% | 1.9 |
| hold_buffer | 2.0 | 10.7% | 0.65 | -30.3% | 1.5 |
| hold_buffer | 3.0 | 12.5% | 0.81 | -28.3% | 1.2 |
| hold_buffer | 4.0 | 12.5% | 0.81 | -28.3% | 1.2 |
| jev_weight | 0.0 | 11.5% | 0.75 | -26.3% | 1.2 |
| jev_weight | 0.05 | 12.5% | 0.88 | -25.9% | 1.2 |
| jev_weight | 0.1 | 13.3% | 0.93 | -25.9% | 1.2 |
| jev_weight | 0.15 | 12.6% | 0.85 | -27.4% | 1.2 |
| jev_weight | 0.2 | 13.0% | 0.87 | -28.6% | 1.2 |
| jev_weight | 0.25 | 11.6% | 0.80 | -28.1% | 1.2 |
| jev_weight | 0.3 | 12.5% | 0.81 | -28.3% | 1.2 |
| cost_multiplier | 0.0 | 13.5% | 0.92 | -28.4% | 1.2 |
| cost_multiplier | 1.0 | 12.5% | 0.81 | -28.3% | 1.2 |
| cost_multiplier | 2.0 | 11.2% | 0.69 | -28.4% | 1.2 |
| cost_multiplier | 3.0 | 9.8% | 0.60 | -28.5% | 1.2 |
| preset | literature | 8.7% | 0.59 | -32.4% | 1.8 |
| preset | equal_themes | 8.3% | 0.58 | -24.8% | 1.8 |
| preset | momentum_quality | 12.5% | 0.70 | -33.9% | 1.8 |
| preset | quality_value | 8.4% | 0.56 | -25.9% | 1.3 |
| preset | defensive | 12.5% | 0.81 | -28.3% | 1.2 |
| preset | momentum_only | 17.5% | 0.89 | -38.7% | 2.9 |
| preset | literature_factor_momentum | 11.3% | 0.66 | -30.4% | 1.9 |
| preset | literature_ic_shrunk | 9.3% | 0.67 | -27.2% | 1.5 |

## 7. Jev

Jev features used: True (feature set `jfs_ab5d5f8fc4f9`; requested `typesafe-ai/jev`, resolved version unknown (not exposed by Vercel AI Gateway)).

Ablation (fold medians): `{"best_quant_only": {"median_cagr": 0.11488231752016209, "median_sharpe": 0.7462458189385804, "worst_fold_max_drawdown": -0.2628775814216153, "objective": 1.2711789133107778}, "best_with_jev": {"median_cagr": 0.1330055724508541, "median_sharpe": 0.9277815819611048, "worst_fold_max_drawdown": -0.2586128352061512, "objective": 1.6554003738951804, "jev_weight": 0.1}}`
Historical Jev results are an upper bound (LLM look-ahead); production uses Jev only after forward validation (see docs/RESEARCH.md §5).

## 8. Diagnostics

- **warning** `survivorship`: Partially mitigated: delisted securities are included where the data source provided them, but coverage of historical delistings is incomplete.
- Look-ahead audit: {'future_factor_values': 0, 'future_technical_values': 0, 'future_snapshots': 0, 'passed': True}

Costs assumed: `{"commission_per_trade_usd": 1.0, "slippage_bps": 10, "spread_cost": true, "max_spread_cost_bps": 200, "transaction_cost_bps": 5, "delisting_haircut": 0.0, "distress_haircut": 0.3, "distress_price": 2.0, "distress_drawdown": 0.6}`

Ending equity by series ($10,000 start): bench_QQQ $147,247, bench_SPY $75,735, bench_XLK $184,389, walk_forward_fixed_prior $33,662, walk_forward_free_selection_with_jev $16,021, incumbent $47,733, bench_EW_universe $70,769, walk_forward_promotion_with_jev $23,824, walk_forward_free_selection_quant_only $69,934, bench_XBI $66,785, bench_XLE $27,760, bench_XME $18,678, walk_forward_promotion_quant_only $27,345, best_model $56,832
