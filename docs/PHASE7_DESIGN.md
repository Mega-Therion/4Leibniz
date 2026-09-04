# Phase 7 Design: Byzantine Validation and Proof-Carrying Consensus

Phase 7 makes peer collaboration adversarially aware. A node is not trusted merely because it participates: proposals must be signed, fresh, non-replayed, and accepted by a quorum that tolerates a declared number of faulty nodes.

## BFT decision contract

`bft.py` implements a deterministic weighted decision layer. For fault tolerance `f`, the classical minimum participant count is `3f + 1`; the default decision also requires a two-thirds weighted quorum. Conflicting votes from one node in the same proposal round are classified as equivocation and withhold acceptance. Incentives are transparent accounting deltas, not a currency or an economic security guarantee: aligned votes receive a small reward after an accepted decision, equivocation receives a penalty, and honest dissent remains visible without punishment.

The protocol is intentionally separate from Lean. Consensus establishes distributed agreement about an artifact; it does not establish mathematical truth. A node’s incentive must never depend on suppressing dissent or upgrading a claim beyond its kernel-backed status.

## Signed envelopes and replay protection

`security.py` now signs a canonical envelope containing `node_id`, payload, timestamp, and nonce. Verification checks the Ed25519 signature and content digest. `ReplayGuard` rejects stale timestamps and previously accepted `(node_id, nonce)` pairs. The Cloudflare Durable Object applies the same checks at the edge, stores nonce keys with a bounded expiration, rejects malformed or stale messages, and broadcasts only verified envelopes.

Production deployment should add peer admission, key rotation and revocation, room authorization, durable audit events, rate limiting, clock policy, and protection against storage exhaustion. A public Worker should not use a convenience key-generation endpoint as its identity authority.

## Groth16 verification

The circuit in `circuits/private_premise.circom` proves a bounded private lower-bound relation. The local workflow now compiles the circuit with `circom2`, generates an initial Groth16 proving key from an 8-power ceremony artifact, generates a witness and proof for `secret_value = 7` and `public_floor = 5`, exports a verification key, and verifies the proof with snarkjs. The Flask endpoint `/api/zk/verify` invokes the same verifier against the local verification key or an explicitly supplied key.

The demo uses an initial proving key for reproducibility; it is not a substitute for a production multi-party ceremony. The ceremony artifact provenance and hash must be pinned, and the final system should use a reviewed contribution chain, independently verified keys, circuit audits, public-input binding tests, malformed-witness tests, and proof-replay policy. The API reports verification only when snarkjs returns success.

| Layer | Evidence | Status |
|---|---|---|
| Circuit source | Circom constraints | Implemented |
| R1CS/WASM compilation | circom2 output | Implemented locally |
| Groth16 setup | Initial zkey from pinned demo ptau | Implemented locally; ceremony trust limited |
| Proof generation | Witness and proof JSON | Implemented locally |
| Proof verification | snarkjs and Flask endpoint | Implemented locally |
| Production privacy guarantee | Audited ceremony and circuit | Not claimed |
