"""Jev adapter for Vercel AI Gateway's native evaluation API (POST {base_url}/evaluate).

All provider specifics live here so an API change is isolated to this module. Verified live (2026-09-25):
  request : {"model": "typesafe-ai/jev", "state": str, "questions": {id: {type, instructions, criteria?}}}
  boolean : answer {"type": "boolean", "probability": float}
  choice  : criteria {label: description}; answer {"type","choice","probabilities":{label: p},"confidence"}
  score   : criteria [ordered levels];     answer {"type","score","probabilities":{"0": p, ...},"confidence"}
  response: {"model", "answers", "usage": {"inputTokens","outputTokens"},
             "providerMetadata": {"typesafe": {"confidence": {...}}, "gateway": {"cost","marketCost","generationId",...}}}
The response does not expose an underlying Jev release version; callers record it as unknown.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal

import httpx
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from src.config import get_settings, load_config


class BooleanAnswer(BaseModel):
    type: Literal["boolean"]
    probability: float = Field(ge=0.0, le=1.0)


class ChoiceAnswer(BaseModel):
    type: Literal["choice"]
    choice: str
    probabilities: dict[str, float] | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class ScoreAnswer(BaseModel):
    type: Literal["score"]
    score: float = Field(ge=0.0)
    probabilities: dict[str, float] | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


Answer = Annotated[BooleanAnswer | ChoiceAnswer | ScoreAnswer, Field(discriminator="type")]
_answer_adapter = TypeAdapter(Answer)


class JevError(RuntimeError):
    def __init__(self, kind: str, message: str, status: int | None = None, retryable: bool = False):
        super().__init__(f"{kind}: {message}")
        self.kind = kind
        self.status = status
        self.retryable = retryable


@dataclass
class JevResult:
    model_returned: str | None
    answers: dict[str, dict]
    probabilities: dict[str, Any]
    confidence: dict[str, float]
    usage: dict[str, Any]
    cost_usd: float | None
    market_cost_usd: float | None
    provider_request_id: str | None
    latency_ms: float
    retry_count: int
    raw: dict = field(default_factory=dict)


def validate_questions(questions: dict[str, dict]) -> None:
    """Reject malformed question definitions before spending a request."""
    if not questions:
        raise JevError("invalid_questions", "at least one question is required")
    for qid, q in questions.items():
        t = q.get("type")
        if t not in ("boolean", "choice", "score"):
            raise JevError("invalid_questions", f"{qid}: unsupported type {t!r}")
        if not q.get("instructions"):
            raise JevError("invalid_questions", f"{qid}: instructions are required")
        if t == "choice" and not (isinstance(q.get("criteria"), dict) and q["criteria"]):
            raise JevError("invalid_questions", f"{qid}: choice needs criteria {{label: description}}")
        if t == "score" and not (isinstance(q.get("criteria"), list) and len(q["criteria"]) >= 2):
            raise JevError("invalid_questions", f"{qid}: score needs >= 2 ordered criteria levels")


def parse_response(body: dict, questions: dict[str, dict]) -> tuple[dict, dict, dict]:
    """Validate answers against the question schema; returns (answers, probabilities, confidence)."""
    if not isinstance(body, dict) or not isinstance(body.get("answers"), dict):
        raise JevError("invalid_response", "response has no 'answers' object")
    answers, probs, conf = {}, {}, {}
    meta_conf = (body.get("providerMetadata") or {}).get("typesafe", {}).get("confidence", {}) or {}
    for qid, q in questions.items():
        raw = body["answers"].get(qid)
        if raw is None:
            raise JevError("invalid_response", f"missing answer for question {qid!r}")
        try:
            ans = _answer_adapter.validate_python(raw)
        except ValidationError as exc:
            raise JevError("invalid_response", f"{qid}: {exc.errors()[:1]}") from exc
        if ans.type != q["type"]:
            raise JevError("invalid_response", f"{qid}: expected {q['type']}, got {ans.type}")
        if isinstance(ans, ScoreAnswer) and ans.score > len(q["criteria"]) - 1 + 1e-6:
            raise JevError("invalid_response", f"{qid}: score {ans.score} outside 0..{len(q['criteria']) - 1}")
        answers[qid] = ans.model_dump(exclude_none=True)
        if isinstance(ans, BooleanAnswer):
            probs[qid] = {"true": ans.probability, "false": round(1.0 - ans.probability, 6)}
        else:
            probs[qid] = ans.probabilities
            c = ans.confidence if ans.confidence is not None else meta_conf.get(qid)
            if c is not None:
                conf[qid] = float(c)
    return answers, probs, conf


def _to_float(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class JevClient:
    # Test hook: tests install an httpx.MockTransport here so no code path can reach the network.
    default_transport: httpx.AsyncBaseTransport | httpx.BaseTransport | None = None

    def __init__(self, api_key: str | None = None, model: str | None = None,
                 transport: httpx.AsyncBaseTransport | None = None, sync_transport: httpx.BaseTransport | None = None):
        s = get_settings()
        cfg = load_config("jev")
        self.cfg = cfg
        self.api_key = api_key if api_key is not None else s.ai_gateway_api_key
        self.model = model or s.jev_model
        self.url = cfg["base_url"].rstrip("/") + cfg["endpoint"]
        self.timeout = float(cfg["timeout_seconds"])
        self.max_retries = int(cfg["max_retries"])
        self._transport = transport or JevClient.default_transport
        self._sync_transport = sync_transport or JevClient.default_transport
        self.http_requests = 0
        if not self.api_key:
            raise JevError("unavailable", "AI_GATEWAY_API_KEY is not set; Jev is unavailable")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    @staticmethod
    def _classify(resp: httpx.Response) -> JevError:
        try:
            err = resp.json().get("error", {})
            msg, etype = err.get("message", resp.text[:200]), err.get("type", "error")
        except ValueError:
            msg, etype = resp.text[:200], "error"
        code = resp.status_code
        if code == 401:
            return JevError("authentication_error", msg, code)
        if code == 402:
            return JevError("quota_exceeded", msg, code)
        if code == 403:
            return JevError("forbidden", msg, code)
        if code == 400:
            return JevError(etype or "invalid_request", msg, code)
        if code in (408, 409, 425, 429, 500, 502, 503, 504, 529):
            return JevError(etype or "transient", msg, code, retryable=True)
        return JevError(etype, msg, code)

    @staticmethod
    def _delay(resp: httpx.Response | None, attempt: int) -> float:
        if resp is not None:
            ra = resp.headers.get("retry-after")
            if ra:
                try:
                    return min(120.0, float(ra))
                except ValueError:
                    pass
        return min(60.0, 1.5 * 2 ** attempt)

    def _result(self, body: dict, questions: dict, latency: float, retries: int) -> JevResult:
        answers, probs, conf = parse_response(body, questions)
        gw = (body.get("providerMetadata") or {}).get("gateway", {}) or {}
        return JevResult(model_returned=body.get("model"), answers=answers, probabilities=probs, confidence=conf,
                         usage=body.get("usage") or {}, cost_usd=_to_float(gw.get("cost")),
                         market_cost_usd=_to_float(gw.get("marketCost")),
                         provider_request_id=gw.get("generationId"), latency_ms=latency, retry_count=retries,
                         raw={"providerMetadata": {"gateway": {k: v for k, v in gw.items() if k != "routing"},
                                                   "routing_final_provider": (gw.get("routing") or {}).get("finalProvider")}})

    def evaluate(self, state: str, questions: dict[str, dict]) -> JevResult:
        validate_questions(questions)
        payload = {"model": self.model, "state": state, "questions": questions}
        attempt = 0
        with httpx.Client(timeout=self.timeout, transport=self._sync_transport) as client:
            while True:
                started = time.perf_counter()
                resp = None
                try:
                    self.http_requests += 1
                    resp = client.post(self.url, headers=self._headers(), json=payload)
                    latency = (time.perf_counter() - started) * 1000
                    if resp.status_code == 200:
                        return self._result(resp.json(), questions, latency, attempt)
                    err = self._classify(resp)
                except httpx.TimeoutException as exc:
                    err = JevError("timeout", str(exc), None, retryable=True)
                except httpx.TransportError as exc:
                    err = JevError("transport_error", str(exc), None, retryable=True)
                if not err.retryable or attempt >= self.max_retries:
                    err.retry_count = attempt  # type: ignore[attr-defined]
                    raise err
                time.sleep(self._delay(resp, attempt))
                attempt += 1

    async def aevaluate(self, client: httpx.AsyncClient, state: str, questions: dict[str, dict]) -> JevResult:
        validate_questions(questions)
        payload = {"model": self.model, "state": state, "questions": questions}
        attempt = 0
        while True:
            started = time.perf_counter()
            resp = None
            try:
                self.http_requests += 1
                resp = await client.post(self.url, headers=self._headers(), json=payload)
                latency = (time.perf_counter() - started) * 1000
                if resp.status_code == 200:
                    return self._result(resp.json(), questions, latency, attempt)
                err = self._classify(resp)
            except httpx.TimeoutException as exc:
                err = JevError("timeout", str(exc), None, retryable=True)
            except httpx.TransportError as exc:
                err = JevError("transport_error", str(exc), None, retryable=True)
            if not err.retryable or attempt >= self.max_retries:
                err.retry_count = attempt  # type: ignore[attr-defined]
                raise err
            await asyncio.sleep(self._delay(resp, attempt))
            attempt += 1

    def async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.timeout, transport=self._transport)
