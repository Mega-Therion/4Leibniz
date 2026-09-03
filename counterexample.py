"""Bounded model search for transparent counterexample certificates.

This is a falsifier for the current relational fragment, not a complete theorem
prover. A witness is decisive for the searched integer model; no witness is
inconclusive.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, itertools, json, re
from proof_engine import _relation
from ucalculus import Claim

@dataclass(frozen=True)
class Counterexample:
    outcome: str
    model: str
    bound: int
    assignment: dict[str, int]
    satisfied_premises: tuple[str, ...]
    violated_conclusion: str
    fingerprint: str
    explanation: str

def _terms(text: str) -> set[str]:
    relation = _relation(text)
    if not relation: return set()
    return {x for x in (relation[0], relation[2]) if not re.fullmatch(r"-?\d+", x)}

def _value(term: str, assignment: dict[str, int]) -> int:
    return int(term) if re.fullmatch(r"-?\d+", term) else assignment[term]

def _holds(text: str, assignment: dict[str, int]) -> bool | None:
    rel = _relation(text)
    if not rel: return None
    left, op, right = rel
    a, b = _value(left, assignment), _value(right, assignment)
    return {">=": a >= b, "<=": a <= b, ">": a > b, "<": a < b, "=": a == b}[op]

def _certify(claim: Claim, bound: int, assignment: dict[str, int]) -> Counterexample | None:
    premises = tuple(p.text for p in claim.premises)
    if any(_holds(p, assignment) is not True for p in premises): return None
    conclusion = _holds(claim.conclusion, assignment)
    if conclusion is not False: return None
    payload = json.dumps({"bound": bound, "assignment": assignment, "claim": claim.conclusion}, sort_keys=True).encode()
    return Counterexample("refuted", "integers", bound, assignment, premises, claim.conclusion,
                          hashlib.sha256(payload).hexdigest(),
                          "All declared premises hold, but the conclusion fails in the bounded integer model.")

def find(claim: Claim, max_bound: int = 3) -> Counterexample:
    symbols = sorted(set().union(*(_terms(p.text) for p in claim.premises), _terms(claim.conclusion)))
    for bound in range(max_bound + 1):
        for values in itertools.product(range(-bound, bound + 1), repeat=len(symbols)):
            witness = _certify(claim, bound, dict(zip(symbols, values)))
            if witness: return witness
    return Counterexample("no-witness", "integers", max_bound, {}, tuple(p.text for p in claim.premises), claim.conclusion, "",
                          "No counterexample was found within the declared bounded integer model; the claim is not proved.")

def find_for_claim(claim: Claim, max_bound: int = 3) -> dict:
    return asdict(find(claim, max_bound))
