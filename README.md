# 4Leibniz

<p align="left">
  <a href="https://huggingface.co/datasets/ChyRho/4leibniz"><img src="https://img.shields.io/badge/Hugging%20Face-ChyRho%2F4leibniz-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="Hugging Face Dataset"></a>
  <a href="https://orcid.org/0009-0001-1303-7190"><img src="https://img.shields.io/badge/ORCID-0009--0001--1303--7190-A6CE39?style=flat-square&logo=orcid&logoColor=white" alt="ORCID"></a>
  <a href="https://resnova-hub-f4ucvy3e.manus.space"><img src="https://img.shields.io/badge/Research%20Atlas-resnova--hub-0070f3?style=flat-square&logo=safari&logoColor=white" alt="Research Atlas"></a>
  <a href="https://www.linkedin.com/in/r-w-yett-152085293/"><img src="https://img.shields.io/badge/LinkedIn-R.W._Yett-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://x.com/_chyrho_"><img src="https://img.shields.io/badge/X-@__ChyRho__-000000?style=flat-square&logo=x&logoColor=white" alt="X"></a>
</p>

Formal Relational Information Geometry & Automated Verification in Lean 4 — Dedicated to Gottfried Wilhelm Leibniz.

![4Leibniz Formal Claim Flow](docs/visuals/formal-claim-flow.svg)

## System Role

`4Leibniz` is the canonical mathematical and formal proof source of truth across the Chyren constellation. It provides formalizations of relational information geometry, epistemic logic, and classical philosophical foundations in Lean 4.

Downstream consumer applications—including `4leibniz-web` (scholarly archive) and `leibniz-oracle` (interactive mobile guide)—consume versioned proof artifacts emitted by this repository. Neither consumer maintains an independent theorem database or has authority to assert that a theorem is proved.

## Active Workstreams

- **Open problem `chiral-floor` — CLOSED 2026-09-12**: the continuity floor `chiFloor = 1/√2` is derived from first principles as the equipartition bound of the vis viva (`Leibniz.VisViva.chiral_dominance_ge_floor`, `Leibniz.LexContinuitatis.chiFloor_is_dyadic_floor`): the stronger member of any dyad carries at least half the total living force, with equality exactly at equipartition. `chiFloor_lt_chiCeil` was promoted from a bare axiom to a theorem in the same pass.

- **Issue #11**: Publish a proof-grounded formal-claim export for `4leibniz-web` and `leibniz-oracle` (`artifacts/v1/formal-claims.json`).
- **Issue #10**: Consume RYTT via `integration/4leibniz_bridge.json` — symbolic notation and interchange layer without forking the grammar.

## Architecture

```
Lean Source (Leibniz/*.lean) ──► Pinned Lake Check ──► Export Generator ──► artifacts/v1/formal-claims.json
                                                           │
                                                           ├──► 4leibniz-web (scholarly display)
                                                           └──► leibniz-oracle (guided learning)
```

## Epistemic Standard

- A claim receives status `proved` **only** when the pinned Lean toolchain compiles the declaration without unresolved `sorry` placeholders or non-standard axioms.
- In-progress, conditional, or philosophical claims remain labeled as `conditional`, `informal`, or `open_problem`.
- Explanation and retrieval in web/mobile interfaces never elevate an unverified claim to `proved`.

## Toolchain & Verification

- **Lean Toolchain**: Pinned in `lean-toolchain`.
- **Manifest**: `lake-manifest.json` tracks locked package dependencies.
- **Lakefile**: `lakefile.lean` defines the core `Leibniz` library target.
- **Test Suite**: Multi-phase verification covering phases 2–12, security hardening, consensus, and RYTT bridge (`tests/`).

```bash
# Build formal library
lake build

# Run Python verification suite
pytest tests/
```
