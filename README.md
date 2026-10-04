# 4Leibniz

[![Lean 4 Verification](https://github.com/Mega-Therion/4Leibniz/actions/workflows/verify.yml/badge.svg)](https://github.com/Mega-Therion/4Leibniz/actions/workflows/verify.yml)
[![Lean 4: zero sorry](https://img.shields.io/badge/Lean_4-zero--sorry-brightgreen.svg)](scripts/check_sorries.py)
[![Playground](https://img.shields.io/badge/site-four--leibniz.vercel.app-0070f3)](https://four-leibniz.vercel.app)

<p align="left">
  <a href="https://huggingface.co/datasets/ChyRho/4leibniz"><img src="https://img.shields.io/badge/Hugging%20Face-ChyRho%2F4leibniz-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="Hugging Face Dataset"></a>
  <a href="https://orcid.org/0009-0001-1303-7190"><img src="https://img.shields.io/badge/ORCID-0009--0001--1303--7190-A6CE39?style=flat-square&logo=orcid&logoColor=white" alt="ORCID"></a>
  <a href="https://res-nova-atlas.vercel.app"><img src="https://img.shields.io/badge/Research%20Atlas-res--nova-0070f3?style=flat-square&logo=safari&logoColor=white" alt="Res Nova Atlas"></a>
  <a href="https://www.linkedin.com/in/r-w-yett/"><img src="https://img.shields.io/badge/LinkedIn-R.W._Yett-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://x.com/_chyrho_"><img src="https://img.shields.io/badge/X-@__ChyRho__-000000?style=flat-square&logo=x&logoColor=white" alt="X"></a>
</p>

Formal relational information geometry and automated verification in Lean 4. Dedicated to Gottfried Wilhelm Leibniz.

The library is the source of truth. A declaration is `proved` only when the pinned Lean toolchain compiles it with no `sorry` and no non-standard axiom. `scripts/check_sorries.py` scans `Leibniz/` for the `sorry` tactic. The web and oracle apps display those artifacts. They do not decide that a theorem is proved.

One closed result, so it is not buried: `chiFloor = 1/√2` is a theorem, the equipartition bound of the vis viva (`Leibniz.VisViva.chiral_dominance_ge_floor`, `Leibniz.LexContinuitatis.chiFloor_is_dyadic_floor`). That is a statement about the formal dyad. It is not a physical measurement.

This repository does not have its own Zenodo record. A badge here used to point at Res-Nova's concept DOI. That DOI now opens on a physics correction, not on this library.

![4Leibniz Formal Claim Flow](docs/visuals/formal-claim-flow.svg)

## System Role

`4Leibniz` is the canonical mathematical and formal proof source of truth across the Chyren constellation. It provides formalizations of relational information geometry, epistemic logic, and classical philosophical foundations in Lean 4.

Two consumer applications live alongside the Lean library: [`apps/web`](apps/web/) (scholarly archive, formerly the `4leibniz-web` repository) and [`apps/oracle`](apps/oracle/) (interactive mobile guide, formerly `leibniz-oracle`), merged here on 2026-10-03. Both consume the versioned proof artifacts emitted by the Lean build. Neither maintains an independent theorem database or has authority to assert that a theorem is proved.

## What the kernel checks, and what it does not

The Lean kernel rejects an unfinished proof and a `sorry`. It does not notice a true-but-vacuous statement, and it does not notice a statement that is not the one you meant. The witness check that catches `∀ a : Nat, a < 0 → a = 5` lives in the [deductive sycophancy pilot](https://github.com/Mega-Therion/deductive-sycophancy-pilot), not in this library.

- **Zero `sorry` in `Leibniz/`.** `scripts/check_sorries.py` fails the build if the tactic appears.
- **No second theorem database.** `apps/web` and `apps/oracle` read the exported artifacts. They cannot mark a claim proved.
- **Receipts are build products.** A `proof-receipt.json` is only as current as the commit that wrote it. Do not treat a stale receipt hash as the present tree.

## Active Workstreams

- **`chiral-floor` — closed 2026-09-12.** Stated above. `chiFloor_lt_chiCeil` was promoted from an axiom to a theorem in that pass.
- **Issue #11 — closed.** `artifacts/v1/formal-claims.json` is the export `apps/web` and `apps/oracle` consume.
- **Issue #10 — open.** Consume RYTT through `integration/4leibniz_bridge.json`. Do not fork the grammar.

## Architecture

```
Lean Source (Leibniz/*.lean) ──► Pinned Lake Check ──► Export Generator ──► artifacts/v1/formal-claims.json
                                                           │
                                                           ├──► apps/web (scholarly display)
                                                           └──► apps/oracle (guided learning)
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

## How this was built

R.W. Yett directs the work. Much of the code and prose was written with AI coding assistants; those commits carry `Co-Authored-By` trailers. A Lean check shows that a declaration compiles. It does not grade the physics or the prose.
