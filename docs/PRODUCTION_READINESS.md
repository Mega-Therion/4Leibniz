# Production readiness

Source: an independent "4Leibniz Production-Grade Release Assessment and
Full-Stack Blueprint" (assessment date 2026-09-07, examined at commit
`344d2cb`). This document tracks its findings against what has actually been
implemented, so the gap between "assessed" and "fixed" stays visible instead
of getting lost in commit history.

**Verdict, unchanged by this pass:** 4Leibniz is a substantial research
prototype with a credible formal core, not a hardened multi-user product. The
correct release posture is public research preview / developer preview, not
"production-grade full stack," until the phases below close. See the
[README's release-posture section](../README.md#release-posture-research-preview-not-a-hardened-public-service)
for the operator-facing summary.

## What this pass closed: Phase 1, "secure the existing runtime"

The assessment's Phase 1 exit gate is: *no unauthenticated mutation or
process-spawning endpoint; security tests pass in a clean environment.* That
gate is met for the existing Flask monolith. It is a stopgap access-control
layer appropriate to a research preview, not the identity-aware gateway with
RBAC/ABAC that Phase 3 describes — see `api.py`'s `require_auth` docstring.

| ID | Finding | Disposition |
|---|---|---|
| B-01 | No auth on the Flask API | **Fixed (scoped).** Every mutation/dangerous route requires `Authorization: Bearer $LEIBNIZ_API_TOKEN`; unset token = every such route refuses all requests (secure by default). Read-only/stateless routes (claim compile/prove/repl, counterexample, divergence, metadata, dashboards) stay public — that is the "public read-only claim exploration" the blueprint itself describes as acceptable. |
| B-02 | Unauthenticated `/api/build` remote code execution | **Fixed (scoped).** Disabled by default (404) regardless of auth; opt-in via `LEIBNIZ_ENABLE_BUILD_ENDPOINT=1` for local dev, and still requires the bearer token when enabled. The real fix — queued, sandboxed jobs with resource limits and artifact isolation — is Phase 3 (job service), not done here. |
| B-03 | `/api/security/keypair` returns a private key over the network | **Fixed (scoped).** Disabled by default (404); `scripts/generate_keypair.py` generates a key locally and writes it to a 0600 file instead of printing it. The endpoint itself still exists behind an explicit opt-in flag for local dev convenience — a production deployment should never set that flag. |
| B-04 | ZK verifier shells out to `npx` using request material written into a shared path | **Fixed (scoped).** `zk_verify.py` now validates proof/public-signal shape and size before touching disk, writes to a fresh `tempfile.TemporaryDirectory()` per request instead of the shared `circuits/build/`, and calls `npx --no` so a request can never trigger an on-demand package install. Still a subprocess wrapper, not the isolated verifier worker Phase 4 describes. |
| B-05 | In-memory security/coordination state | **Partially fixed.** `ReplayGuard` accepts an optional `db_path` and persists seen nonces in SQLite when `LEIBNIZ_STATE_DB` is set, so the replay window survives a process restart on one node. `AckStore` and the rest of the coordination state are unchanged — they need the durable, multi-node transactional store Phase 3 describes (Postgres + object storage), not a single-file workaround. |
| B-12 | No systematic input/resource limits | **Partially fixed.** `MAX_CONTENT_LENGTH` caps every request body at 1 MiB (413 on overflow); the ZK route additionally bounds proof/public-signal size and shape. Recursion/complexity budgets and per-route quotas are not implemented. |

Negative tests for all of the above live in `tests/test_security_hardening.py`
(unauthorized access, wrong token, no-token-configured, disabled-by-default
routes, malformed ZK input, replay persistence, oversized body). The existing
49→60-plus-test suite continues to pass unchanged; `tests/conftest.py` is new
and only exists to give tests a token to authenticate with.

CI (`machine` job in `.github/workflows/verify.yml`) now runs the **full**
`tests/` suite instead of two files, and installs the ZK circuit tooling
(`npm ci` in `circuits/`) so the previously-uncovered Groth16 API test
actually executes instead of silently never running. A non-blocking
`pip-audit` step was added as a first security-scan signal (B-13).

## What this pass did not attempt, and why

The assessment's Phases 2 through 6 describe splitting this Flask monolith
into a typed frontend, an API gateway, a claim service, an async job/worker
plane, a Postgres + object-storage evidence ledger, an isolated ZK
verification service, a durably-stated consensus/governance service,
containerized reproducible builds, chaos-tested fault recovery, and a full
operations layer (telemetry, SLOs, incident response, staged rollout). That
is real, multi-week infrastructure work requiring services (Postgres, object
storage, a container/job orchestrator) that do not exist in this repository
or this environment. Claiming to have "done" that in one pass would be
fabrication. What follows is the phase list, kept as a live checklist rather
than restated prose, so future work has a fixed target instead of
re-deriving scope from the PDF each time.

- [x] **Phase 0 — Freeze the research contract.** Partially reflected in the
  existing epistemic-status vocabulary (`proven`/`derived`/`conjectured`/
  `open` in `api.py`'s `MODULES`/`THEOREMS`) and in `security.py`'s own
  docstrings distinguishing signature validity from proof truth. Not yet a
  formal, versioned claim/evidence schema with promotion rules enforced in
  code.
- [x] **Phase 1 — Secure the existing runtime.** Done, scoped as above.
- [ ] **Phase 2 — Reproducible build evidence.** CI now runs the full test
  suite (this pass); still missing: containerized Lean/ZK build images,
  lockable Python dependencies, a required independent-kernel lane on release
  tags, and a signed CI-generated proof receipt (the committed
  `proof-receipt.json` predates this audit and must not be read as current).
- [ ] **Phase 3 — Split the full-stack product.** Typed frontend, gateway,
  claim/job/evidence services, Postgres + object storage, tenant isolation.
  Not started; this is the multi-week rewrite referenced above.
- [ ] **Phase 4 — Harden the ZK and distributed lanes.** Reviewed circuit
  provenance, a real ceremony or transparent setup, chaos/fault-injection
  testing for consensus. Not started.
- [ ] **Phase 5 — Operate the service.** Telemetry, SLOs, backups, key
  rotation, incident response. Not started.
- [ ] **Phase 6 — Public release.** Staged rollout (research preview →
  verified preview → production), SBOM, external security review. This
  document and the README's release-posture note are the current substitute
  for a formal staged-release process.

## Trust-model vocabulary

Carried over from the assessment verbatim, because it is the single most
important thing for anyone extending the API to internalize: **"proven" is
never a synonym for "parsed," "accepted by consensus," "signature-valid,"
"ZK-verified," or "Lean-elaborated."**

| State | Means | Does not mean |
|---|---|---|
| `parsed` | Conforms to the DSL grammar | The statement is true |
| `derived` | A deterministic engine found a rule-based derivation | A Lean kernel checked it |
| `kernel_checked` | The pinned Lean kernel accepted the artifact | Physical assumptions are justified |
| `multi_verified` | Independent verifiers agree on a matching digest | The verifiers are organizationally independent |
| `signature_valid` | A key signed canonical content and freshness/replay rules passed | The signed content is mathematically true |
| `zk_verified` | A verifier accepted a proof under a specific circuit and key | The circuit expresses the intended real-world claim |
| `governance_accepted` | Policy quorum accepted an operational proposal | The proposition is proven |
| `open` | Evidence is incomplete or a counterexample path remains | The claim is false |

`governance.py`'s existing behavior already respects the last row's
implication (governance evaluates operational proposals, never promotes a
mathematical claim); that boundary should stay enforced in the domain model
as the product grows, not just in this document.
