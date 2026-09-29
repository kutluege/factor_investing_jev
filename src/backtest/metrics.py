"""Performance metrics from daily equity curves."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TRADING_DAYS = 252


def _clean(x) -> float | None:
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) or np.isinf(f) else f


def drawdown_series(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1.0


def drawdown_durations(equity: pd.Series) -> list[int]:
    """Lengths (sessions) of each underwater episode."""
    dd = drawdown_series(equity) < 0
    out, run = [], 0
    for under in dd:
        if under:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def rolling_return(equity: pd.Series, sessions: int) -> pd.Series:
    return (equity / equity.shift(sessions) - 1.0).dropna()


def performance(equity: pd.Series, bench: dict[str, pd.Series] | None = None, trades: pd.DataFrame | None = None,
                risk_free: float = 0.0) -> dict:
    """Standard metric set. ``equity``: daily values (first value = starting capital)."""
    equity = equity.dropna()
    if len(equity) < 3:
        return {"error": "insufficient data"}
    rets = equity.pct_change().dropna()
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    total = equity.iloc[-1] / equity.iloc[0] - 1.0
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1.0 if equity.iloc[-1] > 0 else -1.0
    vol = rets.std() * np.sqrt(TRADING_DAYS)
    downside = rets[rets < 0].std() * np.sqrt(TRADING_DAYS)
    dd = drawdown_series(equity)
    mdd = dd.min()
    under = dd[dd < 0]
    durations = drawdown_durations(equity)
    monthly = equity.resample("ME").last().pct_change().dropna()
    m: dict = {
        "initial_capital": _clean(equity.iloc[0]), "ending_equity": _clean(equity.iloc[-1]),
        "total_return": _clean(total), "cagr": _clean(cagr), "annual_volatility": _clean(vol),
        "max_drawdown": _clean(mdd), "median_drawdown": _clean(under.median()) if len(under) else 0.0,
        "max_drawdown_duration_days": int(max(durations)) if durations else 0,
        "sharpe": _clean((rets.mean() * TRADING_DAYS - risk_free) / vol) if vol > 0 else None,
        "sortino": _clean((rets.mean() * TRADING_DAYS - risk_free) / downside) if downside and downside > 0 else None,
        "calmar": _clean(cagr / abs(mdd)) if mdd < 0 else None,
        "monthly_win_rate": _clean((monthly > 0).mean()) if len(monthly) else None,
        "best_month": _clean(monthly.max()) if len(monthly) else None,
        "worst_month": _clean(monthly.min()) if len(monthly) else None,
        "months": int(len(monthly)),
        "years": _clean(years),
    }
    for label, n in (("3m", 63), ("6m", 126), ("12m", 252)):
        rr = rolling_return(equity, n)
        m[f"rolling_{label}_median"] = _clean(rr.median()) if len(rr) else None
        m[f"rolling_{label}_worst"] = _clean(rr.min()) if len(rr) else None
    if trades is not None and not trades.empty:
        avg_eq = equity.mean()
        traded = trades["gross"].abs().sum()
        m["turnover_annual"] = _clean(traded / 2.0 / avg_eq / years)
        m["transactions"] = int(len(trades))
        m["total_costs"] = _clean((trades["commission"] + trades["transaction_cost"] + trades["slippage_cost"]).sum())
    else:
        m["turnover_annual"], m["transactions"], m["total_costs"] = 0.0, 0, 0.0
    for name, b in (bench or {}).items():
        b = b.reindex(equity.index).ffill().dropna()
        if len(b) < 20:
            continue
        br = b.pct_change().dropna()
        j = pd.concat([rets, br], axis=1, join="inner").dropna()
        if len(j) < 20:
            continue
        cov = np.cov(j.iloc[:, 0], j.iloc[:, 1])
        beta = cov[0, 1] / cov[1, 1] if cov[1, 1] > 0 else np.nan
        active = j.iloc[:, 0] - j.iloc[:, 1]
        te = active.std() * np.sqrt(TRADING_DAYS)
        alpha = (j.iloc[:, 0].mean() - beta * j.iloc[:, 1].mean()) * TRADING_DAYS
        b_total = b.iloc[-1] / b.iloc[0] - 1
        b_cagr = (b.iloc[-1] / b.iloc[0]) ** (1 / years) - 1
        m[f"bench_{name}"] = {
            "total_return": _clean(b_total), "cagr": _clean(b_cagr), "max_drawdown": _clean(drawdown_series(b).min()),
            "beta": _clean(beta), "alpha_annual": _clean(alpha), "tracking_error": _clean(te),
            "information_ratio": _clean(active.mean() * TRADING_DAYS / te) if te > 0 else None,
            "excess_cagr": _clean(cagr - b_cagr),
        }
    return m


def segment(equity: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    """Equity sub-series re-based at the last value on/before ``start`` (so the first return is included)."""
    before = equity[equity.index <= start]
    seg = equity[(equity.index > start) & (equity.index <= end)]
    if before.empty or seg.empty:
        return pd.Series(dtype=float)
    return pd.concat([before.iloc[-1:], seg])


def sector_exposure(holdings: pd.DataFrame) -> pd.DataFrame:
    h = holdings[holdings["symbol"] != "__CASH__"]
    if h.empty:
        return pd.DataFrame()
    tot = holdings.groupby("rebalance_date")["value"].sum()
    g = h.groupby(["rebalance_date", "sector_group"])["value"].sum().unstack(fill_value=0.0)
    return g.div(tot, axis=0)


def information_coefficients(scores: pd.DataFrame, labels: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    """Per-date Pearson IC and Spearman rank IC of score columns vs forward returns."""
    j = scores.merge(labels, on=["rebalance_date", "symbol"], how="inner")
    rows = []
    for d, g in j.groupby("rebalance_date"):
        for c in score_cols:
            gg = g[[c, "fwd_return"]].dropna()
            if len(gg) < 20:
                continue
            rows.append({"rebalance_date": d, "score": c, "n": len(gg),
                         "ic": float(np.corrcoef(gg[c], gg["fwd_return"])[0, 1]),
                         "rank_ic": float(spearmanr(gg[c], gg["fwd_return"]).statistic)})
    return pd.DataFrame(rows)


def quantile_spreads(scores: pd.DataFrame, labels: pd.DataFrame, col: str, q: int = 5) -> pd.DataFrame:
    """Mean forward return by score quintile per date, plus top-minus-bottom spread."""
    j = scores.merge(labels, on=["rebalance_date", "symbol"], how="inner").dropna(subset=[col, "fwd_return"])
    rows = []
    for d, g in j.groupby("rebalance_date"):
        if len(g) < q * 5:
            continue
        b = pd.qcut(g[col].rank(method="first"), q, labels=False)
        means = g.groupby(b)["fwd_return"].mean()
        rows.append({"rebalance_date": d, **{f"q{int(k) + 1}": float(v) for k, v in means.items()},
                     "spread": float(means.iloc[-1] - means.iloc[0])})
    return pd.DataFrame(rows)
