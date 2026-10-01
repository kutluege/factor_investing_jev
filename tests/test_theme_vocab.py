"""Keyword discovery: log-odds ranks theme-specific terms above generic ones."""
from src.themes.vocab import document_frequencies, log_odds, precision_at

POS = ["We build collaborative robots and machine vision for factory automation. Our robots weld."] * 12
BG = ["We sell insurance and banking services to retail customers in many markets."] * 30 + \
     ["We manufacture valves for factory pipelines."] * 5


def test_log_odds_ranks_specific_terms_first():
    lo = log_odds(document_frequencies(POS), document_frequencies(BG), len(POS), len(BG))
    order = lo["term"].tolist()
    assert order.index("robots") < order.index("factory")
    assert "valves" not in order and bool(lo.set_index("term").loc["robots", "clear"])
    assert lo.set_index("term").loc["robots", "delta"] > lo.set_index("term").loc["factory", "delta"]


def test_precision_at_counts_documents():
    p = precision_at("robots", POS, BG, 2)
    assert p["pos_docs"] == 12 and p["bg_docs"] == 0 and p["precision"] == 1.0
