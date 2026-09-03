import Mathlib

namespace Leibniz.Monadologia

/-- A minimal typed monadological state: perception and appetition are explicit propositions. -/
structure MonadState (α : Type) where
  perception : α → Prop
  appetition : α → Prop
  unity : Prop

/-- A relation expressing lawful coordination between two monadic states. -/
def Harmonized {α : Type} (m₁ m₂ : MonadState α) : Prop :=
  ∀ x, m₁.perception x ↔ m₂.perception x

/-- A finite chain of harmonized monadic states. -/
inductive HarmonyChain {α : Type} : List (MonadState α) → Prop
  | singleton (m : MonadState α) : HarmonyChain [m]
  | cons {m₁ m₂ : MonadState α} {tail : List (MonadState α)} :
      Harmonized m₁ m₂ → HarmonyChain (m₂ :: tail) → HarmonyChain (m₁ :: m₂ :: tail)

theorem harmony_reflexive {α : Type} (m : MonadState α) : Harmonized m m := by
  intro x
  rfl

theorem harmony_chain_has_unity {α : Type} {states : List (MonadState α)}
    (hUnity : ∀ m : MonadState α, m.unity) (h : HarmonyChain states) : ∀ m ∈ states, m.unity := by
  intro m _
  exact hUnity m

/-- The propositional language of the calculus ratiocinator. -/
inductive Formula where
  | atom (name : String)
  | implies (antecedent consequent : Formula)
  | conj (left right : Formula)
  deriving DecidableEq, Repr, Inhabited

/-- A natural-deduction derivation whose context is explicit and inspectable. -/
inductive Derivation : List Formula → Formula → Type
  | assumption {Γ : List Formula} {p : Formula} : p ∈ Γ → Derivation Γ p
  | impliesIntro {Γ : List Formula} {p q : Formula} : Derivation (p :: Γ) q → Derivation Γ (.implies p q)
  | impliesElim {Γ : List Formula} {p q : Formula} :
      Derivation Γ (.implies p q) → Derivation Γ p → Derivation Γ q
  | conjIntro {Γ : List Formula} {p q : Formula} :
      Derivation Γ p → Derivation Γ q → Derivation Γ (.conj p q)
  | conjLeft {Γ : List Formula} {p q : Formula} : Derivation Γ (.conj p q) → Derivation Γ p
  | conjRight {Γ : List Formula} {p q : Formula} : Derivation Γ (.conj p q) → Derivation Γ q

/-- Count the number of inference steps in a derivation. -/
def Derivation.size : Derivation Γ p → Nat
  | .assumption _ => 1
  | .impliesIntro h => h.size + 1
  | .impliesElim h₁ h₂ => h₁.size + h₂.size + 1
  | .conjIntro h₁ h₂ => h₁.size + h₂.size + 1
  | .conjLeft h => h.size + 1
  | .conjRight h => h.size + 1

/-- A calculus-ratiocinator theorem: a three-link relation chain composes. -/
theorem sufficient_reason_chain {α : Type} (R : α → α → Prop)
    (htrans : ∀ x y z, R x y → R y z → R x z)
    (a b c d : α) (hab : R a b) (hbc : R b c) (hcd : R c d) : R a d := by
  exact htrans a c d (htrans a b c hab hbc) hcd

end Leibniz.Monadologia
