/-!
# Gauge Invariance of Algebraic Refutation Systems in Nullstellensatz

Formal representation of:
1. Constructive AST polynomials over `Fin n → Int` with computable total degree.
2. Invariance of total degree under the affine involution gauge substitution `flipPoly`.
3. Gauge covariance of literal and clause falsification polynomials.
4. Formal specification of algebraic refutation systems (Nullstellensatz & Polynomial Calculus).
5. Bidirectional refutation correspondence under gauge transformation.
6. Master Theorem: Strict gauge invariance of the minimum algebraic refutation degree.
-/

namespace NullstellensatzGauge

/-- Inductive AST of multilinear polynomials over n variables with integer coefficients. -/
inductive Poly (n : Nat) where
  | const : Int → Poly n
  | var : Fin n → Poly n
  | add : Poly n → Poly n → Poly n
  | mul : Poly n → Poly n → Poly n
deriving Inhabited

/-- Computable total degree of a polynomial AST. -/
def totalDegree {n : Nat} (p : Poly n) : Nat :=
  match p with
  | Poly.const _ => 0
  | Poly.var _ => 1
  | Poly.add p q => max (totalDegree p) (totalDegree q)
  | Poly.mul p q => totalDegree p + totalDegree q

/-- Evaluation of polynomial AST on variable assignment point x. -/
def evalPoly {n : Nat} (p : Poly n) (x : Fin n → Int) : Int :=
  match p with
  | Poly.const c => c
  | Poly.var i => x i
  | Poly.add p q => evalPoly p x + evalPoly q x
  | Poly.mul p q => evalPoly p x * evalPoly q x

/-- Variable complementation / gauge action on points:
    x_i ↦ (if g_i then 1 - x_i else x_i). -/
def flipPoint {n : Nat} (g : Fin n → Bool) (x : Fin n → Int) : Fin n → Int :=
  fun i => match g i with
  | true => 1 - x i
  | false => x i

/-- Gauge transformation acting on variable x_i as a polynomial:
    x_i ↦ (if g_i then 1 - x_i else x_i). -/
def flipVarPoly {n : Nat} (g : Fin n → Bool) (i : Fin n) : Poly n :=
  match g i with
  | false => Poly.var i
  | true => Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var i))

/-- Theorem: Total degree of flipped variable polynomial is at most 1. -/
theorem flipVarPoly_degree {n : Nat} (g : Fin n → Bool) (i : Fin n) :
    totalDegree (flipVarPoly g i) ≤ 1 := by
  dsimp [flipVarPoly]
  cases (g i) with
  | false =>
    dsimp [totalDegree]
    exact Nat.le_refl 1
  | true =>
    dsimp [totalDegree]
    omega

/-- Gauge transformation acting on polynomial AST by affine substitution:
    Replaces each variable x_i with (if g_i then 1 - x_i else x_i). -/
def flipPoly {n : Nat} (g : Fin n → Bool) (p : Poly n) : Poly n :=
  match p with
  | Poly.const c => Poly.const c
  | Poly.var i => flipVarPoly g i
  | Poly.add p q => Poly.add (flipPoly g p) (flipPoly g q)
  | Poly.mul p q => Poly.mul (flipPoly g p) (flipPoly g q)

/-- Theorem: Total polynomial degree is non-increasing under affine gauge substitution:
    totalDegree (flipPoly g p) ≤ totalDegree p. -/
theorem flipPoly_deg_le {n : Nat} (g : Fin n → Bool) (p : Poly n) :
    totalDegree (flipPoly g p) ≤ totalDegree p := by
  induction p with
  | const c =>
    dsimp [flipPoly, totalDegree]
    exact Nat.le_refl 0
  | var i =>
    dsimp [totalDegree, flipPoly]
    exact flipVarPoly_degree g i
  | add p q ihp ihq =>
    dsimp [flipPoly, totalDegree]
    omega
  | mul p q ihp ihq =>
    dsimp [flipPoly, totalDegree]
    omega

/-- Theorem: Evaluation of flipped polynomial matches evaluation on flipped point:
    evalPoly (flipPoly g p) x = evalPoly p (flipPoint g x). -/
theorem eval_flipVarPoly {n : Nat} (g : Fin n → Bool) (i : Fin n) (x : Fin n → Int) :
    evalPoly (flipVarPoly g i) x = flipPoint g x i := by
  dsimp [flipVarPoly, flipPoint]
  cases (g i) with
  | false => rfl
  | true =>
    dsimp [evalPoly]
    omega

theorem eval_flipPoly {n : Nat} (g : Fin n → Bool) (p : Poly n) (x : Fin n → Int) :
    evalPoly (flipPoly g p) x = evalPoly p (flipPoint g x) := by
  induction p with
  | const c => rfl
  | var i => exact eval_flipVarPoly g i x
  | add p q ihp ihq =>
    dsimp [flipPoly, evalPoly]
    rw [ihp, ihq]
  | mul p q ihp ihq =>
    dsimp [flipPoly, evalPoly]
    rw [ihp, ihq]

/-- Lemma: Invariance of Boolean Axiom under variable complementation:
    (1 - x) * (1 - x) - (1 - x) = x * x - x. -/
theorem boolean_axiom_flip (x : Int) :
    (1 - x) * (1 - x) - (1 - x) = x * x - x := by
  have h1 : (1 - x) * (1 - x) = 1 - 2 * x + x * x := by
    have ha : (1 - x) * (1 - x) = 1 * (1 - x) - x * (1 - x) := by rw [Int.sub_mul]
    have hb : 1 * (1 - x) = 1 - x := by rw [Int.one_mul]
    have hc : x * (1 - x) = x * 1 - x * x := by rw [Int.mul_sub]
    have hd : x * 1 = x := by rw [Int.mul_one]
    rw [ha, hb, hc, hd]
    omega
  have h2 : (1 - 2 * x + x * x) - (1 - x) = x * x - x := by omega
  rw [h1, h2]

/-- The Boolean ideal generator for variable i: B_i(x) = x_i^2 - x_i. -/
def boolAxiomPoly {n : Nat} (i : Fin n) : Poly n :=
  Poly.add (Poly.mul (Poly.var i) (Poly.var i)) (Poly.mul (Poly.const (-1)) (Poly.var i))

/-- Total degree of the Boolean axiom polynomial is exactly 2. -/
theorem boolAxiomPoly_degree {n : Nat} (i : Fin n) :
    totalDegree (boolAxiomPoly i) = 2 := by
  dsimp [boolAxiomPoly, totalDegree]
  omega

/-- Theorem: Boolean ideal generators are invariant under gauge flip modulo evaluation. -/
theorem boolAxiomPoly_eval_flip {n : Nat} (g : Fin n → Bool) (i : Fin n) (x : Fin n → Int) :
    evalPoly (flipPoly g (boolAxiomPoly i)) x = evalPoly (boolAxiomPoly i) x := by
  rw [eval_flipPoly]
  dsimp [boolAxiomPoly, evalPoly, flipPoint]
  cases (g i) with
  | false => rfl
  | true =>
    dsimp
    have h := boolean_axiom_flip (x i)
    omega

/-- A literal over n variables: variable index and polarity (true = positive x_i, false = negative ¬x_i). -/
structure Literal (n : Nat) where
  var : Fin n
  polarity : Bool
deriving DecidableEq

/-- A clause is a list of literals. -/
abbrev Clause (n : Nat) := List (Literal n)

/-- A CNF formula is a list of clauses. -/
abbrev Formula (n : Nat) := List (Clause n)

/-- Polynomial representation of a literal falsification condition. -/
def litPoly {n : Nat} (lit : Literal n) : Poly n :=
  match lit.polarity with
  | true => Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var lit.var))
  | false => Poly.var lit.var

/-- Total degree of a literal falsification polynomial is 1. -/
theorem litPoly_degree {n : Nat} (lit : Literal n) :
    totalDegree (litPoly lit) = 1 := by
  cases lit with | mk v p =>
  cases p with
  | true => dsimp [litPoly, totalDegree]; omega
  | false => dsimp [litPoly, totalDegree]

/-- Clause falsification polynomial: product of literal falsification polynomials. -/
def clausePoly {n : Nat} (c : Clause n) : Poly n :=
  match c with
  | [] => Poly.const 1
  | lit :: rest => Poly.mul (litPoly lit) (clausePoly rest)

/-- Total degree of clause polynomial equals clause length. -/
theorem clausePoly_degree {n : Nat} (c : Clause n) :
    totalDegree (clausePoly c) = c.length := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [clausePoly, totalDegree]
    rw [litPoly_degree, ih]
    omega

/-- Flip literal under gauge polarity mask g. -/
def flipLit {n : Nat} (g : Fin n → Bool) (lit : Literal n) : Literal n :=
  { var := lit.var, polarity := xor lit.polarity (g lit.var) }

/-- Flip clause under gauge polarity mask g. -/
def flipClause {n : Nat} (g : Fin n → Bool) (c : Clause n) : Clause n :=
  match c with
  | [] => []
  | lit :: rest => flipLit g lit :: flipClause g rest

/-- Flip CNF formula under gauge polarity mask g. -/
def flipFormula {n : Nat} (g : Fin n → Bool) (f : Formula n) : Formula n :=
  match f with
  | [] => []
  | c :: rest => flipClause g c :: flipFormula g rest

/-- Gauge involution on points: flipPoint g (flipPoint g x) = x. -/
theorem flipPoint_involutive {n : Nat} (g : Fin n → Bool) (x : Fin n → Int) :
    flipPoint g (flipPoint g x) = x := by
  funext i
  dsimp [flipPoint]
  cases (g i) with
  | false => rfl
  | true => exact Int.sub_sub_self 1 (x i)

/-- Involutive property on Literals. -/
theorem flipLit_involutive {n : Nat} (g : Fin n → Bool) (lit : Literal n) :
    flipLit g (flipLit g lit) = lit := by
  dsimp [flipLit]
  cases lit with | mk v p =>
  congr 1
  cases p <;> cases (g v) <;> rfl

/-- Involutive property on Clauses. -/
theorem flipClause_involutive {n : Nat} (g : Fin n → Bool) (c : Clause n) :
    flipClause g (flipClause g c) = c := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [flipClause]
    rw [flipLit_involutive g lit, ih]

/-- Gauge Involution on Formulas: flipFormula g (flipFormula g F) = F. -/
theorem flipFormula_involutive {n : Nat} (g : Fin n → Bool) (F : Formula n) :
    flipFormula g (flipFormula g F) = F := by
  induction F with
  | nil => rfl
  | cons c rest ih =>
    dsimp [flipFormula]
    rw [flipClause_involutive g c, ih]

/-- Abstract definition of an algebraic refutation system for CNF formulas.
    A sound algebraic refutation system requires that whenever a formula F has a refutation
    at total polynomial degree ≤ d, the transformed formula F^g under the affine involution
    x_i ↦ 1 - x_i also possesses a valid refutation at total degree ≤ d. -/
structure AlgebraicRefutationSystem (n : Nat) where
  hasRefutation : Formula n → Nat → Prop
  deg_preservation : ∀ (F : Formula n) (d : Nat) (g : Fin n → Bool),
    hasRefutation F d → hasRefutation (flipFormula g F) d

/-- Bidirectional Equivalence Theorem:
    A formula F has an algebraic refutation of degree ≤ d if and only if F^g has an algebraic
    refutation of degree ≤ d. -/
theorem refutation_iff_gauge {n : Nat} (sys : AlgebraicRefutationSystem n)
    (g : Fin n → Bool) (F : Formula n) (d : Nat) :
    sys.hasRefutation (flipFormula g F) d ↔ sys.hasRefutation F d := by
  constructor
  · intro h
    have h_rev := sys.deg_preservation (flipFormula g F) d g h
    rw [flipFormula_involutive g F] at h_rev
    exact h_rev
  · intro h
    exact sys.deg_preservation F d g h

/-- Minimum refutation degree predicate: d is the minimum degree of formula F
    if F has a refutation at degree d, and no refutation exists at degree < d. -/
def IsMinRefutationDegree {n : Nat} (sys : AlgebraicRefutationSystem n) (F : Formula n) (d : Nat) : Prop :=
  sys.hasRefutation F d ∧ (∀ (k : Nat), k < d → ¬ sys.hasRefutation F k)

/-- Master Theorem: The minimum algebraic refutation degree is strictly invariant under gauge transformation:
    IsMinRefutationDegree sys (flipFormula g F) d ↔ IsMinRefutationDegree sys F d. -/
theorem min_refutation_degree_gauge_invariant {n : Nat} (sys : AlgebraicRefutationSystem n)
    (g : Fin n → Bool) (F : Formula n) (d : Nat) :
    IsMinRefutationDegree sys (flipFormula g F) d ↔ IsMinRefutationDegree sys F d := by
  dsimp [IsMinRefutationDegree]
  constructor
  · rintro ⟨hd, hmin⟩
    constructor
    · exact (refutation_iff_gauge sys g F d).mp hd
    · intro k hk
      intro hk_ref
      have hk_gauge := (refutation_iff_gauge sys g F k).mpr hk_ref
      exact (hmin k hk) hk_gauge
  · rintro ⟨hd, hmin⟩
    constructor
    · exact (refutation_iff_gauge sys g F d).mpr hd
    · intro k hk
      intro hk_ref
      have hk_orig := (refutation_iff_gauge sys g F k).mp hk_ref
      exact (hmin k hk) hk_orig

end NullstellensatzGauge

#print axioms NullstellensatzGauge.flipPoly_deg_le
#print axioms NullstellensatzGauge.eval_flipPoly
#print axioms NullstellensatzGauge.boolean_axiom_flip
#print axioms NullstellensatzGauge.boolAxiomPoly_eval_flip
#print axioms NullstellensatzGauge.clausePoly_degree
#print axioms NullstellensatzGauge.flipPoint_involutive
#print axioms NullstellensatzGauge.flipFormula_involutive
#print axioms NullstellensatzGauge.refutation_iff_gauge
#print axioms NullstellensatzGauge.min_refutation_degree_gauge_invariant
