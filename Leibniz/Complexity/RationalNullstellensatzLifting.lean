/-!
# Rational Nullstellensatz Lifting, Degree Collapse, and Embedding Boundaries

This module formalizes:
1. Field-parameterized polynomial representation `Poly R n` and coefficient embedding `mapCoeff`.
2. Exact coefficient lifting $\iota : \mathbb{Z} \hookrightarrow \mathbb{Q}$ mapping integer certificates to rational certificates:
     `liftConcreteNSRefutation : ConcreteIntNSRefutation F d → ConcreteRatNSRefutation F d`.
3. The one-way embedding theorem:
     `int_cert_implies_rat_cert : Nonempty (ConcreteIntNSRefutation F d) → Nonempty (ConcreteRatNSRefutation F d)`.
4. Demonstration of syntactic vs. reduced quotient degree collapse in $\mathbb{Q}[x] / \langle x_i^2 - x_i \rangle$:
     `totalDegree (x_i^2) = 2`, but `totalDegree (reducePoly (x_i^2)) = 1`.
5. Formal denominator clearing obstruction:
     `denominator_clearing_obstruction : ∀ D > 1, ¬ ∃ k : ℤ, D * k = 1`,
   proving why rational refutations do not invert trivially to integer refutations.
-/

namespace RationalNullstellensatz

/-- Exact fractional representation of rational coefficients without external library dependencies. -/
structure RatCoeff where
  num : Int
  den : Nat
  den_pos : 0 < den

instance : Inhabited RatCoeff where
  default := ⟨0, 1, Nat.zero_lt_one⟩

def RatCoeff.ofInt (z : Int) : RatCoeff := ⟨z, 1, Nat.zero_lt_one⟩
def RatCoeff.zero : RatCoeff := ⟨0, 1, Nat.zero_lt_one⟩
def RatCoeff.one : RatCoeff := ⟨1, 1, Nat.zero_lt_one⟩
def RatCoeff.neg_one : RatCoeff := ⟨-1, 1, Nat.zero_lt_one⟩

/-- Addition of rational coefficients. -/
def addRat (a b : RatCoeff) : RatCoeff :=
  ⟨a.num * (b.den : Int) + b.num * (a.den : Int), a.den * b.den, Nat.mul_pos a.den_pos b.den_pos⟩

/-- Multiplication of rational coefficients. -/
def mulRat (a b : RatCoeff) : RatCoeff :=
  ⟨a.num * b.num, a.den * b.den, Nat.mul_pos a.den_pos b.den_pos⟩

/-- Homomorphism lemma: integer addition lifts to rational addition. -/
theorem addRat_ofInt (a b : Int) :
    addRat (RatCoeff.ofInt a) (RatCoeff.ofInt b) = RatCoeff.ofInt (a + b) := by
  dsimp [addRat, RatCoeff.ofInt]
  congr 1
  omega

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

/-- Degree preservation under arbitrary coefficient maps: total degree is purely structural. -/
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

abbrev IntPoly (n : Nat) := Poly Int n
abbrev RatPoly (n : Nat) := Poly RatCoeff n

/-- Canonical embedding of integer polynomials into rational polynomials. -/
def liftIntPoly {n : Nat} (p : IntPoly n) : RatPoly n :=
  mapCoeff RatCoeff.ofInt p

/-- Total degree is invariant under integer-to-rational lifting. -/
theorem liftIntPoly_degree {n : Nat} (p : IntPoly n) :
    totalDegree (liftIntPoly p) = totalDegree p :=
  mapCoeff_degree RatCoeff.ofInt p

/-- Evaluation of integer polynomials on integer points. -/
def evalIntPoly {n : Nat} (p : IntPoly n) (x : Fin n → Int) : Int :=
  match p with
  | Poly.const c => c
  | Poly.var i => x i
  | Poly.add p q => evalIntPoly p x + evalIntPoly q x
  | Poly.mul p q => evalIntPoly p x * evalIntPoly q x

/-- Evaluation of rational polynomials on rational points. -/
def evalRatPoly {n : Nat} (p : RatPoly n) (x : Fin n → RatCoeff) : RatCoeff :=
  match p with
  | Poly.const c => c
  | Poly.var i => x i
  | Poly.add p q => addRat (evalRatPoly p x) (evalRatPoly q x)
  | Poly.mul p q => mulRat (evalRatPoly p x) (evalRatPoly q x)

/-- Exact evaluation preservation theorem for polynomial lifting. -/
theorem eval_liftIntPoly_exact {n : Nat} (p : IntPoly n) (x : Fin n → Int) :
    evalRatPoly (liftIntPoly p) (fun i => RatCoeff.ofInt (x i)) =
    RatCoeff.ofInt (evalIntPoly p x) := by
  induction p with
  | const c => rfl
  | var i => rfl
  | add p q ihp ihq =>
    change addRat (evalRatPoly (liftIntPoly p) (fun i => RatCoeff.ofInt (x i)))
                   (evalRatPoly (liftIntPoly q) (fun i => RatCoeff.ofInt (x i))) =
           RatCoeff.ofInt (evalIntPoly p x + evalIntPoly q x)
    rw [ihp, ihq]
    dsimp [addRat, RatCoeff.ofInt]
    congr 1
    omega
  | mul p q ihp ihq =>
    change mulRat (evalRatPoly (liftIntPoly p) (fun i => RatCoeff.ofInt (x i)))
                   (evalRatPoly (liftIntPoly q) (fun i => RatCoeff.ofInt (x i))) =
           RatCoeff.ofInt (evalIntPoly p x * evalIntPoly q x)
    rw [ihp, ihq]
    dsimp [mulRat, RatCoeff.ofInt]

structure Literal (n : Nat) where
  var : Fin n
  polarity : Bool
deriving DecidableEq

abbrev Clause (n : Nat) := List (Literal n)
abbrev Formula (n : Nat) := List (Clause n)

/-- Literal polynomial with integer coefficients. -/
def intLitPoly {n : Nat} (lit : Literal n) : IntPoly n :=
  match lit.polarity with
  | true => Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var lit.var))
  | false => Poly.var lit.var

/-- Clause polynomial with integer coefficients. -/
def intClausePoly {n : Nat} (c : Clause n) : IntPoly n :=
  match c with
  | [] => Poly.const 1
  | lit :: rest => Poly.mul (intLitPoly lit) (intClausePoly rest)

/-- Boolean idempotency generator with integer coefficients. -/
def intBoolAxiomPoly {n : Nat} (i : Fin n) : IntPoly n :=
  Poly.add (Poly.mul (Poly.var i) (Poly.var i)) (Poly.mul (Poly.const (-1)) (Poly.var i))

/-- Literal polynomial with rational coefficients. -/
def ratLitPoly {n : Nat} (lit : Literal n) : RatPoly n :=
  match lit.polarity with
  | true => Poly.add (Poly.const RatCoeff.one) (Poly.mul (Poly.const RatCoeff.neg_one) (Poly.var lit.var))
  | false => Poly.var lit.var

/-- Clause polynomial with rational coefficients. -/
def ratClausePoly {n : Nat} (c : Clause n) : RatPoly n :=
  match c with
  | [] => Poly.const RatCoeff.one
  | lit :: rest => Poly.mul (ratLitPoly lit) (ratClausePoly rest)

/-- Boolean idempotency generator with rational coefficients. -/
def ratBoolAxiomPoly {n : Nat} (i : Fin n) : RatPoly n :=
  Poly.add (Poly.mul (Poly.var i) (Poly.var i)) (Poly.mul (Poly.const RatCoeff.neg_one) (Poly.var i))

/-- Integer literal polynomial lifts exactly to rational literal polynomial. -/
theorem lift_intLitPoly {n : Nat} (lit : Literal n) :
    liftIntPoly (intLitPoly lit) = ratLitPoly lit := by
  cases lit with | mk v p =>
  cases p with
  | true => rfl
  | false => rfl

/-- Integer clause polynomial lifts exactly to rational clause polynomial. -/
theorem lift_intClausePoly {n : Nat} (c : Clause n) :
    liftIntPoly (intClausePoly c) = ratClausePoly c := by
  induction c with
  | nil => rfl
  | cons lit rest ih =>
    dsimp [intClausePoly, ratClausePoly]
    change Poly.mul (liftIntPoly (intLitPoly lit)) (liftIntPoly (intClausePoly rest)) =
           Poly.mul (ratLitPoly lit) (ratClausePoly rest)
    rw [lift_intLitPoly lit, ih]

/-- Integer Boolean generator lifts exactly to rational Boolean generator. -/
theorem lift_intBoolAxiomPoly {n : Nat} (i : Fin n) :
    liftIntPoly (intBoolAxiomPoly i) = ratBoolAxiomPoly i := by
  rfl

/-- Evaluates sum of clause terms for integer certificates. -/
def evalIntClauseTerms {n : Nat} (q : List (IntPoly n)) (F : Formula n) (x : Fin n → Int) : Int :=
  match q, F with
  | [], _ => 0
  | _, [] => 0
  | q_head :: q_tail, c :: F_tail =>
    evalIntPoly q_head x * evalIntPoly (intClausePoly c) x + evalIntClauseTerms q_tail F_tail x

/-- Evaluates sum of clause terms for rational certificates. -/
def evalRatClauseTerms {n : Nat} (q : List (RatPoly n)) (F : Formula n) (x : Fin n → RatCoeff) : RatCoeff :=
  match q, F with
  | [], _ => RatCoeff.zero
  | _, [] => RatCoeff.zero
  | q_head :: q_tail, c :: F_tail =>
    addRat (mulRat (evalRatPoly q_head x) (evalRatPoly (ratClausePoly c) x))
           (evalRatClauseTerms q_tail F_tail x)

/-- Evaluates sum of Boolean terms for integer certificates. -/
def evalIntBoolTerms {n : Nat} (r : Fin n → IntPoly n) (x : Fin n → Int) : Int :=
  (List.finRange n).foldl (fun acc i => acc + evalIntPoly (r i) x * evalIntPoly (intBoolAxiomPoly i) x) 0

/-- Evaluates sum of Boolean terms for rational certificates. -/
def evalRatBoolTerms {n : Nat} (r : Fin n → RatPoly n) (x : Fin n → RatCoeff) : RatCoeff :=
  (List.finRange n).foldl (fun acc i => addRat acc (mulRat (evalRatPoly (r i) x) (evalRatPoly (ratBoolAxiomPoly i) x))) RatCoeff.zero

/-- Evaluation covariance theorem for lifted clause terms. -/
theorem eval_liftClauseTerms {n : Nat} (q : List (IntPoly n)) (F : Formula n) (x : Fin n → Int) :
    evalRatClauseTerms (q.map liftIntPoly) F (fun i => RatCoeff.ofInt (x i)) =
    RatCoeff.ofInt (evalIntClauseTerms q F x) := by
  induction q generalizing F with
  | nil => rfl
  | cons q_head q_tail ih =>
    cases F with
    | nil => rfl
    | cons c F_tail =>
      dsimp [evalRatClauseTerms, evalIntClauseTerms, List.map]
      rw [eval_liftIntPoly_exact q_head x]
      rw [← lift_intClausePoly c]
      rw [eval_liftIntPoly_exact (intClausePoly c) x]
      have ih_call := ih F_tail
      rw [ih_call]
      dsimp [addRat, mulRat, RatCoeff.ofInt]
      congr 1
      omega

/-- Congruence lemma for rational list folding. -/
theorem foldl_rat_int_lift {α : Type} (L : List α) (f : α → Int) (acc : Int) :
    L.foldl (fun (s : RatCoeff) a => addRat s (RatCoeff.ofInt (f a))) (RatCoeff.ofInt acc) =
    RatCoeff.ofInt (L.foldl (fun s a => s + f a) acc) := by
  induction L generalizing acc with
  | nil => rfl
  | cons hd tl ih =>
    dsimp [List.foldl]
    have h_step : addRat (RatCoeff.ofInt acc) (RatCoeff.ofInt (f hd)) = RatCoeff.ofInt (acc + f hd) := by
      dsimp [addRat, RatCoeff.ofInt]
      congr 1
      omega
    rw [h_step]
    exact ih (acc + f hd)

/-- Evaluation covariance theorem for lifted Boolean terms. -/
theorem eval_liftBoolTerms {n : Nat} (r : Fin n → IntPoly n) (x : Fin n → Int) :
    evalRatBoolTerms (fun i => liftIntPoly (r i)) (fun i => RatCoeff.ofInt (x i)) =
    RatCoeff.ofInt (evalIntBoolTerms r x) := by
  dsimp [evalRatBoolTerms, evalIntBoolTerms]
  have h_term : ∀ i : Fin n,
      mulRat (evalRatPoly (liftIntPoly (r i)) (fun j => RatCoeff.ofInt (x j)))
             (evalRatPoly (ratBoolAxiomPoly i) (fun j => RatCoeff.ofInt (x j))) =
      RatCoeff.ofInt (evalIntPoly (r i) x * evalIntPoly (intBoolAxiomPoly i) x) := by
    intro i
    rw [eval_liftIntPoly_exact (r i) x]
    rw [← lift_intBoolAxiomPoly i]
    rw [eval_liftIntPoly_exact (intBoolAxiomPoly i) x]
    dsimp [mulRat, RatCoeff.ofInt]
  have h_fold := foldl_rat_int_lift (List.finRange n)
    (fun i => evalIntPoly (r i) x * evalIntPoly (intBoolAxiomPoly i) x) 0
  have h_step_eq : (fun acc i => addRat acc (mulRat (evalRatPoly (liftIntPoly (r i)) (fun j => RatCoeff.ofInt (x j)))
                                                  (evalRatPoly (ratBoolAxiomPoly i) (fun j => RatCoeff.ofInt (x j))))) =
                   (fun acc i => addRat acc (RatCoeff.ofInt (evalIntPoly (r i) x * evalIntPoly (intBoolAxiomPoly i) x))) := by
    funext acc i
    rw [h_term i]
  rw [h_step_eq]
  exact h_fold

/-- Concrete Nullstellensatz refutation certificate with Integer coefficients. -/
structure ConcreteIntNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (IntPoly n)
  r : Fin n → IntPoly n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (intClausePoly (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  identity : ∀ (x : Fin n → Int),
    evalIntClauseTerms q F x + evalIntBoolTerms r x = 1

/-- Concrete Nullstellensatz refutation certificate with Rational coefficients. -/
structure ConcreteRatNSRefutation {n : Nat} (F : Formula n) (d : Nat) where
  q : List (RatPoly n)
  r : Fin n → RatPoly n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (ratClausePoly (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  identity : ∀ (x : Fin n → Int),
    addRat (evalRatClauseTerms q F (fun i => RatCoeff.ofInt (x i)))
           (evalRatBoolTerms r (fun i => RatCoeff.ofInt (x i))) = RatCoeff.one

theorem get_map_liftIntPoly {n : Nat} (q : List (IntPoly n)) (i : Nat) (hq : i < (q.map liftIntPoly).length) :
    (q.map liftIntPoly).get ⟨i, hq⟩ = liftIntPoly (q.get ⟨i, by rw [List.length_map] at hq; exact hq⟩) := by
  induction q generalizing i with
  | nil =>
    have : i < 0 := by rw [List.length_map] at hq; exact hq
    contradiction
  | cons hd tl ih =>
    cases i with
    | zero => rfl
    | succ j =>
      dsimp [List.map, List.get]
      have hj : j < (tl.map liftIntPoly).length := by
        dsimp [List.map] at hq
        omega
      exact ih j hj

/-- Constructive lifting of an Integer Nullstellensatz refutation to a Rational Nullstellensatz refutation. -/
def liftConcreteNSRefutation {n : Nat} {F : Formula n} {d : Nat}
    (cert : ConcreteIntNSRefutation F d) :
    ConcreteRatNSRefutation F d where
  q := cert.q.map liftIntPoly
  r := fun i => liftIntPoly (cert.r i)
  q_len := by
    rw [List.length_map, cert.q_len]
  clause_deg_bound := by
    intro i hq hF
    have hq_orig : i < cert.q.length := by rw [List.length_map] at hq; exact hq
    rw [get_map_liftIntPoly]
    rw [liftIntPoly_degree]
    rw [← lift_intClausePoly (F.get ⟨i, hF⟩), liftIntPoly_degree]
    exact cert.clause_deg_bound i hq_orig hF
  bool_deg_bound := by
    intro i
    rw [liftIntPoly_degree]
    exact cert.bool_deg_bound i
  identity := by
    intro x
    rw [eval_liftClauseTerms, eval_liftBoolTerms]
    rw [addRat_ofInt]
    rw [cert.identity x]
    rfl

/-- Master One-Way Embedding Theorem:
    Any formula admitting an integer Nullstellensatz refutation of degree ≤ d
    admits a rational Nullstellensatz refutation of degree ≤ d. -/
theorem int_cert_implies_rat_cert {n : Nat} {F : Formula n} {d : Nat} :
    Nonempty (ConcreteIntNSRefutation F d) → Nonempty (ConcreteRatNSRefutation F d) := by
  rintro ⟨cert⟩
  exact ⟨liftConcreteNSRefutation cert⟩

/-- Multilinear reduction operator mapping monomials modulo x_i^2 - x_i. -/
def reducePoly {n : Nat} (p : IntPoly n) : IntPoly n :=
  match p with
  | Poly.const c => Poly.const c
  | Poly.var i => Poly.var i
  | Poly.add p q => Poly.add (reducePoly p) (reducePoly q)
  | Poly.mul p q =>
    match p, q with
    | Poly.var i, Poly.var j =>
      if i = j then Poly.var i else Poly.mul (Poly.var i) (Poly.var j)
    | _, _ => Poly.mul (reducePoly p) (reducePoly q)

/-- Formal demonstration of Syntactic Degree Collapse under Boolean Reduction:
    The monomial x_i^2 has syntactic total degree 2, while its canonical reduction x_i has degree 1. -/
theorem degree_collapse_example {n : Nat} (i : Fin n) :
    totalDegree (Poly.mul (Poly.var i : IntPoly n) (Poly.var i)) = 2 ∧
    totalDegree (reducePoly (Poly.mul (Poly.var i : IntPoly n) (Poly.var i))) = 1 := by
  dsimp [totalDegree, reducePoly]
  have h_eq : (if i = i then (Poly.var i : IntPoly n) else Poly.mul (Poly.var i) (Poly.var i)) = Poly.var i := by
    simp only [ite_true]
  rw [h_eq]
  dsimp [totalDegree]
  decide

/-- Denominator Clearing Obstruction Theorem:
    A rational certificate equation with common denominator D > 1 clears to ∑ q'_C p_C + ∑ r'_i B_i = D.
    Because D is not invertible in ℤ, clearing denominators cannot directly yield an integer certificate (RHS = 1).
    Therefore, the converse implication RatCert(F, d) → IntCert(F, d) does not follow trivially. -/
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

#print axioms RationalNullstellensatz.liftConcreteNSRefutation
#print axioms RationalNullstellensatz.int_cert_implies_rat_cert
#print axioms RationalNullstellensatz.degree_collapse_example
#print axioms RationalNullstellensatz.denominator_clearing_obstruction
