/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║              LEIBNIZ: DISSIPATIO (CONCRETE CHANNELS)                 ║
  ║       Phase 2b of the lindblad-cp attack — study 2026-09-12           ║
  ╚══════════════════════════════════════════════════════════════════════╝

The two paradigm dissipative qubit channels — dephasing and amplitude
damping — instantiated as concrete (H, L) pairs and pushed through the
Phase 2a bridge `eulerLindbladStep_eq`.

For dephasing the jump operator is `√(γ/2) • σz` and the generator
collapses to the textbook coherence-damping map
`𝓛(ρ) = (γ/2)(σz ρ σz − ρ)`: populations are untouched while the
off-diagonal coherence decays by the factor `1 − γh` per Euler step.

For amplitude damping the jump operator is `√γ • σ⁻` and the generator
is the textbook population-flow map
`𝓛(ρ) = γ(σ⁻ ρ σ⁺ − ½ {P₁, ρ})`: the ground state is a fixed point,
the excited population decays by `1 − γh`, and the ground population
grows by exactly the excited population that decayed.

Both discrete Euler steps are Kraus families, so complete positivity of
each step is the Phase 1 lemma `krausMap_completely_positive`
re-instantiated — the bridge makes the special cases one-liners.
-/

import Mathlib
import Leibniz.Kraus

namespace Leibniz.Dissipatio

open Matrix Complex
open Harmonia Kraus

/-! ### The qubit ladder and Pauli Z -/

/-- Pauli Z: the phase-flip operator `diag(1, −1)`. -/
def sigmaZ : Operator := !![(1 : ℂ), 0; 0, -1]

/-- The lowering operator `σ⁻ = |0⟩⟨1|`: maps the excited state to the
ground state and annihilates the ground state. -/
def sigmaMinus : Operator := !![(0 : ℂ), 1; 0, 0]

/-- The raising operator `σ⁺ = |1⟩⟨0|`, the adjoint of `σ⁻`. -/
def sigmaPlus : Operator := !![(0 : ℂ), 0; 1, 0]

/-- The ground-state projector `|0⟩⟨0|`. -/
def projGround : Operator := !![(1 : ℂ), 0; 0, 0]

/-- The excited-state projector `|1⟩⟨1|`. -/
def projExcited : Operator := !![(0 : ℂ), 0; 0, 1]

/-! ### Algebra of the ladder -/

/-- Pauli Z is Hermitian. -/
theorem sigmaZ_hermitian : sigmaZ.IsHermitian := by
  refine Matrix.IsHermitian.ext (fun i j => ?_)
  fin_cases i <;> fin_cases j <;> simp [sigmaZ] <;> norm_num

/-- Pauli Z squares to the identity. -/
theorem sigmaZ_mul_sigmaZ : sigmaZ * sigmaZ = 1 := by
  ext i j
  fin_cases i <;> fin_cases j
  <;> simp [sigmaZ, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]

/-- Pauli Z is unitary: `σz* σz = 1`. -/
theorem star_sigmaZ_mul_sigmaZ : star sigmaZ * sigmaZ = 1 := by
  rw [show star sigmaZ = sigmaZ from sigmaZ_hermitian.star_eq, sigmaZ_mul_sigmaZ]

/-- The adjoint of the lowering operator is the raising operator. -/
theorem star_sigmaMinus : star sigmaMinus = sigmaPlus := by
  rw [Matrix.star_eq_conjTranspose]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [sigmaMinus, sigmaPlus]

/-- `σ⁺ σ⁻` projects onto the excited state: `σ⁺σ⁻ = |1⟩⟨1|`. -/
theorem sigmaPlus_mul_sigmaMinus : sigmaPlus * sigmaMinus = projExcited := by
  ext i j
  fin_cases i <;> fin_cases j
  <;> simp [sigmaPlus, sigmaMinus, projExcited, Matrix.mul_apply, Matrix.vecMul,
      dotProduct, Fin.sum_univ_two]

/-- `σ⁻ σ⁺` projects onto the ground state: `σ⁻σ⁺ = |0⟩⟨0|`. -/
theorem sigmaMinus_mul_sigmaPlus : sigmaMinus * sigmaPlus = projGround := by
  ext i j
  fin_cases i <;> fin_cases j
  <;> simp [sigmaMinus, sigmaPlus, projGround, Matrix.mul_apply, Matrix.vecMul,
      dotProduct, Fin.sum_univ_two]

/-- Conjugation by the raising/lowering pair extracts exactly the excited
population: `σ⁻ ρ σ⁺ = ρ₁₁ • |0⟩⟨0|`. -/
theorem sigmaMinus_mul_mul_sigmaPlus (rho : Operator) :
    sigmaMinus * rho * sigmaPlus = (rho 1 1) • projGround := by
  ext i j
  fin_cases i <;> fin_cases j
  <;> simp [sigmaMinus, sigmaPlus, projGround, Matrix.mul_apply, Matrix.vecMul,
      dotProduct, Fin.sum_univ_two]
  <;> norm_num

/-- The excited and ground projectors are mutually orthogonal. -/
theorem projExcited_mul_projGround : projExcited * projGround = 0 := by
  ext i j
  fin_cases i <;> fin_cases j
  <;> simp [projExcited, projGround, Matrix.mul_apply, Matrix.vecMul,
      dotProduct, Fin.sum_univ_two]

theorem projGround_mul_projExcited : projGround * projExcited = 0 := by
  ext i j
  fin_cases i <;> fin_cases j
  <;> simp [projExcited, projGround, Matrix.mul_apply, Matrix.vecMul,
      dotProduct, Fin.sum_univ_two]

/-! ### Dephasing -/

/-- The dephasing jump-operator family: a single jump operator
`√(γ/2) • σz` with zero Hamiltonian. -/
noncomputable def dephasingL (gamma : ℝ) : Fin 1 → Operator :=
  fun _ => ((Real.sqrt (gamma / 2) : ℂ)) • sigmaZ

/-- The GKLS generator of dephasing collapses to the textbook
coherence-damping map: `𝓛(ρ) = (γ/2)(σz ρ σz − ρ)`. -/
theorem dephasing_gen (gamma : ℝ) (hg : 0 ≤ gamma) (rho : Operator) :
    lindbladRhsFam 0 (dephasingL gamma) rho
      = (gamma / 2 : ℂ) • (sigmaZ * rho * sigmaZ - rho) := by
  have hgsqrt : ((Real.sqrt (gamma / 2) : ℂ)) * ((Real.sqrt (gamma / 2) : ℂ))
      = (gamma / 2 : ℂ) := by
    push_cast
    exact mod_cast Real.mul_self_sqrt (by linarith)
  have hstarL : star ((Real.sqrt (gamma / 2) : ℂ)) = ((Real.sqrt (gamma / 2) : ℂ)) := by
    rw [Complex.star_def, Complex.conj_ofReal]
  have hstarZ : star sigmaZ = sigmaZ := sigmaZ_hermitian.star_eq
  have hstarLZ : star (dephasingL gamma 0) = dephasingL gamma 0 := by
    simp only [dephasingL]
    rw [Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
      ← Matrix.star_eq_conjTranspose, Complex.star_def, Complex.conj_ofReal, hstarZ]
  have hLL : star (dephasingL gamma 0) * dephasingL gamma 0 = (gamma / 2 : ℂ) • 1 := by
    rw [hstarLZ]
    simp only [dephasingL]
    rw [smul_mul_assoc, mul_smul_comm, smul_smul, hgsqrt, sigmaZ_mul_sigmaZ]
  have hLrL : dephasingL gamma 0 * rho * star (dephasingL gamma 0)
      = (gamma / 2 : ℂ) • (sigmaZ * rho * sigmaZ) := by
    rw [hstarLZ]
    simp only [dephasingL, smul_mul_assoc, mul_smul_comm, smul_smul]
    rw [hgsqrt]
  simp only [lindbladRhsFam, Harmonia.commutator, zero_mul, mul_zero, sub_zero,
    smul_zero, add_zero, Fin.sum_univ_one, Harmonia.dissipator, hLrL, hLL,
    Harmonia.anticommutator, smul_mul_assoc, mul_smul_comm, smul_smul, one_mul, mul_one]
  module

/-- Dephasing preserves the diagonal: populations are invariant under
the first-order dephasing step, at every step size. -/
theorem dephasing_population_preserved (gamma h : ℝ) (hg : 0 ≤ gamma) (rho : Operator)
    (i : Fin 2) :
    (rho + (h : ℂ) • lindbladRhsFam 0 (dephasingL gamma) rho) i i = rho i i := by
  rw [dephasing_gen gamma hg]
  have hzz : ∀ j : Fin 2, (sigmaZ * rho * sigmaZ) j j = rho j j := by
    intro j
    fin_cases j
    <;> simp [sigmaZ, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]
  rw [Matrix.add_apply, Matrix.smul_apply, Matrix.smul_apply, Matrix.sub_apply, hzz i]
  push_cast
  ring

/-- Dephasing damps the coherence: the off-diagonal entry of the
first-order step is `(1 − γh) • ρ₀₁` — exponential decay in the number
of Euler steps. -/
theorem dephasing_coherence_decay (gamma h : ℝ) (hg : 0 ≤ gamma) (rho : Operator) :
    (rho + (h : ℂ) • lindbladRhsFam 0 (dephasingL gamma) rho) 0 1
      = ((1 - h * gamma : ℝ) : ℂ) * rho 0 1 := by
  rw [dephasing_gen gamma hg]
  have hzz : (sigmaZ * rho * sigmaZ) 0 1 = -(rho 0 1) := by
    simp [sigmaZ, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]
  rw [Matrix.add_apply, Matrix.smul_apply, Matrix.smul_apply, Matrix.sub_apply, hzz]
  push_cast
  ring

/-- The full Euler-discrete dephasing step, computed through the bridge:
`krausMap (eulerLindbladStep 0 L h) ρ = ρ + h • 𝓛(ρ) + (hγ/4)² • ρ` —
the textbook damping plus a positive scalar multiple of `ρ` itself. -/
theorem dephasing_step (gamma : ℝ) (hg : 0 ≤ gamma) (h : ℝ) (hh : 0 ≤ h) (rho : Operator) :
    krausMap (eulerLindbladStep 0 (dephasingL gamma) h) rho
      = rho + (h : ℂ) • ((gamma / 2 : ℂ) • (sigmaZ * rho * sigmaZ - rho))
        + ((h : ℂ) * (h : ℂ) * ((gamma : ℂ) / 4) * ((gamma : ℂ) / 4)) • rho := by
  have hH0 : (0 : Operator).IsHermitian := isHermitian_zero
  have hgsqrt : ((Real.sqrt (gamma / 2) : ℂ)) * ((Real.sqrt (gamma / 2) : ℂ))
      = (gamma / 2 : ℂ) := by
    push_cast
    exact mod_cast Real.mul_self_sqrt (by linarith)
  have hstarL : star ((Real.sqrt (gamma / 2) : ℂ)) = ((Real.sqrt (gamma / 2) : ℂ)) := by
    rw [Complex.star_def, Complex.conj_ofReal]
  have hstarZ : star sigmaZ = sigmaZ := sigmaZ_hermitian.star_eq
  have hsum : ∑ i, star (dephasingL gamma i) * dephasingL gamma i
      = (gamma / 2 : ℂ) • 1 := by
    rw [Fin.sum_univ_one]
    simp only [dephasingL]
    rw [Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
      ← Matrix.star_eq_conjTranspose, Complex.star_def, Complex.conj_ofReal, hstarZ]
    rw [smul_mul_assoc, mul_smul_comm, smul_smul, hgsqrt, sigmaZ_mul_sigmaZ]
  rw [eulerLindbladStep_eq 0 hH0 (dephasingL gamma) h hh rho, dephasing_gen gamma hg rho,
    smul_zero, smul_zero, zero_add, hsum]
  have hW : (1 / 2 : ℂ) • ((gamma / 2 : ℂ) • (1 : Operator)) = ((gamma : ℂ) / 4) • 1 := by
    rw [smul_smul]
    congr 1
    push_cast
    ring
  rw [hW]
  simp only [smul_mul_assoc, one_mul, mul_one, mul_smul_comm, smul_smul]
  module

/-- The dephasing Euler step is completely positive for every ancilla
dimension — the Phase 1 lemma re-instantiated at the dephasing family. -/
theorem dephasing_step_completely_positive (gamma : ℝ) (h : ℝ) {m : ℕ}
    {rho' : Matrix (Fin m × Fin 2) (Fin m × Fin 2) ℂ}
    (hρ' : PositiveSemidefinite rho') :
    PositiveSemidefinite (krausMapExt (eulerLindbladStep 0 (dephasingL gamma) h) rho') :=
  krausMap_completely_positive _ hρ'

/-! ### Amplitude damping -/

/-- The amplitude-damping jump-operator family: a single jump operator
`√γ • σ⁻` with zero Hamiltonian. -/
noncomputable def amplitudeDampingL (gamma : ℝ) : Fin 1 → Operator :=
  fun _ => ((Real.sqrt gamma : ℂ)) • sigmaMinus

/-- The GKLS generator of amplitude damping is the textbook
population-flow map: `𝓛(ρ) = γ(σ⁻ ρ σ⁺ − ½ {P₁, ρ})`. -/
theorem amplitudeDamping_gen (gamma : ℝ) (hg : 0 ≤ gamma) (rho : Operator) :
    lindbladRhsFam 0 (amplitudeDampingL gamma) rho
      = (gamma : ℂ) • (sigmaMinus * rho * sigmaPlus
          - (1 / 2 : ℂ) • Harmonia.anticommutator projExcited rho) := by
  have hgsqrt : ((Real.sqrt gamma : ℂ)) * ((Real.sqrt gamma : ℂ)) = (gamma : ℂ) := by
    push_cast
    exact mod_cast Real.mul_self_sqrt hg
  have hstarL : star ((Real.sqrt gamma : ℂ)) = ((Real.sqrt gamma : ℂ)) := by
    rw [Complex.star_def, Complex.conj_ofReal]
  have hstarLZ : star (amplitudeDampingL gamma 0)
      = ((Real.sqrt gamma : ℂ)) • sigmaPlus := by
    simp only [amplitudeDampingL]
    rw [Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
      ← Matrix.star_eq_conjTranspose, Complex.star_def, Complex.conj_ofReal,
      star_sigmaMinus]
  have hLL : star (amplitudeDampingL gamma 0) * amplitudeDampingL gamma 0
      = (gamma : ℂ) • projExcited := by
    rw [hstarLZ]
    simp only [amplitudeDampingL]
    rw [smul_mul_assoc, mul_smul_comm, smul_smul, hgsqrt, sigmaPlus_mul_sigmaMinus]
  have hLrL : amplitudeDampingL gamma 0 * rho * star (amplitudeDampingL gamma 0)
      = (gamma : ℂ) • (sigmaMinus * rho * sigmaPlus) := by
    rw [hstarLZ]
    simp only [amplitudeDampingL, smul_mul_assoc, mul_smul_comm, smul_smul]
    rw [hgsqrt]
  simp only [lindbladRhsFam, Harmonia.commutator, zero_mul, mul_zero, sub_zero,
    smul_zero, add_zero, Fin.sum_univ_one, Harmonia.dissipator, hLrL, hLL,
    Harmonia.anticommutator, smul_mul_assoc, mul_smul_comm, smul_smul, one_mul, mul_one]
  module

/-- Amplitude damping fixes the ground state: the pure ground projector
is a stationary point of the flow. -/
theorem amplitudeDamping_fixes_ground (gamma : ℝ) (hg : 0 ≤ gamma) :
    lindbladRhsFam 0 (amplitudeDampingL gamma) projGround = 0 := by
  rw [amplitudeDamping_gen gamma hg, sigmaMinus_mul_mul_sigmaPlus]
  simp only [Harmonia.anticommutator, projExcited_mul_projGround,
    projGround_mul_projExcited, add_zero, smul_zero, sub_zero]
  simp [projGround]

/-- The excited population decays: the `(1,1)` entry of the first-order
step is `(1 − γh) • ρ₁₁`. -/
theorem amplitudeDamping_excited_decays (gamma : ℝ) (hg : 0 ≤ gamma) (h : ℝ)
    (rho : Operator) :
    (rho + (h : ℂ) • lindbladRhsFam 0 (amplitudeDampingL gamma) rho) 1 1
      = ((1 - h * gamma : ℝ) : ℂ) * rho 1 1 := by
  rw [amplitudeDamping_gen gamma hg, sigmaMinus_mul_mul_sigmaPlus]
  have hP1 : (projExcited * rho) 1 1 = rho 1 1 := by
    simp [projExcited, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]
  have hP2 : (rho * projExcited) 1 1 = rho 1 1 := by
    simp [projExcited, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]
  have hPG : projGround 1 1 = 0 := by simp [projGround]
  simp only [Harmonia.anticommutator, Matrix.add_apply, Matrix.smul_apply,
    Matrix.sub_apply, hP1, hP2, hPG, mul_zero, zero_sub]
  push_cast
  ring

/-- The ground population grows by exactly the excited population that
decayed: the first-order step preserves total population. -/
theorem amplitudeDamping_ground_grows (gamma : ℝ) (hg : 0 ≤ gamma) (h : ℝ)
    (rho : Operator) :
    (rho + (h : ℂ) • lindbladRhsFam 0 (amplitudeDampingL gamma) rho) 0 0
      = rho 0 0 + ((h * gamma : ℝ) : ℂ) * rho 1 1 := by
  rw [amplitudeDamping_gen gamma hg, sigmaMinus_mul_mul_sigmaPlus]
  have hP3 : (projExcited * rho) 0 0 = 0 := by
    simp [projExcited, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]
  have hP4 : (rho * projExcited) 0 0 = 0 := by
    simp [projExcited, Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_two]
  have hPG : projGround 0 0 = 1 := by simp [projGround]
  simp only [Harmonia.anticommutator, Matrix.add_apply, Matrix.smul_apply,
    Matrix.sub_apply, hP3, hP4, hPG, one_mul, mul_zero, add_zero, zero_add, sub_zero]
  push_cast
  ring

/-- The amplitude-damping Euler step is completely positive for every
ancilla dimension — the Phase 1 lemma re-instantiated at the
amplitude-damping family. -/
theorem amplitudeDamping_step_completely_positive (gamma : ℝ) (h : ℝ) {m : ℕ}
    {rho' : Matrix (Fin m × Fin 2) (Fin m × Fin 2) ℂ}
    (hρ' : PositiveSemidefinite rho') :
    PositiveSemidefinite
      (krausMapExt (eulerLindbladStep 0 (amplitudeDampingL gamma) h) rho') :=
  krausMap_completely_positive _ hρ'

end Leibniz.Dissipatio
