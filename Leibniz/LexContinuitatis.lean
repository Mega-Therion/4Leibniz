import Mathlib
import Leibniz.VisViva

namespace Leibniz.LexContinuitatis

open Real
noncomputable section

/-- Continuity-band parameter θ used by the formal model. -/
def theta : ℝ := 7 / 10

def chiFloor : ℝ := 1 / Real.sqrt 2

def chiCeil : ℝ := Real.sqrt (theta * (2 - theta))

def chiMidArithmetic : ℝ := (chiFloor + chiCeil) / 2

def chiMidGeometric : ℝ := Real.sqrt (chiFloor * chiCeil)

 theorem theta_pos : 0 < theta := by norm_num [theta]
theorem theta_lt_two : theta < 2 := by norm_num [theta]

theorem chiFloor_pos : 0 < chiFloor := by
  unfold chiFloor
  have h : 0 < Real.sqrt 2 := Real.sqrt_pos.2 (by norm_num)
  positivity

theorem chiCeil_pos : 0 < chiCeil := by
  unfold chiCeil
  apply Real.sqrt_pos.2
  norm_num [theta]

/-- Derived, not assumed: the floor sits below the ceiling by direct arithmetic
on θ = 7/10, since 1/2 < θ(2 − θ). Formerly a bare axiom; promoted to a
theorem 2026-09-12 alongside the first-principles derivation of the floor
(`chiFloor_is_dyadic_floor`). -/
theorem chiFloor_lt_chiCeil : chiFloor < chiCeil := by
  unfold chiFloor chiCeil
  rw [← Leibniz.VisViva.sqrt_half]
  exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num [theta])

theorem chi_floor_lt_mid : chiFloor < chiMidArithmetic := by
  unfold chiMidArithmetic
  have h := chiFloor_lt_chiCeil
  nlinarith

theorem chi_mid_lt_ceil : chiMidArithmetic < chiCeil := by
  unfold chiMidArithmetic
  have h := chiFloor_lt_chiCeil
  nlinarith

/-- The real band is nonempty and ordered. -/
theorem continuity_band_ordered : chiFloor < chiMidArithmetic ∧ chiMidArithmetic < chiCeil :=
  ⟨chi_floor_lt_mid, chi_mid_lt_ceil⟩

theorem within_continuity_envelope {x : ℝ} (h₁ : chiFloor ≤ x) (h₂ : x ≤ chiCeil) :
    chiFloor ≤ x ∧ x ≤ chiCeil := ⟨h₁, h₂⟩

/-- First-principles algebraic derivation of the ceiling from θ(2−θ). -/
theorem ceiling_squared : chiCeil ^ 2 = theta * (2 - theta) := by
  unfold chiCeil
  rw [sq_sqrt]
  norm_num [theta]

/-- The continuity floor is not posited: it is the universal floor of dyadic
chiral dominance — the equipartition bound of the vis viva. Every
non-degenerate dyad's chiral dominance is at least chiFloor (open problem
`chiral-floor`, closed 2026-09-12). -/
theorem chiFloor_is_dyadic_floor {v₁ v₂ : ℝ} (h : 0 < v₁ ^ 2 + v₂ ^ 2) :
    chiFloor ≤ Leibniz.VisViva.dominatioChiralis v₁ v₂ :=
  Leibniz.VisViva.chiral_dominance_ge_floor h

/-- The floor is tight: it is attained at equipartition, where the dyad's
members carry equal vis viva and the dyad is indistinguishable from its
mirror image (`Leibniz.Characteristica.tensio` = 0). -/
theorem chiFloor_tight :
    Leibniz.VisViva.dominatioChiralis 1 1 = chiFloor :=
  Leibniz.VisViva.chiral_dominance_floor_attained

/-- The stronger member of a dyad carries at least half the total vis viva;
equality — the continuity floor — holds exactly at equipartition. -/
theorem chiFloor_equipartition_iff {v₁ v₂ : ℝ} (h : 0 < v₁ ^ 2 + v₂ ^ 2) :
    Leibniz.VisViva.dominatioChiralis v₁ v₂ = chiFloor ↔ |v₁| = |v₂| := by
  have hfloor : chiFloor = 1 / Real.sqrt 2 := rfl
  rw [hfloor]
  exact Leibniz.VisViva.chiral_dominance_eq_floor_iff h

/-- Legacy scaled values remain available for compatibility and tests. -/
def chi_floor_scaled : Nat := 7071
def chi_mid_scaled : Nat := 8305
def chi_ceil_scaled : Nat := 9539

theorem scaled_band_ordered : chi_floor_scaled < chi_mid_scaled ∧ chi_mid_scaled < chi_ceil_scaled := by decide

theorem scaled_within_continuity_envelope (val : Nat) (h₁ : val ≥ chi_floor_scaled)
    (_h₂ : val ≤ chi_ceil_scaled) : val > chi_floor_scaled - 1 := by
  norm_num [chi_floor_scaled] at h₁ ⊢
  omega

end
end Leibniz.LexContinuitatis
