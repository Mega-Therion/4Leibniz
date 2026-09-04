# Phase 5 Design: Signed Collaboration and Private Premises

Phase 5 extends the collaborative calculus from trusted transport to verifiable peer messages and privacy-preserving evidence boundaries.

## Peer-to-peer cryptographic signing

Each proof proposal is serialized canonically and signed with an Ed25519 private key. The signed envelope contains the node identifier, public key, proposal payload, signature, and SHA-256 digest. A receiving node verifies both the signature and the digest before admitting a vote. Proposal hashes remain content-addressed, so the same logical artifact has the same identity across nodes.

The current implementation is in `security.py` and is exposed by `/api/security/sign` and `/api/security/verify`. Key storage, rotation, revocation, transport encryption, replay protection, and identity binding remain deployment responsibilities. The convenience keypair endpoint is intentionally marked for local setup only; production nodes should use an external secret manager or hardware-backed key.

## Zero-knowledge verification boundary

Private premises require more than hashing. A commitment hides a statement only when the nonce is secret, but it does not prove that the hidden statement satisfies a predicate. Therefore Phase 5 exposes `PrivatePremiseCommitment` as an explicit boundary object with `verified: false`, rather than claiming that a hash is a zero-knowledge proof.

The next secure layer should define a circuit or Sigma protocol for a narrow predicate, publish its constraint system, implement proof generation and verification, and test soundness, completeness, zero-knowledge, nonce reuse, and transcript binding. Candidate integrations may include a reviewed SNARK/STARK library, but no external proof system should be accepted without a stable serialization format and independent verification tests.

## Benchmark methodology

The performance harness measures the eight-case `leibniz-philosophical-benchmark-v1` corpus using three available local backends: universal-calculus proof search, bounded integer model search, and the Lean kernel build. Z3 and CVC5 are recorded as unavailable because they are not installed in the benchmark environment; their timings are not fabricated. Measurements are wall-clock signals for this environment, not portable performance guarantees.

The report contains both a logarithmic backend comparison and a per-case comparison. The full machine-readable result is `benchmarks/artifacts/performance.json`; the charts are `performance.png` and `per_case_performance.png`; the human-readable report is `PERFORMANCE_REPORT.md`. Re-run all artifacts with `export PATH="$HOME/.elan/bin:$PATH" && python3 benchmarks/report.py`.

| Backend | Role | Verification status |
|---|---|---|
| Universal-calculus search | Transparent declared-rule orchestration | Available |
| Bounded integer model search | Counterexample/falsification search | Available |
| Lean kernel build | Formal compilation and checking | Available |
| Z3 / CVC5 | Future SMT comparison | Not installed; no timing imputed |

The central rule remains: signatures establish message origin and integrity, consensus records distributed agreement, commitments establish hiding boundaries, and Lean establishes formal proof. None of these layers substitutes for another.
