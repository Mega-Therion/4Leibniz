# V-KERNEL implementation status (hardened 2026-10-09)

Honest status of each capability, per the V-KERNEL v3 brief's four grades. This is the
Python implementation at `4Leibniz/scripts/vkernel/`, protocol **vkernel/0.2**. It is not
the Rust 7-crate rewrite the brief sketches; it is the existing, running signed-service
verifier hardened on the three axes RY selected: sandbox, canonical hashing, statement-match.

## Implemented and integration-tested (real Lean, this host)
- **Signed-service attest → no-Lean verify.** `attest.py` builds a Lean project, audits
  named theorems (elaborated-statement hash, definition-closure hash, `collectAxioms` set)
  and signs a record; `verify.py` checks it with Python + PyNaCl only. End-to-end on the
  fixture and on Res-Nova's 47-theorem formal project (`MuStdFoundations` … `TensorSpeed`,
  7 checker modules): build 0, probe 0, all axioms within `standard-3`, all 7 rechecks clean.
- **Sandboxed build + separate recheck.** `sandbox.py` runs the untrusted `lake build`,
  the probe, and each `leanchecker` recheck under bubblewrap: read-only root, writable
  project only, **network unshared (verified unreachable)**, dedicated temp HOME + tmpfs,
  CPU/file-size rlimits, wall-clock timeout with `--die-with-parent`, bounded output. The
  recheck runs as a **separate** sandboxed process from the build. Isolation level achieved
  is recorded in the record (`build_isolation`, `recheck_isolation`, `network_blocked`);
  if bwrap were absent it would record `unshare`/`none` rather than pretend.
- **Strict canonical hashing + domain separation.** `vkcanon.py` replaces the old
  sorted-json `canon()`: rejects duplicate keys, floats, NaN/Inf, oversize and over-deep
  input; `payload_digest` is a domain-separated, length-framed SHA-256 over the canonical
  bytes; the Ed25519 signature is over a framed `signing_message`, and the consumer
  **recomputes** the digest rather than trusting the supplied one. Self-test: 12/12.
- **Statement-match comparator (structural identity).** With `--challenge <manifest>`,
  attest compares each theorem's elaborated-statement hash to a trusted challenge and sets
  `statement_match` (`structural-match` / `mismatch`, `comparison_relation:
  structural-hash-identity`). The consumer re-derives the match from the authenticated
  payload + trusted challenge, not from the record's own flag.
- **Sabotage suite (`test_vkernel.sh`): 19/19.** Each guard is broken on a copy and a check
  fails — including the three new guards: build+recheck sandboxed with network blocked,
  duplicate-key record rejected by the strict parser, forged `payload_digest` rejected,
  wrong-statement challenge rejected by the consumer, attest rejecting on statement mismatch.
- **Backward compatibility.** `verify.py` dispatches on `payload.protocol`: 0.2 uses the
  hardened scheme; legacy **0.1** records still verify under the old sorted-json scheme, so
  nothing committed is stranded. `--min-protocol vkernel/0.2` lets a consumer refuse legacy.

## Experimentally supported / scoped
- **Non-vacuity** stays `not-established` always (the vacuity screen is a sidecar, never a
  pass). The v3 "established with a bound witness obligation" is not built; the conservative
  default is honest, not complete.
- **Statement-match is structural-hash identity only**, not definitional equality under a
  trusted environment. The brief explicitly permits this scoped artifact-identity scheme.
- **Independent checker** is `leanchecker` — the toolchain's own kernel re-run, **not** a
  second independent kernel. Recorded as such; never called dual-kernel.

## Deferred (interfaces/claims not built)
- Rust 7-crate workspace; JSON Schemas; Merkle dependency-environment commitment + vectors.
- Envelope nonce / expiry / revocation / freshness policy (issued_at is recorded; not enforced).
- A truly independent second kernel (nanoda not wired; reported incompatible earlier).
- Hardware-attested and ZK backends (would return UNSUPPORTED_BACKEND; not present).
- Hard RSS cap on the sandbox (needs a cgroup via systemd-run; currently bounded by
  wall-clock + `LEAN_NUM_THREADS`, AS-rlimit deliberately unset or Lean threading breaks).

## Environment boundaries found (2026-10-09)
- 4Leibniz pins Lean `v4.34.0-rc2`, which is **not installed** here (only 4.30, 4.33 are),
  so its record cannot be regenerated to 0.2 offline until that toolchain returns. Its
  committed `VisViva` record remains a valid **0.1** record and verifies via the legacy path.
- Res-Nova's committed records predate the current formal source (their `source_commitment`
  does not match `--source` HEAD) — a freshness gap that predates this work; regenerating at
  current source produces a clean 0.2 record (validated, 47/47).
