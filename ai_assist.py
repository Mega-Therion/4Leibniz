"""Optional AI assistance for premise suggestion and lemma discovery.

The adapter is deliberately advisory: returned suggestions are unverified until
compiled and accepted by Lean. Without API credentials it provides a deterministic
fallback so local tests and offline development remain reproducible.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json, os
from typing import Any

@dataclass(frozen=True)
class Suggestion:
    kind: str
    statement: str
    rationale: str
    confidence: float
    status: str = "unverified"
    model: str = "deterministic-fallback"

def _fallback(claim_text: str) -> list[Suggestion]:
    return [Suggestion("premise", "transitivity is admissible for the declared relation",
                       "The current proof engine closes ordered chains through transitivity.", 0.62)]

def suggest(claim_text: str, model: str = "gpt-5-mini") -> dict[str, Any]:
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("OPENAI_API_BASE"):
        suggestions = _fallback(claim_text)
        return {"model": "deterministic-fallback", "verified": False,
                "suggestions": [asdict(s) for s in suggestions]}
    try:
        from openai import OpenAI
        client = OpenAI()
        schema = {"type": "object", "properties": {"suggestions": {"type": "array", "items": {
            "type": "object", "properties": {"kind": {"type": "string"}, "statement": {"type": "string"},
            "rationale": {"type": "string"}, "confidence": {"type": "number"}},
            "required": ["kind", "statement", "rationale", "confidence"], "additionalProperties": False}}},
            "required": ["suggestions"], "additionalProperties": False}
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "Suggest only Lean-checkable premises or lemmas. Never claim verification."},
                      {"role": "user", "content": claim_text}],
            response_format={"type": "json_schema", "json_schema": {"name": "premise_suggestions", "strict": True, "schema": schema}},
            max_completion_tokens=1200)
        data = json.loads(response.choices[0].message.content)
        suggestions = [Suggestion(item["kind"], item["statement"], item["rationale"], float(item["confidence"]), model=model)
                       for item in data["suggestions"]]
        return {"model": model, "verified": False, "suggestions": [asdict(s) for s in suggestions]}
    except Exception as exc:
        return {"model": "deterministic-fallback", "verified": False, "error": str(exc),
                "suggestions": [asdict(s) for s in _fallback(claim_text)]}
