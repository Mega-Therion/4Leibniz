# Open-Source Integration Matrix

4Leibniz deliberately composes established projects instead of reimplementing infrastructure.

| Capability | Integrated project | Role | License / provenance |
|---|---|---|---|
| Mathematical foundation | [Mathlib](https://github.com/leanprover-community/mathlib4) | Real analysis, topology, matrices, and measure-theory vocabulary | Community-maintained Lean library |
| API documentation | [doc-gen4](https://github.com/leanprover/doc-gen4) | Generates searchable Lean API documentation | Apache-2.0 |
| Independent checking path | [lean4lean](https://github.com/digama0/lean4lean) | Optional external kernel-checking lane for release verification | Apache-2.0 |
| Real-time transport | [websockets](https://github.com/python-websockets/websockets) | Streams `lake build` events to the dashboard | BSD-3-Clause |
| CI documentation publishing | [docgen-action](https://github.com/leanprover-community/docgen-action) | Publishes API docs through GitHub Actions / Pages | Open-source GitHub Action |

The repository pins source and toolchain state in `proof-receipt.json`, keeps research claims visible through `OpenProblems.lean`, and separates proven kernel results from explicit axiomatic interfaces.

## Verification policy

The normal push and pull-request lane uses Lean's trusted kernel and rejects `sorry` placeholders. The `workflow_dispatch` lane adds [Lean-for-Lean](https://github.com/digama0/lean4lean), a mostly pure-Lean external checker, so maintainers can independently inspect the compiled module graph before a release. This lane is intentionally manual because it builds a second compiler/checker stack and is materially more expensive than ordinary CI.
