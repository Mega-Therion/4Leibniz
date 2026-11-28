//! `archon_kernel` — Rust port of the 4Leibniz verified epistemic and
//! consensus primitives, per the SAMO v2.0 spec §8 integration map
//! (Target 2: `4Leibniz` → Rust `archon_kernel`).
//!
//! Every module is a faithful port of a named Python reference in the
//! 4Leibniz repository; nothing here upgrades the reference's claims.
//! Where the Python is a structural model or a delegation layer (see
//! [`zk_verify`]), the Rust says so plainly and behaves the same way.
//!
//! | Rust module | Python / Lean source of truth |
//! |---|---|
//! | [`epistemic`] | SAMO §3.1–§3.2; `Leibniz/Epistemic.lean` (`Status` lattice); `STATUSES` in `bft.py` / `multiprover.py` |
//! | [`counterexample`] | `counterexample.py`; `ucalculus.py` (`Claim`, `Premise`); `proof_engine.py::_relation` |
//! | [`zk_verify`] | `zk_verify.py` (shape bounds + snarkjs delegation) |
//! | [`bft`] | `bft.py::decide` |
//! | [`multiprover`] | `multiprover.py::aggregate` |
//! | [`jsoncanon`] | CPython `json.dumps` canonicalization used by the hash inputs above |
//!
//! Hash parity with the Python reference is tested against golden
//! values produced by running the Python modules themselves
//! (certificate fingerprints, BFT proposal hashes, multi-prover
//! receipts).

pub mod bft;
pub mod counterexample;
pub mod epistemic;
pub mod jsoncanon;
pub mod multiprover;
pub mod zk_verify;
