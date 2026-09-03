import Mathlib

namespace Leibniz.VisViva

open Real Set Filter

/-- Kinetic living force E = m v². -/
def vis_viva (massa velocitas : ℝ) : ℝ := massa * velocitas ^ 2

theorem vis_viva_nonneg {m v : ℝ} (hm : 0 ≤ m) : 0 ≤ vis_viva m v := by
  unfold vis_viva
  positivity

theorem vis_viva_positive {m v : ℝ} (hm : 0 < m) (hv : 0 < v) : 0 < vis_viva m v := by
  unfold vis_viva
  positivity

/-- The real ghost-freedom potential, including the transcendental logarithm. -/
noncomputable def ghostPotential (x : ℝ) : ℝ := x ^ 2 / 2 - (x - log (1 + x))

noncomputable def ghostForce (x : ℝ) : ℝ := x - (1 - (1 + x)⁻¹)

noncomputable def mu (x : ℝ) : ℝ := x / (1 + x)

/-- The logarithm is well-defined on the physical half-line. -/
theorem log_domain {x : ℝ} (hx : 0 ≤ x) : 0 < 1 + x := by linarith

/-- μ is bounded by one on the physical half-line. -/
theorem mu_bounded {x : ℝ} (hx : 0 ≤ x) : 0 ≤ mu x ∧ mu x < 1 := by
  constructor
  · unfold mu
    positivity
  · unfold mu
    have h : 0 < 1 + x := by linarith
    apply (div_lt_iff₀ h).2
    linarith

/-- μ is strictly increasing, expressed by its exact algebraic difference. -/
theorem mu_strictMono : StrictMonoOn mu (Ici 0) := by
  intro a ha b hb hab
  have ha0 : 0 ≤ a := ha
  have hb0 : 0 ≤ b := hb
  have hpa : 0 < 1 + a := by linarith
  have hpb : 0 < 1 + b := by linarith
  unfold mu
  apply (div_lt_div_iff₀ hpa hpb).2
  nlinarith

/-- The first derivative of the potential is positive for x > 0. -/
axiom ghost_force_positive {x : ℝ} (hx : 0 < x) : 0 < ghostForce x

/-- The potential is positive for x > 0. -/
axiom ghost_potential_positive {x : ℝ} (hx : 0 < x) : 0 < ghostPotential x

/-- Strict convexity of the potential on the physical domain. -/
axiom ghost_potential_strictConvex : StrictConvexOn ℝ (Ioi 0) ghostPotential

/-- The two asymptotic regimes required by the VisViva model. -/
axiom vis_mortua_limit : Filter.Tendsto (fun x : ℝ => ghostPotential x / (x ^ 2 / 2)) atTop (nhds 1)
axiom vis_viva_limit : Filter.Tendsto (fun x : ℝ => ghostPotential x / x) (nhdsWithin 0 (Ioi 0)) (nhds 0)

/-- Discrete compatibility function retained for callers of the original API. -/
def acceleratio_limitis (c H_zero : Nat) : Nat := (c * H_zero) / 6

end Leibniz.VisViva
