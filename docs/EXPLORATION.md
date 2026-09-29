# Maximum-return exploration

Run `ex_20260929_180435_cd46ba`. Out-of-sample window from 2014-07-31. Strategies were declared after the main research results were seen (exploratory). Same engine, costs and data as the main research. Deflated Sharpe counts all 208 configurations tested.

| Strategy | CAGR | Volatility | Sharpe | Max DD | Worst month | vs QQQ CAGR | vs EW CAGR | Turnover/yr | Deflated Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| prior_reference | 10.5% | 20.9% | 0.58 | -30.4% | -11.3% | -8.8% | -3.1% | 2.0 | 82.6% |
| momentum_20 | 12.2% | 33.3% | 0.51 | -63.7% | -19.1% | -7.1% | -1.5% | 3.6 | 69.9% |
| momentum_20_regime | 8.4% | 29.5% | 0.42 | -57.8% | -19.1% | -10.8% | -5.2% | 3.4 | 56.4% |
| momentum_10_regime | 12.3% | 34.6% | 0.51 | -56.9% | -26.5% | -6.9% | -1.3% | 4.1 | 65.7% |
| mom_quality_15 | 9.3% | 23.0% | 0.50 | -34.6% | -11.5% | -9.9% | -4.3% | 2.3 | 75.4% |
| mom_quality_15_regime | 7.7% | 20.9% | 0.46 | -34.8% | -11.5% | -11.6% | -5.9% | 2.3 | 70.1% |
| mom_quality_10_regime | 4.2% | 21.8% | 0.30 | -39.0% | -12.4% | -15.1% | -9.5% | 2.8 | 38.8% |
| largecap_mom_quality_15 | 12.1% | 19.7% | 0.68 | -30.4% | -13.5% | -7.2% | -1.6% | 1.3 | 91.3% |
| largecap_momentum_10 | 15.1% | 26.3% | 0.67 | -35.4% | -21.5% | -4.1% | 1.5% | 2.7 | 90.5% |
| largecap_literature_15_regime | 8.2% | 16.7% | 0.56 | -26.6% | -12.8% | -11.0% | -5.4% | 1.4 | 82.7% |
| equal_themes_20 | 9.9% | 17.9% | 0.62 | -22.5% | -11.8% | -9.4% | -3.8% | 2.3 | 84.1% |
| broad_anti_junk_60 | 10.5% | 20.3% | 0.59 | -31.0% | -10.8% | -8.8% | -3.2% | 1.2 | 84.6% |
| Benchmark QQQ | 19.3% | — | — | -35.1% | — | — | — | — | — |
| Benchmark SPY | 13.9% | — | — | -33.7% | — | — | — | — | — |
| Benchmark EW_universe | 13.6% | — | — | -47.2% | — | — | — | — | — |

Configurations:

- **prior_reference**: `{"preset": "literature", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 20, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
- **momentum_20**: `{"preset": "momentum_only", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 20, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
- **momentum_20_regime**: `{"preset": "momentum_only", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 20, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0, "regime_filter": "cash"}`
- **momentum_10_regime**: `{"preset": "momentum_only", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 10, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0, "regime_filter": "cash"}`
- **mom_quality_15**: `{"preset": "momentum_quality", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 15, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
- **mom_quality_15_regime**: `{"preset": "momentum_quality", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 15, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0, "regime_filter": "half"}`
- **mom_quality_10_regime**: `{"preset": "momentum_quality", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 10, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0, "regime_filter": "cash"}`
- **largecap_mom_quality_15**: `{"preset": "momentum_quality", "min_market_cap": 10000000000, "min_adv20": 5000000.0, "portfolio_size": 15, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
- **largecap_momentum_10**: `{"preset": "momentum_only", "min_market_cap": 10000000000, "min_adv20": 5000000.0, "portfolio_size": 10, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
- **largecap_literature_15_regime**: `{"preset": "literature", "min_market_cap": 10000000000, "min_adv20": 5000000.0, "portfolio_size": 15, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0, "regime_filter": "half"}`
- **equal_themes_20**: `{"preset": "equal_themes", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 20, "weighting": "equal", "hold_buffer": 3.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
- **broad_anti_junk_60**: `{"preset": "literature", "min_market_cap": 300000000, "min_adv20": 5000000.0, "portfolio_size": 60, "weighting": "equal", "hold_buffer": 2.0, "jev_weight": 0.0, "cost_multiplier": 1.0}`
