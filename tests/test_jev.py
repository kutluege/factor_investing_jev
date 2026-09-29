import json

import pandas as pd
import pytest

from src.db.schema import connect
from src.jev.client import JevClient, JevError, parse_response, validate_questions
from src.jev.state import build_state, cache_key, state_hash
from src.jev.store import JevTask, decisions_frame, feature_set_id, generate, observability, question_set
from src.model.scoring import combine_final, jev_raw_score
from tests.synthetic import jev_transport

QS = question_set("candidate").questions


def valid_body():
    return {"model": "typesafe-ai/jev", "answers": {
        "momentum_persistence": {"type": "boolean", "probability": 0.8},
        "fundamental_deterioration": {"type": "boolean", "probability": 0.1},
        "value_trap": {"type": "boolean", "probability": 0.2},
        "relative_outperformance": {"type": "boolean", "probability": 0.7},
        "regime_fit": {"type": "score", "score": 3.1, "probabilities": {"0": 0, "1": 0, "2": 0.1, "3": 0.7, "4": 0.2},
                       "confidence": 0.6}},
        "usage": {"inputTokens": 400, "outputTokens": 30},
        "providerMetadata": {"gateway": {"cost": "0", "marketCost": "0.00002", "generationId": "gen_x"}}}


def test_question_schema_validation():
    validate_questions(QS)
    with pytest.raises(JevError):
        validate_questions({"x": {"type": "score", "instructions": "rate", "criteria": ["only one"]}})
    with pytest.raises(JevError):
        validate_questions({"x": {"type": "choice", "instructions": "pick", "criteria": []}})
    with pytest.raises(JevError):
        validate_questions({"x": {"type": "freeform", "instructions": "write a report"}})


def test_response_schema_validation():
    answers, probs, conf = parse_response(valid_body(), QS)
    assert answers["momentum_persistence"]["probability"] == 0.8  # stored as a probability, not a boolean
    assert probs["momentum_persistence"] == {"true": 0.8, "false": 0.2}
    assert conf["regime_fit"] == 0.6
    bad = valid_body()
    bad["answers"]["momentum_persistence"]["probability"] = 1.7
    with pytest.raises(JevError, match="invalid_response"):
        parse_response(bad, QS)
    missing = valid_body()
    del missing["answers"]["value_trap"]
    with pytest.raises(JevError, match="missing answer"):
        parse_response(missing, QS)
    wrong = valid_body()
    wrong["answers"]["regime_fit"]["score"] = 7.0  # outside 0..4
    with pytest.raises(JevError):
        parse_response(wrong, QS)


def test_jev_raw_score_is_deterministic_arithmetic():
    comps = {"momentum_persistence": 0.5, "fundamental_deterioration": -0.5}
    a = {"momentum_persistence": {"type": "boolean", "probability": 0.8},
         "fundamental_deterioration": {"type": "boolean", "probability": 0.2}}
    assert jev_raw_score(a, comps, QS) == pytest.approx((0.5 * 0.8 + 0.5 * 0.8) / 1.0)


def test_client_retries_rate_limit_then_succeeds():
    calls = []
    client = JevClient(sync_transport=jev_transport(calls, fail_first=2))
    res = client.evaluate("state", {"q": {"type": "boolean", "instructions": "x?"}})
    assert res.retry_count == 2 and len(calls) == 3
    assert res.provider_request_id == "gen_3"


def test_client_auth_error_not_retried():
    calls = []
    client = JevClient(sync_transport=jev_transport(calls, status=401))
    with pytest.raises(JevError) as ei:
        client.evaluate("state", {"q": {"type": "boolean", "instructions": "x?"}})
    assert ei.value.kind == "authentication_error" and len(calls) == 1


def test_missing_key_reports_unavailable(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "")
    with pytest.raises(JevError, match="unavailable"):
        JevClient()


def tasks(n):
    d = pd.Timestamp("2023-06-30")
    return [JevTask(f"S{i}", d, f"context: test\nfactor: {i}") for i in range(n)]


def test_cache_prevents_duplicate_requests_and_never_overwrites():
    con = connect(":memory:")
    calls = []
    client = JevClient(transport=jev_transport(calls))
    s1 = generate(con, tasks(6), client=client, max_concurrency=3)
    assert s1.completed == 6 and len(calls) == 6
    before = con.execute("SELECT decision_id, answers_payload, created_at FROM jev_decisions ORDER BY decision_id").fetchall()
    s2 = generate(con, tasks(6), client=client)
    assert s2.cached == 6 and s2.completed == 0 and len(calls) == 6  # no new HTTP requests
    after = con.execute("SELECT decision_id, answers_payload, created_at FROM jev_decisions ORDER BY decision_id").fetchall()
    assert before == after


def test_interrupted_generation_resumes_without_repeating():
    con = connect(":memory:")
    calls = []
    client = JevClient(transport=jev_transport(calls))
    first = generate(con, tasks(10), client=client, max_new=4)  # simulate interruption after 4
    assert first.completed == 4 and first.pending == 10
    second = generate(con, tasks(10), client=client)
    assert second.cached == 4 and second.completed == 6 and len(calls) == 10
    states = [c["state"] for c in calls]
    assert len(states) == len(set(states))  # nothing evaluated twice
    obs = observability(con)
    assert obs["cached_evaluations"] == 10 and obs["pending_evaluations"] == 0


def test_identical_states_share_one_request():
    con = connect(":memory:")
    calls = []
    d = pd.Timestamp("2023-06-30")
    same = [JevTask("A", d, "same state"), JevTask("B", d, "same state")]
    s = generate(con, same, client=JevClient(transport=jev_transport(calls)))
    assert s.unique_states == 1 and len(calls) == 1
    fsid = feature_set_id(JevClient().model, question_set("candidate"))
    assert set(decisions_frame(con, fsid)["symbol"]) == {"A", "B"}


def test_failed_evaluations_are_recorded_and_quant_continues():
    con = connect(":memory:")
    s = generate(con, tasks(3), client=JevClient(transport=jev_transport(status=401)))
    assert s.completed == 0 and s.errors.get("authentication_error", 0) >= 1
    rows = con.execute("SELECT status, error_type FROM jev_decisions").fetchall()
    assert rows and all(r[0] == "failed" for r in rows)
    # quant-only fallback: missing Jev contributes nothing, never a fabricated score
    quant = pd.Series({"A": 2.0, "B": 1.0, "C": 0.0})
    out = combine_final(quant, None, 0.3, quant.index)
    assert list(out.index) == ["A", "B", "C"] and (out["jev_z"] == 0).all()


def test_state_is_anonymized_and_hash_stable():
    row = pd.Series({"sector_group": "technology", "market_cap": 5e9, "adv20": 3e7, "ret_3m": 0.12,
                     "price_sma200": 0.08, "rsi14": 61.2})
    fam = pd.Series({"value": 0.3, "price_momentum": 0.9})
    s = build_state(row, fam, {"market_trend": "uptrend"}, include_identifiers=False,
                    identifiers={"symbol": "NVDA", "date": "2023-01-31"})
    assert "NVDA" not in s and "2023" not in s
    assert state_hash(s) == state_hash(s + "\n")
    assert cache_key("m", s, "v1", "q1") != cache_key("m", s, "v2", "q1")


def test_question_edits_create_new_version(monkeypatch):
    import src.config as cfgmod
    original = cfgmod._load_yaml

    def patched(name):
        c = json.loads(json.dumps(original(name)))
        if name == "jev":
            c["questions"]["value_trap"]["instructions"] += " (edited)"
        return c
    base = question_set("candidate").question_schema_version
    monkeypatch.setattr(cfgmod, "_load_yaml", patched)
    assert question_set("candidate").question_schema_version != base
