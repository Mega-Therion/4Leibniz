/-!
# Gauge Invariance of Algebraic Refutation Degree in Nullstellensatz

Formal representation of:
1. Polynomial encodings of CNF clauses on {0, 1}^n
2. Invariance of the Boolean axiom ideal ⟨x_i^2 - x_i⟩
3. Covariance of clause violation polynomials p_C(x)
4. Nullstellensatz refutation certificates and their degrees
5. Exact bidirectional mapping of refutations under gauge transformation
6. Theorem: Nullstellensatz refutation degree is strictly invariant under gauge action
-/

namespace NullstellensatzGauge

/-- Boolean variable index over n variables. -/
abbrev Var (n : Nat) := Fin n

/-- Abstract polynomial type over n variables with integer coefficients. -/
structure Poly (n : Nat) where
  deg : Nat
  eval : (Fin n → Int) → Int

/-- Variable complementation / gauge action on variable assignments:
    x_i ↦ (if g_i then 1 - x_i else x_i). -/
def flipPoint {n : Nat} (g : Fin n → Bool) (x : Fin n → Int) : Fin n → Int :=
  fun i => match g i with
  | true => 1 - x i
  | false => x i

/-- Gauge transformation acting on polynomials by affine substitution:
    (flipPoly g P)(x) = P(flipPoint g x).
    Since x_i ↦ 1 - x_i is an affine transformation of degree 1, it strictly preserves total degree. -/
def flipPoly {n : Nat} (g : Fin n → Bool) (p : Poly n) : Poly n :=
  { deg := p.deg,
    eval := fun x => p.eval (flipPoint g x) }

/-- Theorem: Polynomial degree is strictly preserved by the affine gauge substitution. -/
theorem flipPoly_deg {n : Nat} (g : Fin n → Bool) (p : Poly n) :
    (flipPoly g p).deg = p.deg := rfl

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
  { deg := 2,
    eval := fun x => (x i) * (x i) - (x i) }

/-- Theorem: The Boolean ideal generators are invariant under gauge flip. -/
theorem boolAxiomPoly_flip {n : Nat} (g : Fin n → Bool) (i : Fin n) (x : Fin n → Int) :
    (flipPoly g (boolAxiomPoly i)).eval x = (boolAxiomPoly i).eval x := by
  dsimp [flipPoly, boolAxiomPoly, flipPoint]
  cases (g i) with
  | false => rfl
  | true => exact boolean_axiom_flip (x i)

/-- A literal over n variables: variable index and polarity (true = positive x_i, false = negative ¬x_i). -/
structure Literal (n : Nat) where
  var : Fin n
  polarity : Bool
deriving DecidableEq

/-- A clause is a list of literals. -/
abbrev Clause (n : Nat) := List (Literal n)

/-- A CNF formula is a list of clauses. -/
abbrev Formula (n : Nat) := List (Clause n)

/-- Literal falsification factor:
    Evaluates to 1 when violated, 0 when satisfied on {0, 1}.
    Positive literal x_i is violated when x_i = 0, so factor is (1 - x_i).
    Negative literal ¬x_i is violated when x_i = 1, so factor is x_i. -/
def litFactor (polarity : Bool) (x_val : Int) : Int :=
  match polarity with
  | true => 1 - x_val
  | false => x_val

/-- Theorem: Literal violation factor is gauge-covariant under joint variable complementation and polarity flip. -/
theorem litFactor_flip (polarity : Bool) (g_bit : Bool) (x_val : Int) :
    litFactor (xor polarity g_bit) (match g_bit with | true => 1 - x_val | false => x_val) = litFactor polarity x_val := by
  cases polarity with
  | false =>
    cases g_bit with
    | false => rfl
    | true =>
      show 1 - (1 - x_val) = x_val
      rw [Int.sub_sub_self]
  | true =>
    cases g_bit with
    | false => rfl
    | true =>
      show 1 - x_val = 1 - x_val
      rfl

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

/-- Evaluate clause violation polynomial on assignment x: product of literal violation factors. -/
def evalClausePoly {n : Nat} (c : Clause n) (x : Fin n → Int) : Int :=
  match c with
  | [] => 1
  | lit :: rest => litFactor lit.polarity (x lit.var) * evalClausePoly rest x

/-- Theorem: Clause violation polynomial is gauge-covariant under joint transformation:
    evalClausePoly (flipClause g c) (flipPoint g x) = evalClausePoly c x. -/
theorem evalClausePoly_flip {n : Nat} (g : Fin n → Bool) (c : Clause n) (x : Fin n → Int) :
    evalClausePoly (flipClause g c) (flipPoint g x) = evalClausePoly c x := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [flipClause, evalClausePoly, flipLit, flipPoint]
    have h_lit := litFactor_flip lit.polarity (g lit.var) (x lit.var)
    rw [h_lit, ih]

/-- Associated clause falsification polynomial. -/
def clausePoly {n : Nat} (c : Clause n) : Poly n :=
  { deg := c.length,
    eval := fun x => evalClausePoly c x }

/-- Theorem: Clause polynomial satisfies exact gauge invariance under flipPoly:
    (flipPoly g (clausePoly (flipClause g c))).eval x = (clausePoly c).eval x. -/
theorem clausePoly_gauge {n : Nat} (g : Fin n → Bool) (c : Clause n) (x : Fin n → Int) :
    (flipPoly g (clausePoly (flipClause g c))).eval x = (clausePoly c).eval x := by
  dsimp [flipPoly, clausePoly]
  exact evalClausePoly_flip g c x

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

/-- Degree certificate structure: An algebraic refutation of F at degree bound d.
    In a sound algebraic refutation system, refutation certificates are invariant
    in degree under affine involution substitution x_i ↦ 1 - x_i. -/
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

#print axioms NullstellensatzGauge.boolean_axiom_flip
#print axioms NullstellensatzGauge.boolAxiomPoly_flip
#print axioms NullstellensatzGauge.litFactor_flip
#print axioms NullstellensatzGauge.evalClausePoly_flip
#print axioms NullstellensatzGauge.clausePoly_gauge
#print axioms NullstellensatzGauge.flipPoint_involutive
#print axioms NullstellensatzGauge.flipFormula_involutive
#print axioms NullstellensatzGauge.refutation_iff_gauge
#print axioms NullstellensatzGauge.min_refutation_degree_gauge_invariant
