"""Semantic divergence tracking for revisions of universal-calculus claims."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Iterable
from ucalculus import Claim, compile_claim

@dataclass(frozen=True)
class Divergence:
    before: str
    after: str
    classes: tuple[str, ...]
    changed_fields: tuple[str, ...]
    logical_impact: str
    explanation: str

def _fingerprint(claim: Claim) -> str:
    return compile_claim(claim).fingerprint

def compare(before: Claim, after: Claim) -> Divergence:
    changed: list[str] = []
    classes: list[str] = []
    if before.name != after.name:
        changed.append("name"); classes.append("lexical")
    if before.premises != after.premises:
        changed.append("premises"); classes.append("logical")
    if before.conclusion != after.conclusion:
        changed.append("conclusion"); classes.append("logical")
    if before.status != after.status:
        changed.append("status"); classes.append("epistemic")
    if before.source != after.source:
        changed.append("source"); classes.append("provenance")
    if before.tags != after.tags:
        changed.append("tags"); classes.append("structural")
    if not changed:
        classes.append("lexical")
    logical = "proof obligations changed" if any(x in changed for x in ("premises", "conclusion")) else "proof obligations preserved"
    return Divergence(_fingerprint(before), _fingerprint(after), tuple(dict.fromkeys(classes)), tuple(changed), logical,
                      "Revision changes: " + (", ".join(changed) if changed else "none"))

def compare_text(before: str, after: str) -> dict:
    return asdict(compare(__import__('ucalculus').parse(before), __import__('ucalculus').parse(after)))
