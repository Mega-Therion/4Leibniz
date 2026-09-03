/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                      LEIBNIZ: VIS VIVA (LIVING FORCE)                 ║
  ║                 Specimen Dynamicum (1695) & Cosmic Dynamics           ║
  ╚═══════════════════════════════════════════════════════════════════════╝

  PILLAR 5: The dual-channel convex potential and its ghost-freedom proof.
  The interpolant F(x) = ½x² - (x - ln(1+x)) bridges Vis Mortua (Newtonian
  limit) to Vis Viva (cosmic horizon limit). The key theorem — ghost-freedom —
  proves F''(x) > 0 for all x > 0, establishing strict convexity.

  The second derivative F''(x) = x(2+x)/(1+x)² is a rational function;
  its positivity is proved by exact Nat arithmetic on the numerator and
  denominator, requiring no transcendental infrastructure.
-/

namespace Leibniz.VisViva

/--
  VIS VIVA (Living Force): The fundamental kinetic invariant E = m · v².
-/
def vis_viva (massa velocitas : Nat) : Nat :=
  massa * velocitas * velocitas

/-- [P] Vis Viva is strictly positive for positive mass and velocity. -/
theorem vis_viva_positive (m v : Nat) (hm : m > 0) (hv : v > 0) : vis_viva m v > 0 := by
  unfold vis_viva
  have h1 : m * v > 0 := Nat.mul_pos hm hv
  exact Nat.mul_pos h1 hv

/--
  Cosmic Horizon Boundary Scale (a₀ = c · H₀ / 2π in discrete Planck units).
  When local acceleration drops below the horizon threshold, relational
  tension dominates over Newtonian gravity.
  2π ≈ 6.28 → integer approximation by 6.
-/
def acceleratio_limitis (c H_zero : Nat) : Nat :=
  (c * H_zero) / 6

/--
  POSITIVE RATIONAL: A rational number num/den with both numerator and
  denominator strictly positive. Used for exact kernel verification of
  the convexity proof without requiring real-number infrastructure.
-/
structure PosRat where
  num : Nat
  den : Nat
  hnum : num > 0
  hden : den > 0

/-
  THE DUAL-CHANNEL CONVEX POTENTIAL:
    F(x) = ½x² - (x - ln(1+x))
    F'(x) = x - 1 + 1/(1+x) = x²/(1+x)
    F''(x) = 1 - 1/(1+x)² = x(2+x)/(1+x)²

  For x = num/den:
    F''(x) = [num · (2·den + num)] / [(den + num)²]

  Both numerator and denominator are strictly positive for num, den > 0,
  therefore F''(x) > 0 — the potential is strictly convex (ghost-free).

  The ln(1+x) term cancels in the second derivative, so the convexity
  proof requires only rational arithmetic — no transcendental infrastructure.
-/

/-- Numerator of F''(x) when x = num/den: num · (2·den + num). -/
def F_second_deriv_num (x : PosRat) : Nat :=
  x.num * (2 * x.den + x.num)

/-- Denominator of F''(x) when x = num/den: (den + num)². -/
def F_second_deriv_den (x : PosRat) : Nat :=
  (x.den + x.num) * (x.den + x.num)

/--
  [P] GHOST-FREEDOM: F''(x) > 0 for all x > 0.
  The numerator and denominator of F''(x) are both strictly positive,
  therefore F''(x) > 0, and the dual-channel potential is strictly convex.
  No ghost modes — the interpolant is monotonically stable.
-/
theorem ghost_freedom : ∀ (x : PosRat),
    F_second_deriv_num x > 0 ∧ F_second_deriv_den x > 0 := by
  intro ⟨num, den, hnum, hden⟩
  constructor
  · show num * (2 * den + num) > 0
    have h2d : 2 * den > 0 := Nat.mul_pos (by decide) hden
    have hsum : 2 * den + num > 0 := by omega
    exact Nat.mul_pos hnum hsum
  · show (den + num) * (den + num) > 0
    have hsum : den + num > 0 := by omega
    exact Nat.mul_pos hsum hsum

/--
  THE INTERPOLATION FUNCTION: μ(x) = x/(1+x).
  For x = num/den: μ(x) = num/(den + num).
  This function governs the transition between the two asymptotic regimes.
-/
def mu_num (x : PosRat) : Nat := x.num
def mu_den (x : PosRat) : Nat := x.den + x.num

/-- [P] μ(x) > 0 for all x > 0. -/
theorem mu_positive : ∀ (x : PosRat), mu_num x > 0 ∧ mu_den x > 0 := by
  intro ⟨num, den, hnum, hden⟩
  constructor
  · exact hnum
  · show den + num > 0
    omega

/-- [P] μ(x) < 1 for all x > 0 (the interpolation is bounded). -/
theorem mu_bounded : ∀ (x : PosRat), mu_num x < mu_den x := by
  intro ⟨num, den, hnum, hden⟩
  show num < den + num
  omega

/-
  ASYMPTOTIC LIMITS:
  - Vis Mortua (Dead Force / Newtonian-Poisson limit): x ≫ 1, μ(x) → 1,
    F(x) → ½x². This is the Newtonian gravitational regime.
    [D] Derived: follows from the functional form.
  - Vis Viva (Living Force / deep-MOND cosmic horizon limit): x ≪ 1,
    μ(x) → x, F(x) → 0 to leading order. Dynamics governed by
    a₀ = cH₀/2π.
    [D] Derived: follows from the functional form.
-/

end Leibniz.VisViva
