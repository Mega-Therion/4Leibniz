# V-KERNEL (vkernel/0.1): signed Lean verification records

A consumer can check a record **without Lean, Lake or Mathlib**: `verify.py` needs only Python + PyNaCl.

## What a record establishes
- The holder of a trusted Ed25519 key ran `lake build` and a Lean probe on sources with the given `source_commitment`.
- For each named theorem: a hash of its elaborated statement, a hash of the definition closure its statement reaches (definition bodies and inductive types, not proof bodies), and the axioms Lean's `collectAxioms` reports.
- `formal_result: accepted` only if the build and probe exited 0, no theorem is missing, and every theorem's axioms sit inside the policy (`standard-3` = `propext`, `Classical.choice`, `Quot.sound`).

## What a record does NOT establish (fields say so explicitly)
- `evidence_mode: signed-service`: a signature says the key holder asserts the run happened. It is not a proof that the run happened.
- `statement_match: not-checked`: no comparison against a trusted challenge statement (Lean `comparator`) yet.
- `independent_checker: not-run`: no `lean4checker` / `nanoda` replay yet.
- `nonvacuity: not-established`: never inferred automatically. A tautology or an impossible premise passes every check here.
- No tier. The record never says `[P]`; the consumer's policy decides.

## Use
    export VKERNEL_SIGNING_KEY=~/.chyren/vkernel/signing.key   # 32-byte seed, chmod 600, never in a repo
    python3 scripts/vkernel/attest.py . scripts/vkernel/vkernel.4leibniz.json proof-record.json
    python3 scripts/vkernel/verify.py proof-record.json scripts/vkernel/trusted_signers.json --source .

## Tests
`scripts/vkernel/test_vkernel.sh` runs on a temp copy of `fixture/` (Lean v4.33.0-rc1, no Mathlib) with a throwaway key. All 8 checks must PASS:
clean accepted / verifies; custom axiom, `sorry`, missing theorem rejected; tampered payload, foreign signer, edited source fail.
`fixture/Fix/Basic.lean` contains a deliberate `axiom` and `sorry`: they are the sabotage targets.

## Next (not built)
1. `comparator` statement match against a trusted challenge file.
2. `lean4checker` replay, recorded in `independent_checker`.
3. A local zk backend, benchmark-only. No paid proving networks, no on-chain verifier.
