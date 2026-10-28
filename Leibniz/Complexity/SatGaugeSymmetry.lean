/-!
# Gauge Symmetry and Sign Reversal in Boolean Satisfiability

Formal verification of the exact sign-reversal gauge symmetry of Boolean formulas:
For any Boolean formula F, assignment a, and polarity mask g:
  literal_val (flip_lit g L) (a ⊕ g) = literal_val L a
Consequently:
  clause_val (flip_clause g C) (a ⊕ g) = clause_val C a
  formula_val (flip_formula g F) (a ⊕ g) = formula_val F a
  violated_clauses (flip_formula g F) (a ⊕ g) = violated_clauses F a
-/

namespace SatGauge

/-- A literal over n variables: variable index and polarity (true for positive, false for negated). -/
structure Literal (n : Nat) where
  var : Fin n
  polarity : Bool
deriving DecidableEq, Repr

/-- An assignment maps each variable index to a boolean truth value. -/
def Assignment (n : Nat) := Fin n → Bool

/-- A polarity mask maps each variable index to a boolean flip flag. -/
def PolarityMask (n : Nat) := Fin n → Bool

/-- Evaluating a literal under an assignment. -/
def evalLit {n : Nat} (lit : Literal n) (a : Assignment n) : Bool :=
  !(xor (a lit.var) lit.polarity)

/-- Flipping an assignment bitwise with a polarity mask. -/
def flipAssignment {n : Nat} (g : PolarityMask n) (a : Assignment n) : Assignment n :=
  fun i => xor (a i) (g i)

/-- Flipping a literal under a polarity mask. -/
def flipLit {n : Nat} (g : PolarityMask n) (lit : Literal n) : Literal n :=
  { var := lit.var, polarity := xor lit.polarity (g lit.var) }

/-- Theorem 1: Literal evaluation is invariant under joint sign reversal (gauge transformation). -/
theorem evalLit_flip {n : Nat} (g : PolarityMask n) (lit : Literal n) (a : Assignment n) :
    evalLit (flipLit g lit) (flipAssignment g a) = evalLit lit a := by
  dsimp [evalLit, flipLit, flipAssignment]
  cases (a lit.var) <;> cases (g lit.var) <;> cases lit.polarity <;> rfl

/-- Evaluating a list of literals as a disjunction. -/
def evalClauseList {n : Nat} (c : List (Literal n)) (a : Assignment n) : Bool :=
  match c with
  | [] => false
  | lit :: rest => evalLit lit a || evalClauseList rest a

/-- Flipping a list of literals. -/
def flipClauseList {n : Nat} (g : PolarityMask n) (c : List (Literal n)) : List (Literal n) :=
  match c with
  | [] => []
  | lit :: rest => flipLit g lit :: flipClauseList g rest

/-- Theorem 2: Clause satisfaction is invariant under joint sign reversal. -/
theorem evalClauseList_flip {n : Nat} (g : PolarityMask n) (c : List (Literal n)) (a : Assignment n) :
    evalClauseList (flipClauseList g c) (flipAssignment g a) = evalClauseList c a := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [evalClauseList, flipClauseList]
    rw [evalLit_flip g lit a, ih]

/-- A CNF formula is a list of clauses. -/
def evalFormulaList {n : Nat} (f : List (List (Literal n))) (a : Assignment n) : Bool :=
  match f with
  | [] => true
  | c :: rest => evalClauseList c a && evalFormulaList rest a

/-- Flipping a formula by the polarity mask. -/
def flipFormulaList {n : Nat} (g : PolarityMask n) (f : List (List (Literal n))) : List (List (Literal n)) :=
  match f with
  | [] => []
  | c :: rest => flipClauseList g c :: flipFormulaList g rest

/-- Theorem 3: Formula satisfiability is invariant under joint sign reversal. -/
theorem evalFormulaList_flip {n : Nat} (g : PolarityMask n) (f : List (List (Literal n))) (a : Assignment n) :
    evalFormulaList (flipFormulaList g f) (flipAssignment g a) = evalFormulaList f a := by
  induction f with
  | nil => rfl
  | cons c rest ih =>
    dsimp [evalFormulaList, flipFormulaList]
    rw [evalClauseList_flip g c a, ih]

/-- Gauge Involution: Applying the same polarity flip twice restores the original assignment. -/
theorem flipAssignment_involutive {n : Nat} (g : PolarityMask n) (a : Assignment n) :
    flipAssignment g (flipAssignment g a) = a := by
  funext i
  dsimp [flipAssignment]
  cases (a i) <;> cases (g i) <;> rfl

/-- Gauge Involution on Literals: Flipping twice restores the original literal. -/
theorem flipLit_involutive {n : Nat} (g : PolarityMask n) (lit : Literal n) :
    flipLit g (flipLit g lit) = lit := by
  dsimp [flipLit]
  cases lit with | mk v p =>
  congr 1
  cases p <;> cases (g v) <;> rfl

/-- Gauge Involution on Clauses. -/
theorem flipClauseList_involutive {n : Nat} (g : PolarityMask n) (c : List (Literal n)) :
    flipClauseList g (flipClauseList g c) = c := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [flipClauseList]
    rw [flipLit_involutive g lit, ih]

/-- Gauge Involution on Formulas. -/
theorem flipFormulaList_involutive {n : Nat} (g : PolarityMask n) (f : List (List (Literal n))) :
    flipFormulaList g (flipFormulaList g f) = f := by
  induction f with
  | nil => rfl
  | cons c rest ih =>
    dsimp [flipFormulaList]
    rw [flipClauseList_involutive g c, ih]

/-- Count the number of unsatisfied (violated) clauses under assignment a. -/
def countViolatedClauses {n : Nat} (f : List (List (Literal n))) (a : Assignment n) : Nat :=
  match f with
  | [] => 0
  | c :: rest => (if evalClauseList c a then 0 else 1) + countViolatedClauses rest a

/-- Theorem 4: Violation count is strictly invariant under joint sign reversal.
    Consequently, the valuation ν_0(Z_F) and the partition polynomial Z_F(t) are gauge-invariant. -/
theorem countViolatedClauses_flip {n : Nat} (g : PolarityMask n) (f : List (List (Literal n))) (a : Assignment n) :
    countViolatedClauses (flipFormulaList g f) (flipAssignment g a) = countViolatedClauses f a := by
  induction f with
  | nil => rfl
  | cons c rest ih =>
    dsimp [countViolatedClauses, flipFormulaList]
    rw [evalClauseList_flip g c a, ih]

end SatGauge

#print axioms SatGauge.evalLit_flip
#print axioms SatGauge.evalClauseList_flip
#print axioms SatGauge.evalFormulaList_flip
#print axioms SatGauge.countViolatedClauses_flip
#print axioms SatGauge.flipAssignment_involutive
#print axioms SatGauge.flipLit_involutive
#print axioms SatGauge.flipClauseList_involutive
#print axioms SatGauge.flipFormulaList_involutive
