# Phase 3 Design: Counterexamples and Semantic Divergence

Phase 3 will extend proof search from “no rule closed the claim” to a structured diagnosis of why the claim failed. It will distinguish a false claim, an under-specified claim, and a claim that diverges semantically from a competing formulation.

## Counterexample pipeline

1. **Normalize the claim.** Parse relational expressions into a typed predicate form and retain the source fingerprint.
2. **Select a model domain.** Start with finite integers and rationals for order/equality claims; later add finite sets, Boolean algebras, matrices, and bounded real intervals.
3. **Search bounded assignments.** Enumerate assignments to symbols appearing in the premises and conclusion, recording the smallest domain and assignment that satisfies the premises while violating the conclusion.
4. **Minimize the witness.** Remove irrelevant variables and premises, then return a minimal counterexample certificate.
5. **Classify the failure.** Return `refuted` when a witness exists, `under-specified` when premises are satisfiable but no conclusion follows, and `unsupported` when the language is outside the current model theory.

Every witness will contain the model, variable assignment, satisfied premises, violated conclusion, search bound, and deterministic fingerprint.

## Semantic divergence tracking

A divergence record compares two claims after normalization rather than comparing their raw strings. It records the changed symbols, relation operators, premises added or removed, source/status changes, and whether the difference changes the proof result. The system will expose a directed graph of revisions:

```text
claim@hash₁ --[conclusion_changed]--> claim@hash₂
claim@hash₂ --[premise_added]-------> claim@hash₃
```

Divergence classes will be `lexical` (formatting only), `structural` (AST changed), `logical` (proof obligations changed), `epistemic` (status or assumptions changed), and `provenance` (source changed). A failed proof can then say not only “open,” but “open because revision 2 removed the bridge premise that made revision 1 transitive.”

## API and UI contract

Phase 3 will add `POST /api/counterexample`, `POST /api/divergence`, and `GET /api/divergence/<fingerprint>`. The dashboard will show a minimized witness beside failed proof output and overlay divergence edges on the argument graph. No numerical witness will ever be promoted to a Lean proof; it is evidence for refutation or model exploration only.

## Soundness boundary

The bounded search engine is a falsifier, not a complete theorem prover. A found witness is decisive for the declared model, while failure to find a witness is inconclusive. Lean remains the authority for formal proof, and all Phase 3 results will carry the model class and search bound explicitly.
