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
  { id := "lindblad-cp", title := "Complete positivity of the GKLS flow", status := "closed",
    dependencies := ["Harmonia", "Kraus"],
    closureRequirement := "Closed 2026-09-13: the vacuous axiom (forall n, 0 < n -> True) was retired and replaced by Leibniz.Kraus.lindblad_completely_positive — every Euler-discrete Lindblad step of a GKLS system with Hermitian Hamiltonian is completely positive at every ancilla dimension. Route: Kraus maps CP (krausMap_completely_positive, Phase 1) + the Euler bridge (eulerLindbladStep_eq, Phase 2a) + both paradigm channels instantiated (Leibniz.Dissipatio, Phase 2b: dephasing and amplitude damping). Companions: lindbladRhsFam_trace_zero and eulerLindbladStep_trace give exact first-order trace preservation with an explicit Kraus-form h^2 residual." },
  { id := "wilson-loop", title := "Path-ordered quantum-field holonomy", status := "conjectured",
    dependencies := ["SpatiumRelativum"], closureRequirement := "A connection and parallel-transport construction" }
]

end Leibniz.OpenProblems
