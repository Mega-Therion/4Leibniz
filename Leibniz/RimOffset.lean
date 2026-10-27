import Init.Data.Rat.Lemmas

/-
Quadratic truncation of the offset-sphere radius.

  f(μ) = 1 - ε μ + (ε^2 / 2) (1 - μ^2)

is the expansion of √(1 - 2 ε μ + ε^2) through order ε^2.
On [-1, 1] its Legendre coefficients satisfy a₁ = -ε and a₂ = -ε^2 / 3,
so |a₂ / a₁| = ε / 3 = (d / R) / 3 whenever ε ≠ 0.

The definite integrals below are the evaluated antiderivatives.
`decide +kernel` checks the rational arithmetic. This file imports nothing,
because the 4Leibniz mathlib build is not present in `.lake/packages`.
-/

/-- ∫₀¹ μ² dμ = 1/3, so ∫_{-1}^{1} μ² dμ = 2/3. -/
theorem int_mu_sq : ((1 : Rat) ^ 3 / 3) - (((-1 : Rat) ^ 3) / 3) = 2 / 3 := by
  decide +kernel

/-- ∫₀¹ (-3 μ^4 + 4 μ^2 - 1) dμ = -4/15.
    That integrand is what remains of (1-μ²) P₂ after the even reduction. -/
theorem int_quad_weight : ((-3 : Rat) / 5 + 4 / 3 - 1) = -4 / 15 := by
  decide +kernel

/-- Dipole: a₁ = (3/2) ∫ f μ dμ and only -ε μ² survives, giving a₁ = -ε. -/
theorem rim_dipole_coeff : (3 / 2 : Rat) * ((-2) / 3) = -1 := by
  decide +kernel

theorem rim_a1 (ε : Rat) : (3 / 2 : Rat) * ((-2) / 3 * ε) = -ε := by
  rw [← Rat.mul_assoc, rim_dipole_coeff, Rat.neg_mul, Rat.one_mul]

/-- Quadrupole weight of (1-μ²): ∫ (1-μ²) P₂ dμ = -4/15. -/
theorem rim_quad_integral : (1 / 2 : Rat) * (-4 / 15) * 2 = -4 / 15 := by
  decide +kernel

/-- (5/2) * (1/2) * (-4/15) = -1/3, the constant in a₂ = (-1/3) ε². -/
theorem rim_quad_coeff : (5 / 2 : Rat) * (1 / 2) * (-4 / 15) = -1 / 3 := by
  decide +kernel

/-- At ε = 1/100, (-1/3) ε² / ε = 1/300, which is (d/R)/3. -/
theorem rim_ratio_from_coeffs : ((-1 : Rat) / 3 * (1 / 100 * (1 / 100))) / (-(1 / 100)) = 1 / 300 := by
  decide +kernel

/-- At the computed shell d/R = 1/100 the truncation ratio is 1/300. -/
theorem rim_ratio_at_one_percent : (1 : Rat) / 100 / 3 = 1 / 300 := by
  decide +kernel
