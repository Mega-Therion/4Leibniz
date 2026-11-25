//! Epistemic monad taint propagation (SAMO v2.0 spec §3.1–§3.2).
//!
//! Source trace:
//! * The certainty lattice (`open < conjectured < axiomatic < derived <
//!   proven`, with `rank`, `join`, `meet`) is ported from the Lean 4
//!   reference `4Leibniz/Leibniz/Epistemic.lean` (`Leibniz.Epistemic.Status`,
//!   machine-checked there with `sorry`-free lattice lemmas).
//! * The same five statuses, in the same order, are the `STATUSES` tuples in
//!   `4leibniz/bft.py` and `4leibniz/multiprover.py`, whose aggregation
//!   rules (`multiprover.aggregate`) already implement the taint law: an
//!   aggregate is never upgraded above the weakest evidence supplied.
//! * The monadic bind law itself is normative spec text (SAMO §3.2): any
//!   reasoning step composing inputs of tiers `T1..Tk` outputs at most
//!   `min(T1..Tk)` **unless** an independent deterministic verifier executes
//!   and emits a new witness receipt. [`ClaimM::verify`] is the only
//!   promotion path in this module, mirroring that exception.
//!
//! Memory tiers (§3.1) are provenance classes, not statuses: see
//! [`MemoryTier`] for the ratchet rules.

use std::cmp::Ordering;

/// Epistemic certainty status. Ported from `Leibniz/Epistemic.lean`
/// (`Status`) and the `STATUSES` tuples of `bft.py` / `multiprover.py`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Status {
    Open,
    Conjectured,
    Axiomatic,
    Derived,
    Proven,
}

/// All statuses in ascending rank order — mirrors the Python
/// `STATUSES = ("open", "conjectured", "axiomatic", "derived", "proven")`.
pub const STATUSES: [Status; 5] = [
    Status::Open,
    Status::Conjectured,
    Status::Axiomatic,
    Status::Derived,
    Status::Proven,
];

impl Status {
    /// `Status.rank` in `Epistemic.lean`: open=0 .. proven=4.
    pub fn rank(self) -> u8 {
        match self {
            Status::Open => 0,
            Status::Conjectured => 1,
            Status::Axiomatic => 2,
            Status::Derived => 3,
            Status::Proven => 4,
        }
    }

    /// The canonical lowercase name used by the Python modules and the
    /// universal-calculus IR (`ucalculus.py`).
    pub fn name(self) -> &'static str {
        match self {
            Status::Open => "open",
            Status::Conjectured => "conjectured",
            Status::Axiomatic => "axiomatic",
            Status::Derived => "derived",
            Status::Proven => "proven",
        }
    }

    /// Parse a canonical status name, as validated by `ucalculus.parse`
    /// (`status:` clause) and the `STATUSES` membership checks in
    /// `bft.decide` / `multiprover.aggregate`.
    pub fn from_name(name: &str) -> Option<Status> {
        STATUSES.iter().copied().find(|s| s.name() == name)
    }

    /// `Status.join` in `Epistemic.lean`: the stronger of two statuses.
    pub fn join(self, other: Status) -> Status {
        if self.rank() <= other.rank() {
            other
        } else {
            self
        }
    }

    /// `Status.meet` in `Epistemic.lean`: the weaker of two statuses.
    /// This is the taint operator of the monadic bind law (spec §3.2).
    pub fn meet(self, other: Status) -> Status {
        if self.rank() <= other.rank() {
            self
        } else {
            other
        }
    }
}

impl PartialOrd for Status {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Status {
    /// `Status.le` in `Epistemic.lean`: order by rank.
    fn cmp(&self, other: &Self) -> Ordering {
        self.rank().cmp(&other.rank())
    }
}

/// The taint of a composition: the minimum tier over all inputs
/// (spec §3.2 monadic bind law). Returns `None` for an empty composition,
/// where the law has nothing to bound. This is the same rule
/// `multiprover.aggregate` applies to a winning report set
/// (`min(statuses)`), generalized to arbitrary compositions.
pub fn taint_of(tiers: &[Status]) -> Option<Status> {
    tiers.iter().copied().reduce(Status::meet)
}

/// A witness receipt emitted by an independent deterministic verifier —
/// the *only* artifact that may raise a claim's tier above the taint of
/// its inputs (spec §3.2: "unless an independent deterministic verifier
/// executes and emits a new witness receipt").
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct VerifierReceipt {
    /// Identifier of the verifying kernel/prover (e.g. a Lean kernel,
    /// an SMT solver, or a multi-prover quorum receipt hash).
    pub verifier_id: String,
    /// Tier the verifier attests.
    pub tier: Status,
    /// Hash of the verifier's witness (proof receipt, certificate
    /// fingerprint, or aggregation receipt).
    pub witness_hash: String,
}

/// A typed epistemic container: `ClaimM<Tier, Provenance, WitnessHash>`
/// wrapping a value, per spec §3.2.
///
/// In the Python reference implementation the container is implicit — a
/// `ucalculus.Claim` carries `status`, `source`, and a content
/// `fingerprint` (see `ucalculus.py`, `divergence.py::_fingerprint`) —
/// and the taint law is enforced procedurally by `multiprover.aggregate`
/// and `bft.decide`. This struct makes the container explicit so the
/// law is enforced by construction in Rust.
#[derive(Debug, Clone, PartialEq)]
pub struct ClaimM<T> {
    pub tier: Status,
    /// Free-form provenance string (the Python `Claim.source` analogue).
    pub provenance: String,
    /// Content/witness hash of the wrapped artifact (SHA-256 hex, as in
    /// `ucalculus.compile_claim`'s `fingerprint`).
    pub witness_hash: String,
    pub value: T,
}

impl<T> ClaimM<T> {
    pub fn new(
        value: T,
        tier: Status,
        provenance: impl Into<String>,
        witness_hash: impl Into<String>,
    ) -> Self {
        ClaimM {
            tier,
            provenance: provenance.into(),
            witness_hash: witness_hash.into(),
            value,
        }
    }

    /// Functor map: transforming the payload never changes the tier
    /// (a rewrite is not a verification).
    pub fn map<U>(self, f: impl FnOnce(T) -> U) -> ClaimM<U> {
        ClaimM {
            tier: self.tier,
            provenance: self.provenance,
            witness_hash: self.witness_hash,
            value: f(self.value),
        }
    }

    /// Monadic bind / composition taint: combining this claim with
    /// others caps the result at the minimum input tier (spec §3.2).
    /// The returned tier is the ceiling for any value derived from
    /// these inputs without a fresh [`VerifierReceipt`].
    pub fn combined_taint(&self, others: &[ClaimM<impl Sized>]) -> Status {
        let mut taint = self.tier;
        for other in others {
            taint = taint.meet(other.tier);
        }
        taint
    }

    /// The verifier exception to the bind law: an independent
    /// deterministic verifier's receipt re-tiers the claim and replaces
    /// its witness hash with the verifier's. This is the *only* method
    /// in this module that can raise a tier.
    pub fn verify(self, receipt: &VerifierReceipt) -> ClaimM<T> {
        ClaimM {
            tier: receipt.tier,
            provenance: self.provenance,
            witness_hash: receipt.witness_hash.clone(),
            value: self.value,
        }
    }

    /// Weaken a claim to a lower tier (always sound; mirrors
    /// `ProvenArgument.weaken` in `Epistemic.lean`). Attempting to
    /// "weaken" to a higher tier is a no-op rather than a promotion.
    pub fn weaken(self, tier: Status) -> ClaimM<T> {
        ClaimM {
            tier: self.tier.meet(tier),
            ..self
        }
    }
}

/// The four-tier monotonic memory partition of spec §3.1. These are
/// provenance classes for stored artifacts; the ratchet rules below are
/// the normative promotion/demotion constraints from §3.1.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum MemoryTier {
    /// Tier 0 — mechanically verified artifacts with reproducible
    /// receipts (`[P]`/`[D]`/`[E]`).
    Canon,
    /// Tier 1 — partially verified, explicitly fenced with coverage
    /// bounds (`checks_unavailable` is a first-class output).
    Conditional,
    /// Tier 2 — unverified outputs and exploratory drafts; ephemeral
    /// working context.
    Sandbox,
    /// Tier 3 — refuted claims and reproducible counterexamples;
    /// append-only negative-knowledge cache.
    Quarantine,
}

impl MemoryTier {
    /// §3.1 Canon ratchet: a tier may advance to `Canon` *only* via
    /// independent deterministic verification emitting a witness
    /// receipt — never by prose, aggregation, or self-assertion.
    pub fn promote(self, target: MemoryTier, receipt: Option<&VerifierReceipt>) -> MemoryTier {
        match (self, target) {
            (_, MemoryTier::Canon) if receipt.is_none() => self,
            _ => target,
        }
    }

    /// §3.1: Canon is demoted *only* by a verified `[X]` counterexample
    /// certificate (see [`crate::counterexample`]); the demotion target
    /// is always `Quarantine`, where the refuted artifact is retained
    /// as a regression warning, never silently deleted.
    pub fn demote_by_counterexample(self, verified_refutation: bool) -> MemoryTier {
        if verified_refutation {
            MemoryTier::Quarantine
        } else {
            self
        }
    }

    /// §3.1: `Sandbox` artifacts are strictly barred from auto-promoting
    /// into `Canon`; any path out of Sandbox requires the receipt-gated
    /// [`MemoryTier::promote`] above.
    pub fn auto_promote(self) -> MemoryTier {
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lattice_matches_epistemic_lean() {
        // rank order: open < conjectured < axiomatic < derived < proven
        assert!(Status::Open < Status::Conjectured);
        assert!(Status::Conjectured < Status::Axiomatic);
        assert!(Status::Axiomatic < Status::Derived);
        assert!(Status::Derived < Status::Proven);
        // join = max, meet = min (Epistemic.lean join_upper/meet_lower lemmas)
        assert_eq!(Status::Derived.join(Status::Open), Status::Derived);
        assert_eq!(Status::Derived.meet(Status::Proven), Status::Derived);
        for a in STATUSES {
            for b in STATUSES {
                assert!(a <= a.join(b) && b <= a.join(b));
                assert!(a.meet(b) <= a && a.meet(b) <= b);
            }
        }
    }

    #[test]
    fn bind_law_caps_at_weakest_input() {
        let tiers = [Status::Proven, Status::Derived, Status::Conjectured];
        assert_eq!(taint_of(&tiers), Some(Status::Conjectured));
        assert_eq!(taint_of(&[]), None);
        let strong = ClaimM::new("a", Status::Proven, "test", "h1");
        let weak = ClaimM::new("b", Status::Open, "test", "h2");
        assert_eq!(strong.combined_taint(&[weak]), Status::Open);
    }

    #[test]
    fn only_a_receipt_promotes() {
        let claim = ClaimM::new(1, Status::Conjectured, "draft", "h0");
        let receipt = VerifierReceipt {
            verifier_id: "lean-kernel".into(),
            tier: Status::Proven,
            witness_hash: "hw".into(),
        };
        let promoted = claim.clone().verify(&receipt);
        assert_eq!(promoted.tier, Status::Proven);
        assert_eq!(promoted.witness_hash, "hw");
        // map and weaken can never raise the tier
        assert_eq!(claim.clone().map(|x| x + 1).tier, Status::Conjectured);
        assert_eq!(claim.weaken(Status::Proven).tier, Status::Conjectured);
    }

    #[test]
    fn memory_tier_ratchet() {
        // No receipt -> no Canon promotion.
        assert_eq!(
            MemoryTier::Sandbox.promote(MemoryTier::Canon, None),
            MemoryTier::Sandbox
        );
        let receipt = VerifierReceipt {
            verifier_id: "mvpc-x".into(),
            tier: Status::Derived,
            witness_hash: "hw".into(),
        };
        assert_eq!(
            MemoryTier::Sandbox.promote(MemoryTier::Canon, Some(&receipt)),
            MemoryTier::Canon
        );
        // Demotion only via verified refutation, and only into Quarantine.
        assert_eq!(
            MemoryTier::Canon.demote_by_counterexample(false),
            MemoryTier::Canon
        );
        assert_eq!(
            MemoryTier::Canon.demote_by_counterexample(true),
            MemoryTier::Quarantine
        );
        assert_eq!(MemoryTier::Sandbox.auto_promote(), MemoryTier::Sandbox);
    }
}
