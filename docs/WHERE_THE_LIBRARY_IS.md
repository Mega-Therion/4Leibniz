# Where the library is

The Lean library is `Leibniz/` and `Leibniz.lean`. A declaration is proved only when the pinned toolchain compiles it with no `sorry` and no non-standard axiom. `apps/web` and `apps/oracle` read the build artifacts. They do not decide a proof.

The repository root also contains a distributed-systems prototype: `bft.py`, `consensus.py`, `zk_pipeline.py`, `zk_verify.py`, `replica_membership.py`, `replicated_coordinator.py`. Those files are not the Lean library. This note does not move them.

`LICENSE` in the tree is the MIT license text. On 2026-10-25 the GitHub license API returned SPDX `NOASSERTION` (`key: other`) for this repository. This note does not change `LICENSE`.
