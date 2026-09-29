# Research basis of the factor model (v2)

This document records *why* the model looks the way it does. Signals and construction rules were fixed from the
published evidence **before** looking at backtest results; the backtest is used to choose among a handful of
interpretable alternatives and to validate — not to invent new signals. Results are in
[`RESULTS.md`](RESULTS.md).

## 1. What the evidence says (summary)

* **Replication.** Most well-known anomalies replicate (Jensen, Kelly & Pedersen 2023, JF: ~82% of US factors; Chen &
  Zimmermann 2022), but returns fall by roughly a quarter out of sample and about half after publication (McLean &
  Pontiff 2016). Many anomalies are microcap-only (Hou, Xue & Zhang 2020). After spreads and post-2005 decay a single
  anomaly earns very little (Chen & Velikov 2023); only combinations of robust themes are worth trading.
* **Long-only.** Roughly half of value and momentum profits come from the long side (Israel & Moskowitz 2013); most
  of the long-only value added is avoiding "junk" — heavy issuers, cash-burning, lottery-like and distressed stocks
  (Stambaugh, Yu & Yuan 2012; Asness et al. 2018).
* **Realistic target.** For a concentrated long-only small/mid-cap portfolio: ~1–3%/yr net excess over the
  equal-weight universe, information ratio ~0.1–0.3. Much better backtests should be treated as overfit.

## 2. Characteristics used (all point-in-time)

| Theme | Characteristic | Definition | Sign | Source |
|---|---|---|---|---|
| Momentum | `res_mom_12_2` | Sum of residuals t-12..t-2 from a 36-month regression on QQQ and sector-group returns, / their std | + | Blitz, Huij & Martens (2011); Blitz, Hanauer & Vidojevic (2020) |
| | `dist_52w_high` | Price / 252-session high − 1 | + | George & Hwang (2004) |
| | `mom_12_1` | 12-1 month return | + | Jegadeesh & Titman (1993) |
| | `mom_12_7` | 12-7 month return | + | Novy-Marx (2012) |
| | `sector_mom_6m` | Sector-group median 6-month return (energy, mining only) | + | Moskowitz & Grinblatt (1999) |
| Quality | `cop_at` | Operating cash flow (TTM) / total assets — cash-based profitability proxy | + | Ball, Gerakos, Linnainmaa & Nikolaev (2016) |
| | `gross_profitability` | Gross profit (TTM) / total assets | + | Novy-Marx (2013) |
| | `fscore` | Piotroski F-score (9 signals, scaled over computable signals) | + | Piotroski (2000) |
| Investment | `asset_growth` | Total assets YoY growth | − | Cooper, Gulen & Schill (2008) |
| | `share_issuance` | log(split-adjusted shares / shares one year earlier) | − | Pontiff & Woodgate (2008) |
| | `cash_runway_years` | Cash / annual FCF burn (biotech) | + | dilution-risk proxy |
| Value | `ebit_ev`, `ocf_ev` | EBIT / EV, operating cash flow / EV (not biotech) | + | Loughran & Wellman (2011); Asness et al. |
| | `book_to_market` | Book equity / market cap | + | Fama & French (1992) |
| | `rd_intensity` | R&D (TTM) / market cap (tech, biotech) | + | Chan, Lakonishok & Sougiannis (2001) |
| | `cash_to_mcap` | Cash + short-term investments / market cap (biotech) | + | |
| Fundamental momentum | `droe` | Quarterly ROE minus ROE four quarters earlier | + | Hou, Mo, Xue & Zhang (2021) |
| | `sue` | (NI_q − NI_{q−4}) / std of last 8 seasonal changes | + | Foster, Olsen & Shevlin (1984); Novy-Marx (2015) |
| Low risk | `max_ret_21d` | Largest daily return over 21 sessions | − | Bali, Cakici & Whitelaw (2011) |
| | `idio_vol_60d` | Volatility of daily returns net of beta × QQQ | − | Ang, Hodrick, Xing & Zhang (2006) |

Notes: fundamentals become usable the day after the SEC filing date (not the period end). SUE uses the 10-Q/10-K
filing date, which lags the earnings press release, so its drift is weaker than in studies using announcement dates
(and post-earnings drift has largely disappeared in large caps since ~2006; Martineau 2022). Technical-analysis
indicators are deliberately excluded from the model; the user applies technical analysis separately.

## 3. Combination and construction

* **Normalization:** rank → normal scores per date; accounting ratios ranked *within* sector group, price signals
  across the universe (definitions differ by industry, but forced sector neutrality hurts long-only portfolios:
  Ehsani, Harvey & Li 2023).
* **Theme weights** ("literature" preset): momentum 30, quality 25, investment 20, value 15, fundamental momentum 5,
  low risk 5. Alternatives tested: equal themes, momentum-quality, quality-value, defensive, momentum-only, a
  factor-momentum tilt (±30%, Ehsani & Linnainmaa 2022) and IC weights shrunk 50% toward the literature weights.
  With ~15 years of data, shrunk/simple weights beat estimated ones (DeMiguel, Garlappi & Uppal 2009; Kozak, Nagel &
  Santosh 2020).
* **Portfolio:** 5–30 names, equal / score / inverse-vol weights, single-name cap max(8%, 1.5/N), sector-group cap
  45%, buy/hold buffer (buy inside the top N, hold until rank > N × buffer; Novy-Marx & Velikov 2016), minimum
  trade $150.
* **Costs:** $1 commission, 10 bps slippage + half the Abdi–Ranaldo (2017) spread estimate (capped at 200 bps),
  5 bps fees; execution at the next session's open.

## 4. Validation protocol

* Expanding walk-forward folds (36-month minimum training, 12-month tests, 1-month embargo, 126-day label purge).
* Honest estimate = nested walk-forward: in every fold the configuration is chosen using *training-window*
  performance only, then traded in the test window (with switching costs).
* Probability of backtest overfitting via CSCV (Bailey, Borwein, López de Prado & Zhu 2017) across all tested
  configurations, and the deflated Sharpe ratio (Bailey & López de Prado 2014).
* Benchmarks: equal-weight eligible universe (the honest hurdle), QQQ, SPY and sector ETFs.

## 5. Jev (LLM decision model)

LLM-based signals cannot be validated on historical data: models memorize and can reconstruct firms and dates even
from anonymized inputs (Lopez-Lira, Tang & Zhu 2025; Glasserman & Lin 2023; Sarkar & Vafa 2024). Historical Jev
backtests are therefore reported as an *upper bound*, and in production Jev runs in **shadow mode**: its scores are
recorded every month, and it only receives weight after ≥ 12 matured forward months show a significant (t ≥ 2) rank
IC beyond the quant score (`config/jev.yaml → production_policy`, `src/jev/forward.py`).

## 6. Survivorship

Delisted NASDAQ companies are recovered from FMP's full symbol list minus actively traded symbols, classified via
profiles, and priced from FMP's history (which retains delisted symbols). Residual gaps: tickers later reused by a
different company, and companies FMP no longer lists.

## References

Abdi & Ranaldo (2017, RFS); Ang, Hodrick, Xing & Zhang (2006, JF); Asness, Frazzini & Pedersen (2019, RAS); Asness,
Frazzini, Israel, Moskowitz & Pedersen (2018, JFE); Bailey & López de Prado (2014, JPM); Bailey, Borwein, López de
Prado & Zhu (2017, JCF); Bali, Cakici & Whitelaw (2011, JFE); Ball, Gerakos, Linnainmaa & Nikolaev (2016, JFE);
Blitz, Huij & Martens (2011, JEF); Blitz, Hanauer & Vidojevic (2020, IREF); Chan, Lakonishok & Sougiannis (2001, JF);
Chen & Velikov (2023, JFQA); Chen & Zimmermann (2022, CFR); Cooper, Gulen & Schill (2008, JF); DeMiguel, Garlappi &
Uppal (2009, RFS); Ehsani, Harvey & Li (2023, FAJ); Ehsani & Linnainmaa (2022, JF); George & Hwang (2004, JF);
Glasserman & Lin (2023); Hou, Mo, Xue & Zhang (2021, RoF); Hou, Xue & Zhang (2020, RFS); Israel & Moskowitz (2013,
JFE); Jegadeesh & Titman (1993, JF); Jensen, Kelly & Pedersen (2023, JF); Kozak, Nagel & Santosh (2020, JFE);
Lopez-Lira, Tang & Zhu (2025); Martineau (2022, CFR); McLean & Pontiff (2016, JF); Moskowitz & Grinblatt (1999, JF);
Novy-Marx (2012, JFE; 2013, JFE; 2015 NBER WP); Novy-Marx & Velikov (2016, RFS); Piotroski (2000, JAR); Pontiff &
Woodgate (2008, JF); Sarkar & Vafa (2024); Stambaugh, Yu & Yuan (2012, JFE).
