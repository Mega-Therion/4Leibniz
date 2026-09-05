# Lean dependency report

- Modules: 10
- Declarations: 107
- Theorem-like declarations: 34

> This is a reproducible source-level import/declaration inventory. It does not claim a full elaborated theorem-to-theorem dependency graph.

## Module inventory

| Module | Imports | Theorem-like declarations |
|---|---|---:|
| `Leibniz.Calculemus` | `Mathlib`, `Leibniz.Characteristica`, `Leibniz.SpatiumRelativum`, `Leibniz.VisViva`, `Leibniz.LexContinuitatis`, `Leibniz.Harmonia` | 1 |
| `Leibniz.Characteristica` | `Mathlib` | 3 |
| `Leibniz.Epistemic` | `Mathlib` | 7 |
| `Leibniz.Harmonia` | `Mathlib`, `Leibniz.LexContinuitatis` | 2 |
| `Leibniz.LexContinuitatis` | `Mathlib` | 11 |
| `Leibniz.Monadologia` | `Mathlib` | 3 |
| `Leibniz.OpenProblems` | `Mathlib` | 0 |
| `Leibniz.Sources` | `Mathlib` | 0 |
| `Leibniz.SpatiumRelativum` | `Mathlib`, `Leibniz.Characteristica` | 2 |
| `Leibniz.VisViva` | `Mathlib` | 5 |

## Declaration details

### `Leibniz.Calculemus`
- `inductive` `Proposition`
- `inductive` `Verdict`
- `structure` `Adjudication`
- `def` `adjudicate`
- `def` `oracle`
- `structure` `VeritasReceipt`
- `def` `execute_calculemus`
- `theorem` `calculemus_omnibus_verum`
- `structure` `GaugePath`
- `def` `holonomy`
- `def` `vonNeumannEntropy`

### `Leibniz.Characteristica`
- `inductive` `EpistemicStatus`
- `def` `Proven`
- `def` `Derived`
- `def` `Axiomatic`
- `def` `Conjectured`
- `def` `Open`
- `structure` `EpistemicRecord`
- `inductive` `Dyas`
- `def` `tensio`
- `theorem` `tensio_symm`
- `theorem` `tensio_self`
- `theorem` `tensio_max`
- `def` `metadata`

### `Leibniz.Epistemic`
- `inductive` `Status`
- `def` `rank`
- `def` `le`
- `def` `join`
- `def` `meet`
- `theorem` `le_refl`
- `theorem` `le_trans`
- `theorem` `join_upper_left`
- `theorem` `join_upper_right`
- `theorem` `meet_lower_left`
- `theorem` `meet_lower_right`
- `inductive` `EvidenceKind`
- `structure` `Assumption`
- `structure` `AssumptionContext`
- `def` `ids`
- `def` `contains`
- `def` `add`
- `inductive` `Evidence`
- `structure` `SourceRef`
- `structure` `ArgumentBundle`
- `abbrev` `ProvenArgument`
- `abbrev` `DerivedArgument`
- `theorem` `ProvenArgument.proof`
- `def` `ProvenArgument.weaken`
- `def` `statusOf`

### `Leibniz.Harmonia`
- `abbrev` `Qubit`
- `abbrev` `Operator`
- `structure` `DensityMatrix`
- `structure` `LindbladSystem`
- `def` `commutator`
- `def` `anticommutator`
- `def` `harmonia_stabilis`
- `theorem` `anti_drift_preservation`
- `theorem` `coherence_preservation_invariant`

### `Leibniz.LexContinuitatis`
- `def` `theta`
- `def` `chiFloor`
- `def` `chiCeil`
- `def` `chiMidArithmetic`
- `def` `chiMidGeometric`
- `theorem` `theta_pos`
- `theorem` `theta_lt_two`
- `theorem` `chiFloor_pos`
- `theorem` `chiCeil_pos`
- `theorem` `chi_floor_lt_mid`
- `theorem` `chi_mid_lt_ceil`
- `theorem` `continuity_band_ordered`
- `theorem` `within_continuity_envelope`
- `theorem` `ceiling_squared`
- `def` `chi_floor_scaled`
- `def` `chi_mid_scaled`
- `def` `chi_ceil_scaled`
- `theorem` `scaled_band_ordered`
- `theorem` `scaled_within_continuity_envelope`

### `Leibniz.Monadologia`
- `structure` `MonadState`
- `def` `Harmonized`
- `inductive` `HarmonyChain`
- `theorem` `harmony_reflexive`
- `theorem` `harmony_chain_has_unity`
- `inductive` `Formula`
- `inductive` `Derivation`
- `def` `Derivation.size`
- `theorem` `sufficient_reason_chain`

### `Leibniz.OpenProblems`
- `structure` `OpenProblem`
- `def` `registry`

### `Leibniz.Sources`
- `structure` `HistoricalSource`
- `def` `concordance`
- `def` `sourceFor`

### `Leibniz.SpatiumRelativum`
- `structure` `Monas`
- `def` `distantia_relativa`
- `theorem` `distantia_symm`
- `theorem` `distantia_self`
- `def` `Stiefel`
- `def` `tangentSpace`
- `def` `geodesic`
- `structure` `GlobalFieldState`
- `structure` `Holonomia`

### `Leibniz.VisViva`
- `def` `vis_viva`
- `theorem` `vis_viva_nonneg`
- `theorem` `vis_viva_positive`
- `theorem` `log_domain`
- `theorem` `mu_bounded`
- `theorem` `mu_strictMono`
- `def` `acceleratio_limitis`
