# 📜 4Leibniz Volunteer Compute Protocol (VCP)
### *A SETI@home Architecture for Distributed Archival Philology and Lean 4 Formal Verification*

```
                         4LEIBNIZ VOLUNTEER NETWORK
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
             [ COORDINATOR ]                   [ VOLUNTEER CLIENT ]
          Work-Unit Dispatcher                Idle-Resource Daemon
             (Job Queue)                      (CPU / GPU / Memory)
                    │                                 │
                    ├─────────► WORK UNIT ◄───────────┤
                    │           (LH-XXXV-0042)        │
                    │                                 │
                    ▼                                 ▼
         ┌─────────────────────┐           ┌─────────────────────┐
         │ STATISTICAL JOBS    │           │ DETERMINISTIC JOBS  │
         ├─────────────────────┤           ├─────────────────────┤
         │ • HTR Transcription │           │ • Lean 4 Compile    │
         │ • Latin/DE Transl.  │           │ • Proof Search      │
         │ • Cross-Reference   │           │ • BFT Consensus     │
         └─────────────────────┘           └─────────────────────┘
                    │                                 │
                    └────────────────┬────────────────┘
                                     ▼
                           [ BFT CONSENSUS / KERNEL ]
                                     │
                                     ▼
                         [ CANONICAL CORPUS REPO ]
```

---

## 1. Executive Summary

The **4Leibniz Volunteer Compute Protocol (VCP)** adapts the proven architecture of **SETI@home** and **Folding@home** to solve one of the largest unfinished intellectual challenges in the history of science: transcribing, translating, and formally verifying the ~200,000 unprinted manuscript folios of Gottfried Wilhelm Leibniz held at the Gottfried Wilhelm Leibniz Bibliothek in Hanover.

Rather than relying solely on a small team of paleographers and formal mathematicians, VCP allows anyone running the `4Leibniz` client to donate idle computational power.

---

## 2. Core Architectural Principles

1. **Zero-Trust Workers**:
   - Volunteer workers are assumed to be noisy, resource-constrained, and potentially Byzantine (faulty or malicious).
   - No worker output is accepted directly into the canonical corpus without independent verification.

2. **Dual-Track Verification Pipeline**:
   - **Track A: Statistical Consensus (HTR & Translation)**
     - Non-deterministic tasks (Handwritten Text Recognition from manuscript scans, translation candidate generation) are assigned to $K \ge 3$ independent volunteer nodes.
     - Results are compared using character-level Levenshtein consensus and semantic embedding agreement.
     - When $K$ workers agree above a threshold confidence ($\ge 0.95$), the transcript is marked as a candidate for final scholarly review.
   - **Track B: Deterministic Verification (Formal Lean 4 Proof Checking)**
     - Formal proof checking is absolute. A worker checking a Lean 4 proof compiles the script with `lake env lean <target>.lean`.
     - The output is binary: either it typechecks with exit code `0` and contains no unverified axioms or `sorry`, or it fails.

3. **Strict Sandboxing & Safety**:
   - Work units contain only bounded, declarative data.
   - No arbitrary shell commands or remote network execution are permitted on volunteer machines.
   - Execution occurs within isolated container/process sandboxes with capped CPU percentage, memory bounds, and temperature throttling.

---

## 3. Work-Unit (Job) Lifecycle

```
[ UNTRANSCRIBED FOLIO ] ──► [ SLICED FRAGMENT ] ──► [ JOB SPEC ]
                                                           │
┌──────────────────────────────────────────────────────────┘
│
├──► Dispatched to Worker A (CPU/HTR) ──► Candidate "ens" (conf: 0.98)
├──► Dispatched to Worker B (GPU/HTR) ──► Candidate "ens" (conf: 0.97)
└──► Dispatched to Worker C (CPU/HTR) ──► Candidate "ens" (conf: 0.99)
                                                │
                                                ▼
                                    [ BFT 3-WAY CONSENSUS ]
                                                │
                                                ▼
                                      "ens" (Accepted)
```

---

## 4. Job Classes

| Job Class | Input Type | Computational Engine | Verification Method |
| :--- | :--- | :--- | :--- |
| **`HTR_TRANSCRIPTION`** | Image fragment (TIFF/PNG) of Leibniz cursive | Local PyLaia / Kraken / Vision model | $K$-of-$N$ BFT Agreement |
| **`LATIN_TRANSLATION`** | Verified Latin transcript chunk | Local translation LLM / Rule-based parser | Semantic Cosine + Human-in-the-loop |
| **`CROSS_REFERENCE`** | Concept phrase (e.g. *Analysis Situs*) | Vector index / BM25 search across Nachlass | Deterministic Exact Match |
| **`LEAN4_PROOF_CHECK`** | Lean 4 script with premises | `lake env lean` compiler | Exit Code 0, 0 sorries, 0 axioms |
| **`BOUNDED_PROOF_SEARCH`** | Target claim & declared premises | `4Leibniz.proof_engine` | Step trace reproduction |

---

## 5. Security & Privacy Guarantees

- **No Crypto-Mining**: Proofs of work verify actual historical philology or mathematical theorems, never cryptocurrency hashes.
- **Resource Constraints**: Default configuration restricts client to:
  - Max 50% idle CPU
  - Run only when on AC power
  - Pause if CPU temperature exceeds 75°C
  - Max 2 GB RAM consumption
- **Signed Payloads**: All jobs dispatched by the central coordinator are cryptographically signed using Ed25519 keys.

---

## 6. Integration with 4Leibniz Codebase

The volunteer subsystem directly integrates with existing `4Leibniz` infrastructure:
- **Consensus**: Integrates directly with [`bft.py`](file:///home/mega/4Leibniz/bft.py) and [`consensus.py`](file:///home/mega/4Leibniz/consensus.py).
- **Multi-prover Validation**: Uses [`multiprover.py`](file:///home/mega/4Leibniz/multiprover.py).
- **Lean 4 Proof Kernel**: Connects to the lake build environment at [`Leibniz.lean`](file:///home/mega/4Leibniz/Leibniz.lean).
