# Phase 12: Authenticated Replicas and Failover

## Purpose

Phase 12 extends the Phase 11 replicated coordinator with authenticated replica membership, signed decision votes, deterministic coordinator failover, and crash recovery. The trusted Lean kernel remains separate from this distributed systems layer: Python consensus code is operational infrastructure and does not create Lean theorems or convert research assumptions into kernel proofs.

## Recovery invariant

A coordinator snapshot contains the replica identifier, the hash-linked ordered-log snapshot, decisions already observed by the replica, and recorded equivocations. `ReplicatedDecisionLog.recover` reconstructs this state without inventing missing entries. `AckStore.recover` reconstructs idempotent participant acknowledgements. Recovery is therefore state restoration, not proof of the underlying transaction.

**English.** A restored state is accepted only because its serialized invariants are reconstructed and subsequent validation is still required.

**Latina.** Status restitutus admittitur tantum quia invariantia serializata iterum construuntur; verificatio ulterior semper requiritur.

## Authenticated membership

A membership record binds a replica identifier to an Ed25519 public key, a positive voting weight, an admission interval, and a revocation flag. A signed membership proposal is retained alongside the record. Votes are accepted only when the signer is active, the public key matches the admitted member, the proposal signature verifies, and the payload is explicitly typed as a decision vote.

**English.** Authentication establishes who signed a vote; it does not establish that the vote is correct.

**Latina.** Authenticatio ostendit quis suffragium signaverit; non ostendit suffragium verum esse.

## Failover rule

`elect_coordinator` selects the active replica with the greatest weight, breaking ties lexicographically by replica identifier. The epoch is carried into the returned receipt so callers can reject stale failover results. No active member yields an explicit negative result rather than an unsafe coordinator choice.

| Condition | Result |
|---|---|
| Active weighted member exists | Deterministic coordinator and eligible set |
| All members expired or revoked | Failover rejected with `no active replicas` |
| Signed vote has wrong key or stale member | Vote rejected |
| Duplicate acknowledgement with identical payload | Idempotent success |
| Duplicate acknowledgement with conflicting payload | Explicit conflict error |

## Test evidence

The Phase 12 suite covers snapshot restoration, acknowledgement restoration, signed votes, expiry rejection, deterministic failover, and all prior regression tests. The deterministic fuzz run uses seed `12` and 200 cases. It recovered 200/200 generated coordinator logs and reported zero harness failures. These tests are evidence about the implementation; they are not a replacement for a formal proof of distributed consensus under an asynchronous network.

## Boundary of trust

The Ed25519 implementation delegates cryptographic verification to the audited library. The membership and failover policy remain unverified Python code. Lean proofs remain the only kernel-checked claims in the formal layer, and no `sorry` or untrusted axiom is introduced by Phase 12.
