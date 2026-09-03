import Mathlib

namespace Leibniz.Epistemic

/-- Epistemic statuses form a finite, ordered certainty lattice. -/
inductive Status where
  | open
  | conjectured
  | axiomatic
  | derived
  | proven
  deriving DecidableEq, Repr, Inhabited

namespace Status

def rank : Status → Nat
  | .open => 0
  | .conjectured => 1
  | .axiomatic => 2
  | .derived => 3
  | .proven => 4

def le (a b : Status) : Prop := rank a ≤ rank b

instance : LE Status := ⟨le⟩

def join (a b : Status) : Status := if rank a ≤ rank b then b else a
def meet (a b : Status) : Status := if rank a ≤ rank b then a else b

theorem le_refl (a : Status) : a ≤ a := by
  change rank a ≤ rank a
  exact Nat.le_refl _
theorem le_trans {a b c : Status} : a ≤ b → b ≤ c → a ≤ c := by
  intro hab hbc
  exact Nat.le_trans hab hbc

theorem join_upper_left (a b : Status) : a ≤ join a b := by
  unfold join
  split
  · exact ‹rank a ≤ rank b›
  · exact le_refl a

theorem join_upper_right (a b : Status) : b ≤ join a b := by
  unfold join
  split
  · exact le_refl b
  · exact Nat.le_of_not_ge ‹¬ rank a ≤ rank b›

theorem meet_lower_left (a b : Status) : meet a b ≤ a := by
  unfold meet
  split
  · exact le_refl a
  · exact Nat.le_of_not_ge ‹¬ rank a ≤ rank b›

theorem meet_lower_right (a b : Status) : meet a b ≤ b := by
  unfold meet
  split
  · exact Nat.le_trans (by rfl) ‹rank a ≤ rank b›
  · exact le_refl b

end Status

inductive EvidenceKind where
  | logical | empirical | historical | computational
  deriving DecidableEq, Repr, Inhabited

structure Assumption where
  id : String
  proposition : Prop
  kind : EvidenceKind
  rationale : String := ""
  deriving Inhabited

structure AssumptionContext where
  name : String
  assumptions : List Assumption := []
  deriving Inhabited

namespace AssumptionContext

def ids (ctx : AssumptionContext) : List String := ctx.assumptions.map Assumption.id

def contains (ctx : AssumptionContext) (id : String) : Bool := id ∈ ctx.ids

def add (ctx : AssumptionContext) (a : Assumption) : AssumptionContext :=
  { ctx with assumptions := a :: ctx.assumptions }

end AssumptionContext

/-- Evidence is indexed by both the declared status and the proposition. -/
inductive Evidence : Status → Prop → Type
  | proven {p : Prop} : p → Evidence .proven p
  | derived {p : Prop} : p → Evidence .derived p
  | axiomatic {p : Prop} : Evidence .axiomatic p
  | conjectured {p : Prop} : Evidence .conjectured p
  | open {p : Prop} : Evidence .open p

structure SourceRef where
  id : String
  locator : String
  deriving Repr, Inhabited

/-- A proof-carrying argument whose epistemic status is part of its type. -/
structure ArgumentBundle (p : Prop) (s : Status) where
  evidence : Evidence s p
  context : AssumptionContext := { name := "anonymous" }
  dependencies : List String := []
  sources : List SourceRef := []
  statement : String := ""
  fingerprint : String := ""

abbrev ProvenArgument (p : Prop) := ArgumentBundle p .proven
abbrev DerivedArgument (p : Prop) := ArgumentBundle p .derived

/-- Extract a proposition from a proven argument. -/
theorem ProvenArgument.proof {p : Prop} (a : ProvenArgument p) : p :=
  match a.evidence with
  | .proven h => h

/-- A verified argument can be safely transported to a weaker status. -/
def ProvenArgument.weaken {p : Prop} (a : ProvenArgument p) : DerivedArgument p :=
  { evidence := .derived a.proof, context := a.context, dependencies := a.dependencies,
    sources := a.sources, statement := a.statement, fingerprint := a.fingerprint }

/-- The status of a bundle is queryable without inspecting its proof term. -/
def statusOf {p : Prop} {s : Status} (_ : ArgumentBundle p s) : Status := s

end Leibniz.Epistemic
