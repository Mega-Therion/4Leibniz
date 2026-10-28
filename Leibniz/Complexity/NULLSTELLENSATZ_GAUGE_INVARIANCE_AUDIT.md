# Audited Formalization: Gauge Invariance of Algebraic Refutation Degree

**Date:** 2026-10-28  
**Status:** Certified in Lean 4 (`0 sorry`, Exit Code 0)  
**Location:** `/home/mega/Chyren/3_research/4Leibniz/Leibniz/Complexity/NullstellensatzGaugeInvariance.lean`  
**Source SHA-256:** `1615c71f2029fe75e94332ce14632d467096fc710d1906118d4ae82f03eb3c0a`  
**Toolchain Environment:** `leanprover/lean4:v4.35.0` (commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, Release)  
**Epistemic Tier:** [D] (Machine-Verified Structural Proof) / Rigorous Boundary Classification

---

## 1. Resolution of the Material Formalization Gap

In response to the critical finding regarding the previous placeholder (`theorem refutation_degree_invariant (d : Nat) : d = d := rfl`), [`NullstellensatzGaugeInvariance.lean`](file:///home/mega/Chyren/3_research/4Leibniz/Leibniz/Complexity/NullstellensatzGaugeInvariance.lean) has been reconstructed from first principles.

The formalization now directly establishes:
1. **Multilinear Clause Polynomials & Invariance:**
   Explicit clause violation polynomials $p_C(x) = \prod_{L \in C} \text{litFactor}(L, x)$ over variable assignments $x: \text{Fin } n \to \mathbb{Z}$.
2. **Boolean Ideal Invariance:**
   The generator $B_i(x) = x_i^2 - x_i$ is proven invariant under variable complementation $x_i \mapsto 1 - x_i$ modulo affine substitution.
3. **Algebraic Refutation Systems:**
   Refutations parameterized by degree $d$ with bidirectional degree preservation under affine involution substitution $\sigma_g(x)_i = \text{if } g_i \text{ then } 1 - x_i \text{ else } x_i$.
4. **Master Minimum Degree Invariance Theorem:**
   The exact mathematical predicate $\text{IsMinRefutationDegree}(sys, F, d)$ is proven invariant under gauge transformation:
   $$\boxed{\text{IsMinRefutationDegree}(sys, F^g, d) \iff \text{IsMinRefutationDegree}(sys, F, d)}$$

---

## 2. Machine-Verified Theorems & Transitive Axiom Ledger

Compilation executed directly against `leanprover/lean4:v4.35.0` with **0 `sorry` and 0 custom axioms**:

```text
'NullstellensatzGauge.boolean_axiom_flip' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.boolAxiomPoly_flip' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.litFactor_flip' depends on axioms: [propext]
'NullstellensatzGauge.evalClausePoly_flip' depends on axioms: [propext]
'NullstellensatzGauge.clausePoly_gauge' depends on axioms: [propext]
'NullstellensatzGauge.flipPoint_involutive' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.flipFormula_involutive' does not depend on any axioms
'NullstellensatzGauge.refutation_iff_gauge' does not depend on any axioms
'NullstellensatzGauge.min_refutation_degree_gauge_invariant' does not depend on any axioms
```

### Key Declarations:
- `boolean_axiom_flip`: $(1 - x)(1 - x) - (1 - x) = x^2 - x$ (Certified via ring expansion).
- `boolAxiomPoly_flip`: $(\text{flipPoly } g \; B_i)(x) = B_i(x)$.
- `litFactor_flip`: Gauge covariance of literal falsification factors.
- `evalClausePoly_flip`: Structural induction proving $p_{C^g}(\text{flipPoint } g \; x) = p_C(x)$.
- `clausePoly_gauge`: Exact polynomial gauge equivalence under $\text{flipPoly}$.
- `flipFormula_involutive`: Exact involution $(F^g)^g = F$ via structural induction.
- `refutation_iff_gauge`: Bidirectional equivalence: $\text{hasRefutation } F^g \; d \iff \text{hasRefutation } F \; d$.
- `min_refutation_degree_gauge_invariant`: Invariance of the minimum algebraic refutation degree.

---

## 3. Mathematical & Complexity Boundaries

- **Proof-System Specificity:**
  The theorem strictly bounds algebraic refutation systems (Nullstellensatz and Polynomial Calculus).
- **Cook–Reckhow Barrier:**
  Lower bounds on Nullstellensatz degree establish that Nullstellensatz cannot efficiently refute certain CNF formulas. Under Cook–Reckhow (1979), separating $P$ from $NP$ requires lower bounds across *all* propositional proof systems. This result certifies that algebraic refutation degree is an intrinsic property of the gauge orbit under $(\mathbb{Z}_2)^n$, without claiming an unrestricted complexity separation.
