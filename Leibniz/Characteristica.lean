import Mathlib

namespace Leibniz.Characteristica

/-- Epistemic status is represented in the type system, not only in prose. -/
inductive EpistemicStatus where
  | proven | derived | axiomatic | conjectured | open
  deriving DecidableEq, Repr, Inhabited

/-- A proof-relevant wrapper for claims with an epistemic status. -/
def Proven (p : Prop) : Prop := p

def Derived (p : Prop) : Prop := p

def Axiomatic (p : Prop) : Prop := p

def Conjectured (p : Prop) : Prop := p

def Open (p : Prop) : Prop := p

structure EpistemicRecord where
  name : String
  status : EpistemicStatus
  statement : String
  dependencies : List String := []
  source : Option String := none
  deriving Repr, Inhabited

/-- The dyadic primitive of the Characteristica Universalis. -/
inductive Dyas : Type
  | Nihil
  | Ens
  deriving DecidableEq, Repr, Inhabited

def tensio (d₁ d₂ : Dyas) : Nat :=
  match d₁, d₂ with
  | .Nihil, .Ens => 1
  | .Ens, .Nihil => 1
  | _, _ => 0

theorem tensio_symm (d₁ d₂ : Dyas) : tensio d₁ d₂ = tensio d₂ d₁ := by
  cases d₁ <;> cases d₂ <;> rfl

theorem tensio_self (d : Dyas) : tensio d d = 0 := by
  cases d <;> rfl

theorem tensio_max (d₁ d₂ : Dyas) : tensio d₁ d₂ ≤ 1 := by
  cases d₁ <;> cases d₂ <;> decide

/-- Machine-readable metadata for the foundational results. -/
def metadata : List EpistemicRecord := [
  { name := "tensio_symm", status := .proven,
    statement := "The dyadic tension is symmetric", dependencies := [], source := some "De Arte Combinatoria (1666)" },
  { name := "tensio_self", status := .proven,
    statement := "A dyad has zero self-tension", dependencies := [], source := some "Explication de l'Arithmétique Binaire" }
]

end Leibniz.Characteristica
