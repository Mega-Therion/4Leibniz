# Phase 10 Design: Cross-Shard Atomic Commit and State Synchronization

Phase 10 extends the ordered-log model across multiple shards. A transaction is prepared on every participant, committed only when all required participants are reachable and prepared, or aborted before state mutation when preparation fails. If a partition occurs during commit, the transaction enters `in_doubt` and requires an explicit coordinator decision during recovery.

## Transaction states

| State | Meaning |
|---|---|
| `prepared` | Every reachable participant has validated and durably recorded its intended writes. |
| `committed` | Every participant applied the writes and appended a commit record. |
| `aborted` | Preparation failed or a participant was unavailable before commit; prepared work was released. |
| `in_doubt` | The network partitioned after preparation and before all commit acknowledgements; recovery must apply one coordinator decision consistently. |

Each shard maintains its own `OrderedLog`, state map, and prepared transaction table. Transaction receipts hash the transaction id, phase, participant set, and resolved shards. This creates an auditable record but does not eliminate the need for a replicated coordinator or consensus-backed decision log in production.

## State synchronization

A shard snapshot contains the shard id, state, ordered-log snapshot, and state hash. A receiving shard validates the shard identity, replays the hash-linked log, checks the state hash, and only then replaces local state. Synchronization is therefore resumable and corruption-detecting rather than a blind map overwrite.

## Partition audit methodology

`partition_benchmark.py` evaluates connected, partially reachable, and fully unreachable participant sets. It records commit or abort latency, participant states, in-doubt recovery, and invariant checks. These are deterministic local simulations and should be complemented by multi-region tests, delayed messages, duplicate prepare messages, coordinator loss, and snapshot truncation before production deployment.
