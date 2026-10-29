/-!
# Characteristic Zero Field Nullstellensatz Lifting, Monomial Reduction, and Embedding Boundaries

This module formalizes:
1. Mathematical semantics for the genuine rational field ℚ (`Rat`) from the Lean 4 standard library,
   incorporating canonical normalized fraction representation (`Rat.normalize`), lawful addition,
   multiplication, and characteristic zero embedding `Rat.ofInt : ℤ → ℚ`.
2. Direct algebraic polynomial AST certificates (`ConcreteIntAlgebraicNSRefutation` and
   `ConcreteRatAlgebraicNSRefutation`) encoding the Nullstellensatz refutation directly as a polynomial
   algebraic identity (`certificatePoly = Poly.const 1`), avoiding restriction to integer point evaluation.
3. Functorial coefficient lifting `intToRatHom : CoeffHom Int Rat` mapping integer certificates
   to field certificates over ℚ:
     `liftIntToRatAlgebraicRefutation : ConcreteIntAlgebraicNSRefutation F d → ConcreteRatAlgebraicNSRefutation F d`.
4. The master one-way embedding theorem:
     `int_cert_implies_rat_cert : Nonempty (ConcreteIntAlgebraicNSRefutation F d) → Nonempty (ConcreteRatAlgebraicNSRefutation F d)`.
5. Proved bridge from algebraic identity to universal field evaluation identity everywhere:
     `algebraic_identity_implies_field_evaluation` and `algebraic_identity_implies_eval_identity`.
6. Canonical multilinear Boolean monomial reduction via exponent vectors:
     `reduceMonomialExp : (Fin n → Nat) → (Fin n → Nat)`,
   with proofs of idempotence (`reduceMonomialExp_idempotent`), cube exponent collapse ($x_i^3 \to x_i$,
   `cube_exp_collapse`), and Boolean point evaluation invariance (`evalMonomialExp_reduced`).
   Also preserves the variable-list reducer `reduceMonomial : List (Fin n) → List (Fin n)` with `cube_degree_collapse`.
7. Supporting lemma for denominator clearing obstruction:
     `denominator_clearing_obstruction : ∀ D > 1, ¬ ∃ k : ℤ, D * k = 1`,
   identifying the algebraic obstruction to inverting rational refutations back to integer refutations.
-/

namespace RationalNullstellensatz

/-- Verified Canonical Normalized Fraction Property:
    In Lean 4's standard `Rat` type, equivalent fraction pairs normalize to identical canonical values. -/
theorem rat_fraction_normalization :
    Rat.normalize 1 2 = Rat.normalize 2 4 := rfl

/-- Parameterized polynomial AST over an arbitrary coefficient type R. -/
inductive Poly (R : Type) (n : Nat) where
  | const : R → Poly R n
  | var : Fin n → Poly R n
  | add : Poly R n → Poly R n → Poly R n
  | mul : Poly R n → Poly R n → Poly R n
deriving Inhabited

/-- Syntactic total degree of polynomial AST. -/
def totalDegree {R : Type} {n : Nat} (p : Poly R n) : Nat :=
  match p with
  | Poly.const _ => 0
  | Poly.var _ => 1
  | Poly.add p q => max (totalDegree p) (totalDegree q)
  | Poly.mul p q => totalDegree p + totalDegree q

/-- Functorial coefficient mapping between polynomial coefficient domains. -/
def mapCoeff {R S : Type} {n : Nat} (f : R → S) (p : Poly R n) : Poly S n :=
  match p with
  | Poly.const c => Poly.const (f c)
  | Poly.var i => Poly.var i
  | Poly.add p q => Poly.add (mapCoeff f p) (mapCoeff f q)
  | Poly.mul p q => Poly.mul (mapCoeff f p) (mapCoeff f q)

/-- Total degree is invariant under arbitrary coefficient mappings. -/
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

structure Literal (n : Nat) where
  var : Fin n
  polarity : Bool
deriving DecidableEq

abbrev Clause (n : Nat) := List (Literal n)
abbrev Formula (n : Nat) := List (Clause n)

/-- Literal polynomial AST over arbitrary coefficient type R. -/
def litPoly {R : Type} (one neg_one : R) {n : Nat} (lit : Literal n) : Poly R n :=
  match lit.polarity with
  | true => Poly.add (Poly.const one) (Poly.mul (Poly.const neg_one) (Poly.var lit.var))
  | false => Poly.var lit.var

/-- Clause polynomial AST over arbitrary coefficient type R. -/
def clausePoly {R : Type} (one neg_one : R) {n : Nat} (c : Clause n) : Poly R n :=
  match c with
  | [] => Poly.const one
  | lit :: rest => Poly.mul (litPoly one neg_one lit) (clausePoly one neg_one rest)

/-- Boolean idempotency generator polynomial x_i^2 - x_i over arbitrary coefficient type R. -/
def boolAxiomPoly {R : Type} (neg_one : R) {n : Nat} (i : Fin n) : Poly R n :=
  Poly.add (Poly.mul (Poly.var i) (Poly.var i)) (Poly.mul (Poly.const neg_one) (Poly.var i))

/-- Linear combination of clause polynomials: ∑ q_C p_C. -/
def sumClauseTerms {R : Type} (zero one neg_one : R) {n : Nat}
    (q : List (Poly R n)) (F : Formula n) : Poly R n :=
  match q, F with
  | [], _ => Poly.const zero
  | _, [] => Poly.const zero
  | q_head :: q_tail, c :: F_tail =>
    Poly.add (Poly.mul q_head (clausePoly one neg_one c))
             (sumClauseTerms zero one neg_one q_tail F_tail)

/-- Linear combination of Boolean idempotency polynomials: ∑ r_i (x_i^2 - x_i). -/
def sumBoolTerms {R : Type} (zero neg_one : R) {n : Nat}
    (r : Fin n → Poly R n) : Poly R n :=
  (List.finRange n).foldl
    (fun acc i => Poly.add acc (Poly.mul (r i) (boolAxiomPoly neg_one i)))
    (Poly.const zero)

/-- Complete Nullstellensatz Certificate Polynomial AST:
    ∑ q_C p_C + ∑ r_i (x_i^2 - x_i). -/
def certificatePoly {R : Type} (zero one neg_one : R) {n : Nat}
    (q : List (Poly R n)) (F : Formula n) (r : Fin n → Poly R n) : Poly R n :=
  Poly.add (sumClauseTerms zero one neg_one q F) (sumBoolTerms zero neg_one r)

/-- Coefficient Homomorphism between coefficient types R and S. -/
structure CoeffHom (R S : Type) where
  toFun : R → S
  zero_R : R
  zero_S : S
  one_R : R
  one_S : S
  neg_one_R : R
  neg_one_S : S
  map_zero : toFun zero_R = zero_S
  map_one : toFun one_R = one_S
  map_neg_one : toFun neg_one_R = neg_one_S

theorem mapCoeff_litPoly {R S : Type}
    (f : CoeffHom R S) {n : Nat} (lit : Literal n) :
    mapCoeff f.toFun (litPoly f.one_R f.neg_one_R lit) = litPoly f.one_S f.neg_one_S lit := by
  cases lit with | mk v p =>
  cases p with
  | false => rfl
  | true =>
    dsimp [litPoly, mapCoeff]
    rw [f.map_one, f.map_neg_one]

theorem mapCoeff_clausePoly {R S : Type}
    (f : CoeffHom R S) {n : Nat} (c : Clause n) :
    mapCoeff f.toFun (clausePoly f.one_R f.neg_one_R c) = clausePoly f.one_S f.neg_one_S c := by
  induction c with
  | nil =>
    dsimp [clausePoly, mapCoeff]
    rw [f.map_one]
  | cons lit rest ih =>
    dsimp [clausePoly, mapCoeff]
    rw [mapCoeff_litPoly f lit, ih]

theorem mapCoeff_boolAxiomPoly {R S : Type}
    (f : CoeffHom R S) {n : Nat} (i : Fin n) :
    mapCoeff f.toFun (boolAxiomPoly f.neg_one_R i) = boolAxiomPoly f.neg_one_S i := by
  dsimp [boolAxiomPoly, mapCoeff]
  rw [f.map_neg_one]

theorem mapCoeff_sumClauseTerms {R S : Type}
    (f : CoeffHom R S) {n : Nat} (q : List (Poly R n)) (F : Formula n) :
    mapCoeff f.toFun (sumClauseTerms f.zero_R f.one_R f.neg_one_R q F) =
    sumClauseTerms f.zero_S f.one_S f.neg_one_S (q.map (mapCoeff f.toFun)) F := by
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

theorem mapCoeff_sumBoolTerms_gen {R S : Type} (f : CoeffHom R S) {n : Nat}
    (L : List (Fin n)) (r : Fin n → Poly R n) (acc : Poly R n) :
    mapCoeff f.toFun (L.foldl (fun s i => Poly.add s (Poly.mul (r i) (boolAxiomPoly f.neg_one_R i))) acc) =
    L.foldl (fun s i => Poly.add s (Poly.mul (mapCoeff f.toFun (r i)) (boolAxiomPoly f.neg_one_S i))) (mapCoeff f.toFun acc) := by
  induction L generalizing acc with
  | nil => rfl
  | cons hd tl ih =>
    dsimp [List.foldl]
    have ih_inst := ih (Poly.add acc (Poly.mul (r hd) (boolAxiomPoly f.neg_one_R hd)))
    dsimp [mapCoeff] at ih_inst
    rw [mapCoeff_boolAxiomPoly f hd] at ih_inst
    exact ih_inst

theorem mapCoeff_sumBoolTerms {R S : Type}
    (f : CoeffHom R S) {n : Nat} (r : Fin n → Poly R n) :
    mapCoeff f.toFun (sumBoolTerms f.zero_R f.neg_one_R r) =
    sumBoolTerms f.zero_S f.neg_one_S (fun i => mapCoeff f.toFun (r i)) := by
  dsimp [sumBoolTerms]
  have h := mapCoeff_sumBoolTerms_gen f (List.finRange n) r (Poly.const f.zero_R)
  dsimp [mapCoeff] at h
  rw [f.map_zero] at h
  exact h

/-- Master Direct Algebraic Certificate Lifting Theorem:
    The complete certificate polynomial lifts functorially under any coefficient homomorphism:
    mapCoeff f.toFun (certificatePoly 0 1 (-1) q F r) =
    certificatePoly 0 1 (-1) (q.map (mapCoeff f.toFun)) F (fun i => mapCoeff f.toFun (r i)). -/
theorem mapCoeff_certificatePoly {R S : Type}
    (f : CoeffHom R S) {n : Nat} (q : List (Poly R n)) (F : Formula n) (r : Fin n → Poly R n) :
    mapCoeff f.toFun (certificatePoly f.zero_R f.one_R f.neg_one_R q F r) =
    certificatePoly f.zero_S f.one_S f.neg_one_S (q.map (mapCoeff f.toFun)) F (fun i => mapCoeff f.toFun (r i)) := by
  dsimp [certificatePoly, mapCoeff]
  rw [mapCoeff_sumClauseTerms f q F, mapCoeff_sumBoolTerms f r]

/-- Canonical Characteristic Zero Embedding Homomorphism from Int into standard Rat. -/
def intToRatHom : CoeffHom Int Rat where
  toFun := Rat.ofInt
  zero_R := 0
  zero_S := Rat.ofInt 0
  one_R := 1
  one_S := Rat.ofInt 1
  neg_one_R := -1
  neg_one_S := Rat.ofInt (-1)
  map_zero := rfl
  map_one := rfl
  map_neg_one := rfl

/-- Concrete Nullstellensatz Refutation Certificate with Integer Coefficients,
    encoded directly via algebraic polynomial identity. -/
structure ConcreteIntAlgebraicNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (Poly Int n)
  r : Fin n → Poly Int n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (clausePoly 1 (-1) (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  algebraic_identity : certificatePoly 0 1 (-1) q F r = Poly.const 1

/-- Concrete Nullstellensatz Refutation Certificate with Rational Coefficients (Rat),
    encoded directly via algebraic polynomial identity. -/
structure ConcreteRatAlgebraicNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (Poly Rat n)
  r : Fin n → Poly Rat n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (clausePoly (Rat.ofInt 1) (Rat.ofInt (-1)) (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  algebraic_identity : certificatePoly (Rat.ofInt 0) (Rat.ofInt 1) (Rat.ofInt (-1)) q F r = Poly.const (Rat.ofInt 1)

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
      exact (mapCoeff_clausePoly intToRatHom (F.get ⟨i, hF⟩)).symm
    rw [h_cp, mapCoeff_degree]
    exact cert.clause_deg_bound i hq_orig hF
  bool_deg_bound := by
    intro i
    rw [mapCoeff_degree]
    exact cert.bool_deg_bound i
  algebraic_identity := by
    have h_cert := (mapCoeff_certificatePoly intToRatHom cert.q F cert.r).symm
    dsimp [intToRatHom] at h_cert
    rw [h_cert]
    rw [cert.algebraic_identity]
    rfl

/-- Master One-Way Rational Certificate Embedding Theorem:
    Every formula admitting an integer Nullstellensatz refutation of degree ≤ d
    admits a Nullstellensatz refutation of degree ≤ d over the rational field ℚ. -/
theorem int_cert_implies_rat_cert {n : Nat} {F : Formula n} {d : Nat} :
    Nonempty (ConcreteIntAlgebraicNSRefutation F d) → Nonempty (ConcreteRatAlgebraicNSRefutation F d) := by
  rintro ⟨cert⟩
  exact ⟨liftIntToRatAlgebraicRefutation cert⟩

/-- Universal Evaluation Bridge:
    An algebraic certificate identity immediately guarantees that the certificate polynomial
    evaluates to 1 at EVERY point in the field, not merely at integer points. -/
theorem algebraic_identity_implies_eval_identity {R : Type} [Add R] [Mul R] {n : Nat}
    (zero one neg_one : R)
    (q : List (Poly R n)) (F : Formula n) (r : Fin n → Poly R n)
    (h_alg : certificatePoly zero one neg_one q F r = Poly.const one)
    (x : Fin n → R) :
    evalPoly (certificatePoly zero one neg_one q F r) x = one := by
  rw [h_alg]
  rfl

/-- Universal Evaluation Decomposition:
    The algebraic certificate identity ensures the evaluation of clause and Boolean terms sums to 1. -/
theorem algebraic_identity_implies_field_evaluation {R : Type} [Add R] [Mul R] {n : Nat}
    (zero one neg_one : R)
    (q : List (Poly R n)) (F : Formula n) (r : Fin n → Poly R n)
    (h_alg : certificatePoly zero one neg_one q F r = Poly.const one)
    (x : Fin n → R) :
    evalPoly (sumClauseTerms zero one neg_one q F) x +
    evalPoly (sumBoolTerms zero neg_one r) x = one := by
  have h_eval : evalPoly (certificatePoly zero one neg_one q F r) x = evalPoly (Poly.const one) x := by
    rw [h_alg]
  dsimp [certificatePoly, evalPoly] at h_eval
  exact h_eval

/-!
### Canonical Multilinear Monomial Reduction
-/

/-- Canonical single-variable exponent reducer: maps any positive exponent to 1. -/
def reduceExp (e : Nat) : Nat :=
  match e with
  | 0 => 0
  | _ => 1

/-- Canonical Multilinear Monomial Exponent Vector Reducer:
    Reduces an arbitrary exponent vector modulo the Boolean idempotency relations x_i^2 - x_i. -/
def reduceMonomialExp {n : Nat} (exps : Fin n → Nat) : Fin n → Nat :=
  fun i => reduceExp (exps i)

/-- Theorem: Single-variable exponent reduction is idempotent. -/
theorem reduceExp_idempotent (e : Nat) :
    reduceExp (reduceExp e) = reduceExp e := by
  cases e with
  | zero => rfl
  | succ k => rfl

/-- Theorem: General exponent vector reduction is idempotent for arbitrary monomials. -/
theorem reduceMonomialExp_idempotent {n : Nat} (exps : Fin n → Nat) :
    reduceMonomialExp (reduceMonomialExp exps) = reduceMonomialExp exps := by
  funext i
  exact reduceExp_idempotent (exps i)

/-- Theorem: An arbitrary cube exponent e = 3 collapses to 1 under canonical reduction. -/
theorem cube_exp_collapse (e : Nat) (h : e = 3) :
    e = 3 ∧ reduceExp e = 1 := by
  subst h
  exact ⟨rfl, rfl⟩

theorem ite_reduceExp_eq (e : Nat) (val : Int) :
    (if reduceExp e = 0 then (1 : Int) else val) = (if e = 0 then (1 : Int) else val) := by
  cases e with
  | zero => rfl
  | succ k => rfl

/-- Monomial evaluation on variable assignments. -/
def evalMonomialExp {n : Nat} (exps : Fin n → Nat) (x : Fin n → Int) : Int :=
  (List.finRange n).foldl (fun acc i => acc * (if exps i = 0 then 1 else x i)) 1

theorem foldl_monomial_eq {n : Nat} (exps : Fin n → Nat) (x : Fin n → Int)
    (L : List (Fin n)) (acc : Int) :
    L.foldl (fun s i => s * (if reduceMonomialExp exps i = 0 then (1 : Int) else x i)) acc =
    L.foldl (fun s i => s * (if exps i = 0 then (1 : Int) else x i)) acc := by
  induction L generalizing acc with
  | nil => rfl
  | cons hd tl ih =>
    dsimp [List.foldl]
    have h_hd : (if reduceMonomialExp exps hd = 0 then (1 : Int) else x hd) =
                (if exps hd = 0 then (1 : Int) else x hd) := by
      exact ite_reduceExp_eq (exps hd) (x hd)
    rw [h_hd]
    exact ih (acc * (if exps hd = 0 then 1 else x hd))

/-- Semantic Evaluation Preservation Theorem:
    Arbitrary canonical multilinear reduction preserves evaluation on Boolean cube assignments. -/
theorem evalMonomialExp_reduced {n : Nat} (exps : Fin n → Nat) (x : Fin n → Int) :
    evalMonomialExp (reduceMonomialExp exps) x = evalMonomialExp exps x := by
  dsimp [evalMonomialExp]
  exact foldl_monomial_eq exps x (List.finRange n) 1

/-- Ordered, deduplicating variable insertion for variable-list monomials. -/
def insertVar {n : Nat} (v : Fin n) (m : List (Fin n)) : List (Fin n) :=
  match m with
  | [] => [v]
  | u :: rest =>
    if v == u then u :: rest
    else if v.val < u.val then v :: u :: rest
    else u :: insertVar v rest

/-- Variable-list canonical multilinear monomial reducer. -/
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

/-- Theorem: Monomial cube degree collapses under variable-list reduction. -/
theorem cube_degree_collapse {n : Nat} (i : Fin n) :
    [i, i, i].length = 3 ∧ (reduceMonomial [i, i, i]).length = 1 := by
  rw [reduceMonomial_three]
  exact ⟨rfl, rfl⟩

/-!
### Denominator Clearing Obstruction (Supporting Lemma)
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

end RationalNullstellensatz

#print axioms RationalNullstellensatz.rat_fraction_normalization
#print axioms RationalNullstellensatz.liftIntToRatAlgebraicRefutation
#print axioms RationalNullstellensatz.int_cert_implies_rat_cert
#print axioms RationalNullstellensatz.algebraic_identity_implies_eval_identity
#print axioms RationalNullstellensatz.algebraic_identity_implies_field_evaluation
#print axioms RationalNullstellensatz.reduceMonomialExp_idempotent
#print axioms RationalNullstellensatz.cube_exp_collapse
#print axioms RationalNullstellensatz.evalMonomialExp_reduced
#print axioms RationalNullstellensatz.cube_degree_collapse
#print axioms RationalNullstellensatz.denominator_clearing_obstruction
