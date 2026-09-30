"""T3r: automated membership review (Gate 2, user decision: answer gates with FMP data).

The label for each sampled current member comes from an INDEPENDENT source — the FMP company profile description,
which the classifier never sees — checked against a broader, documented validation vocabulary per subtheme. The
FMP description is used only as a validation label, never for backtest membership (CLAUDE.md §1).
"""
from __future__ import annotations

import pandas as pd

# Broader than the 10-K keywords on purpose: a validation label should confirm the business line, not re-use the
# classifier's exact phrases.
VALIDATION_TERMS: dict[str, list[str]] = {
    "industrial_automation": ["robot", "automation", "motion control", "machine vision", "factory", "warehouse",
                              "automated", "programmable"],
    "surgical_medical": ["surgical", "surgery", "robot", "minimally invasive"],
    "autonomous_drone": ["autonomous", "self-driving", "lidar", "drone", "unmanned", "driverless", "robotaxi"],
    "components": ["robot", "automation", "motion", "actuator", "sensor", "servo", "machine vision"],
    "biotech_all": ["biotech", "pharmaceutical", "therapeut", "drug", "clinical", "biolog", "therap", "medicine",
                    "vaccine", "diagnostic"],
    "oil_gas": ["oil", "natural gas", "petroleum", "crude", "pipeline", "midstream", "refin", "drilling", "gas"],
    "power_utilities": ["electric", "utility", "power", "generation", "energy"],
    "nuclear_uranium": ["uranium", "nuclear"],
    "grid_equipment": ["transmission", "transformer", "switchgear", "grid", "electrical", "power"],
    "renewables": ["solar", "wind", "renewable", "storage", "hydrogen", "fuel cell", "geothermal", "clean energy"],
}


def stratified_sample(members: pd.DataFrame, n_total: int = 120, seed: int = 7) -> pd.DataFrame:
    """At least ``n_total`` members, spread evenly over subthemes (all members of small subthemes)."""
    groups = list(members.groupby("subtheme"))
    per = max(1, n_total // max(1, len(groups)))
    parts = [g.sample(min(len(g), per), random_state=seed) for _, g in groups]
    out = pd.concat(parts)
    if len(out) < n_total:
        rest = members.drop(out.index)
        out = pd.concat([out, rest.sample(min(len(rest), n_total - len(out)), random_state=seed)])
    return out


def auto_label(subtheme: str, description: str | None, industry: str | None) -> tuple[str, str]:
    text = f"{description or ''} {industry or ''}".lower()
    if not text.strip():
        return "unknown", "no FMP description"
    terms = VALIDATION_TERMS.get(subtheme, [])
    hit = [t for t in terms if t in text]
    return ("correct", ", ".join(hit[:4])) if hit else ("wrong", "no validation term in FMP description")
