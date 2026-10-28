# Rational Nullstellensatz Lifting, Degree Collapse, and Embedding Boundaries

**Date:** 2026-10-28  
**Status:** Certified in Lean 4 (`0 sorry`, Exit Code 0)  
**Location:** `/home/mega/Chyren/3_research/4Leibniz/Leibniz/Complexity/RationalNullstellensatzLifting.lean`  
**Source SHA-256:** `1291fa7c2818936de51fb6949171eef2d7ebdaf2c0e144689c9a117f59a0b082`  
**Toolchain:** `leanprover/lean4:v4.35.0` (commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, Release)  
**Epistemic Classification:** Machine-Checked Formal Theorem (`0 sorry`, standard Lean core axioms); One-Way Certificate Embedding Certified; Strict Non-Equivalence Boundary Preserved

---

## 1. Accomplished Formal Advancements

This formalization establishes the bridge from the integer-coefficient Nullstellensatz certificate system to field-based certificates over $\mathbb{Q}$, formalizes the syntactic vs. reduced quotient degree separation, and mathematically demonstrates the obstruction preventing naive reverse equivalence.

### A. Field-Parameterized Polynomial AST and Coefficient Mapping
- **Type Structure (`Poly R n`):** Parameterized over arbitrary coefficient domains $R$, with inductive constructors for constants, variables, addition, and multiplication.
- **Functorial Coefficient Lifting (`mapCoeff`):**
  $$\text{mapCoeff}(f, p) \implies \text{applies } f \text{ coefficient-wise}$$
- **Structural Degree Invariance (`mapCoeff_degree`):**
  $$\text{totalDegree}(\text{mapCoeff } f \; p) = \text{totalDegree}(p)$$
  Proving that total degree is a purely structural property of the polynomial AST, invariant under coefficient injection.

### B. Canonical Injection $\iota : \mathbb{Z} \hookrightarrow \mathbb{Q}$ and Evaluation Preservation
- **Rational Representation (`RatCoeff`):** Certified constructive fraction structure with arithmetic operations without external non-core dependencies.
- **Exact Evaluation Agreement (`eval_liftIntPoly_exact`):**
  $$\text{evalRatPoly}(\text{liftIntPoly } p, \lambda i \implies \text{ofInt}(x_i)) = \text{ofInt}(\text{evalIntPoly } p \; x)$$
- **Clause and Boolean Multiplier Lifting:**
  $$\text{liftIntPoly}(\text{intLitPoly } L) = \text{ratLitPoly } L$$
  $$\text{liftIntPoly}(\text{intClausePoly } C) = \text{ratClausePoly } C$$
  $$\text{liftIntPoly}(\text{intBoolAxiomPoly } i) = \text{ratBoolAxiomPoly } i$$
  $$\text{evalRatClauseTerms}(\text{lift } q, F, \text{lift } x) = \text{ofInt}(\text{evalIntClauseTerms } q \; F \; x)$$
  $$\text{evalRatBoolTerms}(\text{lift } r, \text{lift } x) = \text{ofInt}(\text{evalIntBoolTerms } r \; x)$$

### C. One-Way Embedding Theorem: $\operatorname{IntCert}(F, d) \implies \operatorname{RatCert}(F, d)$
- **Constructive Certificate Lifting (`liftConcreteNSRefutation`):**
  ```lean
  def liftConcreteNSRefutation {n : Nat} {F : Formula n} {d : Nat}
      (cert : ConcreteIntNSRefutation F d) :
      ConcreteRatNSRefutation F d
  ```
- **Master One-Way Embedding Theorem (`int_cert_implies_rat_cert`):**
  $$\operatorname{Nonempty}(\operatorname{ConcreteIntNSRefutation}(F, d)) \implies \operatorname{Nonempty}(\operatorname{ConcreteRatNSRefutation}(F, d))$$
  Proving that every formula refutable with integer multipliers at degree $\le d$ is refutable with rational multipliers at degree $\le d$.

### D. Syntactic vs. Reduced Quotient Degree Collapse
In the Boolean polynomial ring quotient $\mathbb{Q}[x_1, \dots, x_n] / \langle x_i^2 - x_i \rangle$, the relation $x_i^2 \equiv x_i$ allows powers to collapse.
- **Formal Demonstration (`degree_collapse_example`):**
  $$\text{totalDegree}(x_i^2) = 2 \quad \wedge \quad \text{totalDegree}(\operatorname{reducePoly}(x_i^2)) = 1$$
  Certified in Lean 4 with 0 axioms.

### E. Denominator Clearing Obstruction (Non-Equivalence Boundary)
Clearing common denominators $D > 1$ from a rational refutation $\sum q_C p_C + \sum r_i B_i = 1$ produces:
$$\sum q'_C p_C + \sum r'_i B_i = D \quad (q'_C, r'_i \in \mathbb{Z}[x])$$
- **Theorem (`denominator_clearing_obstruction`):**
  $$\forall D \in \mathbb{Z}, \quad D > 1 \implies \neg (\exists k \in \mathbb{Z}, \; D \cdot k = 1)$$
  Because $D$ is not invertible in the ring $\mathbb{Z}$, division by $D$ is impossible over integers. Consequently, **the converse implication $\operatorname{RatCert}(F, d) \implies \operatorname{IntCert}(F, d)$ does not hold trivially**, and minimum degree equivalence cannot be claimed.

---

## 2. Standalone Verification & Axiom Receipt

Direct compilation executed against `leanprover/lean4:v4.35.0`:

```text
'RationalNullstellensatz.liftConcreteNSRefutation' depends on axioms: [propext, Quot.sound]
'RationalNullstellensatz.int_cert_implies_rat_cert' depends on axioms: [propext, Quot.sound]
'RationalNullstellensatz.degree_collapse_example' depends on axioms: [propext]
'RationalNullstellensatz.denominator_clearing_obstruction' depends on axioms: [propext, Quot.sound]
```

- **Custom Axioms:** `0`
- **`sorry` Instances:** `0`
- **Standard Core Axioms:** Relies solely on standard propositional extensionality (`propext`) and quotient sound extensionality (`Quot.sound`).

---

## 3. Epistemic Scope & Complexity Frontiers

1. **One-Way Direction Bound:** This module formally establishes only $\operatorname{IntCert}(F, d) \implies \operatorname{RatCert}(F, d)$. It explicitly rejects claiming bidirectional minimum degree equivalence between $\mathbb{Z}$ and $\mathbb{Q}$ certificate systems.
2. **Finite Field Distinction:** Unlike the injection $\mathbb{Z} \hookrightarrow \mathbb{Q}$, reduction modulo $p$ ($\mathbb{Z} \to \mathbb{F}_p$) has non-trivial kernel $p\mathbb{Z}$, causing coefficients and degrees to collapse differently. Characteristic $p$ systems require a separate non-injective quotient analysis.
3. **Complexity Separation:** Neither rational nor integer Nullstellensatz certificate degree bounds provide super-polynomial lower bounds against general propositional proof systems (Cook–Reckhow barrier), and do not resolve $P$ vs $NP$.
