/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                 LEIBNIZ: SPATIUM RELATIVUM & MONADOLOGIA              ║
  ║       La Monadologie (1714) & Leibniz-Clarke Correspondence (1715)    ║
  ╚═══════════════════════════════════════════════════════════════════════╝
-/

import Leibniz.Characteristica

namespace Leibniz.SpatiumRelativum

open Leibniz.Characteristica

/--
  MONAS (The Monad): An indivisible point-like unit of relational information.
  Carries an identifier, an internal perceptual state, and an informational weight.
-/
structure Monas where
  index : Nat
  perceptio : Dyas
  pondus : Nat
  deriving DecidableEq, Repr

/--
  SPATIUM RELATIVUM: Distance is not an absolute coordinate interval,
  but the informational divergence between the perceptions of two monads.
-/
def distantia_relativa (m₁ m₂ : Monas) : Nat :=
  (m₁.pondus + m₂.pondus) * tensio m₁.perceptio m₂.perceptio

theorem distantia_symm (m₁ m₂ : Monas) : distantia_relativa m₁ m₂ = distantia_relativa m₂ m₁ := by
  unfold distantia_relativa
  rw [Nat.add_comm, tensio_symm]

theorem distantia_self (m : Monas) : distantia_relativa m m = 0 := by
  unfold distantia_relativa
  rw [tensio_self, Nat.mul_zero]

end Leibniz.SpatiumRelativum
