/-! Fixture for vkernel tests. `ok` is clean; the other two must be rejected. -/
theorem ok (n : Nat) : n + 0 = n := rfl
axiom cheat : False
theorem uses_axiom : 1 = 2 := cheat.elim
theorem uses_sorry : 1 = 2 := by sorry
