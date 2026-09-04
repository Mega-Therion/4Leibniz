# Phase 4 Design: Collaborative Calculus and Historical Evaluation

Phase 4 turns 4Leibniz into a collaborative proof network while preserving the central rule of the project: consensus may organize evidence, but only a checked proof may establish a formal theorem.

## Distributed proof collaboration

Each node stores a content-addressed proposal containing the universal-calculus source, compiled IR, Lean skeleton, proof receipt, assumptions, and parent revision fingerprints. Nodes exchange proposals and votes over a transport layer that can later be backed by WebSockets, libp2p, or a signed HTTP federation. A node must declare its identity, capabilities, and weight. The current reference implementation aggregates weighted votes with a configurable two-thirds default quorum.

Consensus is intentionally not truth. It is an epistemic coordination result. A proposal can be accepted as `derived` by a network while remaining unproven in Lean. Votes should be signed by production deployments, replay-protected with proposal hashes, and append-only in durable storage. The current Python layer provides deterministic aggregation and leaves transport and cryptographic identity as explicit deployment responsibilities.

| Layer | Responsibility | Authority |
|---|---|---|
| Claim source | Human-readable universal-calculus declaration | Author and provenance record |
| Search result | Candidate derivation and proof steps | Transparent search rules |
| Node vote | Local assessment and rationale | Declaring node |
| Consensus | Weighted quorum and dissent record | Network policy |
| Lean proof | Kernel-checked theorem | Lean kernel |

## AI-assisted premise and lemma discovery

`ai_assist.py` uses structured JSON output when credentials are present and falls back deterministically offline. Suggestions include a statement, rationale, confidence, model, and the fixed status `unverified`. The adapter instructs the model to suggest only Lean-checkable premises or lemmas, but the instruction is not a proof. A suggestion becomes trusted only after compilation and kernel checking.

The current default model is `gpt-5-mini`, selected from the live model catalog for cost-aware structured assistance. The API exposes this through `POST /api/ai/suggest`. Production deployments should store prompts and responses as provenance artifacts, redact sensitive inputs, rate-limit requests, and never permit model output to execute as code.

## Historical benchmark corpus

`benchmarks/leibniz_benchmark.json` contains eight compact, source-linked test cases based on sections of public-domain editions. The corpus includes both positive transitivity chains and open controls. It tests whether the engine distinguishes a mechanically closed relation from a historically meaningful but formally under-specified claim.

The corpus is not a benchmark of philosophical truth or historical interpretation. It is a regression suite for parsing, relation search, status preservation, and error classification. Full texts remain at their linked sources: the [Monadology text hosted by the Marxists Internet Archive](https://www.marxists.org/reference/subject/philosophy/works/ge/leibniz.htm), [Project Gutenberg's public-domain French edition](https://www.gutenberg.org/ebooks/17641), and the [Internet Archive collected works edition](https://archive.org/details/philosophicalwor00leibuoft).

Run the benchmark with:

```bash
python3 benchmarks/runner.py
```

The runner records per-case expected and actual outcomes, correctness, corpus version, and elapsed time. Future versions should add stratified splits for direct reuse, transitivity, conjunction, implication, contradiction, provenance-only edits, and adversarial paraphrases. A serious evaluation should separately report parse accuracy, proof closure rate, false-positive rate, counterexample discovery rate, and kernel acceptance rate.

## Phase 4 invariants

The project will enforce four invariants. First, model-generated suggestions cannot upgrade epistemic status. Second, a quorum cannot override a failed kernel check. Third, benchmark labels must identify whether they are logical controls, historical reconstructions, or open scholarly questions. Fourth, dissent is retained rather than averaged away, since disagreement is itself a valuable object in a calculus of reason.
