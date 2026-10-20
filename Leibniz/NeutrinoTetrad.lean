import Mathlib
import Leibniz.SpatiumRelativum

/-!
### Minkowski signature (1,3) and tetrads

Defines the Minkowski metric `η = diag(1, -1, -1, -1)` on ℝ⁴, proves `det η = -1`, and proves
that every invertible tetrad `e` induces a metric `g = eᵀ η e` with negative determinant, so a
tetrad cannot leave the Lorentzian determinant class.

The two-right-handed-neutrino seesaw texture is recorded below as a parameter structure only.
Its rank bound (one massless light neutrino) is not formalized in this file.
-/

noncomputable section

namespace Leibniz.NeutrinoTetrad

open Matrix

/-- The Minkowski metric with signature (1,3) on ℝ⁴. -/
def eta13 : Matrix (Fin 4) (Fin 4) ℝ :=
  Matrix.diagonal ![1, -1, -1, -1]

/-- `det η = -1`. -/
theorem det_eta13_eq_neg_one : eta13.det = -1 := by
  simp [eta13, Matrix.det_diagonal, Fin.prod_univ_four]

/-- `η` is invertible: its determinant is a unit. -/
theorem isUnit_det_eta13 : IsUnit eta13.det := by
  rw [det_eta13_eq_neg_one]
  exact isUnit_one.neg

/-- A tetrad (vielbein) `e^a_μ`: an invertible 4×4 real matrix. -/
structure Tetrad4 where
  e : Matrix (Fin 4) (Fin 4) ℝ
  invertible_e : Invertible e

/-- The metric induced by a tetrad: `g_μν = e^a_μ η_ab e^b_ν`, i.e. `eᵀ η e`. -/
def inducedMetric (tet : Tetrad4) : Matrix (Fin 4) (Fin 4) ℝ :=
  tet.e.transpose * eta13 * tet.e

/-- Every invertible tetrad induces a metric with negative determinant. -/
theorem induced_metric_det_neg (tet : Tetrad4) : (inducedMetric tet).det < 0 := by
  have h_nonzero : tet.e.det ≠ 0 := by
    haveI := tet.invertible_e
    exact (Matrix.isUnit_det_of_invertible tet.e).ne_zero
  have h_sq_pos : 0 < tet.e.det ^ 2 :=
    lt_of_le_of_ne (sq_nonneg _) (Ne.symm (pow_ne_zero 2 h_nonzero))
  have h_det : (inducedMetric tet).det = -(tet.e.det ^ 2) := by
    rw [inducedMetric, Matrix.det_mul, Matrix.det_mul, Matrix.det_transpose,
      det_eta13_eq_neg_one]
    ring
  rw [h_det]
  linarith

/-- Parameters of a 3×2 Yukawa texture with two right-handed neutrinos. Only the parameters
are recorded; nothing about the light-neutrino mass matrix is proved here. -/
structure SeesawTexture3x2 where
  y11 : ℝ
  y12 : ℝ
  y21 : ℝ
  y22 : ℝ
  y31 : ℝ
  y32 : ℝ
  mR1 : ℝ
  mR2 : ℝ
  mR1_pos : 0 < mR1
  mR2_pos : 0 < mR2

end Leibniz.NeutrinoTetrad

end
