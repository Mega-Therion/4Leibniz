# Phase 6 Design: Private Premises and Live Consensus

Phase 6 adds a concrete Circom/snarkjs circuit boundary and a deployment plan for a live dashboard, REPL, and stateful consensus service.

## zk-SNARK pipeline

`circuits/private_premise.circom` proves a bounded lower-bound predicate without exposing the secret value. The public input is `public_floor`; the private witness contains `secret_value` and an 8-bit decomposition of the nonnegative difference. The circuit enforces bitness and the relation `secret_value = public_floor + delta`.

| Stage | Artifact | Trust requirement |
|---|---|---|
| Authoring | `.circom` source | Code review and constraint audit |
| Compilation | R1CS, WASM, symbols | Reproducible compiler version |
| Setup | Powers of Tau and proving key | Ceremony provenance and toxic-waste hygiene |
| Proving | Witness and proof | Secret witness remains local |
| Verification | Verification key and public signals | Independent verifier and key pinning |
| Publication | Proof receipt | Content hash, circuit hash, and verifier version |

The repository includes a `circuits/package.json` workflow for `compile`, Groth16 setup, contribution, verification, and verifier-key export. The current sandbox does not include `circom` or `snarkjs`, so no proof is claimed until those tools are installed and the ceremony artifacts are pinned. `zk_pipeline.py` reports this status honestly.

A commitment or a circuit source is not a proof. Phase 6 must not mark private premises as verified until a generated proof has been checked by an independent verifier against a pinned verification key. Future work should add circuit-level tests for range soundness, malformed witnesses, public-input binding, replay protection, and trusted-setup provenance.

## Live cloud deployment

The recommended topology is a split deployment. The static dashboard and REPL shell can be deployed from the GitHub production branch to Vercel. A Cloudflare Worker fronts the stateful P2P channel, while a Durable Object owns a consensus room and its WebSocket sessions. Durable Objects are appropriate for long-lived WebSocket coordination and lightweight serialized room state [1]. The existing Python Flask service remains a proof/search backend and should be deployed behind an authenticated internal route or migrated to a managed Python runtime.

| Component | Suggested target | State model |
|---|---|---|
| Dashboard | Vercel Git project | Static assets |
| P2P consensus room | Cloudflare Worker + Durable Object | Serialized room state and WebSockets |
| Lean/proof service | Persistent Python service or managed container | Ephemeral jobs plus durable artifacts |
| Proof artifacts | Object storage | Content-addressed immutable files |
| Secrets | Platform secret manager | Never exposed to browser |

The current repository contains deployment configuration scaffolding but does not silently publish anything. Deployment requires selecting the target project, configuring environment variables, and confirming the external change. A live P2P service must also add authentication, rate limits, replay protection, peer admission, signed envelopes, room authorization, durable event logs, and health monitoring before public exposure.

## References

[1]: https://developers.cloudflare.com/durable-objects/best-practices/websockets/ "Cloudflare Durable Objects WebSocket best practices"
[2]: https://github.com/iden3/circom "iden3 Circom repository"
[3]: https://github.com/iden3/snarkjs "iden3 snarkjs repository"
