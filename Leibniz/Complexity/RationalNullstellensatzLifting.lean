/-!
# Characteristic Zero Field Nullstellensatz Lifting, Monomial Reduction, and Embedding Boundaries

This module formalizes:
1. Mathematical semantics for arbitrary Characteristic Zero Fields $K$ satisfying lawful field axioms
   (`Field K`) equipped with an injective homomorphism `CharacteristicZeroEmbedding K`.
2. Functorial coefficient lifting $\iota : \mathbb{Z} \hookrightarrow K$ mapping integer certificates
   to field certificates over $K$:
     `liftIntToFieldRefutation : ConcreteIntNSRefutation F d → ConcreteFieldNSRefutation K Fld F d`.
3. The master one-way embedding theorem:
     `int_cert_implies_field_cert : Nonempty (ConcreteIntNSRefutation F d) → Nonempty (ConcreteFieldNSRefutation K Fld F d)`.
4. Canonical multilinear Boolean monomial reducer `reduceMonomial : List (Fin n) → List (Fin n)`
   sorting and deduplicating variable lists, with formal proof of cube degree collapse ($x_i^3 \to x_i$)
   and Boolean point evaluation invariance ($x_i \in \{0, 1\} \implies x_i^3 = x_i$).
5. Supporting lemma for denominator clearing obstruction:
     `denominator_clearing_obstruction : ∀ D > 1, ¬ ∃ k : ℤ, D * k = 1`,
   explaining the algebraic obstruction in inverting field refutations back to integer refutations.
-/

namespace FieldNullstellensatz

/-- Axiomatic field structure over carrier type K, establishing all additive,
    multiplicative, and inverse laws required for a commutative field. -/
class Field (K : Type) extends Add K, Mul K, Neg K, Sub K, Zero K, One K where
  add_assoc : ∀ a b c : K, a + b + c = a + (b + c)
  add_comm : ∀ a b : K, a + b = b + a
  zero_add : ∀ a : K, 0 + a = a
  add_left_neg : ∀ a : K, -a + a = 0
  sub_eq_add_neg : ∀ a b : K, a - b = a + -b
  mul_assoc : ∀ a b c : K, a * b * c = a * (b * c)
  mul_comm : ∀ a b : K, a * b = b * a
  one_mul : ∀ a : K, 1 * a = a
  left_distrib : ∀ a b c : K, a * (b + c) = a * b + a * c
  mul_zero : ∀ a : K, a * 0 = 0
  zero_ne_one : (0 : K) ≠ 1
  inv : K → K
  mul_inv_cancel : ∀ a : K, a ≠ 0 → a * inv a = 1

/-- Characteristic zero field embedding: an injective ring homomorphism from ℤ into field K. -/
structure CharacteristicZeroEmbedding (K : Type) [Field K] where
  embedInt : Int → K
  embed_zero : embedInt 0 = 0
  embed_one : embedInt 1 = 1
  embed_add : ∀ a b : Int, embedInt (a + b) = embedInt a + embedInt b
  embed_mul : ∀ a b : Int, embedInt (a * b) = embedInt a * embedInt b
  embed_neg : ∀ a : Int, embedInt (-a) = - embedInt a
  embed_injective : ∀ a b : Int, embedInt a = embedInt b → a = b

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

abbrev IntPoly (n : Nat) := Poly Int n

/-- Evaluation of polynomial AST on variable assignments. -/
def evalPoly {R : Type} [Add R] [Mul R] {n : Nat} (p : Poly R n) (x : Fin n → R) : R :=
  match p with
  | Poly.const c => c
  | Poly.var i => x i
  | Poly.add p q => evalPoly p x + evalPoly q x
  | Poly.mul p q => evalPoly p x * evalPoly q x

/-- Semantic evaluation preservation under field embedding. -/
theorem eval_mapCoeff {K : Type} [Field K] {n : Nat}
    (Fld : CharacteristicZeroEmbedding K) (p : IntPoly n) (x : Fin n → Int) :
    evalPoly (mapCoeff Fld.embedInt p) (fun i => Fld.embedInt (x i)) =
    Fld.embedInt (evalPoly p x) := by
  induction p with
  | const c => rfl
  | var i => rfl
  | add p q ihp ihq =>
    dsimp [mapCoeff, evalPoly]
    rw [ihp, ihq, Fld.embed_add]
  | mul p q ihp ihq =>
    dsimp [mapCoeff, evalPoly]
    rw [ihp, ihq, Fld.embed_mul]

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

/-- Literal polynomial with field coefficients. -/
def fieldLitPoly (K : Type) [Field K] {n : Nat} (lit : Literal n) : Poly K n :=
  match lit.polarity with
  | true => Poly.add (Poly.const 1) (Poly.mul (Poly.const (-1)) (Poly.var lit.var))
  | false => Poly.var lit.var

/-- Clause polynomial with field coefficients. -/
def fieldClausePoly (K : Type) [Field K] {n : Nat} (c : Clause n) : Poly K n :=
  match c with
  | [] => Poly.const 1
  | lit :: rest => Poly.mul (fieldLitPoly K lit) (fieldClausePoly K rest)

/-- Boolean idempotency generator with field coefficients. -/
def fieldBoolAxiomPoly (K : Type) [Field K] {n : Nat} (i : Fin n) : Poly K n :=
  Poly.add (Poly.mul (Poly.var i) (Poly.var i)) (Poly.mul (Poly.const (-1)) (Poly.var i))

theorem mapCoeff_litPoly {K : Type} [Field K] {n : Nat}
    (Fld : CharacteristicZeroEmbedding K) (lit : Literal n) :
    mapCoeff Fld.embedInt (intLitPoly lit) = fieldLitPoly K lit := by
  cases lit with | mk v p =>
  cases p with
  | false => rfl
  | true =>
    dsimp [intLitPoly, fieldLitPoly, mapCoeff]
    have h1 : Fld.embedInt 1 = 1 := Fld.embed_one
    have h_neg1 : Fld.embedInt (-1) = -1 := by
      have h_neg := Fld.embed_neg 1
      rw [Fld.embed_one] at h_neg
      exact h_neg
    rw [h1, h_neg1]

theorem mapCoeff_clausePoly {K : Type} [Field K] {n : Nat}
    (Fld : CharacteristicZeroEmbedding K) (c : Clause n) :
    mapCoeff Fld.embedInt (intClausePoly c) = fieldClausePoly K c := by
  induction c with
  | nil =>
    dsimp [intClausePoly, fieldClausePoly, mapCoeff]
    rw [Fld.embed_one]
  | cons lit rest ih =>
    dsimp [intClausePoly, fieldClausePoly, mapCoeff]
    rw [mapCoeff_litPoly Fld lit, ih]

theorem mapCoeff_boolAxiomPoly {K : Type} [Field K] {n : Nat}
    (Fld : CharacteristicZeroEmbedding K) (i : Fin n) :
    mapCoeff Fld.embedInt (intBoolAxiomPoly i) = fieldBoolAxiomPoly K i := by
  dsimp [intBoolAxiomPoly, fieldBoolAxiomPoly, mapCoeff]
  have h_neg1 : Fld.embedInt (-1) = -1 := by
    have h_neg := Fld.embed_neg 1
    rw [Fld.embed_one] at h_neg
    exact h_neg
  rw [h_neg1]

def evalClauseTerms {R : Type} [Add R] [Mul R] [Zero R] {n : Nat}
    (clauseP : Clause n → Poly R n) (q : List (Poly R n)) (F : Formula n) (x : Fin n → R) : R :=
  match q, F with
  | [], _ => 0
  | _, [] => 0
  | q_head :: q_tail, c :: F_tail =>
    evalPoly q_head x * evalPoly (clauseP c) x + evalClauseTerms clauseP q_tail F_tail x

def evalBoolTerms {R : Type} [Add R] [Mul R] [Zero R] {n : Nat}
    (boolAxiomP : Fin n → Poly R n) (r : Fin n → Poly R n) (x : Fin n → R) : R :=
  (List.finRange n).foldl (fun acc i => acc + evalPoly (r i) x * evalPoly (boolAxiomP i) x) 0

theorem eval_mapClauseTerms {K : Type} [Field K] {n : Nat}
    (Fld : CharacteristicZeroEmbedding K) (q : List (IntPoly n)) (F : Formula n) (x : Fin n → Int) :
    evalClauseTerms (fieldClausePoly K) (q.map (mapCoeff Fld.embedInt)) F (fun i => Fld.embedInt (x i)) =
    Fld.embedInt (evalClauseTerms intClausePoly q F x) := by
  induction q generalizing F with
  | nil =>
    dsimp [evalClauseTerms, List.map]
    rw [Fld.embed_zero]
  | cons q_head q_tail ih =>
    cases F with
    | nil =>
      dsimp [evalClauseTerms, List.map]
      rw [Fld.embed_zero]
    | cons c F_tail =>
      dsimp [evalClauseTerms, List.map]
      rw [eval_mapCoeff Fld q_head x]
      rw [← mapCoeff_clausePoly Fld c]
      rw [eval_mapCoeff Fld (intClausePoly c) x]
      rw [ih F_tail]
      rw [← Fld.embed_mul, ← Fld.embed_add]

theorem foldl_field_int_zero {K : Type} [Field K] {α : Type}
    (Fld : CharacteristicZeroEmbedding K) (L : List α) (f : α → Int) :
    L.foldl (fun (s : K) a => s + Fld.embedInt (f a)) 0 =
    Fld.embedInt (L.foldl (fun s a => s + f a) 0) := by
  have h_gen : ∀ (acc : Int),
    L.foldl (fun (s : K) a => s + Fld.embedInt (f a)) (Fld.embedInt acc) =
    Fld.embedInt (L.foldl (fun s a => s + f a) acc) := by
    intro acc
    induction L generalizing acc with
    | nil => rfl
    | cons hd tl ih =>
      dsimp [List.foldl]
      rw [← Fld.embed_add]
      exact ih (acc + f hd)
  have := h_gen 0
  rw [Fld.embed_zero] at this
  exact this

theorem eval_mapBoolTerms {K : Type} [Field K] {n : Nat}
    (Fld : CharacteristicZeroEmbedding K) (r : Fin n → IntPoly n) (x : Fin n → Int) :
    evalBoolTerms (fieldBoolAxiomPoly K) (fun i => mapCoeff Fld.embedInt (r i)) (fun i => Fld.embedInt (x i)) =
    Fld.embedInt (evalBoolTerms intBoolAxiomPoly r x) := by
  dsimp [evalBoolTerms]
  have h_term : ∀ i : Fin n,
      evalPoly (mapCoeff Fld.embedInt (r i)) (fun j => Fld.embedInt (x j)) *
      evalPoly (fieldBoolAxiomPoly K i) (fun j => Fld.embedInt (x j)) =
      Fld.embedInt (evalPoly (r i) x * evalPoly (intBoolAxiomPoly i) x) := by
    intro i
    rw [eval_mapCoeff Fld (r i) x]
    rw [← mapCoeff_boolAxiomPoly Fld i]
    rw [eval_mapCoeff Fld (intBoolAxiomPoly i) x]
    rw [← Fld.embed_mul]
  have h_fold := foldl_field_int_zero Fld (List.finRange n)
    (fun i => evalPoly (r i) x * evalPoly (intBoolAxiomPoly i) x)
  have h_step_eq : (fun acc i => acc + evalPoly (mapCoeff Fld.embedInt (r i)) (fun j => Fld.embedInt (x j)) *
                                       evalPoly (fieldBoolAxiomPoly K i) (fun j => Fld.embedInt (x j))) =
                   (fun acc i => acc + Fld.embedInt (evalPoly (r i) x * evalPoly (intBoolAxiomPoly i) x)) := by
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
    evalClauseTerms intClausePoly q F x + evalBoolTerms intBoolAxiomPoly r x = 1

/-- Concrete Nullstellensatz refutation certificate with coefficients in an arbitrary field K. -/
structure ConcreteFieldNSRefutation (K : Type) [Field K] (Fld : CharacteristicZeroEmbedding K)
    {n : Nat} (F : Formula n) (d : Nat) where
  q : List (Poly K n)
  r : Fin n → Poly K n
  q_len : q.length = F.length
  clause_deg_bound : ∀ (i : Nat) (hq : i < q.length) (hF : i < F.length),
    totalDegree (q.get ⟨i, hq⟩) + totalDegree (fieldClausePoly K (F.get ⟨i, hF⟩)) ≤ d
  bool_deg_bound : ∀ (i : Fin n), totalDegree (r i) + 2 ≤ d
  identity : ∀ (x : Fin n → Int),
    evalClauseTerms (fieldClausePoly K) q F (fun i => Fld.embedInt (x i)) +
    evalBoolTerms (fieldBoolAxiomPoly K) r (fun i => Fld.embedInt (x i)) = 1

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

/-- Constructive lifting of an Integer Nullstellensatz certificate to an arbitrary characteristic zero field K. -/
def liftIntToFieldRefutation {K : Type} [Field K] (Fld : CharacteristicZeroEmbedding K)
    {n : Nat} {F : Formula n} {d : Nat} (cert : ConcreteIntNSRefutation F d) :
    ConcreteFieldNSRefutation K Fld F d where
  q := cert.q.map (mapCoeff Fld.embedInt)
  r := fun i => mapCoeff Fld.embedInt (cert.r i)
  q_len := by
    rw [List.length_map, cert.q_len]
  clause_deg_bound := by
    intro i hq hF
    have hq_orig : i < cert.q.length := by rw [List.length_map] at hq; exact hq
    rw [get_map_mapCoeff]
    rw [mapCoeff_degree]
    rw [← mapCoeff_clausePoly Fld (F.get ⟨i, hF⟩), mapCoeff_degree]
    exact cert.clause_deg_bound i hq_orig hF
  bool_deg_bound := by
    intro i
    rw [mapCoeff_degree]
    exact cert.bool_deg_bound i
  identity := by
    intro x
    rw [eval_mapClauseTerms Fld, eval_mapBoolTerms Fld]
    rw [← Fld.embed_add]
    rw [cert.identity x]
    exact Fld.embed_one

/-- Master One-Way Field Embedding Theorem:
    Every formula admitting an integer Nullstellensatz refutation of degree ≤ d
    admits a Nullstellensatz refutation of degree ≤ d over any characteristic zero field K. -/
theorem int_cert_implies_field_cert {K : Type} [Field K] (Fld : CharacteristicZeroEmbedding K)
    {n : Nat} {F : Formula n} {d : Nat} :
    Nonempty (ConcreteIntNSRefutation F d) → Nonempty (ConcreteFieldNSRefutation K Fld F d) := by
  rintro ⟨cert⟩
  exact ⟨liftIntToFieldRefutation Fld cert⟩

/-- Ordered, deduplicating variable insertion for canonical multilinear monomials. -/
def insertVar {n : Nat} (v : Fin n) (m : List (Fin n)) : List (Fin n) :=
  match m with
  | [] => [v]
  | u :: rest =>
    if v == u then u :: rest
    else if v.val < u.val then v :: u :: rest
    else u :: insertVar v rest

/-- General Canonical Multilinear Monomial Reducer:
    Reduces an arbitrary variable product x_{i_1} ... x_{i_m} modulo x_i^2 - x_i
    by sorting and eliminating all duplicate variable factors. -/
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

/-- Theorem: Arbitrary cube monomial x_i^3 has syntactic degree 3, but reduced degree 1 under canonical reduction. -/
theorem cube_degree_collapse {n : Nat} (i : Fin n) :
    [i, i, i].length = 3 ∧ (reduceMonomial [i, i, i]).length = 1 := by
  rw [reduceMonomial_three]
  exact ⟨rfl, rfl⟩

/-- Semantic evaluation invariance: on Boolean assignments x ∈ {0, 1}^n, square evaluation is idempotent. -/
theorem evalMonomial_two (val : Int) (h : val = 0 ∨ val = 1) :
    val * (val * 1) = val * 1 := by
  cases h with
  | inl h0 => rw [h0]; rfl
  | inr h1 => rw [h1]; rfl

/-- Semantic evaluation invariance: on Boolean assignments x ∈ {0, 1}^n, cube evaluation collapses to x_i. -/
theorem evalMonomial_three (val : Int) (h : val = 0 ∨ val = 1) :
    val * (val * (val * 1)) = val * 1 := by
  cases h with
  | inl h0 => rw [h0]; rfl
  | inr h1 => rw [h1]; rfl

/-- Denominator Clearing Obstruction Theorem:
    A field refutation cleared of denominators yields ∑ q'_C p_C + ∑ r'_i B_i = D.
    Because D > 1 is not invertible in ℤ, division by D cannot produce an integer refutation (RHS = 1). -/
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

end FieldNullstellensatz

#print axioms FieldNullstellensatz.liftIntToFieldRefutation
#print axioms FieldNullstellensatz.int_cert_implies_field_cert
#print axioms FieldNullstellensatz.cube_degree_collapse
#print axioms FieldNullstellensatz.evalMonomial_three
#print axioms FieldNullstellensatz.denominator_clearing_obstruction
