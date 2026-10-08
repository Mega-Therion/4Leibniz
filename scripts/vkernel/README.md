# V-KERNEL (vkernel/0.1): signed Lean verification records

A consumer can check a record **without Lean, Lake or Mathlib**: `verify.py` needs only Python + PyNaCl.

## What a record establishes
- The holder of a trusted Ed25519 key ran `lake build` and a Lean probe on sources with the given `source_commitment`.
- For each named theorem: a hash of its elaborated statement, a hash of the definition closure its statement reaches (definition bodies and inductive types, not proof bodies), and the axioms Lean's `collectAxioms` reports.
- `formal_result: accepted` only if the build and probe exited 0, no theorem is missing, and every theorem's axioms sit inside the policy (`standard-3` = `propext`, `Classical.choice`, `Quot.sound`).

## What a record does NOT establish (fields say so explicitly)
- `evidence_mode: signed-service`: a signature says the key holder asserts the run happened. It is not a proof that the run happened.
- `statement_match: not-checked`: no comparison against a trusted challenge statement (Lean `comparator`) yet.
- `independent_checker`: `leanchecker` (bundled with the toolchain) replays the stored declarations of each module in `check_modules`. It is the same kernel implementation re-run, not an independent one; a second kernel (nanoda) is not wired. A run fails on a nonzero exit or on any output. (Retested 2026-10-08: leanchecker exits 1 on a missing module and 0 silently on a clean one. An earlier note in this repo said it exits 0 on exceptions; that was a misread and is withdrawn.)
- `nonvacuity: not-established`: never inferred automatically. A tautology or an impossible premise passes every check here.
- No tier. The record never says `[P]`; the consumer's policy decides.

## Use
    export VKERNEL_SIGNING_KEY=~/.chyren/vkernel/signing.key   # 32-byte seed, chmod 600, never in a repo
    python3 scripts/vkernel/attest.py . scripts/vkernel/vkernel.4leibniz.json proof-record.json
    python3 scripts/vkernel/verify.py proof-record.json scripts/vkernel/trusted_signers.json --source .

## Tests
`scripts/vkernel/test_vkernel.sh` runs on a temp copy of `fixture/` (Lean v4.33.0-rc1, no Mathlib) with a throwaway key. All 13 checks must PASS:
clean accepted / verifies; custom axiom, `sorry`, missing theorem, leanchecker failure rejected; tampered payload, foreign signer, edited source fail.
`fixture/Fix/Basic.lean` contains a deliberate `axiom` and `sorry`: they are the sabotage targets.

## Vacuity screen (sidecar, not part of a record)
`vacuity_screen.py <project> <config.json> <out.json> [--preamble F.lean]` runs one Lean process (`VacuityScreen.lean.in`). It classifies each named theorem by the vacuity patterns actually found in chyren-aeon on 2026-10-06 (e8ae1d4, b6ed95b, 2a38838), conjunct by conjunct, before and after unfolding the project's own definitions:
- **REFLEXIVE:** both sides of an `=` are reducibly equal (`15/2 = 15/2`).
- **CLOSED-ARITH:** no free variables; `norm_num`, `decide` or `simp` closes it.
- **RING-ID:** `ring` closes it with every hypothesis removed (`x = −(−x)`, `l − l = 0`).
- **FIELD-ID:** only `≠`/`<` side conditions kept, and `field_simp`/`simp` closes it (`μke/(μk) = e`).
- **HYP-RESTATED:** the conclusion is one of the hypotheses (`(h : c = 1) : c = 1 := h`).
- **HYP-PINNED/K:** after `subst_vars` on the equality hypotheses, the rest falls in class K (`(hT : c_T = 1) (hγ : c_γ = 1) … : |c_T/c_γ − 1| < ε`).
- **CONTRADICTORY-PREMISES:** the hypotheses prove `False`.

**PASS** only means none of these fired. A record's `nonvacuity` stays `not-established`. A screen can't certify meaning, and the CLAUDE.md anti-vacuity rule still applies.

Calibration (`calibration/check_calibration.py`, frozen in `chyren_aeon_expected.json`):
- Must be flagged (8): the 6 statements later replaced as vacuous, copied verbatim from git, plus 2 probes copying the two Res-Nova patterns the first version missed (`physical_frame_tensor_speed_unity`, `gw170817_concordance`).
- Must PASS: 4 genuine replacements.
- Measured 2026-10-08: 8/8 flagged, 4/4 pass.

Sabotage on copies:
- "never flag": the check exits 1, 8 expectation failures.
- "flag everything": the check exits 1, 4 failures.

## Next (not built)
1. `comparator` statement match against a trusted challenge file.
2. A second, independent kernel (nanoda) for dual-kernel consensus.
3. A local zk backend, benchmark-only. No paid proving networks, no on-chain verifier.

## CI mode
The `vkernel` job in `verify.yml` runs `attest.py --unsigned` on GitHub Actions and uploads `proof-record.unsigned.json`. Download it, then `countersign.py` it locally: evidence_mode becomes `ci-run-countersigned` and the payload keeps the run URL. The signing key never enters CI.

## Traps
`traps/`: verifiers that report success when they failed. Only lean4lean is confirmed so far.
