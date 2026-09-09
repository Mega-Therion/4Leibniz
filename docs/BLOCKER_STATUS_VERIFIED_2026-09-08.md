# Blocker status, verified against the code

**Date:** 2026-09-08
**Method:** every claim below was checked against the current tree — routes
enumerated programmatically, hashes recomputed, endpoints read. Nothing is taken
from either the assessment or from `PRODUCTION_READINESS.md` on trust.

**Why this document exists:** the release assessment's summary lists blockers
that were closed in `d7dccf7` the following day. Reading the summary alone
overstates the remaining work; reading the disposition table alone understates
it in two places. This is the reconciled list.

---

## Corrected: closed, and verified closed

| ID | Verification performed | Status |
|---|---|---|
| **B-02** RCE via `/api/build` | Route carries `@require_auth` **and** returns 404 unless `LEIBNIZ_ENABLE_BUILD_ENDPOINT=1` | **Closed in `api.py`** — but see B-15 below, the capability is still reachable elsewhere |
| **B-03** private key over the wire | Disabled by default (404); `scripts/generate_keypair.py` writes 0600 locally | **Closed** |
| **B-04** ZK verifier in shared paths | `zk_verify.py` uses `tempfile.TemporaryDirectory(prefix='zk-verify-')` per request and calls `npx --prefix … --no`, so a request cannot trigger an install | **Closed** |
| **B-05** in-memory security state | `ReplayGuard` persists nonces to SQLite when `LEIBNIZ_STATE_DB` is set; `AckStore` unchanged | **Partial** — as documented |
| **B-12** input/resource limits | `MAX_CONTENT_LENGTH = 1_000_000` | **Partial** — as documented |
| **B-10** dashboard not anonymously reachable | `https://leibnizai-nxwrqb6w.manus.space` returns **HTTP 200**, title "4Leibniz — A living archive", no auth wall | **Closed for this URL** (see note) |

**Note on B-10.** The live site is a **static React application**: zero `/api/`
fetches, no `localhost`, no `ws://`. It is a presentation artifact, not the
dashboard that drives the Flask API. B-08 and B-14 therefore still apply to
`web/index.html`, which is a different file with a different risk profile.

---

## Two findings the assessment did not have

### F-01 — B-02's fix is bypassed by `realtime.py`

`/api/build` was locked behind a bearer token and a disable-by-default flag.
`realtime.py` offers **the same capability with neither control**:

```python
async def handler(websocket):
    message = json.loads(await websocket.recv())
    if message.get("action") == "build":
        await stream_build(websocket)     # spawns `lake build`
```

No token. No job ownership. No concurrency cap. The sole mitigation is the bind
to `127.0.0.1`.

That bind is weaker than it looks. **Browsers do not apply the same-origin policy
to WebSocket connections the way they do to `fetch`**, so any page the operator
visits can open `ws://127.0.0.1:8765` and send `{"action":"build"}` — classic
cross-site WebSocket hijacking. Each connection spawns an unbounded `lake build`,
which on this project pulls Mathlib.

The assessment lists this as B-15 ("local-only and lacks authorization") but does
not connect it to B-02: closing the authenticated route while leaving the
unauthenticated one open means the capability was never actually contained.

**Minimum fix:** require the same bearer token on the WebSocket handshake, bound
concurrent builds, and reject connections whose `Origin` is not an allow-listed
value.

### F-02 — `/api/ai/suggest` is unauthenticated and spends money

Not in the assessment's register, and classified as acceptable-public by the
"read-only/stateless" rule in the disposition table. It is neither:

```python
@app.post("/api/ai/suggest")          # no @require_auth
def ai_suggest():
    text, model = payload.get("text"), payload.get("model", "gpt-5-mini")
    return jsonify(suggest(text, model))
```

`suggest()` calls `client.chat.completions.create(...)` with `max_completion_tokens=1200`
whenever `OPENAI_API_KEY` and `OPENAI_API_BASE` are set. Two consequences:

1. **Unauthenticated cost exhaustion.** Any reachable client can drain the
   provider budget.
2. **`model` is caller-controlled and unvalidated** — an arbitrary, potentially
   far more expensive model name is passed straight through.

It degrades to a deterministic fallback when no key is configured, which is
exactly why it looks harmless in development and in any audit run without
credentials. The route is safe in the environment it was assessed in and unsafe
in the environment it is meant to run in.

**Minimum fix:** `@require_auth`, and an allow-list for `model`.

---

## Still open, verified open

| ID | Verification | Status |
|---|---|---|
| **B-06** stale proof receipt | `proof-receipt.json` claims `fdeab1c2…`; recomputing the receipt's own hash over `origin/main` gives `2ee9938c…` | **Open — confirmed mismatch** |
| **B-11** demo ceremony | `circuits/ceremony.json`: *"Small demo circuit only; not a production ceremony"* | **Open, honestly labelled** |
| **B-14** frontend injection | `web/index.html`: 3 `innerHTML` sites interpolating API values, **0** CSP, 14 inline handlers | **Open** |
| **B-08 / B-09 / B-13** | frontend coupling, durable multi-tenant storage, observability | **Open** — real infrastructure work |

**B-14 is sharper than "maintainability risk".** This is inside an `onclick`
attribute:

```js
onclick="document.querySelector('#latticeInfo').textContent='${n.id}: rank ${n.rank}'"
```

`n.id` is interpolated into a JavaScript string literal inside an HTML attribute.
A single apostrophe in an API-supplied `id` escapes the string and executes. That
is a concrete injection path, not a style concern.

---

## B-07 — mostly closed, with one hole worth naming

CI now runs four lanes and the **full** `tests/` suite rather than two files.
But the `machine` job runs on `ubuntu-latest` with no Lean toolchain, so

```python
@unittest.skipUnless(shutil.which("lake"), "Lean toolchain not available")
```

**skips the kernel integration tests entirely.** The suite reports
*"49 tests in 33s"* — green, fast, and silent about the fact that the most
expensive verification in the project never ran.

The guard tests whether the toolchain is **present**, not whether the check is
**cheap**. Presence is not readiness. This is also why an assessment run in a
toolchain-free sandbox honestly reports a fast green suite that no developer with
Lean installed can reproduce: locally the same command blocked for **13 minutes
with no output** until the import was narrowed (PR #5, 749s → 30s).

**A broader instance of the same problem:** 11 of the `Leibniz/*.lean` modules
carry a bare `import Mathlib`. PR #5 narrowed the generated file only.

---

### F-03 — the volunteer consensus is Sybil-open; the signing layer exists but is never used

`coordinator/queue_manager.py` and `volunteer/` are on `main` today, so this is
live code, not a proposal.

The pipeline's stated safety property is that a transcription is promoted only
when *"at least three independent responses agree exactly."* The
`minimum_workers` guard counts **rows**, and rows are keyed by a
**caller-supplied `worker_id` string** with no authentication anywhere in the
recording path.

Reproduced against the code as committed:

```
one worker    -> {'status': 'pending-review', 'responses': 1,
                  'reason': 'minimum independent workers not reached'}

same actor, three self-chosen worker_ids:
              -> {'status': 'canonical', 'responses': 3,
                  'agreement': 1.0, 'text': 'FORGED TEXT'}
```

Arbitrary text reaches `canonical` at full agreement. `record_response` takes
`worker_id` as a parameter and does no verification; `volunteer/client.py` passes
whatever `--worker-id` the operator typed.

**The sharpest part: the fix is already written and simply not wired in.**
`volunteer/protocol.py` opens with *"Versioned, **signed** work units"* and
provides Ed25519 `sign_work_unit` / `verify_work_unit`. Neither is called by
`client.py` or by `queue_manager.py`. The signing layer exists, is documented,
and sits entirely outside the path it was built to protect.

**Minimum fix:** have `client.py` sign each response with a worker key, have
`record_response` verify against an admitted-key registry (`peer_admission.py`
already implements signed identity admission), and count **distinct verified
keys** rather than rows. Until then, `minimum_workers=3` measures how many
strings were supplied, not how many parties agreed.

**Severity note.** For a project whose thesis is machine-checkable evidence, a
promotion path to `canonical` that any single party can drive is more serious
than its CVSS shape suggests: it corrupts the corpus rather than the host.

---

## What the pipeline gets right, tested adversarially

`volunteer/worker.py` was probed with seven hostile inputs and held on all of
them, while allowing legitimate work:

| attempt | result |
|---|---|
| legitimate `.lean` inside root | allowed |
| `../outside.lean` | blocked — *proof path escapes worker root* |
| absolute `/etc/passwd` | blocked |
| `../../../../etc/hosts` | blocked |
| `sub/../../outside.lean` | blocked |
| kind `run-shell` | blocked — *unsupported work-unit kind* |
| kind `exec` with a payload | blocked |

The documented claim *"the daemon never runs arbitrary code"* is **verified, not
merely asserted**: translation and bounded-proof-search return `expert-review`
without executing anything, the work-unit kind is allow-listed, and
`_file_digest` resolves symlinks before comparing against the worker root.

This is the standard the consensus layer should be held to, and it is set inside
the same subsystem.
