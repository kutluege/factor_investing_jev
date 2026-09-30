"""Kenneth French data library: monthly FF3, FF5 (2x3), momentum and the risk-free rate (THEMES_SPEC §7.4, T5a).

Zip files are cached in ``data/external/french/``; a cached (or manually downloaded) zip younger than
``MAX_AGE_DAYS`` is used without network. Values are converted from percent to decimals and indexed by
calendar month-end. French factors are external benchmarks; they are prefixed ``ff_`` (``mimic_`` is reserved for
this project's own factor-mimicking portfolios, ``fmp_`` for FMP API fields).
"""
from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

from src.config import PROJECT_ROOT

BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
CACHE_DIR = PROJECT_ROOT / "data" / "external" / "french"
MAX_AGE_DAYS = 30
FILES = {
    "ff3": ("F-F_Research_Data_Factors_CSV.zip", {"Mkt-RF": "ff_mkt_rf", "SMB": "ff_smb", "HML": "ff_hml",
                                                   "RF": "ff_rf"}),
    "ff5": ("F-F_Research_Data_5_Factors_2x3_CSV.zip", {"SMB": "ff5_smb", "HML": "ff5_hml", "RMW": "ff_rmw",
                                                         "CMA": "ff_cma"}),
    "mom": ("F-F_Momentum_Factor_CSV.zip", {"Mom": "ff_mom"}),
}


def fetch_zip(name: str, cache_dir: Path = CACHE_DIR, max_age_days: int = MAX_AGE_DAYS,
              client: httpx.Client | None = None) -> bytes:
    path = cache_dir / name
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age_days * 86400:
        return path.read_bytes()
    try:
        c = client or httpx.Client(timeout=60, follow_redirects=True)
        r = c.get(BASE_URL + name)
        r.raise_for_status()
    except httpx.HTTPError:
        if path.exists():  # stale cache beats nothing; the coverage report shows the end month
            return path.read_bytes()
        raise RuntimeError(f"cannot download {name}; place it manually in {cache_dir}") from None
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_bytes(r.content)
    return r.content


def parse_monthly(raw: bytes) -> pd.DataFrame:
    """First (monthly) table of a French CSV: rows ``YYYYMM, v1, v2 ...`` until the first non-monthly line."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    text = z.read(z.namelist()[0]).decode("latin-1")
    header, rows = None, []
    for line in text.splitlines():
        cells = [c.strip() for c in line.split(",")]
        if header is None:
            if len(cells) > 1 and cells[0] == "" and all(cells[1:]):
                header = cells[1:]
            continue
        if len(cells[0]) == 6 and cells[0].isdigit():
            rows.append([cells[0]] + [float(x) for x in cells[1:len(header) + 1]])
        elif rows:
            break
    if header is None or not rows:
        raise ValueError("no monthly table found")
    df = pd.DataFrame(rows, columns=["yyyymm"] + header)
    df.index = pd.to_datetime(df.pop("yyyymm"), format="%Y%m") + pd.offsets.MonthEnd(0)
    df.index.name = "month_end"
    df = df.replace([-99.99, -999.0], np.nan)
    return df / 100.0


def french_monthly(cache_dir: Path = CACHE_DIR, client: httpx.Client | None = None) -> pd.DataFrame:
    """ff_mkt_rf, ff_smb, ff_hml, ff_rf, ff5_smb, ff5_hml, ff_rmw, ff_cma, ff_mom (decimals, month-end index)."""
    parts = []
    for name, cols in FILES.values():
        df = parse_monthly(fetch_zip(name, cache_dir, client=client))
        parts.append(df[list(cols)].rename(columns=cols))
    return pd.concat(parts, axis=1).sort_index()


def coverage(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({c: {"start": df[c].first_valid_index().date(), "end": df[c].last_valid_index().date(),
                             "months": int(df[c].notna().sum())} for c in df}).T


def to_month_end(returns: pd.Series) -> pd.Series:
    """Align a monthly return series stamped on any day of the month (e.g. last trading day) to month-end."""
    out = returns.copy()
    out.index = pd.DatetimeIndex(out.index) + pd.offsets.MonthEnd(0)
    if out.index.has_duplicates:
        raise ValueError("more than one observation per month")
    return out
