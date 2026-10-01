"""Keyword discovery for widening a theme (themes v2, robotics). Judged on classification, never on returns.

Terms (unigrams and bigrams) are ranked by the weighted log-odds ratio with an informative Dirichlet prior
(Monroe, Colaresi & Quinn 2008) between document frequencies in a positive corpus (Item 1 of confirmed members)
and a background corpus (Item 1 of other candidates). The output is a review table; a human-readable subset of
specific terms is then added to config/themes.yaml and validated with T3/T3r (accuracy >= 85%).
"""
from __future__ import annotations

import re
from collections import Counter

import numpy as np
import pandas as pd

_TOKEN = re.compile(r"[a-z][a-z\-]{2,}")
STOP = set("""the and for with that this from are our has have its their which such other these those into
than will also may can not but all any more most each been were was being including include includes
company companies products product customers customer business businesses market markets year years
services service based used use using within through over under per new one two three""".split())


def doc_terms(text: str) -> set[str]:
    toks = [t for t in _TOKEN.findall(text.lower()) if t not in STOP]
    grams = set(toks)
    grams.update(f"{a} {b}" for a, b in zip(toks, toks[1:], strict=False))
    return grams


def document_frequencies(texts: list[str]) -> Counter:
    df: Counter = Counter()
    for t in texts:
        df.update(doc_terms(t))
    return df


def log_odds(pos: Counter, bg: Counter, n_pos: int, n_bg: int, min_pos_df: int = 5, prior: float = 0.01) -> pd.DataFrame:
    """Weighted log-odds (z-score) of each term's document rate in the positive vs. background corpus."""
    terms = [t for t, c in pos.items() if c >= min_pos_df]
    rows = []
    for t in terms:
        a, b = pos.get(t, 0), bg.get(t, 0)
        alpha = prior * (a + b) + 0.5
        lo_pos = np.log((a + alpha) / (n_pos - a + alpha))
        lo_bg = np.log((b + alpha) / (n_bg - b + alpha))
        var = 1 / (a + alpha) + 1 / (b + alpha)
        rows.append({"term": t, "pos_df": a, "pos_rate": a / n_pos, "bg_df": b, "bg_rate": b / n_bg,
                     "delta": lo_pos - lo_bg, "z": (lo_pos - lo_bg) / np.sqrt(var)})
    # specificity first: rank by the log-odds difference among terms whose difference is statistically clear
    df = pd.DataFrame(rows)
    df["clear"] = df["z"] >= 2.0
    return df.sort_values(["clear", "delta"], ascending=False).reset_index(drop=True)


def precision_at(term: str, pos_texts: list[str], bg_texts: list[str], min_hits: int) -> dict:
    """How many positive and background documents a single term would admit at ``min_hits`` occurrences."""
    k = term.lower()
    pos = sum(t.lower().count(k) >= min_hits for t in pos_texts)
    bg = sum(t.lower().count(k) >= min_hits for t in bg_texts)
    return {"term": term, "pos_docs": pos, "bg_docs": bg, "precision": pos / (pos + bg) if pos + bg else np.nan}
