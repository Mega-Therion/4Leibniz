# Phase 11 Design: Replicated Decisions and Byzantine Cross-Shard Validation

Phase 11 adds a replicated coordinator decision layer above the Phase 10 shard transaction model. A decision is accepted only when at least `2f + 1` verified replicas agree for a configured fault tolerance `f`, and all matching votes refer to the same transaction digest.

## Decision validation

`replicated_coordinator.py` records replica decisions in hash-linked logs and rejects local equivocation. `validate_decision` retains invalid signatures, digest mismatches, and conflicting votes as explicit conflict evidence. A commit or abort decision is accepted only from the matching verified quorum; a governance or coordinator caller must not infer a decision from a simple majority that does not satisfy the configured fault bound.

## Durable participant acknowledgements

Each participant acknowledgement includes a shard id, transaction id, phase, transaction digest, sequence, timestamp, and idempotency key. `AckStore` makes retries safe: the same key and identical acknowledgement are idempotent, while a conflicting acknowledgement under the same key is rejected. The store exposes transaction-scoped recovery evidence and a serializable snapshot for durable storage.

| Evidence | Meaning |
|---|---|
| `prepared` | Participant durably recorded the write intent. |
| `committed` | Participant applied the transaction and recorded a commit. |
| `aborted` | Participant released prepared work without applying state. |
| `conflict` | A participant or replica presented incompatible evidence for the same key or digest. |

## Limits

This is a deterministic, testable protocol reference. It does not yet provide a network transport, authenticated replica membership, durable cloud storage, or a complete Byzantine agreement algorithm. Production rollout requires signed replica votes, admitted-replica rotation, a replicated decision log with snapshot recovery, durable acknowledgement storage, coordinator failover, and adversarial network testing.
