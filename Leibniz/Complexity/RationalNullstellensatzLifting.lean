/-!
# Characteristic Zero Field Nullstellensatz Lifting, Monomial Reduction, and Embedding Boundaries

This module formalizes:
1. Mathematical semantics for the genuine rational field ℚ (`Rat`) from the Lean 4 standard library,
   incorporating canonical normalized fraction representation (`Rat.normalize`), lawful addition,
   multiplication, negation, and characteristic zero ring embedding `intToRatEmbedding : RingEmbedding Int Rat`.
2. Ring equivalence relation `PolyRingEq` on polynomial ASTs modulo standard ring laws,
   allowing algebraically valid Nullstellensatz refutations (such as (1 - x) + x = 1) to be accepted
   without requiring unnormalized literal AST equality.
3. Functorial coefficient lifting `mapCoeff_polyRingEq` mapping polynomial ring equivalences
   under any ring homomorphism, used in:
     `liftIntToRatAlgebraicRefutation : ConcreteIntAlgebraicNSRefutation F d → ConcreteRatAlgebraicNSRefutation F d`.
4. The master one-way embedding theorem:
     `int_cert_implies_rat_cert : Nonempty (ConcreteIntAlgebraicNSRefutation F d) → Nonempty (ConcreteRatAlgebraicNSRefutation F d)`.
5. Genuine monomial power evaluation `evalMonomialExp` with `intPow (x i) (exps i)`,
   distinguishing x^2 = 4 from x = 2 at x = 2 (`test_exponent_distinction`), and proving
   semantic evaluation invariance on Boolean cube assignments (`evalMonomialExp_reduced`).
6. Canonical multilinear Boolean monomial reduction via exponent vectors:
     `reduceMonomialExp : (Fin n → Nat) → (Fin n → Nat)`,
   with proofs of idempotence (`reduceMonomialExp_idempotent`) and cube exponent collapse ($x_i^3 \to x_i$,
   `cube_exp_collapse`).
7. Supporting lemma for denominator clearing obstruction:
     `denominator_clearing_obstruction : ∀ D > 1, ¬ ∃ k : ℤ, D * k = 1`.
-/

namespace RationalNullstellensatz

/-!
### 1. Genuine Rational Field Semantics and Ring Embedding
-/

/-- Verified Canonical Normalized Fraction Property:
    In Lean 4's standard `Rat` type, equivalent fraction pairs normalize to identical canonical values. -/
theorem rat_fraction_normalization :
    Rat.normalize 1 2 = Rat.normalize 2 4 := rfl

theorem rat_eq (a b : Rat) (h_num : a.num = b.num) (h_den : a.den = b.den) : a = b := by
  cases a; cases b
  dsimp at h_num h_den
  subst h_num h_den
  rfl

theorem rat_normalize_one (num : Int) :
    Rat.normalize num 1 = Rat.ofInt num := by
  have h_norm := Rat.normalize_eq (by decide : 1 ≠ 0) (num := num)
  have h_gcd : num.natAbs.gcd 1 = 1 := Nat.gcd_one_right (num.natAbs)
  apply rat_eq
  · rw [h_norm]
    dsimp
    rw [h_gcd]
    dsimp [Rat.ofInt]
    rw [Int.ediv_one]
  · rw [h_norm]
    dsimp
    rw [h_gcd]

theorem rat_ofInt_zero : Rat.ofInt 0 = 0 := rfl

theorem rat_ofInt_one : Rat.ofInt 1 = 1 := rfl

theorem rat_ofInt_add (a b : Int) : Rat.ofInt (a + b) = Rat.ofInt a + Rat.ofInt b := by
  have h_add := Rat.add_def (Rat.ofInt a) (Rat.ofInt b)
  rw [h_add]
  have h_norm := rat_normalize_one (a + b)
  rw [← h_norm]
  apply congrArg (fun n => Rat.normalize n 1)
  dsimp [Rat.ofInt]
  omega

theorem rat_ofInt_mul (a b : Int) : Rat.ofInt (a * b) = Rat.ofInt a * Rat.ofInt b := by
  have h_mul := Rat.mul_def (Rat.ofInt a) (Rat.ofInt b)
  rw [h_mul]
  have h_norm := rat_normalize_one (a * b)
  rw [← h_norm]
  rfl

theorem rat_ofInt_neg (a : Int) : Rat.ofInt (-a) = -Rat.ofInt a := rfl

theorem rat_ofInt_injective (a b : Int) (h : Rat.ofInt a = Rat.ofInt b) : a = b :=
  congrArg Rat.num h

/-- Lawful Ring Homomorphism structure preserving additive, multiplicative, unit, and negation laws. -/
structure RingHom (R S : Type) [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                [Add S] [Mul S] [Zero S] [One S] [Neg S] where
  toFun : R → S
  map_zero : toFun 0 = 0
  map_one : toFun 1 = 1
  map_add : ∀ a b : R, toFun (a + b) = toFun a + toFun b
  map_mul : ∀ a b : R, toFun (a * b) = toFun a * toFun b
  map_neg : ∀ a : R, toFun (-a) = -toFun a

/-- Lawful Characteristic Zero Ring Embedding extending RingHom with verified injectivity. -/
structure RingEmbedding (R S : Type) [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                     [Add S] [Mul S] [Zero S] [One S] [Neg S]
    extends RingHom R S where
  injective : ∀ a b : R, toFun a = toFun b → a = b

/-- Certified Ring Embedding from Int to standard Rat. -/
def intToRatEmbedding : RingEmbedding Int Rat where
  toFun := Rat.ofInt
  map_zero := rat_ofInt_zero
  map_one := rat_ofInt_one
  map_add := rat_ofInt_add
  map_mul := rat_ofInt_mul
  map_neg := rat_ofInt_neg
  injective := rat_ofInt_injective

/-- Lawful Commutative Ring Structure discharging PolyRingEq generators. -/
class IsCommRing (R : Type) [Add R] [Mul R] [Zero R] [One R] [Neg R] : Prop where
  add_assoc : ∀ a b c : R, a + b + c = a + (b + c)
  add_comm : ∀ a b : R, a + b = b + a
  add_zero : ∀ a : R, a + 0 = a
  zero_add : ∀ a : R, 0 + a = a
  mul_assoc : ∀ a b c : R, a * b * c = a * (b * c)
  mul_comm : ∀ a b : R, a * b = b * a
  mul_one : ∀ a : R, a * 1 = a
  one_mul : ∀ a : R, 1 * a = a
  left_distrib : ∀ a b c : R, a * (b + c) = a * b + a * c
  right_distrib : ∀ a b c : R, (a + b) * c = a * c + b * c
  neg_add_cancel : ∀ a : R, (-1 : R) * a + a = 0

instance : IsCommRing Int where
  add_assoc := Int.add_assoc
  add_comm := Int.add_comm
  add_zero := Int.add_zero
  zero_add := Int.zero_add
  mul_assoc := Int.mul_assoc
  mul_comm := Int.mul_comm
  mul_one := Int.mul_one
  one_mul := Int.one_mul
  left_distrib := Int.mul_add
  right_distrib := Int.add_mul
  neg_add_cancel := by intro a; omega

theorem rat_neg_one_mul (a : Rat) : (-1 : Rat) * a = -a := by
  have h := Rat.add_mul (-1) 1 a
  have h_zero : (-1 : Rat) + 1 = 0 := Rat.neg_add_cancel 1
  rw [h_zero, Rat.zero_mul] at h
  rw [Rat.one_mul] at h
  have h_add := congrArg (fun x => x + -a) h
  rw [Rat.zero_add] at h_add
  rw [Rat.add_assoc, Rat.add_neg_cancel, Rat.add_zero] at h_add
  exact h_add.symm

instance : IsCommRing Rat where
  add_assoc := Rat.add_assoc
  add_comm := Rat.add_comm
  add_zero := Rat.add_zero
  zero_add := Rat.zero_add
  mul_assoc := Rat.mul_assoc
  mul_comm := Rat.mul_comm
  mul_one := Rat.mul_one
  one_mul := Rat.one_mul
  left_distrib := Rat.mul_add
  right_distrib := Rat.add_mul
  neg_add_cancel := by intro a; rw [rat_neg_one_mul, Rat.neg_add_cancel]

/-!
### 2. Polynomial AST and Ring Equivalence Modulo Ring Laws
-/

/-- Parameterized polynomial AST over an arbitrary coefficient type R. -/
inductive Poly (R : Type) (n : Nat) where
  | const : R → Poly R n
  | var : Fin n → Poly R n
  | add : Poly R n → Poly R n → Poly R n
  | mul : Poly R n → Poly R n → Poly R n
deriving Inhabited

def totalDegree {R : Type} {n : Nat} (p : Poly R n) : Nat :=
  match p with
  | Poly.const _ => 0
  | Poly.var _ => 1
  | Poly.add p q => max (totalDegree p) (totalDegree q)
  | Poly.mul p q => totalDegree p + totalDegree q

def mapCoeff {R S : Type} {n : Nat} (f : R → S) (p : Poly R n) : Poly S n :=
  match p with
  | Poly.const c => Poly.const (f c)
  | Poly.var i => Poly.var i
  | Poly.add p q => Poly.add (mapCoeff f p) (mapCoeff f q)
  | Poly.mul p q => Poly.mul (mapCoeff f p) (mapCoeff f q)

theorem mapCoeff_degree {R S : Type} {n : Nat} (f : R → S) (p : Poly R n) :
    totalDegree (mapCoeff f p) = totalDegree p := by
  induction p with
  | const c => rfl
  | var i => rfl
  | add p q ihp ihq =>
    dsimp [mapCoeff, totalDegree]
    rw [ihp, ihq]
  | mul p q ihp ihq =>
    dsimp [mapCoeff, totalDegree]
    rw [ihp, ihq]

/-- Evaluation of polynomial AST on variable assignments. -/
def evalPoly {R : Type} [Add R] [Mul R] {n : Nat} (p : Poly R n) (x : Fin n → R) : R :=
  match p with
  | Poly.const c => c
  | Poly.var i => x i
  | Poly.add p q => evalPoly p x + evalPoly q x
  | Poly.mul p q => evalPoly p x * evalPoly q x

/-- Polynomial Ring Equivalence Modulo Commutative Ring Laws:
    Equivalence relation generated by associativity, commutativity, distributivity,
    unit/zero identities, additive negation cancellation, and constant operations. -/
inductive PolyRingEq {R : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R] {n : Nat} :
    Poly R n → Poly R n → Prop where
  | refl (p : Poly R n) : PolyRingEq p p
  | symm {p q : Poly R n} : PolyRingEq p q → PolyRingEq q p
  | trans {p q r : Poly R n} : PolyRingEq p q → PolyRingEq q r → PolyRingEq p r
  | add_congr {p1 p2 q1 q2 : Poly R n} : PolyRingEq p1 p2 → PolyRingEq q1 q2 → PolyRingEq (Poly.add p1 q1) (Poly.add p2 q2)
  | mul_congr {p1 p2 q1 q2 : Poly R n} : PolyRingEq p1 p2 → PolyRingEq q1 q2 → PolyRingEq (Poly.mul p1 q1) (Poly.mul p2 q2)
  | add_assoc (p q r : Poly R n) : PolyRingEq (Poly.add (Poly.add p q) r) (Poly.add p (Poly.add q r))
  | add_comm (p q : Poly R n) : PolyRingEq (Poly.add p q) (Poly.add q p)
  | add_zero (p : Poly R n) : PolyRingEq (Poly.add p (Poly.const 0)) p
  | zero_add (p : Poly R n) : PolyRingEq (Poly.add (Poly.const 0) p) p
  | mul_assoc (p q r : Poly R n) : PolyRingEq (Poly.mul (Poly.mul p q) r) (Poly.mul p (Poly.mul q r))
  | mul_comm (p q : Poly R n) : PolyRingEq (Poly.mul p q) (Poly.mul q p)
  | mul_one (p : Poly R n) : PolyRingEq (Poly.mul p (Poly.const 1)) p
  | one_mul (p : Poly R n) : PolyRingEq (Poly.mul (Poly.const 1) p) p
  | left_distrib (p q r : Poly R n) : PolyRingEq (Poly.mul p (Poly.add q r)) (Poly.add (Poly.mul p q) (Poly.mul p r))
  | right_distrib (p q r : Poly R n) : PolyRingEq (Poly.mul (Poly.add p q) r) (Poly.add (Poly.mul p r) (Poly.mul q r))
  | neg_add_cancel (p : Poly R n) : PolyRingEq (Poly.add (Poly.mul (Poly.const (-1)) p) p) (Poly.const 0)
  | const_add (c1 c2 : R) : PolyRingEq (Poly.add (Poly.const c1) (Poly.const c2)) (Poly.const (c1 + c2))
  | const_mul (c1 c2 : R) : PolyRingEq (Poly.mul (Poly.const c1) (Poly.const c2)) (Poly.const (c1 * c2))

/-- Semantic Soundness of Polynomial Ring Equivalence:
    If two polynomial ASTs are equivalent under PolyRingEq, their evaluations
    agree at every point in any lawful commutative ring. -/
theorem polyRingEq_sound {R : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R] [IsCommRing R]
    {n : Nat} {p q : Poly R n} (h : PolyRingEq p q) (x : Fin n → R) :
    evalPoly p x = evalPoly q x := by
  induction h with
  | refl p => rfl
  | symm _ ih => exact ih.symm
  | trans _ _ ih1 ih2 => exact ih1.trans ih2
  | add_congr _ _ ih1 ih2 =>
    dsimp [evalPoly]; rw [ih1, ih2]
  | mul_congr _ _ ih1 ih2 =>
    dsimp [evalPoly]; rw [ih1, ih2]
  | add_assoc p q r =>
    dsimp [evalPoly]; exact IsCommRing.add_assoc (evalPoly p x) (evalPoly q x) (evalPoly r x)
  | add_comm p q =>
    dsimp [evalPoly]; exact IsCommRing.add_comm (evalPoly p x) (evalPoly q x)
  | add_zero p =>
    dsimp [evalPoly]; exact IsCommRing.add_zero (evalPoly p x)
  | zero_add p =>
    dsimp [evalPoly]; exact IsCommRing.zero_add (evalPoly p x)
  | mul_assoc p q r =>
    dsimp [evalPoly]; exact IsCommRing.mul_assoc (evalPoly p x) (evalPoly q x) (evalPoly r x)
  | mul_comm p q =>
    dsimp [evalPoly]; exact IsCommRing.mul_comm (evalPoly p x) (evalPoly q x)
  | mul_one p =>
    dsimp [evalPoly]; exact IsCommRing.mul_one (evalPoly p x)
  | one_mul p =>
    dsimp [evalPoly]; exact IsCommRing.one_mul (evalPoly p x)
  | left_distrib p q r =>
    dsimp [evalPoly]; exact IsCommRing.left_distrib (evalPoly p x) (evalPoly q x) (evalPoly r x)
  | right_distrib p q r =>
    dsimp [evalPoly]; exact IsCommRing.right_distrib (evalPoly p x) (evalPoly q x) (evalPoly r x)
  | neg_add_cancel p =>
    dsimp [evalPoly]; exact IsCommRing.neg_add_cancel (evalPoly p x)
  | const_add c1 c2 => rfl
  | const_mul c1 c2 => rfl

/-- Test variable x_0 in Fin 1 -/
def var0 : Fin 1 := ⟨0, by decide⟩

/-- Test unnormalized polynomial representing (1 - x_0) + x_0. -/
def testOneMinusXPlusX : Poly Int 1 :=
  Poly.add
    (Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var var0)))
    (Poly.var var0)

/-- Verification that literal AST equality FAILS for unnormalized (1 - x_0) + x_0. -/
theorem test_ast_differs : testOneMinusXPlusX ≠ Poly.const 1 := by
  intro h; injection h

/-- Verification that polynomial ring equivalence ACCEPTS (1 - x_0) + x_0 = 1. -/
theorem test_poly_ring_eq_accepts : PolyRingEq testOneMinusXPlusX (Poly.const 1 : Poly Int 1) := by
  have h_assoc : PolyRingEq testOneMinusXPlusX
      (Poly.add (Poly.const 1 : Poly Int 1)
        (Poly.add (Poly.mul (Poly.const (-1) : Poly Int 1) (Poly.var var0)) (Poly.var var0))) := by
    change PolyRingEq
      (Poly.add (Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var var0))) (Poly.var var0))
      (Poly.add (Poly.const 1) (Poly.add (Poly.mul (Poly.const (-1)) (Poly.var var0)) (Poly.var var0)))
    exact PolyRingEq.add_assoc (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var var0)) (Poly.var var0)
  have h_cancel : PolyRingEq
      (Poly.add (Poly.mul (Poly.const (-1) : Poly Int 1) (Poly.var var0)) (Poly.var var0))
      (Poly.const 0 : Poly Int 1) :=
    PolyRingEq.neg_add_cancel (Poly.var var0)
  have h_step : PolyRingEq
      (Poly.add (Poly.const 1 : Poly Int 1)
        (Poly.add (Poly.mul (Poly.const (-1)) (Poly.var var0)) (Poly.var var0)))
      (Poly.add (Poly.const 1 : Poly Int 1) (Poly.const 0 : Poly Int 1)) :=
    PolyRingEq.add_congr (PolyRingEq.refl (Poly.const 1 : Poly Int 1)) h_cancel
  have h_zero : PolyRingEq
      (Poly.add (Poly.const 1 : Poly Int 1) (Poly.const 0 : Poly Int 1))
      (Poly.const 1 : Poly Int 1) :=
    PolyRingEq.add_zero (Poly.const 1 : Poly Int 1)
  exact PolyRingEq.trans h_assoc (PolyRingEq.trans h_step h_zero)

/-- Semantic evaluation theorem for unnormalized (1 - x_0) + x_0:
    Evaluates to 1 for every integer assignment x : Fin 1 → Int. -/
theorem eval_testOneMinusXPlusX (x : Fin 1 → Int) :
    evalPoly testOneMinusXPlusX x = 1 := by
  have h := polyRingEq_sound test_poly_ring_eq_accepts x
  dsimp [evalPoly] at h
  exact h

/-- Test confirming (1 - x_0) + x_0 evaluates to 1 at arbitrary assignment x. -/
theorem test_one_minus_x_plus_x_eval_sound (x : Fin 1 → Int) :
    evalPoly testOneMinusXPlusX x = 1 :=
  eval_testOneMinusXPlusX x

/-- Master Theorem: Functorial mapping of polynomial ring equivalences under any ring homomorphism. -/
theorem mapCoeff_polyRingEq {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                         [Add S] [Mul S] [Zero S] [One S] [Neg S] {n : Nat}
    (f : RingHom R S) {p q : Poly R n} (h : PolyRingEq p q) :
    PolyRingEq (mapCoeff f.toFun p) (mapCoeff f.toFun q) := by
  induction h with
  | refl p => exact PolyRingEq.refl (mapCoeff f.toFun p)
  | symm h ih => exact PolyRingEq.symm ih
  | trans h1 h2 ih1 ih2 => exact PolyRingEq.trans ih1 ih2
  | add_congr h1 h2 ih1 ih2 =>
    dsimp [mapCoeff]
    exact PolyRingEq.add_congr ih1 ih2
  | mul_congr h1 h2 ih1 ih2 =>
    dsimp [mapCoeff]
    exact PolyRingEq.mul_congr ih1 ih2
  | add_assoc p q r =>
    dsimp [mapCoeff]
    exact PolyRingEq.add_assoc (mapCoeff f.toFun p) (mapCoeff f.toFun q) (mapCoeff f.toFun r)
  | add_comm p q =>
    dsimp [mapCoeff]
    exact PolyRingEq.add_comm (mapCoeff f.toFun p) (mapCoeff f.toFun q)
  | add_zero p =>
    dsimp [mapCoeff]
    have h_zero : (Poly.const (f.toFun 0) : Poly S n) = Poly.const 0 := by
      exact congrArg Poly.const f.map_zero
    rw [h_zero]
    exact PolyRingEq.add_zero (mapCoeff f.toFun p)
  | zero_add p =>
    dsimp [mapCoeff]
    have h_zero : (Poly.const (f.toFun 0) : Poly S n) = Poly.const 0 := by
      exact congrArg Poly.const f.map_zero
    rw [h_zero]
    exact PolyRingEq.zero_add (mapCoeff f.toFun p)
  | mul_assoc p q r =>
    dsimp [mapCoeff]
    exact PolyRingEq.mul_assoc (mapCoeff f.toFun p) (mapCoeff f.toFun q) (mapCoeff f.toFun r)
  | mul_comm p q =>
    dsimp [mapCoeff]
    exact PolyRingEq.mul_comm (mapCoeff f.toFun p) (mapCoeff f.toFun q)
  | mul_one p =>
    dsimp [mapCoeff]
    have h_one : (Poly.const (f.toFun 1) : Poly S n) = Poly.const 1 := by
      exact congrArg Poly.const f.map_one
    rw [h_one]
    exact PolyRingEq.mul_one (mapCoeff f.toFun p)
  | one_mul p =>
    dsimp [mapCoeff]
    have h_one : (Poly.const (f.toFun 1) : Poly S n) = Poly.const 1 := by
      exact congrArg Poly.const f.map_one
    rw [h_one]
    exact PolyRingEq.one_mul (mapCoeff f.toFun p)
  | left_distrib p q r =>
    dsimp [mapCoeff]
    exact PolyRingEq.left_distrib (mapCoeff f.toFun p) (mapCoeff f.toFun q) (mapCoeff f.toFun r)
  | right_distrib p q r =>
    dsimp [mapCoeff]
    exact PolyRingEq.right_distrib (mapCoeff f.toFun p) (mapCoeff f.toFun q) (mapCoeff f.toFun r)
  | neg_add_cancel p =>
    dsimp [mapCoeff]
    have h_neg1 : (Poly.const (f.toFun (-1)) : Poly S n) = Poly.const (-1) := by
      have : f.toFun (-1) = -1 := by rw [f.map_neg, f.map_one]
      exact congrArg Poly.const this
    rw [h_neg1]
    have h_zero : (Poly.const (f.toFun 0) : Poly S n) = Poly.const 0 := by
      exact congrArg Poly.const f.map_zero
    rw [h_zero]
    exact PolyRingEq.neg_add_cancel (mapCoeff f.toFun p)
  | const_add c1 c2 =>
    dsimp [mapCoeff]
    have h_add : (Poly.const (f.toFun (c1 + c2)) : Poly S n) = Poly.const (f.toFun c1 + f.toFun c2) := by
      exact congrArg Poly.const (f.map_add c1 c2)
    rw [h_add]
    exact PolyRingEq.const_add (f.toFun c1) (f.toFun c2)
  | const_mul c1 c2 =>
    dsimp [mapCoeff]
    have h_mul : (Poly.const (f.toFun (c1 * c2)) : Poly S n) = Poly.const (f.toFun c1 * f.toFun c2) := by
      exact congrArg Poly.const (f.map_mul c1 c2)
    rw [h_mul]
    exact PolyRingEq.const_mul (f.toFun c1) (f.toFun c2)

/-!
### 3. Clause, Boolean Axiom, and Certificate Polynomials
-/

structure Literal (n : Nat) where
  var : Fin n
  polarity : Bool
deriving DecidableEq

abbrev Clause (n : Nat) := List (Literal n)
abbrev Formula (n : Nat) := List (Clause n)

def litPoly {R : Type} (one neg_one : R) {n : Nat} (lit : Literal n) : Poly R n :=
  match lit.polarity with
  | true => Poly.add (Poly.const one) (Poly.mul (Poly.const neg_one) (Poly.var lit.var))
  | false => Poly.var lit.var

def clausePoly {R : Type} (one neg_one : R) {n : Nat} (c : Clause n) : Poly R n :=
  match c with
  | [] => Poly.const one
  | lit :: rest => Poly.mul (litPoly one neg_one lit) (clausePoly one neg_one rest)

def boolAxiomPoly {R : Type} (neg_one : R) {n : Nat} (i : Fin n) : Poly R n :=
  Poly.add (Poly.mul (Poly.var i) (Poly.var i)) (Poly.mul (Poly.const neg_one) (Poly.var i))

def sumClauseTerms {R : Type} (zero one neg_one : R) {n : Nat}
    (q : List (Poly R n)) (F : Formula n) : Poly R n :=
  match q, F with
  | [], _ => Poly.const zero
  | _, [] => Poly.const zero
  | q_head :: q_tail, c :: F_tail =>
    Poly.add (Poly.mul q_head (clausePoly one neg_one c))
             (sumClauseTerms zero one neg_one q_tail F_tail)

def sumBoolTerms {R : Type} (zero neg_one : R) {n : Nat}
    (r : Fin n → Poly R n) : Poly R n :=
  (List.finRange n).foldl
    (fun acc i => Poly.add acc (Poly.mul (r i) (boolAxiomPoly neg_one i)))
    (Poly.const zero)

def certificatePoly {R : Type} (zero one neg_one : R) {n : Nat}
    (q : List (Poly R n)) (F : Formula n) (r : Fin n → Poly R n) : Poly R n :=
  Poly.add (sumClauseTerms zero one neg_one q F) (sumBoolTerms zero neg_one r)

theorem mapCoeff_litPoly {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                     [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat} (lit : Literal n) :
    mapCoeff f.toFun (litPoly 1 (-1) lit) = litPoly 1 (-1) lit := by
  cases lit with | mk v p =>
  cases p with
  | false => rfl
  | true =>
    dsimp [litPoly, mapCoeff]
    have h1 : f.toFun 1 = 1 := f.map_one
    have h_neg1 : f.toFun (-1) = -1 := by rw [f.map_neg, f.map_one]
    rw [h1, h_neg1]

theorem mapCoeff_clausePoly {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                         [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat} (c : Clause n) :
    mapCoeff f.toFun (clausePoly 1 (-1) c) = clausePoly 1 (-1) c := by
  induction c with
  | nil =>
    dsimp [clausePoly, mapCoeff]
    rw [f.map_one]
  | cons lit rest ih =>
    dsimp [clausePoly, mapCoeff]
    rw [mapCoeff_litPoly f lit, ih]

theorem mapCoeff_boolAxiomPoly {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                           [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat} (i : Fin n) :
    mapCoeff f.toFun (boolAxiomPoly (-1) i) = boolAxiomPoly (-1) i := by
  dsimp [boolAxiomPoly, mapCoeff]
  have h_neg1 : f.toFun (-1) = -1 := by rw [f.map_neg, f.map_one]
  rw [h_neg1]

theorem mapCoeff_sumClauseTerms {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                             [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat} (q : List (Poly R n)) (F : Formula n) :
    mapCoeff f.toFun (sumClauseTerms 0 1 (-1) q F) =
    sumClauseTerms 0 1 (-1) (q.map (mapCoeff f.toFun)) F := by
  induction q generalizing F with
  | nil =>
    dsimp [sumClauseTerms, mapCoeff, List.map]
    rw [f.map_zero]
  | cons q_head q_tail ih =>
    cases F with
    | nil =>
      dsimp [sumClauseTerms, mapCoeff, List.map]
      rw [f.map_zero]
    | cons c F_tail =>
      dsimp [sumClauseTerms, mapCoeff, List.map]
      rw [mapCoeff_clausePoly f c, ih F_tail]

theorem mapCoeff_sumBoolTerms_gen {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                               [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat}
    (L : List (Fin n)) (r : Fin n → Poly R n) (acc : Poly R n) :
    mapCoeff f.toFun (L.foldl (fun s i => Poly.add s (Poly.mul (r i) (boolAxiomPoly (-1) i))) acc) =
    L.foldl (fun s i => Poly.add s (Poly.mul (mapCoeff f.toFun (r i)) (boolAxiomPoly (-1) i))) (mapCoeff f.toFun acc) := by
  induction L generalizing acc with
  | nil => rfl
  | cons hd tl ih =>
    dsimp [List.foldl]
    have ih_inst := ih (Poly.add acc (Poly.mul (r hd) (boolAxiomPoly (-1) hd)))
    dsimp [mapCoeff] at ih_inst
    rw [mapCoeff_boolAxiomPoly f hd] at ih_inst
    exact ih_inst

theorem mapCoeff_sumBoolTerms {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                           [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat} (r : Fin n → Poly R n) :
    mapCoeff f.toFun (sumBoolTerms 0 (-1) r) =
    sumBoolTerms 0 (-1) (fun i => mapCoeff f.toFun (r i)) := by
  dsimp [sumBoolTerms]
  have h := mapCoeff_sumBoolTerms_gen f (List.finRange n) r (Poly.const 0)
  dsimp [mapCoeff] at h
  have h_zero : (Poly.const (f.toFun 0) : Poly S n) = Poly.const 0 := by
    exact congrArg Poly.const f.map_zero
  rw [h_zero] at h
  exact h

theorem mapCoeff_certificatePoly {R S : Type} [Add R] [Mul R] [Zero R] [One R] [Neg R]
                                             [Add S] [Mul S] [Zero S] [One S] [Neg S]
    (f : RingHom R S) {n : Nat} (q : List (Poly R n)) (F : Formula n) (r : Fin n → Poly R n) :
    mapCoeff f.toFun (certificatePoly 0 1 (-1) q F r) =
    certificatePoly 0 1 (-1) (q.map (mapCoeff f.toFun)) F (fun i => mapCoeff f.toFun (r i)) := by
  dsimp [certificatePoly, mapCoeff]
  rw [mapCoeff_sumClauseTerms f q F, mapCoeff_sumBoolTerms f r]

/-!
### 4. Nullstellensatz Certificates and Master Lifting Theorem
-/

/-- Concrete Nullstellensatz Refutation Certificate with Integer Coefficients,
    encoded via polynomial ring equivalence modulo commutative ring laws. -/
structure ConcreteIntAlgebraicNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (Poly Int n)
  r : Fin n → Poly Int n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (clausePoly 1 (-1) (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  algebraic_identity : PolyRingEq (certificatePoly 0 1 (-1) q F r) (Poly.const 1)

/-- Concrete Nullstellensatz Refutation Certificate with Rational Coefficients (Rat),
    encoded via polynomial ring equivalence modulo commutative ring laws. -/
structure ConcreteRatAlgebraicNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (Poly Rat n)
  r : Fin n → Poly Rat n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (clausePoly (Rat.ofInt 1) (Rat.ofInt (-1)) (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  algebraic_identity : PolyRingEq (certificatePoly (Rat.ofInt 0) (Rat.ofInt 1) (Rat.ofInt (-1)) q F r) (Poly.const (Rat.ofInt 1))

theorem get_map_mapCoeff {R S : Type} {n : Nat} (f : R → S) (q : List (Poly R n))
    (i : Nat) (hq : i < (q.map (mapCoeff f)).length) :
    (q.map (mapCoeff f)).get ⟨i, hq⟩ = mapCoeff f (q.get ⟨i, by rw [List.length_map] at hq; exact hq⟩) := by
  induction q generalizing i with
  | nil =>
    have : i < 0 := by rw [List.length_map] at hq; exact hq
    contradiction
  | cons hd tl ih =>
    cases i with
    | zero => rfl
    | succ j =>
      dsimp [List.map, List.get]
      have hj : j < (tl.map (mapCoeff f)).length := by
        dsimp [List.map] at hq
        omega
      exact ih j hj

/-- Constructive lifting of an Integer Algebraic Nullstellensatz refutation to genuine Rat. -/
def liftIntToRatAlgebraicRefutation {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteIntAlgebraicNSRefutation F d) :
    ConcreteRatAlgebraicNSRefutation F d where
  q := cert.q.map (mapCoeff Rat.ofInt)
  r := fun i => mapCoeff Rat.ofInt (cert.r i)
  q_len := by
    rw [List.length_map, cert.q_len]
  clause_deg_bound := by
    intro i hq hF
    have hq_orig : i < cert.q.length := by rw [List.length_map] at hq; exact hq
    rw [get_map_mapCoeff]
    rw [mapCoeff_degree]
    have h_cp : clausePoly (Rat.ofInt 1) (Rat.ofInt (-1)) (F.get ⟨i, hF⟩) =
                mapCoeff Rat.ofInt (clausePoly 1 (-1) (F.get ⟨i, hF⟩)) := by
      exact (mapCoeff_clausePoly intToRatEmbedding.toRingHom (F.get ⟨i, hF⟩)).symm
    rw [h_cp, mapCoeff_degree]
    exact cert.clause_deg_bound i hq_orig hF
  bool_deg_bound := by
    intro i
    rw [mapCoeff_degree]
    exact cert.bool_deg_bound i
  algebraic_identity := by
    have h_lift := mapCoeff_polyRingEq intToRatEmbedding.toRingHom cert.algebraic_identity
    have h_cert := mapCoeff_certificatePoly intToRatEmbedding.toRingHom cert.q F cert.r
    dsimp [intToRatEmbedding] at h_cert h_lift
    rw [h_cert] at h_lift
    have h_one : (mapCoeff Rat.ofInt (Poly.const 1 : Poly Int n)) = (Poly.const 1 : Poly Rat n) := by
      dsimp [mapCoeff]
      exact congrArg Poly.const rat_ofInt_one
    rw [h_one] at h_lift
    exact h_lift

/-- Master One-Way Rational Certificate Embedding Theorem:
    Every formula admitting an integer Nullstellensatz refutation of degree ≤ d
    admits a Nullstellensatz refutation of degree ≤ d over the rational field ℚ. -/
theorem int_cert_implies_rat_cert {n : Nat} {F : Formula n} {d : Nat} :
    Nonempty (ConcreteIntAlgebraicNSRefutation F d) → Nonempty (ConcreteRatAlgebraicNSRefutation F d) := by
  rintro ⟨cert⟩
  exact ⟨liftIntToRatAlgebraicRefutation cert⟩

/-- Semantic evaluation corollary for ConcreteRatAlgebraicNSRefutation:
    The rational certificate polynomial evaluates to 1 at every assignment in ℚ^n. -/
theorem eval_concrete_rat_refutation {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteRatAlgebraicNSRefutation F d) (x : Fin n → Rat) :
    evalPoly (certificatePoly (Rat.ofInt 0) (Rat.ofInt 1) (Rat.ofInt (-1)) cert.q F cert.r) x = 1 := by
  have h := polyRingEq_sound cert.algebraic_identity x
  dsimp [evalPoly] at h
  exact h

/-- Corollary: Every ConcreteRatAlgebraicNSRefutation evaluates to 1 at every rational assignment. -/
theorem rat_cert_evaluates_to_one {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteRatAlgebraicNSRefutation F d) (x : Fin n → Rat) :
    evalPoly (certificatePoly (Rat.ofInt 0) (Rat.ofInt 1) (Rat.ofInt (-1)) cert.q F cert.r) x = 1 :=
  eval_concrete_rat_refutation cert x

/-- Semantic evaluation corollary for ConcreteIntAlgebraicNSRefutation:
    The integer certificate polynomial evaluates to 1 at every assignment in ℤ^n. -/
theorem eval_concrete_int_refutation {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteIntAlgebraicNSRefutation F d) (x : Fin n → Int) :
    evalPoly (certificatePoly 0 1 (-1) cert.q F cert.r) x = 1 := by
  have h := polyRingEq_sound cert.algebraic_identity x
  dsimp [evalPoly] at h
  exact h

/-- Corollary: Every ConcreteIntAlgebraicNSRefutation evaluates to 1 at every integer assignment. -/
theorem int_cert_evaluates_to_one {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteIntAlgebraicNSRefutation F d) (x : Fin n → Int) :
    evalPoly (certificatePoly 0 1 (-1) cert.q F cert.r) x = 1 :=
  eval_concrete_int_refutation cert x

/-!
### 5. Genuine Monomial Exponent Evaluation and Boolean Invariance
-/

/-- Genuine integer exponentiation: computes val^e. -/
def intPow (val : Int) (e : Nat) : Int :=
  match e with
  | 0 => 1
  | Nat.succ k => val * intPow val k

/-- Test distinguishing x^2 = 4 from x^1 = 2 at x = 2 before reduction. -/
theorem test_exponent_distinction :
    intPow 2 2 = 4 ∧ intPow 2 1 = 2 ∧ intPow 2 2 ≠ intPow 2 1 := by
  decide

/-- Canonical single-variable exponent reducer: maps any positive exponent to 1. -/
def reduceExp (e : Nat) : Nat :=
  match e with
  | 0 => 0
  | _ => 1

/-- Canonical Multilinear Monomial Exponent Vector Reducer. -/
def reduceMonomialExp {n : Nat} (exps : Fin n → Nat) : Fin n → Nat :=
  fun i => reduceExp (exps i)

theorem reduceExp_idempotent (e : Nat) :
    reduceExp (reduceExp e) = reduceExp e := by
  cases e with
  | zero => rfl
  | succ k => rfl

theorem reduceMonomialExp_idempotent {n : Nat} (exps : Fin n → Nat) :
    reduceMonomialExp (reduceMonomialExp exps) = reduceMonomialExp exps := by
  funext i
  exact reduceExp_idempotent (exps i)

theorem cube_exp_collapse (e : Nat) (h : e = 3) :
    e = 3 ∧ reduceExp e = 1 := by
  subst h
  exact ⟨rfl, rfl⟩

theorem intPow_zero_pos (k : Nat) : intPow 0 (k + 1) = 0 := by
  dsimp [intPow]
  rw [Int.zero_mul]

theorem intPow_one_any (e : Nat) : intPow 1 e = 1 := by
  induction e with
  | zero => rfl
  | succ k ih =>
    dsimp [intPow]
    rw [Int.one_mul]
    exact ih

/-- Theorem: For any Boolean value val ∈ {0, 1}, exponent reduction preserves evaluation. -/
theorem intPow_boolean_reduced (val : Int) (h : val = 0 ∨ val = 1) (e : Nat) :
    intPow val (reduceExp e) = intPow val e := by
  cases h with
  | inl h0 =>
    rw [h0]
    cases e with
    | zero => rfl
    | succ k =>
      have h_lhs : intPow 0 (reduceExp (k + 1)) = 0 := by
        change intPow 0 1 = 0
        exact intPow_zero_pos 0
      have h_rhs : intPow 0 (k + 1) = 0 := intPow_zero_pos k
      rw [h_lhs, h_rhs]
  | inr h1 =>
    rw [h1]
    rw [intPow_one_any e]
    rw [intPow_one_any (reduceExp e)]

/-- Monomial evaluation computing actual product of variable powers: ∏ x_i^{e_i}. -/
def evalMonomialExp {n : Nat} (exps : Fin n → Nat) (x : Fin n → Int) : Int :=
  (List.finRange n).foldl (fun acc i => acc * intPow (x i) (exps i)) 1

theorem foldl_monomial_pow_eq {n : Nat} (exps : Fin n → Nat) (x : Fin n → Int)
    (h_bool : ∀ i, x i = 0 ∨ x i = 1) (L : List (Fin n)) (acc : Int) :
    L.foldl (fun s i => s * intPow (x i) (reduceMonomialExp exps i)) acc =
    L.foldl (fun s i => s * intPow (x i) (exps i)) acc := by
  induction L generalizing acc with
  | nil => rfl
  | cons hd tl ih =>
    dsimp [List.foldl]
    have h_hd : intPow (x hd) (reduceMonomialExp exps hd) = intPow (x hd) (exps hd) := by
      exact intPow_boolean_reduced (x hd) (h_bool hd) (exps hd)
    rw [h_hd]
    exact ih (acc * intPow (x hd) (exps hd))

/-- Semantic Evaluation Preservation Theorem:
    Canonical multilinear reduction preserves monomial power evaluation on all Boolean cube assignments. -/
theorem evalMonomialExp_reduced {n : Nat} (exps : Fin n → Nat) (x : Fin n → Int)
    (h_bool : ∀ i, x i = 0 ∨ x i = 1) :
    evalMonomialExp (reduceMonomialExp exps) x = evalMonomialExp exps x := by
  dsimp [evalMonomialExp]
  exact foldl_monomial_pow_eq exps x h_bool (List.finRange n) 1

/-- Variable-list canonical multilinear monomial reducer. -/
def insertVar {n : Nat} (v : Fin n) (m : List (Fin n)) : List (Fin n) :=
  match m with
  | [] => [v]
  | u :: rest =>
    if v == u then u :: rest
    else if v.val < u.val then v :: u :: rest
    else u :: insertVar v rest

def reduceMonomial {n : Nat} (m : List (Fin n)) : List (Fin n) :=
  match m with
  | [] => []
  | v :: rest => insertVar v (reduceMonomial rest)

theorem insertVar_self {n : Nat} (i : Fin n) (rest : List (Fin n)) :
    insertVar i (i :: rest) = i :: rest := by
  dsimp [insertVar]
  have h : (i == i) = true := beq_self_eq_true' i
  rw [h]
  rfl

theorem reduceMonomial_two {n : Nat} (i : Fin n) :
    reduceMonomial [i, i] = [i] := by
  dsimp [reduceMonomial]
  exact insertVar_self i []

theorem reduceMonomial_three {n : Nat} (i : Fin n) :
    reduceMonomial [i, i, i] = [i] := by
  change insertVar i (reduceMonomial [i, i]) = [i]
  rw [reduceMonomial_two]
  exact insertVar_self i []

theorem cube_degree_collapse {n : Nat} (i : Fin n) :
    [i, i, i].length = 3 ∧ (reduceMonomial [i, i, i]).length = 1 := by
  rw [reduceMonomial_three]
  exact ⟨rfl, rfl⟩

/-!
### 6. Denominator Clearing Obstruction (Supporting Lemma)
-/

/-- Denominator Clearing Obstruction Theorem (Supporting Lemma):
    Clearing denominators from a rational refutation ∑ (a_C/b_C) p_C + ∑ (c_i/d_i) B_i = 1
    yields an integer identity ∑ a'_C p_C + ∑ c'_i B_i = D, where D = lcm(denominators).
    If D > 1, no integer k satisfies D * k = 1, explaining why division by D cannot produce
    an integer Nullstellensatz refutation directly without additional modular arguments. -/
theorem denominator_clearing_obstruction (D : Int) (hD : D > 1) :
    ¬ (∃ (k : Int), D * k = 1) := by
  rintro ⟨k, hk⟩
  cases k with
  | ofNat n =>
    cases n with
    | zero =>
      dsimp [Int.ofNat] at hk
      omega
    | succ m =>
      have hD2 : 2 ≤ D := by omega
      have hm : 1 ≤ (m : Int) + 1 := by omega
      have h_prod : D * ((m : Int) + 1) ≥ 2 := by
        have : D * ((m : Int) + 1) = D * (m : Int) + D * 1 := by rw [Int.mul_add]
        rw [this, Int.mul_one]
        have h_nonneg : D * (m : Int) ≥ 0 := by
          exact Int.mul_nonneg (by omega) (by omega)
        omega
      have hk_eq : D * ((m : Int) + 1) = 1 := hk
      omega
  | negSucc m =>
    have h1 : D > 0 := by omega
    have h2 : Int.negSucc m < 0 := Int.negSucc_lt_zero m
    have : D * Int.negSucc m < 0 := Int.mul_neg_of_pos_of_neg h1 h2
    omega

/-!
### 7. Refutation Soundness: Nullstellensatz Certificates Imply CNF Unsatisfiability
-/

/-- A Boolean assignment maps each variable index to a boolean truth value. -/
def Assignment (n : Nat) := Fin n → Bool

/-- A literal is satisfied under assignment a if its truth value matches its polarity:
    polarity = true corresponds to positive literal (satisfied if a lit.var = true)
    polarity = false corresponds to negative literal (satisfied if a lit.var = false). -/
def satLit {n : Nat} (lit : Literal n) (a : Assignment n) : Bool :=
  match lit.polarity with
  | true => a lit.var
  | false => !(a lit.var)

/-- Evaluating a clause as a disjunction of literals under assignment a.
    The empty clause is false (unsatisfiable). -/
def satClause {n : Nat} (c : Clause n) (a : Assignment n) : Bool :=
  match c with
  | [] => false
  | lit :: rest => satLit lit a || satClause rest a

/-- Evaluating a formula as a conjunction of clauses under assignment a.
    The empty formula is true (vacuously satisfied). -/
def satFormula {n : Nat} (F : Formula n) (a : Assignment n) : Bool :=
  match F with
  | [] => true
  | c :: rest => satClause c a && satFormula rest a

/-- A formula is unsatisfiable if no assignment satisfies it. -/
def FormulaUnsatisfiable {n : Nat} (F : Formula n) : Prop :=
  ∀ (a : Assignment n), satFormula F a = false

/-- Canonical embedding of a Boolean assignment into ℚ^n. -/
def assignToRat {n : Nat} (a : Assignment n) : Fin n → Rat :=
  fun i => if a i then (1 : Rat) else (0 : Rat)

/-- Canonical embedding of a Boolean assignment into ℤ^n. -/
def assignToInt {n : Nat} (a : Assignment n) : Fin n → Int :=
  fun i => if a i then (1 : Int) else (0 : Int)

/-- Lemma 1a: Evaluation of literal polynomial when literal is satisfied.
    Evaluates to 0 on the embedded Boolean assignment. -/
theorem eval_litPoly_satisfied_rat {n : Nat} (lit : Literal n) (a : Assignment n)
    (h : satLit lit a = true) :
    evalPoly (litPoly (Rat.ofInt 1) (Rat.ofInt (-1)) lit) (assignToRat a) = (0 : Rat) := by
  cases lit with | mk var pol =>
  cases pol with
  | false =>
    dsimp [satLit] at h
    have h_a : a var = false := by
      cases h_v : a var
      · rfl
      · rw [h_v] at h; contradiction
    dsimp [litPoly, evalPoly, assignToRat]
    rw [h_a]
    rfl
  | true =>
    dsimp [satLit] at h
    dsimp [litPoly, evalPoly, assignToRat]
    rw [h]
    dsimp
    have h1 : Rat.ofInt 1 = 1 := rfl
    have h_neg1 : Rat.ofInt (-1) = -1 := rfl
    rw [h1, h_neg1]
    rw [Rat.mul_one]
    exact Rat.add_neg_cancel 1

/-- Lemma 1b: Evaluation of literal polynomial when literal is falsified.
    Evaluates to 1 on the embedded Boolean assignment. -/
theorem eval_litPoly_falsified_rat {n : Nat} (lit : Literal n) (a : Assignment n)
    (h : satLit lit a = false) :
    evalPoly (litPoly (Rat.ofInt 1) (Rat.ofInt (-1)) lit) (assignToRat a) = (1 : Rat) := by
  cases lit with | mk var pol =>
  cases pol with
  | false =>
    dsimp [satLit] at h
    have h_a : a var = true := by
      cases h_v : a var
      · rw [h_v] at h; contradiction
      · rfl
    dsimp [litPoly, evalPoly, assignToRat]
    rw [h_a]
    rfl
  | true =>
    dsimp [satLit] at h
    dsimp [litPoly, evalPoly, assignToRat]
    rw [h]
    dsimp
    have h1 : Rat.ofInt 1 = 1 := rfl
    have h_neg1 : Rat.ofInt (-1) = -1 := rfl
    rw [h1, h_neg1]
    rw [Rat.mul_zero, Rat.add_zero]

/-- Lemma 1: Exact Boolean literal polynomial evaluation dichotomy. -/
theorem eval_litPoly_boolean {n : Nat} (lit : Literal n) (a : Assignment n) :
    (satLit lit a = true ∧ evalPoly (litPoly (Rat.ofInt 1) (Rat.ofInt (-1)) lit) (assignToRat a) = 0) ∨
    (satLit lit a = false ∧ evalPoly (litPoly (Rat.ofInt 1) (Rat.ofInt (-1)) lit) (assignToRat a) = 1) := by
  cases h : satLit lit a with
  | true => exact Or.inl ⟨rfl, eval_litPoly_satisfied_rat lit a h⟩
  | false => exact Or.inr ⟨rfl, eval_litPoly_falsified_rat lit a h⟩

/-- Lemma 2: Evaluation of clause polynomial on embedded Boolean assignment.
    Every satisfied clause evaluates to 0. -/
theorem eval_clausePoly_zero_of_satisfied_rat {n : Nat} (c : Clause n) (a : Assignment n)
    (h : satClause c a = true) :
    evalPoly (clausePoly (Rat.ofInt 1) (Rat.ofInt (-1)) c) (assignToRat a) = (0 : Rat) := by
  induction c with
  | nil =>
    dsimp [satClause] at h
    contradiction
  | cons lit rest ih =>
    dsimp [satClause] at h
    dsimp [clausePoly, evalPoly]
    cases h_lit : satLit lit a
    · rw [h_lit] at h
      change satClause rest a = true at h
      have ih_zero := ih h
      rw [ih_zero, Rat.mul_zero]
    · have h_zero : evalPoly (litPoly (Rat.ofInt 1) (Rat.ofInt (-1)) lit) (assignToRat a) = 0 :=
        eval_litPoly_satisfied_rat lit a h_lit
      rw [h_zero, Rat.zero_mul]

/-- Lemma 3: Evaluation of Boolean axiom polynomial on embedded Boolean assignment.
    For every variable i, x_i^2 - x_i = 0 at x = assignToRat a. -/
theorem eval_boolAxiomPoly_rat {n : Nat} (i : Fin n) (a : Assignment n) :
    evalPoly (boolAxiomPoly (Rat.ofInt (-1)) i) (assignToRat a) = (0 : Rat) := by
  dsimp [boolAxiomPoly, evalPoly, assignToRat]
  cases (a i) with
  | false =>
    dsimp
    rw [Rat.zero_mul, Rat.mul_zero, Rat.add_zero]
  | true =>
    dsimp
    rw [Rat.one_mul, Rat.mul_one]
    exact Rat.add_neg_cancel 1

/-- Fold accumulator lemma for sumBoolTerms evaluation. -/
theorem eval_foldl_sumBoolTerms_rat {n : Nat} (L : List (Fin n))
    (r : Fin n → Poly Rat n) (acc : Poly Rat n) (a : Assignment n)
    (hacc : evalPoly acc (assignToRat a) = 0) :
    evalPoly (L.foldl (fun s i => Poly.add s (Poly.mul (r i) (boolAxiomPoly (Rat.ofInt (-1)) i))) acc) (assignToRat a) = 0 := by
  induction L generalizing acc with
  | nil => exact hacc
  | cons hd tl ih =>
    dsimp [List.foldl]
    apply ih
    dsimp [evalPoly]
    rw [eval_boolAxiomPoly_rat]
    rw [Rat.mul_zero, hacc, Rat.add_zero]

/-- Evaluation of sum of Boolean axiom terms evaluates to 0 on any Boolean assignment. -/
theorem eval_sumBoolTerms_rat {n : Nat} (r : Fin n → Poly Rat n) (a : Assignment n) :
    evalPoly (sumBoolTerms (Rat.ofInt 0) (Rat.ofInt (-1)) r) (assignToRat a) = 0 := by
  dsimp [sumBoolTerms]
  apply eval_foldl_sumBoolTerms_rat
  rfl

/-- Evaluation of sum of clause terms evaluates to 0 under any satisfying assignment. -/
theorem eval_sumClauseTerms_rat {n : Nat} (q : List (Poly Rat n)) (F : Formula n)
    (a : Assignment n) (h_sat : satFormula F a = true) :
    evalPoly (sumClauseTerms (Rat.ofInt 0) (Rat.ofInt 1) (Rat.ofInt (-1)) q F) (assignToRat a) = 0 := by
  induction F generalizing q with
  | nil =>
    cases q <;> rfl
  | cons c rest ih =>
    dsimp [satFormula] at h_sat
    cases h_c : satClause c a
    · rw [h_c] at h_sat
      change false = true at h_sat
      contradiction
    · rw [h_c] at h_sat
      change satFormula rest a = true at h_sat
      cases q with
      | nil => rfl
      | cons q_head q_tail =>
        dsimp [sumClauseTerms, evalPoly]
        have h_c_zero := eval_clausePoly_zero_of_satisfied_rat c a h_c
        rw [h_c_zero, Rat.mul_zero]
        have ih_tail := ih q_tail h_sat
        rw [ih_tail, Rat.zero_add]

/-- Lemma 4: The full Nullstellensatz certificate polynomial evaluates to 0
    at any assignment that satisfies the formula F. -/
theorem eval_certificatePoly_zero_of_satisfied_formula_rat {n : Nat}
    (q : List (Poly Rat n)) (F : Formula n) (r : Fin n → Poly Rat n)
    (a : Assignment n) (h_sat : satFormula F a = true) :
    evalPoly (certificatePoly (Rat.ofInt 0) (Rat.ofInt 1) (Rat.ofInt (-1)) q F r) (assignToRat a) = (0 : Rat) := by
  dsimp [certificatePoly, evalPoly]
  have h_clauses := eval_sumClauseTerms_rat q F a h_sat
  have h_bool := eval_sumBoolTerms_rat r a
  rw [h_clauses, h_bool, Rat.add_zero]

theorem rat_zero_ne_one : (0 : Rat) ≠ 1 := by
  intro h
  have h_num : (0 : Rat).num = (1 : Rat).num := congrArg Rat.num h
  revert h_num
  decide

/-- Theorem: Rational Nullstellensatz Refutation Soundness for CNF formulas.
    If a formula admits a valid Nullstellensatz refutation over ℚ, it is unsatisfiable. -/
theorem rat_refutation_soundness {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteRatAlgebraicNSRefutation F d) :
    FormulaUnsatisfiable F := by
  intro a
  cases h_sat : satFormula F a with
  | false => rfl
  | true =>
    have h_zero := eval_certificatePoly_zero_of_satisfied_formula_rat cert.q F cert.r a h_sat
    have h_one := eval_concrete_rat_refutation cert (assignToRat a)
    rw [h_zero] at h_one
    exfalso
    exact rat_zero_ne_one h_one

/-- Theorem: Integer Nullstellensatz Refutation Soundness for CNF formulas.
    If a formula admits a valid Nullstellensatz refutation over ℤ, it is unsatisfiable. -/
theorem int_refutation_soundness {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteIntAlgebraicNSRefutation F d) :
    FormulaUnsatisfiable F := by
  have rat_cert := liftIntToRatAlgebraicRefutation cert
  exact rat_refutation_soundness rat_cert

/-!
### 8. Concrete Sanity Tests: Satisfiable Unit vs Explicit Contradiction
-/

/-- Satisfiable unit clause formula: F_sat = [[x_0]]. -/
def unitSatFormula : Formula 1 := [[⟨var0, true⟩]]

/-- Verification that unitSatFormula is satisfied by the assignment setting x_0 = true. -/
theorem unitSatFormula_satisfiable : satFormula unitSatFormula (fun _ => true) = true := rfl

/-- Test 1: No Nullstellensatz refutation can exist for the satisfiable unit clause [[x_0]]. -/
theorem no_refutation_of_satisfiable_unit_clause {d : Nat} :
    ¬ Nonempty (ConcreteRatAlgebraicNSRefutation unitSatFormula d) := by
  rintro ⟨cert⟩
  have h_unsat := rat_refutation_soundness cert (fun _ => true)
  have h_sat : satFormula unitSatFormula (fun _ => true) = true := unitSatFormula_satisfiable
  rw [h_sat] at h_unsat
  contradiction

/-- Explicitly contradictory formula: F_contra = [[x_0], [¬x_0]] ((x_0) ∧ (¬x_0)). -/
def contraFormula : Formula 1 := [[⟨var0, true⟩], [⟨var0, false⟩]]

/-- Direct verification that contraFormula is unsatisfiable by exhaustive truth-table check. -/
theorem contraFormula_truth_table_unsat : FormulaUnsatisfiable contraFormula := by
  intro a
  dsimp [contraFormula, satFormula, satClause, satLit]
  cases (a var0) <;> rfl

/-- Test 2: Soundness applies to any refutation of contraFormula:
    If any Nullstellensatz refutation certificate exists for contraFormula at any degree d,
    the semantic soundness theorem concludes that contraFormula is unsatisfiable. -/
theorem contraFormula_unsatisfiable_of_certificate {d : Nat}
    (cert : ConcreteRatAlgebraicNSRefutation contraFormula d) :
    FormulaUnsatisfiable contraFormula :=
  rat_refutation_soundness cert

end RationalNullstellensatz

#print axioms RationalNullstellensatz.rat_fraction_normalization
#print axioms RationalNullstellensatz.intToRatEmbedding
#print axioms RationalNullstellensatz.polyRingEq_sound
#print axioms RationalNullstellensatz.test_ast_differs
#print axioms RationalNullstellensatz.test_poly_ring_eq_accepts
#print axioms RationalNullstellensatz.eval_testOneMinusXPlusX
#print axioms RationalNullstellensatz.test_one_minus_x_plus_x_eval_sound
#print axioms RationalNullstellensatz.mapCoeff_polyRingEq
#print axioms RationalNullstellensatz.liftIntToRatAlgebraicRefutation
#print axioms RationalNullstellensatz.int_cert_implies_rat_cert
#print axioms RationalNullstellensatz.eval_concrete_rat_refutation
#print axioms RationalNullstellensatz.rat_cert_evaluates_to_one
#print axioms RationalNullstellensatz.eval_concrete_int_refutation
#print axioms RationalNullstellensatz.int_cert_evaluates_to_one
#print axioms RationalNullstellensatz.test_exponent_distinction
#print axioms RationalNullstellensatz.intPow_boolean_reduced
#print axioms RationalNullstellensatz.evalMonomialExp_reduced
#print axioms RationalNullstellensatz.reduceMonomialExp_idempotent
#print axioms RationalNullstellensatz.cube_exp_collapse
#print axioms RationalNullstellensatz.cube_degree_collapse
#print axioms RationalNullstellensatz.denominator_clearing_obstruction
#print axioms RationalNullstellensatz.eval_litPoly_satisfied_rat
#print axioms RationalNullstellensatz.eval_litPoly_falsified_rat
#print axioms RationalNullstellensatz.eval_litPoly_boolean
#print axioms RationalNullstellensatz.eval_clausePoly_zero_of_satisfied_rat
#print axioms RationalNullstellensatz.eval_boolAxiomPoly_rat
#print axioms RationalNullstellensatz.eval_sumBoolTerms_rat
#print axioms RationalNullstellensatz.eval_sumClauseTerms_rat
#print axioms RationalNullstellensatz.eval_certificatePoly_zero_of_satisfied_formula_rat
#print axioms RationalNullstellensatz.rat_refutation_soundness
#print axioms RationalNullstellensatz.int_refutation_soundness
#print axioms RationalNullstellensatz.unitSatFormula_satisfiable
#print axioms RationalNullstellensatz.no_refutation_of_satisfiable_unit_clause
#print axioms RationalNullstellensatz.contraFormula_truth_table_unsat
#print axioms RationalNullstellensatz.contraFormula_unsatisfiable_of_certificate
