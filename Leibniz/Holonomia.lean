/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                    LEIBNIZ: HOLONOMIA (WILSON LOOPS)                  ║
  ║           Closing the wilson-loop open problem — 2026-09-13          ║
  ╚══════════════════════════════════════════════════════════════════════╝

The registry's `wilson-loop` entry asked for "a connection and
parallel-transport construction". This module builds it: a discrete
lattice gauge connection, the path-ordered product of its parallel
transporters (the holonomy), and the two real theorems of the subject:

  * path ordering — the holonomy of a concatenated path is the ordered
    product of the holonomies of its parts (`holonomy_path_ordered`);
  * gauge invariance of the Wilson loop — for a closed path, the trace
    of the holonomy is invariant under every gauge transformation
    (`wilson_loop_gauge_invariant`), the endpoint gauge factors
    telescoping away under the cyclic trace.

The previously vacuous `holonomy_path_ordered : True` axiom (Calculemus)
is retired; this module carries its honest replacement.
-/

import Mathlib
import Leibniz.SpatiumRelativum

namespace Leibniz.Holonomia

/-! ### The discrete parallel-transport construction -/

/-- A lattice gauge connection: a parallel transporter `U i j` on every
oriented link `j → i` of the lattice `Fin N`, valued in `n×n` complex
matrices. -/
def Connection (n N : ℕ) := Fin N → Fin N → Matrix (Fin n) (Fin n) ℂ

/-- The endpoint of the path that starts at `i₀` and then visits
`sites`: the site the transported charge arrives at. -/
def endOf {N : ℕ} : Fin N → List (Fin N) → Fin N
  | i₀, [] => i₀
  | _, i₁ :: rest => endOf i₁ rest

/-- The path-ordered product of parallel transporters along the path
`i₀ → i₁ → …`: `holonomyFrom U i₀ [i₁, i₂] = U i₀ i₁ * U i₁ i₂`. The
empty path transports trivially — the identity. -/
def holonomyFrom {n N : ℕ} (U : Connection n N) :
    Fin N → List (Fin N) → Matrix (Fin n) (Fin n) ℂ
  | _, [] => 1
  | i₀, i₁ :: rest => U i₀ i₁ * holonomyFrom U i₁ rest

/-- **Path ordering.** The holonomy of a concatenated path is the
ordered product of the holonomies of its parts: transporting along
`p` and then along `q` composes the two transporters in path order,
with `q` starting where `p` ends. This is the honest replacement for
the retired vacuous `holonomy_path_ordered` axiom. -/
theorem holonomy_path_ordered {n N : ℕ} (U : Connection n N) (i₀ : Fin N)
    (p q : List (Fin N)) :
    holonomyFrom U i₀ (p ++ q)
      = holonomyFrom U i₀ p * holonomyFrom U (endOf i₀ p) q := by
  induction p generalizing i₀ with
  | nil => simp [holonomyFrom, endOf, mul_one]
  | cons i p ih =>
      simp only [List.cons_append, holonomyFrom, endOf, ih, mul_assoc]

/-! ### The flat connection -/

/-- The flat (trivial) connection: every link transports trivially. -/
def flatConnection {n N : ℕ} : Connection n N := fun _ _ => 1

/-- Transport along any path is trivial for the flat connection. -/
theorem holonomy_flat {n N : ℕ} (i₀ : Fin N) (sites : List (Fin N)) :
    holonomyFrom (flatConnection : Connection n N) i₀ sites = 1 := by
  induction sites generalizing i₀ with
  | nil => rfl
  | cons i sites ih => simp [holonomyFrom, ih, mul_one, flatConnection]

/-- The Wilson loop of the flat connection around any closed path is
the matrix dimension: `tr 1 = n`. -/
theorem wilson_loop_flat {n N : ℕ} (i₀ : Fin N) (sites : List (Fin N)) :
    Matrix.trace (holonomyFrom (flatConnection : Connection n N) i₀ sites)
      = (Fintype.card (Fin n) : ℂ) := by
  rw [holonomy_flat, Matrix.trace_one, Fintype.card_fin]

/-! ### Gauge transformations -/

/-- A gauge transformation acts on a connection by conjugating every
link transporter: `U i j ↦ g i * U i j * (g j)⁻¹`, with `g` a unit at
every site. -/
def gaugeTransform {n N : ℕ} (U : Connection n N)
    (g : Fin N → (Matrix (Fin n) (Fin n) ℂ)ˣ) : Connection n N :=
  fun i j => (g i : Matrix (Fin n) (Fin n) ℂ) * U i j * (g j)⁻¹

/-- Gauge transformations conjugate the holonomy: the interior gauge
factors telescope away pairwise, leaving only the factors at the
path's endpoints. -/
theorem holonomy_gauge {n N : ℕ} (U : Connection n N)
    (g : Fin N → (Matrix (Fin n) (Fin n) ℂ)ˣ) (i₀ : Fin N)
    (sites : List (Fin N)) :
    holonomyFrom (gaugeTransform U g) i₀ sites
      = (g i₀ : Matrix (Fin n) (Fin n) ℂ) * holonomyFrom U i₀ sites
          * (g (endOf i₀ sites))⁻¹ := by
  induction sites generalizing i₀ with
  | nil =>
      simp [holonomyFrom, endOf, mul_one, Units.mul_inv]
  | cons i sites ih =>
      have hlink : gaugeTransform U g i₀ i
          = (g i₀ : Matrix (Fin n) (Fin n) ℂ) * U i₀ i * (g i)⁻¹ := rfl
      have hcancel : ∀ (X Y W : Matrix (Fin n) (Fin n) ℂ)
          (u : (Matrix (Fin n) (Fin n) ℂ)ˣ),
          X * (↑u⁻¹ : Matrix (Fin n) (Fin n) ℂ)
            * ((↑u : Matrix (Fin n) (Fin n) ℂ) * Y * W) = X * Y * W := by
        intro X Y W u
        rw [mul_assoc X (↑u⁻¹ : Matrix (Fin n) (Fin n) ℂ)
            ((↑u : Matrix (Fin n) (Fin n) ℂ) * Y * W),
          mul_assoc (↑u : Matrix (Fin n) (Fin n) ℂ) Y W,
          ← mul_assoc (↑u⁻¹ : Matrix (Fin n) (Fin n) ℂ)
            (↑u : Matrix (Fin n) (Fin n) ℂ) (Y * W),
          Units.inv_mul, one_mul, mul_assoc X Y W]
      rw [holonomyFrom, holonomyFrom, endOf, hlink, ih i, hcancel,
        mul_assoc ((g i₀ : Matrix (Fin n) (Fin n) ℂ)) (U i₀ i)
          (holonomyFrom U i sites)]

/-- **The Wilson loop is gauge invariant.** Around a closed path — one
that returns to its start — the trace of the holonomy is unchanged by
any gauge transformation: the conjugating factors at the base point
cancel under the cyclic trace. -/
theorem wilson_loop_gauge_invariant {n N : ℕ} (U : Connection n N)
    (g : Fin N → (Matrix (Fin n) (Fin n) ℂ)ˣ) (i₀ : Fin N)
    (sites : List (Fin N)) (hclosed : endOf i₀ sites = i₀) :
    Matrix.trace (holonomyFrom (gaugeTransform U g) i₀ sites)
      = Matrix.trace (holonomyFrom U i₀ sites) := by
  rw [holonomy_gauge U g i₀ sites, hclosed, Matrix.trace_mul_comm,
    ← mul_assoc, Units.inv_mul, one_mul]

end Leibniz.Holonomia
