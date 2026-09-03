# Universal Calculus Intermediate Language

The Phase 1 declaration language is intentionally small. Its purpose is to make claims easy to author while retaining enough structure to compile into formal obligations and provenance records.

```text
claim Stability:
  given drive u >= dissipation gamma
  given gamma >= continuity_floor
  infer u >= continuity_floor
  source: Harmonia Praestabilita
  status: derived
  tag: dynamics, continuity, stability
```

The compiler in `ucalculus.py` performs four steps. It parses the declaration into a typed abstract syntax tree, normalizes premise text, validates the epistemic status, computes a SHA-256 fingerprint, and emits both a JSON intermediate representation and a Lean theorem skeleton. The generated Lean output is deliberately a proof obligation until a kernel proof is supplied; the compiler never upgrades an unproved inference to `proven`.

## Grammar

```text
claim      ::= "claim" identifier ":" clause*
clause     ::= "given" text
             | "infer" text
             | "source:" text
             | "status:" status
             | "tag:" identifier ("," identifier)*
status     ::= open | conjectured | axiomatic | derived | proven
identifier ::= letter (letter | digit | "_")*
```

The API endpoint `POST /api/compile` accepts `{ "text": "..." }` and returns the typed IR, fingerprint, proof obligations, and generated Lean text. This creates a stable bridge between approachable declarations and rigorous formalization.
