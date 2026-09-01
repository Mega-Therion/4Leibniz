/-
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║                      LEIBNIZ: CHARACTERISTICA UNIVERSALIS            ║
  ║  De Arte Combinatoria (1666) & Explication de l'Arithmétique Binaire ║
  ╚═══════════════════════════════════════════════════════════════════════╝
-/

namespace Leibniz.Characteristica

/-- 
  DYADICA: The fundamental binary primitive of existence.
  - `Nihil` (0): The Void / Ground State.
  - `Ens`   (1): Being / Unity / Coherent State.
  *Omnibus ex nihilo ducendis sufficit unum.*
-/
inductive Dyas : Type
  | Nihil : Dyas  -- 0 (Void / IO)
  | Ens   : Dyas  -- 1 (Unity / OI)
  deriving DecidableEq, Repr

/-- Dual State Tension Metric: Measures informational disparity between states. -/
def tensio (d₁ d₂ : Dyas) : Nat :=
  match d₁, d₂ with
  | Dyas.Nihil, Dyas.Ens   => 1
  | Dyas.Ens,   Dyas.Nihil => 1
  | _,          _          => 0

theorem tensio_symm (d₁ d₂ : Dyas) : tensio d₁ d₂ = tensio d₂ d₁ := by
  cases d₁ <;> cases d₂ <;> rfl

theorem tensio_self (d : Dyas) : tensio d d = 0 := by
  cases d <;> rfl

theorem tensio_max (d₁ d₂ : Dyas) : tensio d₁ d₂ ≤ 1 := by
  cases d₁ <;> cases d₂ <;> decide

end Leibniz.Characteristica
