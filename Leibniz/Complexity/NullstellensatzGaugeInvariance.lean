/-!
# Concrete Nullstellensatz Certificates and Gauge Invariance

This module formalizes:
1. Constructive AST polynomials over `Fin n → Int` with computable total degree.
2. Invariance of total degree under the affine involution gauge substitution `flipPoly`:
     totalDegree (flipPoly g p) ≤ totalDegree p.
3. Evaluation covariance of multilinear clause polynomials:
     evalPoly (clausePoly (flipClause g C)) x = evalPoly (clausePoly C) (flipPoint g x).
4. Evaluation invariance of Boolean idempotency axioms:
     evalPoly (boolAxiomPoly i) (flipPoint g x) = evalPoly (boolAxiomPoly i) x.
5. Concrete Nullstellensatz refutation certificate definition:
   - Exactly aligned multipliers q_idx for each clause occurrence
   - Multipliers r_i for each Boolean axiom
   - Bounded total degrees on both clause terms and Boolean terms:
       totalDegree (q idx) + totalDegree (clausePoly (F.get idx)) ≤ d
       totalDegree (r i) + 2 ≤ d
   - Semantic algebraic certificate identity on assignments:
       ∑_C eval(q_C) * eval(p_C) + ∑_i eval(r_i) * eval(B_i) = 1.
6. Parameterized Algebraic Refutation Systems and Master Minimum-Degree Gauge Invariance Theorem.
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

theorem flipPoint_true {n : Nat} (g : Fin n → Bool) (x : Fin n → Int) (i : Fin n) (h : g i = true) :
    flipPoint g x i = 1 - x i := by
  dsimp [flipPoint]
  rw [h]

theorem flipPoint_false {n : Nat} (g : Fin n → Bool) (x : Fin n → Int) (i : Fin n) (h : g i = false) :
    flipPoint g x i = x i := by
  dsimp [flipPoint]
  rw [h]

/-- Gauge transformation acting on variable x_i as a polynomial:
    x_i ↦ (if g_i then 1 - x_i else x_i). -/
def flipVarPoly {n : Nat} (g : Fin n → Bool) (i : Fin n) : Poly n :=
  match g i with
  | false => Poly.var i
  | true => Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var i))

/-- Total degree of flipped variable polynomial is at most 1. -/
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

/-- Invariance of Boolean Axiom under variable complementation:
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

/-- Theorem: Boolean ideal generators are invariant under gauge flip on points:
    evalPoly (boolAxiomPoly i) (flipPoint g x) = evalPoly (boolAxiomPoly i) x. -/
theorem boolAxiomPoly_eval_flip {n : Nat} (g : Fin n → Bool) (i : Fin n) (x : Fin n → Int) :
    evalPoly (boolAxiomPoly i) (flipPoint g x) = evalPoly (boolAxiomPoly i) x := by
  dsimp [boolAxiomPoly, evalPoly]
  cases hg : g i
  · rw [flipPoint_false g x i hg]
  · rw [flipPoint_true g x i hg]
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

/-- Theorem: Literal violation polynomial evaluation covariance:
    evalPoly (litPoly (flipLit g lit)) x = evalPoly (litPoly lit) (flipPoint g x). -/
theorem eval_litPoly_flip {n : Nat} (g : Fin n → Bool) (lit : Literal n) (x : Fin n → Int) :
    evalPoly (litPoly (flipLit g lit)) x = evalPoly (litPoly lit) (flipPoint g x) := by
  cases lit with | mk v p =>
  cases p <;> cases hg : g v
  · have h_xor : xor false (g v) = false := by rw [hg]; rfl
    dsimp [flipLit]
    rw [h_xor]
    dsimp [litPoly, evalPoly]
    rw [flipPoint_false g x v hg]
  · have h_xor : xor false (g v) = true := by rw [hg]; rfl
    dsimp [flipLit]
    rw [h_xor]
    dsimp [litPoly, evalPoly]
    rw [flipPoint_true g x v hg]
    omega
  · have h_xor : xor true (g v) = true := by rw [hg]; rfl
    dsimp [flipLit]
    rw [h_xor]
    dsimp [litPoly, evalPoly]
    rw [flipPoint_false g x v hg]
  · have h_xor : xor true (g v) = false := by rw [hg]; rfl
    dsimp [flipLit]
    rw [h_xor]
    dsimp [litPoly, evalPoly]
    rw [flipPoint_true g x v hg]
    omega

/-- Theorem: Clause polynomial evaluation covariance bridge:
    evalPoly (clausePoly (flipClause g c)) x = evalPoly (clausePoly c) (flipPoint g x). -/
theorem eval_clausePoly_flip {n : Nat} (g : Fin n → Bool) (c : Clause n) (x : Fin n → Int) :
    evalPoly (clausePoly (flipClause g c)) x = evalPoly (clausePoly c) (flipPoint g x) := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [flipClause, clausePoly, evalPoly]
    rw [eval_litPoly_flip g lit x, ih]

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

/-- Inductive evaluation of clause terms: ∑_i q_i * clausePoly C_i. -/
def evalClauseTerms {n : Nat} (q : List (Poly n)) (F : Formula n) (x : Fin n → Int) : Int :=
  match q, F with
  | [], _ => 0
  | _, [] => 0
  | q_head :: q_tail, c :: F_tail =>
    evalPoly q_head x * evalPoly (clausePoly c) x + evalClauseTerms q_tail F_tail x

/-- Theorem: Evaluation covariance for clause terms under affine gauge flip:
    evalClauseTerms (q.map (flipPoly g)) (flipFormula g F) x = evalClauseTerms q F (flipPoint g x). -/
theorem evalClauseTerms_flip {n : Nat} (g : Fin n → Bool) (q : List (Poly n)) (F : Formula n) (x : Fin n → Int) :
    evalClauseTerms (q.map (flipPoly g)) (flipFormula g F) x =
    evalClauseTerms q F (flipPoint g x) := by
  induction q generalizing F with
  | nil => rfl
  | cons q_head q_tail ih =>
    cases F with
    | nil => rfl
    | cons c F_tail =>
      dsimp [flipFormula, evalClauseTerms, List.map]
      rw [eval_flipPoly g q_head x, eval_clausePoly_flip g c x]
      have ih_call := ih F_tail
      rw [ih_call]

/-- Sum of Boolean axiom terms: ∑_i r_i * boolAxiomPoly i. -/
def evalBoolTerms {n : Nat} (r : Fin n → Poly n) (x : Fin n → Int) : Int :=
  (List.finRange n).foldl (fun acc i => acc + evalPoly (r i) x * evalPoly (boolAxiomPoly i) x) 0

/-- Helper lemma: Congruence for list foldl with term addition. -/
theorem foldl_term_congr {α : Type} (L : List α) (f g : α → Int)
    (h : ∀ a, a ∈ L → f a = g a) (acc : Int) :
    L.foldl (fun s a => s + f a) acc = L.foldl (fun s a => s + g a) acc := by
  induction L generalizing acc with
  | nil => rfl
  | cons hd tl ih =>
    dsimp [List.foldl]
    have h_hd : f hd = g hd := h hd (List.Mem.head tl)
    have h_tl : ∀ a, a ∈ tl → f a = g a := fun a ha => h a (List.Mem.tail hd ha)
    rw [h_hd]
    exact ih h_tl (acc + g hd)

/-- Theorem: Evaluation covariance for Boolean axiom terms under affine gauge flip:
    evalBoolTerms (fun i => flipPoly g (r i)) x = evalBoolTerms r (flipPoint g x). -/
theorem evalBoolTerms_flip {n : Nat} (g : Fin n → Bool) (r : Fin n → Poly n) (x : Fin n → Int) :
    evalBoolTerms (fun i => flipPoly g (r i)) x = evalBoolTerms r (flipPoint g x) := by
  dsimp [evalBoolTerms]
  apply foldl_term_congr
  intro i _
  rw [eval_flipPoly g (r i) x, boolAxiomPoly_eval_flip g i x]

/-- Length preservation of formula under flipFormula. -/
theorem flipFormula_length {n : Nat} (g : Fin n → Bool) (F : Formula n) :
    (flipFormula g F).length = F.length := by
  induction F with
  | nil => rfl
  | cons c rest ih =>
    dsimp [flipFormula]
    rw [ih]

/-- Length preservation of clause under flipClause. -/
theorem flipClause_length {n : Nat} (g : Fin n → Bool) (c : Clause n) :
    (flipClause g c).length = c.length := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [flipClause]
    rw [ih]

/-- List indexing under map flipPoly. -/
theorem get_map_flipPoly {n : Nat} (g : Fin n → Bool) (q : List (Poly n)) (i : Nat) (hq : i < (q.map (flipPoly g)).length) :
    (q.map (flipPoly g)).get ⟨i, hq⟩ = flipPoly g (q.get ⟨i, by rw [List.length_map] at hq; exact hq⟩) := by
  induction q generalizing i with
  | nil =>
    have : i < 0 := by rw [List.length_map] at hq; exact hq
    contradiction
  | cons hd tl ih =>
    cases i with
    | zero => rfl
    | succ j =>
      dsimp [List.map, List.get]
      have hj : j < (tl.map (flipPoly g)).length := by
        dsimp [List.map] at hq
        omega
      exact ih j hj

/-- List indexing under flipFormula. -/
theorem get_flipFormula {n : Nat} (g : Fin n → Bool) (F : Formula n) (i : Nat) (hF : i < (flipFormula g F).length) :
    (flipFormula g F).get ⟨i, hF⟩ = flipClause g (F.get ⟨i, by rw [flipFormula_length] at hF; exact hF⟩) := by
  induction F generalizing i with
  | nil =>
    dsimp [flipFormula] at hF
    contradiction
  | cons c rest ih =>
    cases i with
    | zero => rfl
    | succ j =>
      dsimp [flipFormula, List.get]
      have hj : j < (flipFormula g rest).length := by
        dsimp [flipFormula] at hF
        omega
      exact ih j hj

/-- Concrete Nullstellensatz refutation certificate definition over integer polynomials:
    Contains multiplier polynomials q aligned with each clause occurrence and r for each Boolean axiom,
    with rigorous total degree bounds and algebraic identity certification. -/
structure ConcreteNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (Poly n)
  r : Fin n → Poly n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (clausePoly (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  identity : ∀ (x : Fin n → Int),
    evalClauseTerms q F x + evalBoolTerms r x = 1

/-- Transport theorem for Concrete Nullstellensatz certificates:
    Transforms multipliers q ↦ q.map (flipPoly g) and r ↦ fun i => flipPoly g (r i)
    and verifies that all degree bounds and algebraic identities hold for flipFormula g F at degree ≤ d. -/
def transportConcreteNSRefutation {n : Nat} {F : Formula n} {d : Nat}
    (g : Fin n → Bool) (cert : ConcreteNSRefutation F d) :
    ConcreteNSRefutation (flipFormula g F) d where
  q := cert.q.map (flipPoly g)
  r := fun i => flipPoly g (cert.r i)
  q_len := by
    rw [List.length_map, cert.q_len, flipFormula_length]
  clause_deg_bound := by
    intro i hq hF
    rw [get_map_flipPoly]
    rw [get_flipFormula]
    rw [clausePoly_degree (flipClause g _), flipClause_length]
    rw [← clausePoly_degree (F.get _)]
    have h_orig := cert.clause_deg_bound i (by rw [List.length_map] at hq; exact hq) (by rw [flipFormula_length] at hF; exact hF)
    have h_deg := flipPoly_deg_le g (cert.q.get ⟨i, by rw [List.length_map] at hq; exact hq⟩)
    omega
  bool_deg_bound := by
    intro i
    have h_orig := cert.bool_deg_bound i
    have h_deg := flipPoly_deg_le g (cert.r i)
    omega
  identity := by
    intro x
    rw [evalClauseTerms_flip g cert.q F x]
    rw [evalBoolTerms_flip g cert.r x]
    exact cert.identity (flipPoint g x)

/-- Predicate stating existence of a concrete Nullstellensatz refutation certificate at degree ≤ d. -/
def HasConcreteNSRefutation {n : Nat} (F : Formula n) (d : Nat) : Prop :=
  Nonempty (ConcreteNSRefutation F d)

/-- Bidirectional Equivalence Theorem for Concrete Nullstellensatz refutations:
    A formula F has a concrete Nullstellensatz refutation at degree ≤ d if and only if
    flipFormula g F has a concrete Nullstellensatz refutation at degree ≤ d. -/
theorem hasConcreteNSRefutation_iff_gauge {n : Nat}
    (g : Fin n → Bool) (F : Formula n) (d : Nat) :
    HasConcreteNSRefutation (flipFormula g F) d ↔ HasConcreteNSRefutation F d := by
  constructor
  · rintro ⟨cert⟩
    have cert_flipped := transportConcreteNSRefutation g cert
    rw [flipFormula_involutive g F] at cert_flipped
    exact ⟨cert_flipped⟩
  · rintro ⟨cert⟩
    exact ⟨transportConcreteNSRefutation g cert⟩

/-- Minimum refutation degree predicate for concrete Nullstellensatz certificates. -/
def IsMinConcreteNSDegree {n : Nat} (F : Formula n) (d : Nat) : Prop :=
  HasConcreteNSRefutation F d ∧ (∀ (k : Nat), k < d → ¬ HasConcreteNSRefutation F k)

/-- Master Theorem for Concrete Nullstellensatz:
    The minimum concrete Nullstellensatz refutation degree is strictly invariant under gauge transformation:
    IsMinConcreteNSDegree (flipFormula g F) d ↔ IsMinConcreteNSDegree F d. -/
theorem min_concrete_ns_degree_gauge_invariant {n : Nat}
    (g : Fin n → Bool) (F : Formula n) (d : Nat) :
    IsMinConcreteNSDegree (flipFormula g F) d ↔ IsMinConcreteNSDegree F d := by
  dsimp [IsMinConcreteNSDegree]
  constructor
  · rintro ⟨hd, hmin⟩
    constructor
    · exact (hasConcreteNSRefutation_iff_gauge g F d).mp hd
    · intro k hk hk_ref
      have hk_gauge := (hasConcreteNSRefutation_iff_gauge g F k).mpr hk_ref
      exact (hmin k hk) hk_gauge
  · rintro ⟨hd, hmin⟩
    constructor
    · exact (hasConcreteNSRefutation_iff_gauge g F d).mpr hd
    · intro k hk hk_ref
      have hk_orig := (hasConcreteNSRefutation_iff_gauge g F k).mp hk_ref
      exact (hmin k hk) hk_orig

/-- Abstract definition of an algebraic refutation system for CNF formulas.
    A sound algebraic refutation system requires that whenever a formula F has a refutation
    at total polynomial degree ≤ d, the transformed formula F^g under the affine involution
    x_i ↦ 1 - x_i also possesses a valid refutation at total degree ≤ d. -/
structure AlgebraicRefutationSystem (n : Nat) where
  hasRefutation : Formula n → Nat → Prop
  deg_preservation : ∀ (F : Formula n) (d : Nat) (g : Fin n → Bool),
    hasRefutation F d → hasRefutation (flipFormula g F) d

/-- Concrete Nullstellensatz Refutation System as an instance of AlgebraicRefutationSystem. -/
def concreteNSRefutationSystem (n : Nat) : AlgebraicRefutationSystem n where
  hasRefutation := HasConcreteNSRefutation
  deg_preservation := fun _ _ g ⟨cert⟩ => ⟨transportConcreteNSRefutation g cert⟩

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
#print axioms NullstellensatzGauge.eval_clausePoly_flip
#print axioms NullstellensatzGauge.flipPoint_involutive
#print axioms NullstellensatzGauge.flipFormula_involutive
#print axioms NullstellensatzGauge.transportConcreteNSRefutation
#print axioms NullstellensatzGauge.hasConcreteNSRefutation_iff_gauge
#print axioms NullstellensatzGauge.min_concrete_ns_degree_gauge_invariant
#print axioms NullstellensatzGauge.concreteNSRefutationSystem
#print axioms NullstellensatzGauge.refutation_iff_gauge
#print axioms NullstellensatzGauge.min_refutation_degree_gauge_invariant
