import pandas as pd

from src.themes.config import load_themes_config
from src.themes.membership import (
    choose_primary,
    evidence_sentences,
    keyword_hits,
    members_on,
    membership_rows,
    valid_from_session,
)

SESSIONS = pd.bdate_range("2019-01-01", "2026-12-31")
CFG = load_themes_config()
ROBO_STAGE_A = [{"theme": "robotics", "subtheme": "industrial_automation", "via": "industry", "needs_10k": True}]


def robot_text(n_hits: int) -> str:
    return ("We sell industrial robot arms. " * n_hits) + ("Other words about accounting. " * 400)


def filing(acc: str, acceptance: str, text: str) -> dict:
    return {"accession": acc, "acceptance": acceptance, "item1": text, "item1_words": len(text.split()),
            "status": "ok"}


def test_keyword_hits_substring_case_insensitive():
    hits, m = keyword_hits("Our ROBOTIC arms and robots; a Robot.", ["robot"])
    assert hits == 3 and m == {"robot": 3}


def test_valid_from_session_rule():
    # accepted 10:00 ET on Tue 2024-03-05 -> usable Wed 2024-03-06
    assert valid_from_session("2024-03-05T10:00:00.000Z", SESSIONS) == pd.Timestamp("2024-03-06")
    # accepted 17:30 ET -> news of Wed -> usable Thu
    assert valid_from_session("2024-03-05T17:30:00.000Z", SESSIONS) == pd.Timestamp("2024-03-07")
    # Friday after the close -> Tuesday
    assert valid_from_session("2024-03-08T16:05:00.000Z", SESSIONS) == pd.Timestamp("2024-03-12")


def test_membership_threshold_and_validity_chain():
    fl = [filing("a1", "2021-02-10T09:00:00.000Z", robot_text(6)),
          filing("a2", "2022-02-10T09:00:00.000Z", robot_text(2)),     # below min_hits=5 -> not a member
          filing("a3", "2023-02-10T09:00:00.000Z", robot_text(9))]
    rows = membership_rows("ROBO", "0000000001", ROBO_STAGE_A, fl, CFG, SESSIONS)
    assert [r["filing_accession"] for r in rows] == ["a1", "a3"]
    assert rows[0]["valid_to"] == pd.Timestamp("2022-02-11").date()  # ends when the next 10-K becomes valid
    assert rows[1]["method"] == "keywords" and rows[1]["hits"] == 9


def test_membership_expires_after_18_months_without_new_10k():
    rows = membership_rows("ROBO", "1", ROBO_STAGE_A, [filing("a1", "2021-02-10T09:00:00.000Z", robot_text(6))],
                           CFG, SESSIONS)
    assert rows[0]["valid_to"] == (pd.Timestamp("2021-02-11") + pd.DateOffset(months=18)).date()
    m = pd.DataFrame(rows)
    assert len(members_on(m, pd.Timestamp("2022-06-30"))) == 1
    assert len(members_on(m, pd.Timestamp("2022-09-30"))) == 0


def test_later_filing_never_changes_past_membership():
    """Leakage test: adding a future 10-K must not alter membership on any earlier date."""
    base = [filing("a1", "2021-02-10T09:00:00.000Z", robot_text(6))]
    later = base + [filing("a2", "2023-06-01T09:00:00.000Z", robot_text(0))]
    r1 = pd.DataFrame(membership_rows("ROBO", "1", ROBO_STAGE_A, base, CFG, SESSIONS))
    r2 = pd.DataFrame(membership_rows("ROBO", "1", ROBO_STAGE_A, later, CFG, SESSIONS))
    for d in pd.date_range("2021-01-31", "2023-05-31", freq="ME"):
        assert len(members_on(r1, d)) == len(members_on(r2, d)), d
    # but a filing becoming valid earlier than the 18-month cap does end the window at its own valid date
    earlier_next = base + [filing("a2", "2022-02-10T09:00:00.000Z", robot_text(0))]
    r3 = pd.DataFrame(membership_rows("ROBO", "1", ROBO_STAGE_A, earlier_next, CFG, SESSIONS))
    assert len(members_on(r3, pd.Timestamp("2022-01-31"))) == 1
    assert len(members_on(r3, pd.Timestamp("2022-03-31"))) == 0


def test_primary_subtheme_and_theme_tie_priority():
    q = [{"theme": "robotics", "subtheme": "components", "density": 5.0, "method": "keywords"},
         {"theme": "robotics", "subtheme": "industrial_automation", "density": 9.0, "method": "keywords"}]
    assert choose_primary(q, CFG)["subtheme"] == "industrial_automation"
    q.append({"theme": "energy", "subtheme": "grid_equipment", "density": 50.0, "method": "keywords"})
    assert choose_primary(q, CFG)["theme"] == "energy"  # theme_tie_priority: biotech > energy > robotics
    q2 = [{"theme": "energy", "subtheme": "power_utilities", "density": 0.0, "method": "stage_a"},
          {"theme": "energy", "subtheme": "renewables", "density": 3.0, "method": "keywords"}]
    assert choose_primary(q2, CFG)["subtheme"] == "renewables"  # keyword evidence beats stage-A-only


def test_stage_a_only_subtheme_needs_no_keywords_but_needs_a_10k():
    sa = [{"theme": "biotech", "subtheme": "biotech_all", "via": "industry", "needs_10k": False}]
    rows = membership_rows("BIO", "2", sa, [filing("b1", "2022-03-01T08:00:00.000Z", "")], CFG, SESSIONS)
    assert rows and rows[0]["method"] == "stage_a"
    assert membership_rows("BIO", "2", sa, [], CFG, SESSIONS) == []


def test_evidence_sentences():
    ev = evidence_sentences("First line. We build industrial robots for cars. Unrelated.", ["industrial robot"])
    assert ev == ["We build industrial robots for cars."]
