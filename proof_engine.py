"""Small, deterministic proof-search and semantic-patch layer.

The engine is intentionally transparent: it searches only declared premises and
records the exact rule and premise chain used. It is an orchestration layer, not
a replacement for Lean's kernel.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import re
from ucalculus import Claim, Premise, compile_claim, parse

@dataclass(frozen=True)
class ProofStep:
    rule: str
    conclusion: str
    from_premises: tuple[str, ...]

@dataclass(frozen=True)
class ProofSearchResult:
    outcome: str
    claim: str
    steps: tuple[ProofStep, ...] = ()
    remaining_obligations: tuple[str, ...] = ()
    explanation: str = ""

def _relation(text: str):
    match = re.fullmatch(r"(.+?)\s*(>=|<=|=|>|<)\s*(.+)", text)
    return tuple(part.strip() for part in match.groups()) if match else None

def search(claim: Claim) -> ProofSearchResult:
    target = _relation(claim.conclusion)
    if target is None:
        return ProofSearchResult("under-specified", claim.conclusion,
            explanation="The proof search engine currently supports ordered and equality relations.")
    left, op, right = target
    facts = [_relation(p.text) for p in claim.premises]
    for premise, fact in zip(claim.premises, facts):
        if fact == target:
            return ProofSearchResult("proved", claim.conclusion,
                (ProofStep("direct", claim.conclusion, (premise.text,)),),
                explanation="The conclusion is directly declared as a premise.")
    # Monotone transitivity: a >= b and b >= c implies a >= c.
    if op in (">=", ">"):
        edges = [(f[0], f[2], p.text) for p, f in zip(claim.premises, facts) if f and f[1] in (">=", ">")]
        for a, b, p1 in edges:
            for b2, c, p2 in edges:
                if b == b2 and a == left and c == right:
                    return ProofSearchResult("proved", claim.conclusion,
                        (ProofStep("transitivity", claim.conclusion, (p1, p2)),),
                        explanation="The conclusion follows by transitivity of the declared order.")
    return ProofSearchResult("open", claim.conclusion,
        remaining_obligations=(claim.conclusion,),
        explanation="No supported proof rule closed the conclusion from the declared premises.")

@dataclass(frozen=True)
class SemanticPatch:
    id: str
    description: str
    operation: str
    target: str
    replacement: str = ""

    def apply(self, claim: Claim) -> Claim:
        if self.operation == "rename":
            return Claim(self.replacement if claim.name == self.target else claim.name,
                         claim.premises, claim.conclusion, claim.source, claim.status, claim.tags)
        if self.operation == "replace_conclusion":
            if claim.conclusion != self.target:
                raise ValueError("patch target does not match claim conclusion")
            return Claim(claim.name, claim.premises, self.replacement, claim.source, claim.status, claim.tags)
        if self.operation == "add_premise":
            return Claim(claim.name, claim.premises + (Premise(self.replacement, self.replacement),),
                         claim.conclusion, claim.source, claim.status, claim.tags)
        raise ValueError(f"unsupported semantic patch operation: {self.operation}")

def search_text(text: str) -> dict:
    claim = parse(text)
    result = search(claim)
    ir = compile_claim(claim)
    return {"claim": asdict(claim), "ir": asdict(ir), "search": asdict(result)}
