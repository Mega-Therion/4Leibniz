/-! Calibration preamble: the six chyren-aeon statements later replaced as vacuous,
copied verbatim (statement and proof) from the parents of e8ae1d4, b6ed95b and 2a38838.
The screen must flag every one of these. -/
namespace VacuityCalib.Old
open LeanCore.InvariantTheory

theorem oscillator_n2_singlet_neg_radial (z : ℝ) :
    (2 * z - 3) / Real.sqrt 6 = - (- (2 * z - 3) / Real.sqrt 6) := by
  ring

theorem su11_angular_momentum_conservation (l m : ℝ) :
    l - l = 0 ∧ m - m = 0 := by
  constructor <;> ring

theorem fock_vacuum_norm_chain :
    (1 + 0 : ℝ) * (0 + 0 + 3 / 2) = 3 / 2 ∧
    (15 / 2 : ℝ) = 15 / 2 ∧
    (16 : ℝ) * (15 / 2) = 120 := by
  constructor
  · norm_num
  · constructor
    · rfl
    · norm_num

theorem bohlin_conformal_energy_relation (E_abs k rho : ℝ) (hrho : rho ≠ 0) :
    4 * rho ^ 2 * (-E_abs + k / rho ^ 2) = 4 * k - 4 * E_abs * rho ^ 2 := by
  have hrho2 : rho ^ 2 ≠ 0 := pow_ne_zero 2 hrho
  field_simp
  ring

theorem arnold_bohlin_bertrand_duality :
    (bertrandCoulombExponent + 2) * (bertrandOscillatorExponent + 2) = 4 := by
  decide

theorem runge_lenz_eccentricity_magnitude (mu k e : ℝ) (h_muk : mu * k ≠ 0) :
    mu * k * e / (mu * k) = e := by
  exact mul_div_cancel_left₀ e h_muk

end VacuityCalib.Old
