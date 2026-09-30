"""T0: inventory of FMP sector/industry names and EDGAR SIC codes for NASDAQ + NYSE common stocks."""
from __future__ import annotations

import difflib
import logging
from pathlib import Path

import pandas as pd

from src.config import PROJECT_ROOT
from src.data.fmp import FmpClient
from src.data.http import ApiError
from src.data.sec import SecClient
from src.themes.config import ThemesConfig

log = logging.getLogger(__name__)
OUT_DIR = PROJECT_ROOT / "research" / "themes"
SCREENER_LIMIT = 10000


def fmp_industry_inventory(fmp: FmpClient, exchanges: list[str]) -> pd.DataFrame:
    """Active, non-ETF, non-fund common stocks per exchange with FMP sector/industry and country."""
    frames = []
    for ex in exchanges:
        rows = fmp.company_screener(exchange=ex, isEtf=False, isFund=False, isActivelyTrading=True)
        if len(rows) >= SCREENER_LIMIT:
            raise RuntimeError(f"screener hit the {SCREENER_LIMIT}-row limit for {ex}; results would be truncated")
        df = pd.DataFrame(rows)
        df["exchange_query"] = ex
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    return out[["symbol", "companyName", "exchangeShortName", "exchange_query", "country", "sector", "industry",
                "marketCap"]]


def industry_counts(inv: pd.DataFrame, known: list[str]) -> pd.DataFrame:
    """Firm counts per (sector, industry) and exchange; flags names missing from FMP's industry list."""
    inv = inv.assign(us=inv["country"].eq("US"))
    g = inv.groupby(["sector", "industry"])
    out = pd.DataFrame({
        "n_total": g.size(),
        "n_nasdaq": g.apply(lambda x: int((x["exchange_query"] == "NASDAQ").sum()), include_groups=False),
        "n_nyse": g.apply(lambda x: int((x["exchange_query"] == "NYSE").sum()), include_groups=False),
        "n_us_domiciled": g["us"].sum().astype(int),
    }).reset_index().sort_values(["sector", "industry"])
    out["in_available_industries"] = out["industry"].isin(set(known))
    return out


def sic_inventory(sec: SecClient, exchanges: list[str]) -> pd.DataFrame:
    """SIC code per CIK for SEC-listed tickers on the given exchanges (submissions endpoint, cached)."""
    wanted = {e.lower() for e in exchanges}
    tick = [r for r in sec.company_tickers_exchange() if str(r.get("exchange", "")).lower() in wanted]
    seen, rows = set(), []
    for i, r in enumerate(tick):
        cik = int(r["cik"])
        if cik in seen:
            continue
        seen.add(cik)
        try:
            sub = sec.submissions(cik)
        except ApiError as exc:
            log.debug("submissions %s: %s", cik, exc)
            continue
        sic = sub.get("sic")
        rows.append({"cik": cik, "ticker": r.get("ticker"), "exchange": r.get("exchange"),
                     "sic": int(sic) if str(sic or "").isdigit() else None,
                     "sic_description": sub.get("sicDescription"), "entity_type": sub.get("entityType")})
        if (i + 1) % 500 == 0:
            log.info("sic inventory: %d/%d", i + 1, len(tick))
    return pd.DataFrame(rows)


def sic_counts(sic_inv: pd.DataFrame) -> pd.DataFrame:
    df = sic_inv.dropna(subset=["sic"])
    g = df.groupby(["sic", "sic_description"])
    out = pd.DataFrame({"n_total": g.size(),
                        "n_nasdaq": g["exchange"].apply(lambda x: int((x.str.lower() == "nasdaq").sum())),
                        "n_nyse": g["exchange"].apply(lambda x: int((x.str.lower() == "nyse").sum()))})
    return out.reset_index().sort_values("sic")


def mapping_proposal(cfg: ThemesConfig, counts: pd.DataFrame) -> pd.DataFrame:
    """For every configured fmp_industries entry: exact match or the closest FMP industry names with counts."""
    names = counts.groupby("industry")["n_total"].sum()
    rows = []
    for theme, t in cfg.themes.items():
        for sub, s in t.subthemes.items():
            for name in s.fmp_industries:
                exact = name in names.index
                close = [] if exact else difflib.get_close_matches(name, list(names.index), n=3, cutoff=0.4)
                rows.append({"theme": theme, "subtheme": sub, "configured": name, "exact_match": exact,
                             "n_firms": int(names.get(name, 0)),
                             "closest": "; ".join(f"{c} ({int(names[c])})" for c in close)})
    return pd.DataFrame(rows)


def write_outputs(inv: pd.DataFrame, counts: pd.DataFrame, sics: pd.DataFrame, proposal: pd.DataFrame,
                  out_dir: Path = OUT_DIR) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {"fmp_industries": out_dir / "fmp_industries.csv", "sic_counts": out_dir / "sic_counts.csv",
             "mapping": out_dir / "fmp_industries_mapping.csv", "inventory": out_dir / "fmp_screener_inventory.csv"}
    counts.to_csv(paths["fmp_industries"], index=False)
    sics.to_csv(paths["sic_counts"], index=False)
    proposal.to_csv(paths["mapping"], index=False)
    inv.to_csv(paths["inventory"], index=False)
    return paths
