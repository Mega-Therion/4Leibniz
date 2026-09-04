# Phase 9 Design: Durable Ordered Logs and Automated Peer Admission

Phase 9 gives the P2P edge a durable state model instead of treating the WebSocket room as a broadcast-only transport.

## Ordered log invariants

Each accepted proposal becomes a `LogEntry` with a monotonically increasing sequence, proposal identifier, payload, previous-entry hash, and entry hash. Recovery rejects gaps, replayed sequence numbers, broken predecessor links, or altered payloads. A snapshot records the last sequence and head hash so a Durable Object can resume from storage and detect corruption.

The local `durable_log.py` model is a reference implementation for the Cloudflare Durable Object. It does not by itself provide Byzantine agreement: the caller must append only after the Phase 7 signature, admission, quorum, and governance checks have succeeded.

## Peer admission lifecycle

A peer submits an Ed25519-signed admission proposal whose payload contains `kind = peer_admission` and an identity-bound `node_id`. Admission produces a signed-key record containing capabilities, voting weight, issue time, expiry time, and an auditable receipt. Expired or revoked records are inactive. Governance should be the only path that revokes an admitted peer, with a timelocked record and an append-only log entry.

| State | Meaning |
|---|---|
| `proposed` | A signed admission request exists but has not passed policy. |
| `admitted` | The request passed signature and policy checks and has a bounded lease. |
| `expired` | The lease ended; the peer must re-admit. |
| `revoked` | Governance or security response disabled the identity. |

## Worker integration plan

The Durable Object should store `log:<sequence>` entries, `log:head`, peer records, nonce records, and periodic snapshots. WebSocket messages must include the expected sequence or be rejected; clients should resynchronize from a snapshot plus suffix after reconnect. Admission should happen on an authenticated control path, not implicitly on first WebSocket connection.

Production hardening still requires a real replicated consensus protocol, durable audit export, snapshot signing, key rotation and revocation, bounded storage, backpressure, authorization, and recovery tests across multiple regions. A hash chain provides tamper evidence and order; it does not independently prove that the ordering decision was Byzantine-safe.
