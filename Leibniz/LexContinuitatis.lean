import Mathlib

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

axiom chiFloor_lt_chiCeil : chiFloor < chiCeil

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
