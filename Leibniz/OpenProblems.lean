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
  { id := "chiral-floor", title := "Derive the continuity floor from dynamics", status := "open",
    dependencies := ["VisViva", "LexContinuitatis"], closureRequirement := "A first-principles physical derivation of 1/sqrt 2" },
  { id := "lindblad-cp", title := "Complete positivity of the GKLS flow", status := "conjectured",
    dependencies := ["Harmonia"], closureRequirement := "A finite-dimensional Kraus or semigroup proof" },
  { id := "wilson-loop", title := "Path-ordered quantum-field holonomy", status := "conjectured",
    dependencies := ["SpatiumRelativum"], closureRequirement := "A connection and parallel-transport construction" }
]

end Leibniz.OpenProblems
