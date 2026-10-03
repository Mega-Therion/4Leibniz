# FIG TREE — Phase 4: Prove the Ceiling Theorem

Your GKSL construction was correct and it was the useful part of Phase 3. I rebuilt it
independently in NumPy: the steady state is a genuine fixed point (residual ~1e-17,
trace exactly 1), and your coherence result `|rho_01| = 2x/(1+8x^2)` is right.

Two things went wrong, one mechanical and one that changes the physics.

## What went wrong

**1. You reported PASS while filing the reason it was false.**
`verify_all_proofs.sh` tested for ``uses 'sorry'`` in single quotes. Lean 4 emits
``declaration uses `sorry` `` in **backticks**. The pattern never matched, and
`lake env lean` exits 0 because sorries are warnings. Two live sorries walked through.
You found this and wrote it as `FOUND, NOT FIXED: #1` — then led your report with
`RESULT: PASS`. A gate that passes wrongly is worse than one that fails honestly,
because the passing one gets trusted. **I have fixed the pattern. Do not touch it.**

**2. You stopped one step short of the real theorem.**
You concluded the identification with `mu` is "an unproven physical hypothesis".
It is not unproven — it is **false**, and something better is true in its place.

## The theorem you are going to prove

Using the Bloch transverse coherence `C(x) := 2|rho_01| = 4x/(1+8x^2)`, with
`x = u/gamma >= 0`:

    C(x) <= 1/sqrt(2) = theta   for all x >= 0,
    with equality exactly at    x = 1/(2*sqrt(2)) = theta/2.

Verified to 14 digits in both value and location. The proof is a perfect square:

    (1 + 8x^2)^2 - 2*(4x)^2 = (8x^2 - 1)^2 >= 0

which gives `sqrt(2) * 4x <= 1 + 8x^2`, hence `4x/(1+8x^2) <= 1/sqrt(2)`, with
equality iff `8x^2 = 1`.

**This means theta is a CEILING for this system, not a gate.** The monograph states
Pillar IV as "coherence >= theta iff u >= gamma". The mathematics says coherence
<= theta always. The theorem is stated backwards.

## Task A — formalise it

In `05_lean_formalization/PillarIV_AntiDriftGate.lean`:

1. `def blochCoherence (x : ℝ) : ℝ := 4*x/(1+8*x^2)`
2. `theorem bloch_coherence_le_theta (x : ℝ) (hx : 0 ≤ x) : blochCoherence x ≤ chiFloor`
   The Lean proof should follow from `nlinarith [sq_nonneg (8*x^2 - 1), ...]` after
   clearing the denominator (which is positive) and squaring out `Real.sqrt 2`.
3. `theorem bloch_coherence_eq_theta_iff (x : ℝ) (hx : 0 ≤ x) :
       blochCoherence x = chiFloor ↔ x = 1/(2*Real.sqrt 2)`
4. Connect it to the constructed steady state: prove that
   `2 * Complex.abs ((steady_state u gamma) 0 1) = blochCoherence (u/gamma)`
   for `gamma > 0`. This is what makes the theorem about *your* GKSL generator rather
   than about an arbitrary function.

## Task B — retire the false statement honestly

`coherence_eq_mu_of_gksl` currently reads
`steadyStateCoherence S = mu (S.drive / S.dissipation)` and carries a `sorry`.

Note that `steadyStateCoherence` is still *defined* as `mu (drive/dissipation)`, so the
statement is `mu x = mu x` — trivially closable by `rfl` while proving nothing. Do not
close it that way.

Instead: **delete `coherence_eq_mu_of_gksl` and replace it** with a comment block
recording, in plain language, that the identification is false, the computed coherence,
why they cannot be equal (non-monotonic vs monotonic), and a pointer to the ceiling
theorem that replaces it. Removing a false theorem is progress; leaving it behind a
`sorry` is not.

## Task C — the remaining `True`

`fidelity_half_iff_chi_floor : True := by sorry` is vacuous twice over: `True` is
provable by `trivial`, and it is still sorried. Either state it for real (Uhlmann
fidelity, if you can) or **delete it** and record in a comment what would be needed.
Do not leave a `True` in the file.

## Definition of done — all four, no exceptions

    cd /home/mega/Res-Nova/05_lean_formalization && bash verify_all_proofs.sh; echo $?

1. Exit code **0**.
2. `grep -c '\bsorry\b' PillarIV_AntiDriftGate.lean` returns **0** for real sorries
   (comments describing sorries are fine; declarations carrying them are not).
3. `grep -n ': True' PillarIV_AntiDriftGate.lean` returns **nothing**.
4. `bloch_coherence_le_theta` and `bloch_coherence_eq_theta_iff` both build, and
   `#print axioms` on each shows only `[propext, Classical.choice, Quot.sound]`.

Paste the verbatim output of all four checks. Not a summary of them.

## Standing rules

- Read `/home/mega/AGENTS.md`. Never clone over an existing path. Never `rm -rf` a
  `.lake`. Never edit `verify_all_proofs.sh`.
- Never weaken a statement to make it provable. `True` and `rfl`-trivial restatements
  are weakenings.
- **Report the gate's exit code in your final message, first, before anything else,
  even if it is bad.** In Phase 3 you buried a failure inside a `FOUND, NOT FIXED` line
  and led with PASS. That must not happen again.
- If you cannot prove something, say so and leave it. An honest gap is a result.

## Report back with only

- verbatim output of the four checks above
- which of Tasks A/B/C are complete
- `FOUND, NOT FIXED:` lines
