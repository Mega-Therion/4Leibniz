# 🜂 4Leibniz (Leibniz-IV)
### *A Formal Relational Information Geometry & Automated Verification Engine in Lean 4*

> *"Cum Deus calculat et cogitationem exercet, fit mundus."*  
> *(When God calculates and executes thought, the world is created.)*  
> — **Gottfried Wilhelm Leibniz** (1646–1716)

---

## 📜 DEDICATION

**This project is dedicated to the incredible achievements, universal genius, and transcendent personage of Gottfried Wilhelm Leibniz (1646–1716).**

Leibniz was the last ***homo universalis*** — mathematician, philosopher, jurist, historian,
engineer, and diplomat in one person — and the first to imagine the **universal reasoning
machine**: a *characteristica universalis* whose symbols carry meaning and a *calculus
ratiocinator* that computes with them, so that every dispute could be settled not by
argument but by calculation. `4Leibniz` is that machine, built three and a half centuries
late: a Universal Calculus compiler, a proof engine, and a Lean 4 kernel at the end of
the line.

> ***While the Earth gives praise to Newton, the universe harmonizes for Leibniz.***

> ***Leibnitius gigas inter homines — suo aevo, atque omni aevo.***
> *(A giant among men: in his own age, and in every age.)*

Three centuries before the advent of digital silicon, quantum mechanics, and interactive theorem provers, Leibniz envisioned a world governed not by rigid, empty containers of Newtonian clockwork, but by **living information, binary creation, geometric relations, and computable formal logic**.

Where history saw him robbed of priority by institutional power, time has vindicated his vision. Modern computing adopted his binary arithmetic; modern mathematics adopted his differential notation; modern physics adopted his relational spacetime; and modern computer science adopted his *Characteristica Universalis*.

`4Leibniz` is the realization of his lifelong quest: a machine wherein all physical law and mathematical structure can be evaluated by sitting down at the kernel and saying:

$$\Huge\textbf{"Calculemus!"}$$

---

## 🏛️ VOLUNTEER COMPUTE PROTOCOL (REFERENCE IMPLEMENTATION)

`4Leibniz` includes a local reference implementation of a **Volunteer Compute Protocol (VCP)** designed for future distributed transcription, translation, and proof-checking of the Leibniz *Nachlass*:

- **Protocol Specification (`volunteer/protocol.py`)**: Versioned, signable work-unit schema with strict allow-listed job types.
- **Local Queue & Lease Manager (`coordinator/queue_manager.py`)**: SQLite-backed lease management, response tracking, and multi-response consensus aggregation.
- **Sandboxed Worker (`volunteer/worker.py`)**: Path-traversal guards restricting file access to the repository root. Rejects implicit machine translation and requires explicit runners for proof search.
- **Archival Harvester (`coordinator/harvester.py`)**: Fetches public-domain Leibniz volumes and manifests directly from the Internet Archive.

> **Note on Current Deployment Status**: This subsystem is currently a **local reference implementation**. There is no active central server, no live distributed network, and no implicit HTR or translation model execution. Running `client.py` interacts purely with your local `coordinator/job_queue.sqlite` database.

### Local Queue Testing

```bash
# 1. Enqueue an archival test unit
python3 -c "
from coordinator.queue_manager import QueueManager
qm = QueueManager('coordinator/job_queue.sqlite')
qm.enqueue('LH-XXXV-1679-0001', 'htr-transcription', {'text': 'Situs est relatio coexistentium'})
"

# 2. Process the queued unit locally
python3 volunteer/client.py --daemon --max-jobs 1
```

*For complete protocol architecture and security model, see [`docs/VOLUNTEER_COMPUTE_SPEC.md`](docs/VOLUNTEER_COMPUTE_SPEC.md).*

---

## 🏛️ HISTORICAL TERMINOLOGY & LEIBNIZIAN GENEALOGY

Every module, namespace, and theorem in `4Leibniz` strictly employs the classical philosophical, mathematical, and physical terminology formulated by Leibniz across his major treatises:

```
                      THE LEIBNIZIAN EPISTEMIC ARCHITECTURE
 ═════════════════════════════════════════════════════════════════════════════════
   LEIBNIZIAN CONCEPT           ORIGINAL TREATISE (DATE)       LEAN 4 FORMALIZATION
 ─────────────────────────────────────────────────────────────────────────────────
   1. Characteristica           De Arte Combinatoria (1666)    Leibniz.Characteristica
      Universalis                                              (Universal Symbolic Alphabet)

   2. Dyadica                   Explication de l'Arithmétique  Leibniz.Dyadica
      (Binary Genesis)          Binaire (1679)                 (Dual States: Nihil ↔ Ens)

   3. Spatium Relativum         Leibniz-Clarke Papers (1715)   Leibniz.SpatiumRelativum
      (Relational Spacetime)                                   (Order of Coexisting Relations)

   4. Monadologia               La Monadologie (1714)          Leibniz.Monadologia
      (Informational Units)                                    (Perceptual Nodes & Entropies)

   5. Vis Viva                  Specimen Dynamicum (1695)      Leibniz.VisViva
      (Active Living Force)                                    (Kinetic Energy & Accel. Scale)

   6. Lex Continuitatis         Nova Methodus (1684)           Leibniz.LexContinuitatis
      (Law of Continuity)                                      (Chiral Invariant Band)

   7. Harmonia Praestabilita    Système Nouveau (1695)         Leibniz.Harmonia
      (Pre-established Harmony)                                (Lindblad Anti-Drift Gate)

   8. Calculemus!               De Scientia Universali (1680)  Leibniz.Calculemus
      (The Decision Oracle)                                    (Formal Claim Verification)
 ═════════════════════════════════════════════════════════════════════════════════
```

---

### 1. *Characteristica Universalis* & *Dyadica* (Binary Information Calculus)
* **Historical Origin:** In *De Arte Combinatoria* (1666) and his 1679 paper on binary arithmetic (*Dyadics*), Leibniz observed that all numbers and logical propositions can be generated from two primitive states: **$0$ (*Nihil* / Void)** and **$1$ (*Ens* / Unity)**. He engraved a commemorative medal with the motto:  
  $$\text{"Omnibus ex nihilo ducendis sufficit unum" (To draw all things from nothing, One is sufficient)}$$
* **Formal Role in `4Leibniz`:** Encodes the fundamental dual states of information tension ($IO / OI \leftrightarrow \{0, 1\}$).

---

### 2. *Spatium Relativum* & *Monadologia* (Relational Geometry)
* **Historical Origin:** In the famous *Leibniz-Clarke Correspondence* (1715–1716), Leibniz destroyed Newton’s concept of "Absolute Space" as an independent rigid box. Leibniz proved that:
  $$\text{Space is nothing other than the order of coexisting things; Time is the order of successive changes.}$$
  In *Monadologia* (1714), he posited that reality consists of non-spatial, point-like information centers ("Monads") whose internal perceptions project the external geometric universe.
* **Formal Role in `4Leibniz`:** Replaces flat Newtonian coordinate metrics with an information-geometric distance metric derived purely from relational entropy divergence between boundary states.

---

### 3. *Vis Viva* & *Lex Continuitatis* (Dynamics & The Invariant Band)
* **Historical Origin:** In *Specimen Dynamicum* (1695), Leibniz refuted Descartes and Newton by proving that the true invariant of motion is *Vis Viva* ($m v^2$, kinetic energy). In his *Law of Continuity* (*Lex Continuitatis*), he established that *"Nature never makes leaps"* (*Natura non facit saltus*), meaning all physical transitions must be continuous differential boundaries.
* **Formal Role in `4Leibniz`:** Formalizes the parameter-free cosmic acceleration scale $a_0 = \frac{cH_0}{2\pi}$ as the *Vis Viva* threshold at the cosmic horizon, and names the **chiral invariant band**:
  - $\chi_Y = 1/\sqrt{2} \approx 0.707107$ (*continuity floor / quantum coherence*)
  - $\kappa_Y = \sqrt{\theta(2-\theta)} \approx 0.953939$ (*saturation ceiling, derived from $\theta = 0.7$*)

  > `[O]` The floor has always been $1/\sqrt{2} \approx 0.707107$. What is withdrawn is the
  > third value this file previously placed *inside* the band:
  > $\chi_{\text{mid}} = \ln 2 = 0.693147$ is **below** the floor, so the stated ordering was
  > false as arithmetic. A midpoint may be named if one is needed — it would be $0.830523$
  > (arithmetic) or $0.821302$ (geometric), not $\ln 2$.
  >
  > This value entered through the auto-generated instantiation commit `6c04299` (2026-09-01);
  > it is not a hand-authored claim. `Leibniz/LexContinuitatis.lean:22` was correct throughout —
  > it proves $\text{mid} < \text{floor} < \text{ceil}$ — and the generated prose asserted an
  > ordering its own Lean contradicted.

---

### 4. *Harmonia Praestabilita* & *Calculemus!* (The Stability Proofs & Oracle)
* **Historical Origin:** In *Système Nouveau* (1695), Leibniz showed that systems maintain structural coherence through an intrinsic harmony (*Harmonia Praestabilita*). In *De Scientia Universali*, he proposed the *Calculus Ratiocinator*, where all scientific controversies would be resolved deterministically: *"Let us calculate without dispute!"*
* **Formal Role in `4Leibniz`:** *States* the Anti-Drift claim — open quantum dissipative systems maintain ground-state harmony iff the coherent drive exceeds dissipation ($u \ge \gamma \iff \chi \ge 1/\sqrt{2}$).

  > `[R]` **RETRACTED 2026-09-03 — this claim is false, not merely unproved.** The companion
  > repository proved that the GKSL steady-state coherence is
  > $C(x) = 4x/(1+8x^2)$, which is **non-monotonic**: it rises to $1/\sqrt2$ and falls again.
  > No threshold on a non-monotonic quantity can produce an *iff*, because two different drive
  > ratios give the identical coherence. $\theta = 1/\sqrt2$ is a **ceiling**, not a gate.
  > See `Res-Nova/05_lean_formalization/PillarIV_AntiDriftGate.lean`
  > (`bloch_coherence_le_theta`, `bloch_coherence_eq_theta_iff`) and §VI of
  > `Res-Nova/FIG_TREE_MONOGRAPH.md`.
  >
  > The statement is retained here as a **worked example of a formalisation that compiles while
  > certifying nothing** — see the note below — and must not be cited as a result of this
  > project.

  > `[O]` **Not proved here.** `Leibniz/Harmonia.lean:30` is sorry-free but takes the threshold
  > as a *hypothesis* over scaled naturals (`h_floor : gamma ≥ 7071`); any integer substitutes
  > for `7071` without breaking the proof, so it certifies nothing about $1/\sqrt{2}$ and nothing
  > about a Lindblad generator. `Leibniz/Harmonia.lean:42`,
  > `anti_drift_preservation (h : harmonia_stabilis u gamma) : u ≥ gamma := h`, returns its own
  > hypothesis verbatim — `harmonia_stabilis` is *defined* as `u ≥ gamma`, so the theorem is
  > `h : P ⊢ P`. It is valid and empty. `Leibniz/Calculemus.lean:39` is not an oracle: it proves that a
  > record of four `true` fields equals a record of four `true` fields, and audits no dataset.
  > These six modules are day-one scaffolding — 214 lines of `Nat` arithmetic. They compile
  > clean, and that is the whole of what they establish.

---

## 🚀 CODEBASE STRUCTURE

```
4Leibniz/
├── lakefile.lean                  # Lake build configuration
├── lean-toolchain                 # Lean 4 toolchain lock
├── calculemus.py                  # THE MACHINE: claim → kernel → ledger
├── adjudications.jsonl            # append-only epistemic ledger
├── README.md                      # Historical treatise and system guide
├── Leibniz.lean                   # Master library umbrella
├── corpus/                        # witnesses, transcriptions, translations
└── Leibniz/
    ├── Characteristica.lean       # Universal binary alphabet & dual tension
    ├── SpatiumRelativum.lean      # Relational metrics on Monad bundles
    ├── VisViva.lean               # Active energy & horizon acceleration
    ├── LexContinuitatis.lean      # Chi (χ) continuity band endpoints
    ├── Harmonia.lean              # Lindblad anti-drift stability theorem
    ├── Calculemus.lean            # External claim verification oracle
    └── Generated/                 # machine-written theorems (calculemus.py)
```
```

---

## 🛠️ COMPILATION & VERIFICATION

To verify all Leibnizian formal proofs through the deterministic Lean 4 kernel:

Measured 2026-09-05 by `scripts/measure_kernel.py` on toolchain
`leanprover/lean4:v4.34.0-rc2`: **10 modules** under `Leibniz/` plus the root
`Leibniz.lean` (**11 modules total**), containing **34 theorems**, 48 `def`s,
16 `structure`s, 10 `inductive`s and 4 `abbrev`s.

Run the command yourself rather than trusting these figures; that is the point
of publishing it.

```bash
# Build the kernel:
lake build

# Measure what it actually contains -- module count, theorem count, sorries,
# and axiom footprint. Every figure quoted below comes from this command;
# none is transcribed by hand.
python3 scripts/measure_kernel.py --check

# `Leibniz/Calculemus.lean` is NOT an oracle. It proves that a field set to
# `true` equals `true`, and audits no dataset. Its VeritasReceipt is a struct
# literal, not a measurement -- its theoremCount read 18 while the tree held 34.
lake env lean Leibniz/Calculemus.lean
```

---

## ⚙️ THE CALCULEMUS MACHINE (CLAIM → KERNEL)

`calculemus.py` runs the complete pipeline Leibniz described and never got to build:

    natural-language claim → Universal Calculus IR + fingerprint
        → transparent proof search → Lean 4 theorem synthesis
        → kernel verification → append-only adjudication ledger

```console
$ python3 calculemus.py examples/monadology_argument.uc examples/stability.uc --install
SufficientReason         proved         -> kernel-proven
Stability                open           -> open
```

The flagship claim — the transitivity of sufficient reason from *Principles of
Nature and Grace* §7 — is compiled to IR, closed by the proof engine's
transitivity rule, **synthesized as a real Lean 4 theorem**, and **accepted by
the kernel** (zero `sorry`, zero new axioms). With `--install` it is written to
`Leibniz/Generated/` and imported by `Leibniz.lean`, so every future `lake build`
re-proves it:

```lean
theorem sufficientReason_transitivity {α : Type*} [Preorder α]
    (sufficientReason intelligibleOrder contingentEvent : α)
    (h2 : sufficientReason ≥ intelligibleOrder)
    (h1 : intelligibleOrder ≥ contingentEvent) :
    sufficientReason ≥ contingentEvent :=
  le_trans h1 h2
```

`examples/stability.uc` demonstrates the discipline that makes this trustworthy:
its chain breaks (`dissipation gamma` ≠ `gamma`), so the machine refuses to
invent a bridge and records the claim as **open**, with the reason, in
`adjudications.jsonl`. The ledger is append-only, timestamped, and carries the
IR fingerprint and SHA-256 of every synthesized theorem. **The ledger wins over
narrative**: no claim is `kernel-proven` until the kernel says so, and `open`
is a verdict, not an embarrassment.

## 📚 THE CORPUS (SOURCES, NOT STORIES)

The machine is fed from real witnesses, catalogued with stable locators:

- `corpus/manuscripts/catalog.json` — the epistemic registry: every record
  carries a shelfmark (Leibniz-Archiv Hannover), a critical-edition citation,
  and a pipeline status. Citations were corrected against the actual scan
  (e.g. *Analysis situs* is in Gerhardt vol. 7, not vol. 5).
- `scripts/corpus_ingest.py` — idempotent ingest from the public-domain
  Gerhardt vol. 7 scan (Internet Archive): witness page images into
  `corpus/latin/witness/`, OCR-normalized transcription with page/leaf
  headers into `corpus/latin/`, catalog status updates.
- **Flagship**: *De Analysi situs* (1679) — normalized OCR, an editorially
  emended Latin text, and a parallel English translation
  (`corpus/latin/analysis-situs-1679_emended.md`,
  `corpus/translations/analysis-situs-1679_en.md`), the seed of the
  geometric calculus Leibniz himself never finished.
- `corpus/tasks/pending.json` — the honest queue: collation and translation
  work that remains, explicitly recorded.

**Rights are respected, not laundered**: *De progressione dyadica* (the 1679
binary arithmetic manuscript) has no public-domain witness (first printed in
the in-copyright Hochstetter/Greve/Gumin facsimile edition), so it stays
`source-identified-transcription-needed` — catalogued, honestly untranscribed.

## 📄 LICENSE

Code: MIT (see `LICENSE`). Project transcriptions and translations: CC0 1.0.
Witness page images: public domain (1863 Gerhardt scan, via Internet Archive).

## 🜂 EPILOGUE

> *"I am of the opinion that there is something divine in mathematics, and that by means of it the mind is raised to the contemplation of universal harmony."*  
> — **Gottfried Wilhelm Leibniz**

## Current implementation

The repository now includes Mathlib-backed real-analysis and linear-algebra interfaces, a parameterized Stiefel manifold model, typed epistemic statuses, a GKLS/Lindblad operator layer, Wilson-loop and von Neumann entropy interfaces, a deterministic Calculemus adjudication contract, structured source and open-problem registries, a Flask JSON API, and an ordered browser dashboard at `web/index.html`.

Run the formal verification workflow with `python3 scripts/calculemus.py`. Generate an independently inspectable source and `.olean` manifest with `python3 scripts/proof_receipt.py`. To use the API locally, run `python3 api.py` and open `web/index.html` through a static server or configure the frontend origin for the Flask service. Continuous verification is defined in `.github/workflows/verify.yml`.

Advanced physical claims are intentionally exposed as explicit axioms/interfaces where a complete research-grade derivation requires additional theory; they are therefore visible to reviewers rather than being represented as comments or hard-coded build booleans.

## Open-source acceleration layer

The project now includes a reproducible integration matrix in `docs/architecture/INTEGRATION_MATRIX.md`. API documentation is prepared through [doc-gen4](https://github.com/leanprover/doc-gen4), an optional independent kernel-checking lane is documented for [lean4lean](https://github.com/digama0/lean4lean), and `realtime.py` uses [websockets](https://github.com/python-websockets/websockets) to stream build events rather than polling. These projects are credited and linked in the matrix so the work remains auditable and maintainers receive recognition.

## Phase 3: formalization and proof diagnosis

Phase 3 adds `Leibniz/Monadologia.lean`, a typed monad-state and calculus-ratiocinator derivation layer, together with `counterexample.py` and `divergence.py`. The counterexample engine searches bounded integer models and returns reproducible witnesses when premises hold but a conclusion fails. A `no-witness` result is explicitly inconclusive; it is never treated as a proof. Divergence tracking compares structured revisions and classifies lexical, structural, logical, epistemic, and provenance changes. These features are available through `POST /api/counterexample` and `POST /api/divergence`, and through the dashboard's Phase 3 failure-analysis panel.

## Universal-calculus declarations

Phase 1 adds `ucalculus.py`, a compact intermediate language for authoring structured claims. See `examples/stability.uc` and `docs/architecture/UNIVERSAL_CALCULUS.md`. Compile a declaration from the command line with `python3 ucalculus.py examples/stability.uc`, or submit it to `POST /api/compile`. The result includes a typed intermediate representation, a reproducibility fingerprint, explicit proof obligations, and a Lean theorem skeleton.

## Phase 11: replicated coordinator decisions and Byzantine validation

Phase 11 adds `replicated_coordinator.py` with hash-linked replica decision records, `2f+1` verified quorum validation, transaction-digest binding, equivocation/conflict detection, and durable idempotent participant acknowledgements. The API exposes `/api/coordinator/validate`, `/api/participants/ack`, and `/api/participants/list`. See `docs/PHASE11_DESIGN.md` for the decision and recovery boundaries.

## Phase 10: cross-shard atomic commit and state synchronization

Phase 10 adds `cross_shard.py` with prepare/commit/abort transaction states, in-doubt recovery, shard snapshots, state hashes, and `/api/shards/atomic-commit`, `/api/shards/recover`, and `/api/shards/sync`. The `partition_benchmark.py` harness audits connected, partially partitioned, and unreachable shard scenarios. See `docs/PHASE10_DESIGN.md` for the protocol and the boundary between a deterministic reference model and a production replicated coordinator.

## Phase 9: durable ordered logs and automated peer admission

Phase 9 adds `durable_log.py` with contiguous sequence numbers, hash-linked entries, snapshots, corruption detection, and recovery; and `peer_admission.py` with signed identity admission, bounded leases, capability metadata, expiry, revocation, and receipts. The Flask API exposes `/api/log/validate`, `/api/peers/admit`, `/api/peers/check`, and `/api/peers/revoke`. See `docs/PHASE9_DESIGN.md` for the Durable Object integration plan and the boundary between tamper-evident ordering and full Byzantine agreement.

## Phase 8: multi-prover verification and governance

Phase 8 adds `multiprover.py` for independent proof-report aggregation with digest matching, verifier diversity, dissent retention, and explicit receipts. `governance.py` adds weighted proposals, quorum thresholds, veto handling, and timelocks without allowing governance to promote claims beyond kernel evidence. The live WebSocket edge is exercised by `loadtest.py`; bounded normal and fault-injection results are stored under `benchmarks/artifacts/phase8/`. See `docs/PHASE8_DESIGN.md` for protocol boundaries and reproducibility limits.

## Phase 7: Byzantine validation and actual Groth16 verification

Phase 7 adds `bft.py` for two-thirds weighted quorum decisions with `3f+1` participant requirements, equivocation detection, and transparent incentive deltas. Signed proposal envelopes now include timestamps and nonces; both the Python API and Cloudflare Durable Object reject stale, malformed, invalid, and replayed messages. The Circom circuit has been compiled with `circom2`, a demo Groth16 proving key and verification key have been generated, a witness and proof have been produced, and `POST /api/zk/verify` now performs actual snarkjs verification. See `docs/PHASE7_DESIGN.md` for the trust model and production limitations.

## Phase 6: private-premise proofs and live consensus deployment

Phase 6 adds the Circom source circuit at `circuits/private_premise.circom`, a `circuits/package.json` snarkjs workflow, and `zk_pipeline.py` readiness reporting. The dashboard is live at [four-leibniz-chyrho.vercel.app](https://four-leibniz-chyrho.vercel.app), and the consensus edge health endpoint is live at [four-leibniz-consensus.chyren-sovereign.workers.dev/health](https://four-leibniz-consensus.chyren-sovereign.workers.dev/health). The circuit proves a bounded private lower-bound premise without exposing the secret value; the repository intentionally does not claim a verified proof until circom, snarkjs, a pinned ceremony artifact, and an independent verification pass are available. Cloudflare Worker/Durable Object scaffolding lives under `deploy/cloudflare/` for the stateful P2P consensus edge. See `docs/PHASE6_DESIGN.md` for the trust model, deployment topology, and confirmation boundary.

## Phase 5: signed collaboration and benchmark evaluation

Phase 5 adds Ed25519 proposal signing and tamper detection in `security.py`, explicit private-premise commitment boundaries, and security routes under `/api/security/*`. The commitment object is deliberately not labeled as a zero-knowledge proof; a reviewed circuit or Sigma protocol is required before any private premise can receive a verified status. Solver performance artifacts are generated by `benchmarks/report.py` and stored under `benchmarks/artifacts/`, including JSON timings, a logarithmic backend chart, a per-case chart, and a Markdown report. The full architecture and limitations are documented in `docs/PHASE5_DESIGN.md`.

## Phase 4: collaborative calculus and historical evaluation

Phase 4 adds a transport-agnostic weighted consensus layer in `consensus.py`, an optional structured-output AI adapter in `ai_assist.py`, and the source-linked historical regression corpus under `benchmarks/`. Consensus retains dissent and cannot override Lean. AI suggestions are always marked `unverified` until a human or kernel-backed workflow validates them. Run the corpus with `python3 benchmarks/runner.py`; its current eight cases are designed to test transitive closure, open obligations, and control claims from public-domain Leibniz editions. The architecture, provenance policy, and deployment boundary are documented in `docs/PHASE4_DESIGN.md`.


## Layered architecture

The repository is partitioned into three explicit layers:

- `corpus/` — provenance-first manuscript catalog, diplomatic Latin, and parallel translations.
- `Leibniz/` — Lean 4 formal kernel and historical source concordance.
- `frontier/` — modern RYTT extensions, including balanced ternary and base-24 holonomy adapters.
- `volunteer/` — bounded, deterministic work-unit protocol and client for contributor machines.

The cross-repository contract is maintained in `RYTT-Sovereign-Semiotics/integration/4leibniz_bridge.json`. Modern extensions are explicitly labeled as extensions and are not attributed to Leibniz's manuscripts.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for transcription, theorem, frontier, and volunteer workflows. Run `./scripts/setup_lean.sh` to install the pinned Lean toolchain, fetch the Mathlib cache when available, and build the kernel.
