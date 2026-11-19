import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.Convex.Deriv
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

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

/-- Exact algebraic identity: `ghostForce x = x² / (1 + x)` for `x > -1`. -/
theorem ghost_force_eq {x : ℝ} (hx : -1 < x) : ghostForce x = x ^ 2 / (1 + x) := by
  unfold ghostForce
  have h : 1 + x ≠ 0 := by linarith
  field_simp [h]
  ring

/-- The first derivative of the potential is positive for `x > 0`.
Discharged from Mathlib definitions (previously custom axiom; O37). -/
theorem ghost_force_positive {x : ℝ} (hx : 0 < x) : 0 < ghostForce x := by
  rw [ghost_force_eq (by linarith)]
  positivity

/-- Derivative of `ghostPotential` on `x > -1` equals `ghostForce x`. -/
theorem hasDerivAt_ghostPotential {x : ℝ} (hx : -1 < x) :
    HasDerivAt ghostPotential (ghostForce x) x := by
  have h1 : HasDerivAt (fun t : ℝ => t ^ 2 / 2) x x := by
    have hp := (hasDerivAt_pow 2 x).div_const (2 : ℝ)
    have heq : ((2 : ℕ) : ℝ) * x ^ (2 - 1) / 2 = x := by norm_num
    rwa [heq] at hp
  have h2 : HasDerivAt (fun t : ℝ => t) 1 x := hasDerivAt_id x
  have h3 : HasDerivAt (fun t : ℝ => 1 + t) 1 x := by
    have h := (hasDerivAt_const x (1 : ℝ)).add (hasDerivAt_id x)
    have h' : HasDerivAt (fun t : ℝ => 1 + t) (0 + 1) x :=
      h.congr_of_eventuallyEq (Filter.Eventually.of_forall fun _ => rfl)
    simpa using h'
  have h4 : HasDerivAt (fun t : ℝ => Real.log (1 + t)) ((1 + x)⁻¹) x := by
    have hlog := h3.log (by linarith : 1 + x ≠ 0)
    simpa [one_div] using hlog
  have hsub : HasDerivAt (fun t : ℝ => t - Real.log (1 + t)) (1 - (1 + x)⁻¹) x :=
    (h2.sub h4).congr_of_eventuallyEq (Filter.Eventually.of_forall fun _ => rfl)
  exact (h1.sub hsub).congr_of_eventuallyEq (Filter.Eventually.of_forall fun _ => rfl)

/-- `ghostForce` is strictly increasing on `(0, ∞)`. -/
theorem ghostForce_strictMonoOn : StrictMonoOn ghostForce (Ioi 0) := by
  intro a ha b hb hab
  have ha0 : 0 < a := ha
  have hb0 : 0 < b := hb
  rw [ghost_force_eq (by linarith), ghost_force_eq (by linarith)]
  have hpa : 0 < 1 + a := by linarith
  have hpb : 0 < 1 + b := by linarith
  rw [div_lt_div_iff₀ hpa hpb]
  have hfactor : 0 < (b - a) * (a + b + a * b) :=
    mul_pos (sub_pos.mpr hab) (by nlinarith)
  linarith

/-- The potential is positive for `x > 0`.
Discharged from Mathlib definitions (previously custom axiom; O37). -/
theorem ghost_potential_positive {x : ℝ} (hx : 0 < x) : 0 < ghostPotential x := by
  have hcont : ContinuousOn ghostPotential (Ici 0) := fun t ht =>
    (hasDerivAt_ghostPotential (by linarith [show 0 ≤ t from ht])).continuousAt.continuousWithinAt
  have hderiv : ∀ t ∈ interior (Ici (0 : ℝ)), 0 < deriv ghostPotential t := by
    intro t ht
    rw [interior_Ici] at ht
    rw [(hasDerivAt_ghostPotential (by linarith [show 0 < t from ht])).deriv]
    exact ghost_force_positive ht
  have hmono : StrictMonoOn ghostPotential (Ici 0) :=
    strictMonoOn_of_deriv_pos (convex_Ici 0) hcont hderiv
  have h0 : ghostPotential 0 = 0 := by simp [ghostPotential]
  rw [← h0]
  exact hmono (le_refl (0 : ℝ)) (le_of_lt hx) hx

/-- Strict convexity of the potential on the physical domain `(0, ∞)`.
Discharged from Mathlib definitions (previously custom axiom; O37). -/
theorem ghost_potential_strictConvex : StrictConvexOn ℝ (Ioi 0) ghostPotential := by
  have hcont : ContinuousOn ghostPotential (Ioi 0) := fun t ht =>
    (hasDerivAt_ghostPotential (by linarith [show 0 < t from ht])).continuousAt.continuousWithinAt
  have hderiv_mono : StrictMonoOn (deriv ghostPotential) (interior (Ioi 0)) := by
    rw [interior_Ioi]
    intro a ha b hb hab
    rw [(hasDerivAt_ghostPotential (by linarith [show 0 < a from ha])).deriv,
        (hasDerivAt_ghostPotential (by linarith [show 0 < b from hb])).deriv]
    exact ghostForce_strictMonoOn ha hb hab
  exact StrictMonoOn.strictConvexOn_of_deriv (convex_Ioi 0) hcont hderiv_mono

/-- The high-acceleration asymptotic regime: `ghostPotential x / (x² / 2) → 1` as `x → ∞`.
Discharged from Mathlib definitions (previously custom axiom; O37). -/
theorem vis_mortua_limit :
    Filter.Tendsto (fun x : ℝ => ghostPotential x / (x ^ 2 / 2)) atTop (nhds 1) := by
  have h_inv : Filter.Tendsto (fun x : ℝ => (1 : ℝ) / x) atTop (nhds 0) :=
    tendsto_const_nhds.div_atTop tendsto_id
  have h_two_div : Filter.Tendsto (fun x : ℝ => (2 : ℝ) / x) atTop (nhds 0) :=
    tendsto_const_nhds.div_atTop tendsto_id
  have h_log_div : Filter.Tendsto (fun x : ℝ => Real.log (1 + x) / x ^ 2) atTop (nhds 0) := by
    refine tendsto_of_tendsto_of_tendsto_of_le_of_le' tendsto_const_nhds h_inv ?_ ?_
    · filter_upwards [eventually_gt_atTop (0 : ℝ)] with x hx
      exact div_nonneg (Real.log_nonneg (by linarith)) (sq_nonneg x)
    · filter_upwards [eventually_gt_atTop (0 : ℝ)] with x hx
      have hle : Real.log (1 + x) ≤ x := by
        have := Real.log_le_sub_one_of_pos (by linarith : 0 < 1 + x)
        linarith
      calc
        Real.log (1 + x) / x ^ 2 ≤ x / x ^ 2 :=
          div_le_div_of_nonneg_right hle (sq_nonneg x)
        _ = 1 / x := by
          have hx0 : x ≠ 0 := ne_of_gt hx
          field_simp [hx0]
  have h_rhs : Filter.Tendsto
      (fun x : ℝ => (1 : ℝ) - 2 / x + 2 * (Real.log (1 + x) / x ^ 2)) atTop (nhds 1) := by
    have h1 := ((tendsto_const_nhds (x := (1 : ℝ))).sub h_two_div).add (h_log_div.const_mul 2)
    simpa using h1
  refine h_rhs.congr' ?_
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with x hx
  have hx0 : x ≠ 0 := ne_of_gt hx
  unfold ghostPotential
  field_simp [hx0]
  ring

/-- The low-acceleration asymptotic regime: `ghostPotential x / x → 0` as `x → 0⁺`.
Discharged from Mathlib definitions (previously custom axiom; O37). -/
theorem vis_viva_limit :
    Filter.Tendsto (fun x : ℝ => ghostPotential x / x) (nhdsWithin 0 (Ioi 0)) (nhds 0) := by
  have h_id : Filter.Tendsto (fun x : ℝ => x) (nhdsWithin 0 (Ioi 0)) (nhds 0) :=
    continuousWithinAt_id
  have h_lo : Filter.Tendsto (fun x : ℝ => (1 : ℝ) / (1 + x)) (nhdsWithin 0 (Ioi 0)) (nhds 1) := by
    have hden : Filter.Tendsto (fun x : ℝ => (1 : ℝ) + x) (nhdsWithin 0 (Ioi 0)) (nhds 1) := by
      simpa using (tendsto_const_nhds (x := (1 : ℝ))).add h_id
    have hinv : Filter.Tendsto (fun x : ℝ => (1 + x)⁻¹) (nhdsWithin 0 (Ioi 0)) (nhds 1) := by
      simpa using hden.inv₀ (by norm_num : (1 : ℝ) ≠ 0)
    exact hinv.congr (fun t => (one_div (1 + t)).symm)
  have h_log_ratio :
      Filter.Tendsto (fun x : ℝ => Real.log (1 + x) / x) (nhdsWithin 0 (Ioi 0)) (nhds 1) := by
    refine tendsto_of_tendsto_of_tendsto_of_le_of_le' h_lo tendsto_const_nhds ?_ ?_
    · filter_upwards [self_mem_nhdsWithin] with x hx
      have hx0 : 0 < x := hx
      have h1x : 0 < 1 + x := by linarith
      have hinv := Real.log_le_sub_one_of_pos (inv_pos.mpr h1x)
      rw [Real.log_inv] at hinv
      have hbound : x / (1 + x) ≤ Real.log (1 + x) := by
        have h1 : 1 - (1 + x)⁻¹ = x / (1 + x) := by
          field_simp [ne_of_gt h1x]
          ring
        linarith
      calc
        1 / (1 + x) = (x / (1 + x)) / x := by
          field_simp [ne_of_gt hx0, ne_of_gt h1x]
        _ ≤ Real.log (1 + x) / x := div_le_div_of_nonneg_right hbound (le_of_lt hx0)
    · filter_upwards [self_mem_nhdsWithin] with x hx
      have hx0 : 0 < x := hx
      have hle : Real.log (1 + x) ≤ x := by
        have := Real.log_le_sub_one_of_pos (by linarith : 0 < 1 + x)
        linarith
      calc
        Real.log (1 + x) / x ≤ x / x := div_le_div_of_nonneg_right hle (le_of_lt hx0)
        _ = 1 := div_self (ne_of_gt hx0)
  have h_half : Filter.Tendsto (fun x : ℝ => x / 2) (nhdsWithin 0 (Ioi 0)) (nhds 0) := by
    simpa using h_id.div_const (2 : ℝ)
  have h_rhs : Filter.Tendsto
      (fun x : ℝ => x / 2 - 1 + Real.log (1 + x) / x) (nhdsWithin 0 (Ioi 0)) (nhds 0) := by
    have h1 := (h_half.sub (tendsto_const_nhds (x := (1 : ℝ)))).add h_log_ratio
    simpa using h1
  refine h_rhs.congr' ?_
  filter_upwards [self_mem_nhdsWithin] with x hx
  have hx0 : x ≠ 0 := ne_of_gt hx
  unfold ghostPotential
  field_simp [hx0]
  ring

/-! ## Two-member dyad equipartition bound `1/√2` (scoped per O35)

First-principles algebraic bound on a finite two-member system (a dyad).
The stronger member carries at least half of the dyad's total vis viva `v₁² + v₂²`,
so its amplitude share satisfies `√(parsViva) ≥ 1/√2`, attained exactly at
equipartition (`|v₁| = |v₂|`).

Scope fence (O35): This is strictly a two-member dyad equipartition inequality,
NOT a multi-shell Navier–Stokes dyadic-shell energy floor (an infinite sequence
of shells with `E_j ≥ 1/√2` would diverge in `L²`). -/

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
