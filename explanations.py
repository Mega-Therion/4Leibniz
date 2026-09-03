"""Human-readable proof explanations in English and Latin.

This is a deterministic renderer over proof objects: it never invents a proof
step that is absent from the machine-readable result.
"""
from __future__ import annotations
from proof_engine import ProofSearchResult, ProofStep

_RULES = {
    "direct": {
        "en": "The conclusion is identical to a declared premise.",
        "la": "Conclusio eadem est ac praemissa declarata.",
    },
    "transitivity": {
        "en": "By transitivity, the first relation followed by the second yields the conclusion.",
        "la": "Per transitivitatem, prima relatio cum secunda coniuncta conclusionem efficit.",
    },
}

def explain_step(step: ProofStep, language: str = "en") -> str:
    if language not in ("en", "la"):
        raise ValueError("language must be 'en' or 'la'")
    rule = _RULES.get(step.rule, {"en": "A registered proof rule was applied.", "la": "Regula probationis descripta applicata est."})
    premise_text = "; ".join(step.from_premises)
    if language == "en":
        return f"{rule['en']} From: {premise_text}. Therefore: {step.conclusion}."
    return f"{rule['la']} Ex: {premise_text}. Ergo: {step.conclusion}."

def explain_result(result: ProofSearchResult) -> dict[str, list[str] | str]:
    steps = {lang: [explain_step(step, lang) for step in result.steps] for lang in ("en", "la")}
    if not result.steps:
        steps["en"].append(result.explanation)
        steps["la"].append("Nulla probatio sufficiens inventa est; obligatio manet aperta.")
    return steps
