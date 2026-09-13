/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                    LEIBNIZ: KRAUS (COMPLETE POSITIVITY)               ║
  ║          Phase 1 of the lindblad-cp attack — study 2026-09-12          ║
  ╚══════════════════════════════════════════════════════════════════════╝

Kraus-form quantum channels, proved completely positive.

Positive semidefiniteness over ℂ is phrased through the quadratic form
(`x* M x` is nonnegative real) because ℂ carries no ring order — this is
the inner-product phrasing the 2026-09-12 attack study recommended to
dodge the order friction that blocks `Matrix.PosSemidef` over ℂ.

Complete positivity then falls out of re-instantiating the same
positivity lemma at the composite index type `Fin m × ι`: tensoring a
Kraus map with the identity on an ancilla of any finite dimension is
again a Kraus map (the composite Kraus operators are the originals with
the identity on the ancilla factor), so positivity at the composite
type is complete positivity. `lindblad-cp` itself remains open in the
registry; this module establishes the Kraus half of the road.
-/

import Mathlib
import Leibniz.Harmonia

namespace Leibniz.Kraus

open Matrix Complex
open Kronecker

variable {ι : Type*} [Fintype ι]

/-! ### Positive semidefiniteness over ℂ, via the quadratic form -/

/-- Positive semidefiniteness for complex matrices, phrased via the
quadratic form: Hermitian, and `x* M x` nonnegative real for every `x`.
(The reality of the quadratic form is a separate theorem,
`quadForm_real`.) -/
def PositiveSemidefinite (M : Matrix ι ι ℂ) : Prop :=
  M.IsHermitian ∧ ∀ x : ι → ℂ, 0 ≤ (star x ⬝ᵥ (M *ᵥ x)).re

/-- The quadratic form of a Hermitian complex matrix is real. -/
theorem quadForm_real {M : Matrix ι ι ℂ} (hM : M.IsHermitian) (x : ι → ℂ) :
    (star x ⬝ᵥ (M *ᵥ x)).im = 0 := by
  have h : star (star x ⬝ᵥ (M *ᵥ x)) = star x ⬝ᵥ (M *ᵥ x) := by
    rw [show star x ⬝ᵥ (M *ᵥ x) = (star x ᵥ* M) ⬝ᵥ x from Matrix.dotProduct_mulVec _ _ _,
      ← Matrix.star_dotProduct_star, Matrix.star_vecMul, star_star, hM.eq,
      ← Matrix.dotProduct_mulVec]
  exact Complex.conj_eq_iff_im.mp h

protected theorem PositiveSemidefinite.zero : PositiveSemidefinite (0 : Matrix ι ι ℂ) :=
  ⟨isHermitian_zero, fun x => by simp⟩

protected theorem PositiveSemidefinite.add {A B : Matrix ι ι ℂ}
    (hA : PositiveSemidefinite A) (hB : PositiveSemidefinite B) :
    PositiveSemidefinite (A + B) :=
  ⟨hA.1.add hB.1, fun x => by
    simpa only [Matrix.add_mulVec, dotProduct_add, Complex.add_re] using
      add_nonneg (hA.2 x) (hB.2 x)⟩

/-- A finite sum of positive-semidefinite matrices is positive semidefinite. -/
theorem PositiveSemidefinite.sum {δ : Type*} {s : Finset δ} {f : δ → Matrix ι ι ℂ}
    (h : ∀ i ∈ s, PositiveSemidefinite (f i)) :
    PositiveSemidefinite (∑ i ∈ s, f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using PositiveSemidefinite.zero
  | insert x s hx ih =>
      rw [Finset.sum_insert hx]
      exact PositiveSemidefinite.add (h x (Finset.mem_insert_self _ _))
        (ih fun i hi => h i (Finset.mem_insert_of_mem hi))

/-- Conjugation preserves positive semidefiniteness:
`A ⪰ 0 → B A B* ⪰ 0`, with `B` allowed to be rectangular. -/
theorem PositiveSemidefinite.mul_mul_conjTranspose {A : Matrix ι ι ℂ}
    (hA : PositiveSemidefinite A) {κ : Type*} [Fintype κ] (B : Matrix κ ι ℂ) :
    PositiveSemidefinite (B * A * Bᴴ) := by
  refine ⟨isHermitian_mul_mul_conjTranspose B hA.1, fun x => ?_⟩
  -- the quadratic form of `B A B*` at `x` is the quadratic form of `A` at `B* x`
  have hs : star (Bᴴ *ᵥ x) = star x ᵥ* B := by
    rw [Matrix.star_mulVec, Matrix.conjTranspose_conjTranspose]
  have key : star x ⬝ᵥ ((B * A * Bᴴ) *ᵥ x)
      = star (Bᴴ *ᵥ x) ⬝ᵥ (A *ᵥ (Bᴴ *ᵥ x)) := by
    rw [← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, Matrix.dotProduct_mulVec, hs]
  rw [key]
  exact hA.2 (Bᴴ *ᵥ x)

/-! ### Kraus maps -/

/-- A Kraus map: `Φ(ρ) = Σᵢ Kᵢ ρ Kᵢ*`. -/
def krausMap {n : ℕ} (K : Fin n → Matrix ι ι ℂ) (ρ : Matrix ι ι ℂ) :
    Matrix ι ι ℂ := ∑ i, K i * ρ * star (K i)

/-- Kraus maps are positive: they send positive semidefinite matrices to
positive semidefinite matrices. -/
theorem krausMap_positive {n : ℕ} (K : Fin n → Matrix ι ι ℂ) {ρ : Matrix ι ι ℂ}
    (hρ : PositiveSemidefinite ρ) : PositiveSemidefinite (krausMap K ρ) :=
  PositiveSemidefinite.sum fun i _ => PositiveSemidefinite.mul_mul_conjTranspose hρ (K i)

/-- A unital Kraus family (`Σᵢ Kᵢ* Kᵢ = 1`) preserves the trace. -/
theorem krausMap_trace_preserving {n : ℕ} (K : Fin n → Harmonia.Operator)
    (hK : ∑ i, star (K i) * K i = 1) (ρ : Harmonia.Operator) :
    trace (krausMap K ρ) = trace ρ := by
  have key : ∀ i : Fin n,
      trace (K i * ρ * star (K i)) = trace (ρ * (star (K i) * K i)) :=
    fun i => Harmonia.trace_mul_mul_cycle ρ (K i) (star (K i))
  rw [krausMap, Matrix.trace_sum, Finset.sum_congr rfl (fun i _ => key i),
    ← Matrix.trace_sum, ← Matrix.mul_sum, hK, Matrix.mul_one]

/-! ### Complete positivity -/

/-- The star of a Kronecker product is the Kronecker product of the stars. -/
theorem star_kronecker {l n : Type*} (X : Matrix l l ℂ) (Y : Matrix n n ℂ) :
    star (X ⊗ₖ Y) = star X ⊗ₖ star Y := by
  rw [star_eq_conjTranspose, Matrix.conjTranspose_kronecker, star_eq_conjTranspose,
    star_eq_conjTranspose]

/-- The Kraus map tensored with the identity on an ancilla of dimension
`m`. The composite Kraus operators are the originals with the identity
on the ancilla factor — the textbook tensor extension of a Kraus map. -/
def krausMapExt {n m : ℕ} (K : Fin n → Matrix ι ι ℂ)
    (ρ' : Matrix (Fin m × ι) (Fin m × ι) ℂ) : Matrix (Fin m × ι) (Fin m × ι) ℂ :=
  krausMap (fun i => (1 : Matrix (Fin m) (Fin m) ℂ) ⊗ₖ K i) ρ'

/-- **A Kraus map is completely positive.** For every ancilla dimension
`m`, the extension `Φ ⊗ idₘ` sends positive semidefinite matrices on the
composite space to positive semidefinite matrices. The extension is
itself a Kraus map, so this is the positivity lemma re-instantiated at
the composite index type `Fin m × ι`. -/
theorem krausMap_completely_positive {n : ℕ} (K : Fin n → Matrix ι ι ℂ) {m : ℕ}
    {ρ' : Matrix (Fin m × ι) (Fin m × ι) ℂ} (hρ' : PositiveSemidefinite ρ') :
    PositiveSemidefinite (krausMapExt K ρ') :=
  krausMap_positive _ hρ'

/-! ### The extension on product states -/

/-- On product states the tensor extension acts factorwise:
`(Φ ⊗ id)(A ⊗ ρ) = A ⊗ Φ(ρ)`. -/
theorem krausMapExt_product_state {n : ℕ} (K : Fin n → Matrix ι ι ℂ) {m : ℕ}
    (A : Matrix (Fin m) (Fin m) ℂ) (ρ : Matrix ι ι ℂ) :
    krausMapExt K (A ⊗ₖ ρ) = A ⊗ₖ krausMap K ρ := by
  have hop : ∀ i : Fin n, ((1 : Matrix (Fin m) (Fin m) ℂ) ⊗ₖ K i) * (A ⊗ₖ ρ)
        * star ((1 : Matrix (Fin m) (Fin m) ℂ) ⊗ₖ K i)
      = A ⊗ₖ (K i * ρ * star (K i)) := by
    intro i
    rw [star_kronecker, star_one,
      ← Matrix.mul_kronecker_mul, ← Matrix.mul_kronecker_mul]
    simp
  rw [krausMapExt, krausMap, krausMap]
  rw [Finset.sum_congr rfl (fun i _ => hop i)]
  ext ⟨a, s⟩ ⟨a', s'⟩
  simp only [Matrix.kronecker_apply, Matrix.sum_apply]
  rw [Finset.mul_sum]

/-- On product states, the extension of a unital Kraus family preserves
the total trace: `trace ((Φ ⊗ id)(A ⊗ ρ)) = trace A * trace ρ`. -/
theorem krausMapExt_trace_preserving_product_state {n m : ℕ}
    (K : Fin n → Harmonia.Operator) (hK : ∑ i, star (K i) * K i = 1)
    (A : Matrix (Fin m) (Fin m) ℂ) (ρ : Harmonia.Operator) :
    trace (krausMapExt K (A ⊗ₖ ρ)) = trace A * trace ρ := by
  rw [krausMapExt_product_state, Matrix.trace_kronecker, krausMap_trace_preserving K hK]

/-! ### Phase 2a: the Euler-discrete Lindblad step as a Kraus map

The bridge from the GKLS generator to the Kraus machinery of Phase 1:
with `W = iH + ½ Σ Lᵢ*Lᵢ` and step size `h ≥ 0`, the Euler-discrete
Lindblad step is the Kraus family `K₀ = 1 − h•W`, `Kᵢ₊₁ = √h • Lᵢ`.
Its action is EXACTLY `ρ + h • 𝓛(ρ) + h² • (W ρ W*)`, where `𝓛` is the
GKLS generator: the flow's first-order term is the generator itself,
and the second-order residual is again a Kraus-form completely-positive
contribution, so the discrete step is completely positive for every
step size.
-/

/-- The GKLS generator for a finite jump-operator family:
`𝓛(ρ) = −i [H, ρ] + Σᵢ (Lᵢ ρ Lᵢ* − ½ {Lᵢ* Lᵢ, ρ})`. -/
noncomputable def lindbladRhsFam {k : ℕ} (H : Harmonia.Operator)
    (L : Fin k → Harmonia.Operator) (ρ : Harmonia.Operator) :
    Harmonia.Operator :=
  (-Complex.I) • Harmonia.commutator H ρ + ∑ i, Harmonia.dissipator (L i) ρ

/-- The Euler-discrete Lindblad step as a Kraus family over `Fin (k+1)`:
the contractive branch `K₀ = 1 − h•(iH + ½ Σ Lᵢ*Lᵢ)` followed by the
jump branches `Kᵢ₊₁ = √h • Lᵢ`. -/
noncomputable def eulerLindbladStep {k : ℕ} (H : Harmonia.Operator)
    (L : Fin k → Harmonia.Operator) (h : ℝ) : Fin (k + 1) → Harmonia.Operator :=
  Fin.cons (1 - (h : ℂ) • (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i))
    (fun i => (Real.sqrt h : ℂ) • L i)

/-- The Euler-discrete Lindblad step is exactly the GKLS flow to first
order: `krausMap (eulerLindbladStep H L h) ρ = ρ + h • 𝓛(ρ) + h² • (W ρ W*)`,
with `W = iH + ½ Σ Lᵢ*Lᵢ`. -/
theorem eulerLindbladStep_eq {k : ℕ} (H : Harmonia.Operator) (hH : H.IsHermitian)
    (L : Fin k → Harmonia.Operator) (h : ℝ) (hh : 0 ≤ h) (ρ : Harmonia.Operator) :
    krausMap (eulerLindbladStep H L h) ρ
      = ρ + (h : ℂ) • lindbladRhsFam H L ρ
        + ((h : ℂ) * (h : ℂ)) • ((Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i) * ρ
            * (-Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i)) := by
  have hG : star (∑ i, star (L i) * L i) = ∑ i, star (L i) * L i := by
    simp [star_sum, star_mul, star_star]
  have hstarW : star (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i)
      = -Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i := by
    have hstarI : star (Complex.I : ℂ) = -Complex.I := by
      rw [Complex.star_def]; exact Complex.conj_I
    have h1 : star (Complex.I • H) = -Complex.I • H := by
      rw [Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
        ← Matrix.star_eq_conjTranspose, hH.star_eq, hstarI]
    have h2 : star ((1 / 2 : ℂ) • ∑ i, star (L i) * L i)
        = (1 / 2 : ℂ) • ∑ i, star (L i) * L i := by
      rw [Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
        ← Matrix.star_eq_conjTranspose, hG, star_div₀, star_one, star_ofNat]
    rw [star_add, h1, h2]
  have hstarK : star (1 - (h : ℂ) • (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i))
      = 1 - (h : ℂ) • (-Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i) := by
    rw [star_sub, star_one, Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
      Complex.star_def, Complex.conj_ofReal,
      ← Matrix.star_eq_conjTranspose, hstarW]
  have hjump : ∀ i : Fin k,
      ((Real.sqrt h : ℂ) • L i) * ρ * star ((Real.sqrt h : ℂ) • L i)
        = (h : ℂ) • (L i * ρ * star (L i)) := by
    intro i
    rw [Matrix.star_eq_conjTranspose, Matrix.conjTranspose_smul,
      ← Matrix.star_eq_conjTranspose, Complex.star_def, Complex.conj_ofReal]
    simp only [smul_mul_assoc, mul_smul_comm, smul_smul]
    rw [← Complex.ofReal_mul, Real.mul_self_sqrt hh]
  have hsplit : krausMap (eulerLindbladStep H L h) ρ
      = (1 - (h : ℂ) • (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i)) * ρ
          * star (1 - (h : ℂ) • (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i))
        + ∑ i, ((Real.sqrt h : ℂ) • L i) * ρ * star ((Real.sqrt h : ℂ) • L i) := by
    rw [krausMap, eulerLindbladStep, Fin.sum_univ_succ]
    simp only [Fin.cons_zero, Fin.cons_succ]
  have key : ∀ a b : Harmonia.Operator,
      (1 - a) * ρ * (1 - b) = ρ - ρ * b - a * ρ + a * ρ * b := by
    intro a b
    noncomm_ring
  have hexp : (1 - (h : ℂ) • (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i)) * ρ
      * (1 - (h : ℂ) • (-Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i))
      = ρ - (h : ℂ) • ((Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i) * ρ
          + ρ * (-Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i))
        + ((h : ℂ) * (h : ℂ)) • ((Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i) * ρ
            * (-Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i)) := by
    rw [key]
    simp only [smul_mul_assoc, mul_smul_comm, smul_smul]
    rw [smul_add]
    abel_nf
  have hWsplit : (Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i) * ρ
      + ρ * (-Complex.I • H + (1 / 2 : ℂ) • ∑ i, star (L i) * L i)
      = Complex.I • (H * ρ) + -Complex.I • (ρ * H)
        + ∑ i, (1 / 2 : ℂ) • Harmonia.anticommutator (star (L i) * L i) ρ := by
    simp only [add_mul, mul_add, smul_add, smul_mul_assoc, mul_smul_comm,
      Finset.smul_sum, Finset.sum_mul, Finset.mul_sum, Finset.sum_add_distrib,
      Harmonia.anticommutator]
    abel_nf
  have hsign : Complex.I • (H * ρ) = -(-Complex.I • (H * ρ)) := by
    rw [neg_smul, neg_neg]
  rw [hsplit, hstarK, Finset.sum_congr rfl (fun i _ => hjump i), hexp, hWsplit, hsign]
  simp only [smul_add, smul_sub, smul_neg, Finset.smul_sum, Finset.sum_sub_distrib,
    smul_smul, lindbladRhsFam, Harmonia.commutator, Harmonia.dissipator,
    Harmonia.anticommutator]
  abel_nf

end Leibniz.Kraus

