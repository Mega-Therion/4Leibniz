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


/-! ## The chiral dominance of a dyad and the continuity floor

First-principles derivation of the continuity floor `1/√2` (open problem
`chiral-floor`). The vis viva of a two-member system — a dyad — splits
between its members. The stronger member necessarily carries at least half
of the total vis viva, so the tight universal bound on its amplitude share is
`√(1/2) = 1/√2`, attained exactly when both members carry equal vis viva
(equipartition — the tensionless state of `Leibniz.Characteristica.tensio`,
where the dyad is indistinguishable from its mirror). The continuity floor of
`Leibniz.LexContinuitatis` is thus not a posited constant but the
equipartition bound of the vis viva. -/

/-- The stronger member's share of the total vis viva of a dyad. -/
noncomputable def parsViva (v₁ v₂ : ℝ) : ℝ := (max |v₁| |v₂|) ^ 2 / (v₁ ^ 2 + v₂ ^ 2)

/-- Chiral dominance: the amplitude share of the stronger member,
`√(parsViva)` — the living-force analogue of a direction cosine. -/
noncomputable def dominatioChiralis (v₁ v₂ : ℝ) : ℝ := Real.sqrt (parsViva v₁ v₂)

/-- The two forms of the floor agree: `√(1/2) = 1/√2`. -/
theorem sqrt_half : Real.sqrt ((1:ℝ) / 2) = 1 / Real.sqrt 2 := by
  rw [Real.sqrt_div (by norm_num) 2]
  simp

/-- First principles: the stronger member of a non-degenerate dyad carries at
least half of the total vis viva. -/
theorem pars_viva_ge_half {v₁ v₂ : ℝ} (h : 0 < v₁ ^ 2 + v₂ ^ 2) :
    1 / 2 ≤ parsViva v₁ v₂ := by
  have hm : 0 ≤ max |v₁| |v₂| := (abs_nonneg v₁).trans (le_max_left _ _)
  have h1 : |v₁| ≤ max |v₁| |v₂| := le_max_left _ _
  have h2 : |v₂| ≤ max |v₁| |v₂| := le_max_right _ _
  have hn1 : 0 ≤ |v₁| := abs_nonneg _
  have hn2 : 0 ≤ |v₂| := abs_nonneg _
  have e1 : v₁ ^ 2 ≤ (max |v₁| |v₂|) ^ 2 := by
    rw [← sq_abs v₁]
    exact sq_le_sq' (by linarith) h1
  have e2 : v₂ ^ 2 ≤ (max |v₁| |v₂|) ^ 2 := by
    rw [← sq_abs v₂]
    exact sq_le_sq' (by linarith) h2
  unfold parsViva
  have hhalf : (1:ℝ) / 2 * (v₁ ^ 2 + v₂ ^ 2) = (v₁ ^ 2 + v₂ ^ 2) / 2 := by ring
  rw [le_div_iff₀ h, hhalf, div_le_iff₀ (by norm_num : (0:ℝ) < 2)]
  linarith

/-- The chiral dominance of any non-degenerate dyad is at least the continuity
floor `1/√2` — the equipartition bound of the vis viva. -/
theorem chiral_dominance_ge_floor {v₁ v₂ : ℝ} (h : 0 < v₁ ^ 2 + v₂ ^ 2) :
    1 / Real.sqrt 2 ≤ dominatioChiralis v₁ v₂ := by
  unfold dominatioChiralis
  rw [← sqrt_half]
  exact Real.sqrt_le_sqrt (pars_viva_ge_half h)

/-- The floor is attained exactly at equipartition: the dyad's members carry
equal vis viva, and are indistinguishable from their mirror image. -/
theorem chiral_dominance_eq_floor_iff {v₁ v₂ : ℝ} (h : 0 < v₁ ^ 2 + v₂ ^ 2) :
    dominatioChiralis v₁ v₂ = 1 / Real.sqrt 2 ↔ |v₁| = |v₂| := by
  have hpars : 0 ≤ parsViva v₁ v₂ := by
    unfold parsViva
    exact div_nonneg (sq_nonneg _) (by linarith)
  have hm : 0 ≤ max |v₁| |v₂| := (abs_nonneg v₁).trans (le_max_left _ _)
  have h1 : |v₁| ≤ max |v₁| |v₂| := le_max_left _ _
  have h2 : |v₂| ≤ max |v₁| |v₂| := le_max_right _ _
  have hn1 : 0 ≤ |v₁| := abs_nonneg _
  have hn2 : 0 ≤ |v₂| := abs_nonneg _
  have e1 : v₁ ^ 2 ≤ (max |v₁| |v₂|) ^ 2 := by
    rw [← sq_abs v₁]
    exact sq_le_sq' (by linarith) h1
  have e2 : v₂ ^ 2 ≤ (max |v₁| |v₂|) ^ 2 := by
    rw [← sq_abs v₂]
    exact sq_le_sq' (by linarith) h2
  constructor
  · intro heq
    unfold dominatioChiralis at heq
    rw [← sqrt_half] at heq
    have hp : parsViva v₁ v₂ = 1 / 2 := (Real.sqrt_inj hpars (by norm_num)).1 heq
    unfold parsViva at hp
    field_simp at hp
    have hv1 : v₁ ^ 2 = (max |v₁| |v₂|) ^ 2 := by linarith
    have hv2 : v₂ ^ 2 = (max |v₁| |v₂|) ^ 2 := by linarith
    exact (sq_eq_sq_iff_abs_eq_abs v₁ v₂).1 (by rw [hv1, hv2])
  · intro heq
    have hmax : max |v₁| |v₂| = |v₂| := by
      rw [heq]
      exact max_eq_left (le_refl _)
    have hv : v₁ ^ 2 = v₂ ^ 2 := by rw [← sq_abs v₁, ← sq_abs v₂, heq]
    have hpos : 0 < v₂ ^ 2 := by
      by_contra hc
      have hc' : v₂ ^ 2 ≤ 0 := not_lt.mp hc
      have hz : v₁ ^ 2 + v₂ ^ 2 ≤ 0 := by rw [hv]; linarith
      linarith
    have hp : parsViva v₁ v₂ = 1 / 2 := by
      unfold parsViva
      rw [hmax, hv, sq_abs v₂]
      have hne : (v₂:ℝ) ^ 2 + v₂ ^ 2 ≠ 0 := by positivity
      rw [div_eq_iff hne]
      ring
    unfold dominatioChiralis
    rw [hp, ← sqrt_half]

/-- The floor is attained, so the universal bound is tight, not merely valid. -/
theorem chiral_dominance_floor_attained :
    dominatioChiralis 1 1 = 1 / Real.sqrt 2 :=
  (chiral_dominance_eq_floor_iff (by norm_num)).mpr rfl

/-- Discrete compatibility function retained for callers of the original API. -/
def acceleratio_limitis (c H_zero : Nat) : Nat := (c * H_zero) / 6

end Leibniz.VisViva
