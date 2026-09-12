import Mathlib

namespace Leibniz.OpenProblems

structure OpenProblem where
  id : String
  title : String
  status : String
  dependencies : List String
  closureRequirement : String
  deriving Repr, Inhabited

def registry : List OpenProblem := [
  { id := "chiral-floor", title := "Derive the continuity floor from dynamics", status := "closed",
    dependencies := ["VisViva", "LexContinuitatis"],
    closureRequirement := "Closed 2026-09-12: chiFloor = 1/sqrt 2 is the tight universal floor of dyadic chiral dominance (Leibniz.VisViva.chiral_dominance_ge_floor, Leibniz.LexContinuitatis.chiFloor_is_dyadic_floor) — the equipartition bound of the vis viva, attained exactly when the dyad carries equal living force in both members (chiral_dominance_eq_floor_iff). chiFloor_lt_chiCeil promoted from axiom to theorem in the same pass." },
  { id := "lindblad-cp", title := "Complete positivity of the GKLS flow", status := "conjectured",
    dependencies := ["Harmonia"], closureRequirement := "A finite-dimensional Kraus or semigroup proof" },
  { id := "wilson-loop", title := "Path-ordered quantum-field holonomy", status := "conjectured",
    dependencies := ["SpatiumRelativum"], closureRequirement := "A connection and parallel-transport construction" }
]

end Leibniz.OpenProblems
