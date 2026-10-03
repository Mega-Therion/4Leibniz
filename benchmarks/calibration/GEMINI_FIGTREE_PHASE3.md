# FIG TREE — Phase 3: Close the Gate

Phase 2 is accepted. `lake build` gives exit 0 on 3,365 jobs, Mathlib is present, both
TeX files compile, and your three `FOUND, NOT FIXED` lines were accurate.

You reported the build. You did not report the gate. You ran
`05_lean_formalization/verify_all_proofs.sh` and it returns:

    [gate] TARGETS == lakefile roots (28 modules)
    DRIFT PillarIV_AntiDriftGate.lean on disk but not a declared target
    RESULT: FAIL (target list drift — fix before trusting any result)
    exit 1

That is the repository's own verdict on itself and it is the single most important
measurement in the project. It must appear in every future report whether or not it
is asked for.

## The one success criterion

    cd /home/mega/Res-Nova/05_lean_formalization && bash verify_all_proofs.sh; echo $?

**Exit 0 is the only definition of done in this phase.** Not your assessment, not
`lake build`, not a count of modules. That script is the judge. You do not get to
interpret its output — you paste it.

## Why it fails, stated plainly

`PillarIV_AntiDriftGate.lean` sits on disk carrying three `sorry` (lines 146, 156, 170)
and is **not** in the lakefile target list. So the 3,365-job build is clean *by
excluding it*. The clean build and the unproven sorries coexist because the gate is
looking away. The gate has noticed, and says FAIL.

## Two forbidden shortcuts

The gate can be made to pass in two dishonest ways. Both are out.

1. **Do not delete or move `PillarIV_AntiDriftGate.lean`,** and do not edit
   `verify_all_proofs.sh` to stop checking for drift. Making the detector quiet is not
   fixing the defect.
2. **Do not weaken a theorem to make it provable.** The file already contains two
   statements of the form `theorem foo : True := by sorry`. `True` is provable by
   `trivial` and proves nothing. Converting a `sorry` into a vacuous `True` would make
   the gate pass while making the corpus *less* honest. If you cannot prove a
   statement, leave the `sorry`.

## Task A — the real mathematics

Read `PillarIV_AntiDriftGate.lean` in full. Its own docstrings tell you what is wrong,
in the author's words:

> `steadyStateCoherence` is currently *defined* to be `μ(u/γ)`, which makes every
> theorem about it a restatement of §1. To be non-vacuous this must instead be
> *derived* as a property of the GKSL generator's fixed point.

So the work is:

1. Construct a concrete GKSL (Lindblad) generator for a driven, damped two-level
   system on `Matrix (Fin 2) (Fin 2) ℂ`: Hamiltonian drive `u`, dissipation rate `γ`,
   the standard lowering operator as the jump operator.
2. Show it has a steady state (`gksl_steady_state_exists` — and give that theorem a
   real statement, not `True`).
3. Compute that steady state's coherence and prove it equals `μ(u/γ)`
   (`coherence_eq_mu_of_gksl`). This is the load-bearing premise of Pillar IV.

Attempt these in order. **Partial progress is a good outcome.** If you get (1) and (2)
and not (3), that is real advancement and you say so. Do not force it.

## Task B — whichever outcome you reach, make the gate honest

- If you discharge the sorries: add `PillarIV_AntiDriftGate` to the lakefile roots. The
  gate should then pass on its own merits. Paste the output.
- If you do not: **still add it to the lakefile roots.** The gate will then fail for the
  right reason — an unproven theorem, visible — instead of the wrong one, a file hidden
  from the target list. A gate that fails honestly is worth more than one that passes
  by omission.

Then record in `verify_all_proofs.sh`'s own terms what the exit code is.

## Task C — report

Append to `FIG_TREE_ASSET_LEDGER.md` a section `## Phase 3 — Pillar IV`:

- verbatim output and exit code of `verify_all_proofs.sh`, before and after your changes
- for each of the three sorries: discharged, or still open, and if open, the specific
  mathematical obstacle in one sentence
- the diff of every file you changed
- `FOUND, NOT FIXED:` lines for anything else you hit

## Standing rules

- Read `/home/mega/AGENTS.md` first. Never clone over an existing path. Never `rm -rf`
  a `.lake` directory.
- Record measurements, not conclusions. Exit codes are measurements.
- **Report the gate's exit code in your final message even if everything else fails,
  and even if it is bad news.** Omitting a measurement you took is the one defect that
  costs more than any wrong answer.

## Report back with only

- `verify_all_proofs.sh` exit code, before and after
- how many of the 3 sorries are discharged
- whether `PillarIV_AntiDriftGate` is now a declared lakefile root
- count of `FOUND, NOT FIXED:` lines
