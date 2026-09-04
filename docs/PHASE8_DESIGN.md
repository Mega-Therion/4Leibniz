# Phase 8 Design: Multi-Prover Verification and Automated Governance

Phase 8 treats proof validation as a distributed evidence problem. Independent provers submit signed reports over an artifact digest; the network aggregates matching evidence only when the configured quorum and verifier-diversity requirements are met.

## Multi-prover contract

`multiprover.py` retains every report and dissenting artifact. A report may claim a status, but the aggregate remains `open` unless the required number of reports agree on one digest and at least two reports identify independent-kernel verification when that policy is enabled. Aggregation coordinates evidence; it never substitutes for Lean or an independently reviewed proof verifier.

## Governance contract

`governance.py` evaluates proposals using weighted support, a configurable quorum, veto authority, and an explicit timelock. Every decision receives a deterministic receipt. Governance may change network configuration or admission policy, but it may not promote an unverified mathematical proposition to `proven` merely by vote.

## Load and fault injection

`loadtest.py` connects concurrent clients to the live WebSocket room and records readiness, accepted proposal broadcasts, rejections, timeouts, and connection errors. The fault profiles are deliberately bounded: malformed JSON, stale timestamps, duplicate nonces, and equivocation-shaped traffic. Results are JSON artifacts under `benchmarks/artifacts/phase8/` and are not presented as a capacity guarantee; they are point-in-time observations from one network path and one small client population.

| Profile | Purpose |
|---|---|
| `none` | Valid Ed25519 envelopes and normal broadcast path. |
| `malformed` | Invalid JSON rejection. |
| `stale` | Freshness-window enforcement. |
| `duplicate` | Invalid/replayed envelope path. |
| `equivocation` | Conflicting or malformed proposal behavior. |

Production readiness still requires rate limits, authenticated peer admission, persistent audit logs, backpressure, bounded room membership, key rotation, and a real consensus state machine rather than simple broadcast.
