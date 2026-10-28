# Audited Milestone: Constructive Polynomial ASTs & Conditional Algebraic Refutation Gauge Invariance

**Date:** 2026-10-28  
**Status:** Machine-Checked in Lean 4 (`0 sorry`, Exit Code 0)  
**Location:** `/home/mega/Chyren/3_research/4Leibniz/Leibniz/Complexity/NullstellensatzGaugeInvariance.lean`  
**Source SHA-256:** `550caec7f75882451003ea6203162a77ee6aa2b87606dcb0d2ab45fd969386c3`  
**Toolchain Environment:** `leanprover/lean4:v4.35.0` (commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, Release)  
**Epistemic Classification:** Conditional Gauge-Invariance Theorem (Concrete Proof-System Instantiation Pending)

---

## 1. Concrete Formal Advances: Real Polynomial AST & Total Degree

Following the peer audit, the previous placeholder polynomial structure (which stored degree merely as unverified metadata) has been replaced by a genuine inductive abstract syntax tree (AST) with a computable total degree function.

### A. Inductive Multilinear Polynomial AST
```lean
inductive Poly (n : Nat) where
  | const : Int → Poly n
  | var : Fin n → Poly n
  | add : Poly n → Poly n → Poly n
  | mul : Poly n → Poly n → Poly n
```

### B. Computable Total Degree Function
```lean
def totalDegree {n : Nat} (p : Poly n) : Nat :=
  match p with
  | Poly.const _ => 0
  | Poly.var _ => 1
  | Poly.add p q => max (totalDegree p) (totalDegree q)
  | Poly.mul p q => totalDegree p + totalDegree q
```

### C. Constructive Proof of Degree Preservation Under Affine Gauge Substitution
The substitution $x_i \mapsto (\text{if } g_i \text{ then } 1 - x_i \text{ else } x_i)$ is formalized via `flipPoly`. Because each variable polynomial has degree $\le 1$, structural induction over the AST proves that total degree is non-increasing:
- **Theorem (`flipPoly_deg_le`):**
  $$\text{totalDegree}(\text{flipPoly}(g, p)) \le \text{totalDegree}(p)$$
  *Proof:* Certified in Lean 4 across all AST constructors (`const`, `var`, `add`, `mul`) with 0 `sorry`.
- **Theorem (`eval_flipPoly`):**
  $$\text{evalPoly}(\text{flipPoly}(g, p), x) = \text{evalPoly}(p, \text{flipPoint}(g, x))$$
  *Proof:* Structural induction certifying semantic equivalence of evaluation.
- **Clause Polynomial Degree Theorem (`clausePoly_degree`):**
  $$\text{totalDegree}(\text{clausePoly}(C)) = C.\text{length}$$
  *Proof:* Induction over clause literals proving clause polynomial degree strictly matches clause width.

---

## 2. Transitive Axiom Ledger (`#print axioms`)

Compilation executed directly against `leanprover/lean4:v4.35.0` with **0 `sorry` and 0 custom axioms**:

```text
'NullstellensatzGauge.flipPoly_deg_le' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.eval_flipPoly' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.boolean_axiom_flip' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.boolAxiomPoly_eval_flip' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.clausePoly_degree' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.flipPoint_involutive' depends on axioms: [propext, Quot.sound]
'NullstellensatzGauge.flipFormula_involutive' does not depend on any axioms
'NullstellensatzGauge.refutation_iff_gauge' does not depend on any axioms
'NullstellensatzGauge.min_refutation_degree_gauge_invariant' does not depend on any axioms
```

*Receipt Summary:*
- **Custom Axioms:** `0`
- **`sorry` Instances:** `0`
- **Core Standard Axioms:** Relies exclusively on standard propositional extensionality (`propext`) and quotient sound extensionality (`Quot.sound`).

---

## 3. Explicit Epistemic Boundary: The Conditional Invariance Theorem

To ensure complete transparency and prevent overstating the formalization scope:

1. **What is Fully Proved in Lean 4:**
   - The polynomial AST and its computable total degree function.
   - The non-increasing total degree bound under affine gauge substitution (`flipPoly_deg_le`).
   - The semantic evaluation equivalence (`eval_flipPoly`).
   - The exact degree of clause falsification polynomials (`clausePoly_degree`).
   - The formula involution identity (`(F^g)^g = F`).
   - The structural deduction that **any** algebraic refutation system satisfying `deg_preservation` exhibits strict minimum-degree gauge invariance:
     $$\text{IsMinRefutationDegree}(sys, F^g, d) \iff \text{IsMinRefutationDegree}(sys, F, d)$$
2. **What Remains Open / Pending Concrete Instantiation:**
   - The concrete instantiation proving that a certificate $\sum_C q_C p_C + \sum_i r_i (x_i^2 - x_i) = 1$ in Nullstellensatz can be constructively reorganized into a certificate of $F^g$ at the exact same degree without degree expansion.
   - The formalization is therefore classified as:
     **"Conditional Gauge-Invariance Theorem — Concrete Proof-System Instantiation Pending"**.
