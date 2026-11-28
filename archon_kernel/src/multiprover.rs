//! Multi-prover evidence aggregation.
//!
//! Faithful port of `4leibniz/multiprover.py::aggregate` (Phase 8). Per
//! the Python module docstring: "Aggregation coordinates independent
//! verifier reports; it never upgrades a claim above the strongest
//! evidence actually supplied by an authorized verifier." The accepted
//! status is the *minimum* status across the winning report set — the
//! epistemic monad bind law of SAMO §3.2 applied to aggregation (see
//! [`crate::epistemic::taint_of`]).
//!
//! Python behaviors preserved exactly, including:
//! * the winning artifact is chosen by report count, with ties broken
//!   by the lexicographically *largest* digest (Python
//!   `sorted(..., key=(count, digest), reverse=True)`);
//! * acceptance requires `independent >= 2` independent-kernel reports
//!   when `require_independent` is set — the constant is 2 in the
//!   Python regardless of the `required` quorum size;
//! * when not accepted, the status stays `"open"` no matter what was
//!   reported;
//! * dissent includes winning-digest reports whose status differs from
//!   the final (minimum) status once accepted.

use crate::epistemic::Status;
use crate::jsoncanon::{dumps_default, sha256_hex, JVal};

/// Mirrors `multiprover.ProofReport`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProofReport {
    pub prover_id: String,
    pub artifact_digest: String,
    /// Canonical status name (see [`Status`]).
    pub status: String,
    pub independent_kernel: bool,
    pub signature_verified: bool,
    pub rationale: String,
}

impl ProofReport {
    pub fn new(
        prover_id: impl Into<String>,
        artifact_digest: impl Into<String>,
        status: impl Into<String>,
    ) -> Self {
        ProofReport {
            prover_id: prover_id.into(),
            artifact_digest: artifact_digest.into(),
            status: status.into(),
            independent_kernel: false,
            signature_verified: false,
            rationale: String::new(),
        }
    }

    pub fn with_flags(
        prover_id: impl Into<String>,
        artifact_digest: impl Into<String>,
        status: impl Into<String>,
        independent_kernel: bool,
        signature_verified: bool,
    ) -> Self {
        ProofReport {
            independent_kernel,
            signature_verified,
            ..ProofReport::new(prover_id, artifact_digest, status)
        }
    }

    fn to_jval(&self) -> JVal {
        JVal::Map(vec![
            (
                "artifact_digest".into(),
                JVal::Str(self.artifact_digest.clone()),
            ),
            (
                "independent_kernel".into(),
                JVal::Bool(self.independent_kernel),
            ),
            ("prover_id".into(), JVal::Str(self.prover_id.clone())),
            ("rationale".into(), JVal::Str(self.rationale.clone())),
            (
                "signature_verified".into(),
                JVal::Bool(self.signature_verified),
            ),
            ("status".into(), JVal::Str(self.status.clone())),
        ])
    }
}

/// The aggregation record returned by [`aggregate`]; mirrors the dict
/// returned by `multiprover.aggregate` field-for-field.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AggregateResult {
    pub artifact_digest: String,
    pub accepted: bool,
    /// Final status name: the minimum status of the winning set when
    /// accepted, otherwise `"open"`.
    pub status: String,
    pub report_count: usize,
    pub quorum_required: usize,
    pub matching_reports: usize,
    pub independent_kernel_reports: usize,
    pub signed_reports: usize,
    /// All valid reports, in input order.
    pub reports: Vec<ProofReport>,
    pub dissent: Vec<ProofReport>,
    /// SHA-256 receipt over the canonical winning-set payload.
    pub receipt: String,
    pub explanation: String,
}

/// Port of `multiprover.aggregate` with the Python defaults
/// (`required=2`, `require_independent=True`).
pub fn aggregate_default(reports: &[ProofReport]) -> AggregateResult {
    aggregate(reports, 2, true)
}

/// Port of `multiprover.aggregate(reports, required, require_independent)`.
pub fn aggregate(
    reports: &[ProofReport],
    required: usize,
    require_independent: bool,
) -> AggregateResult {
    let valid: Vec<ProofReport> = reports
        .iter()
        .filter(|r| {
            Status::from_name(&r.status).is_some()
                && !r.artifact_digest.is_empty()
                && !r.prover_id.is_empty()
        })
        .cloned()
        .collect();

    // Group by digest, preserving first-seen digest order and in-group
    // input order (Python dict semantics).
    let mut by_digest: Vec<(String, Vec<ProofReport>)> = Vec::new();
    for r in &valid {
        match by_digest.iter_mut().find(|(d, _)| d == &r.artifact_digest) {
            Some((_, group)) => group.push(r.clone()),
            None => by_digest.push((r.artifact_digest.clone(), vec![r.clone()])),
        }
    }
    // ranked = sorted(by_digest.items(), key=(len, digest), reverse=True)
    by_digest.sort_by(|a, b| (a.1.len(), &a.0).cmp(&(b.1.len(), &b.0)).reverse());
    let (digest, winning) = by_digest
        .into_iter()
        .next()
        .unwrap_or_else(|| (String::new(), Vec::new()));

    let independent = winning.iter().filter(|r| r.independent_kernel).count();
    let signed = winning.iter().filter(|r| r.signature_verified).count();
    let accepted = !winning.is_empty()
        && winning.len() >= required
        && (!require_independent || independent >= 2);
    let status = if accepted {
        winning
            .iter()
            .filter_map(|r| Status::from_name(&r.status))
            .min()
            .expect("accepted implies a non-empty winning set")
            .name()
            .to_string()
    } else {
        "open".to_string()
    };
    let dissent: Vec<ProofReport> = valid
        .iter()
        .filter(|r| r.artifact_digest != digest || (accepted && r.status != status))
        .cloned()
        .collect();

    // receipt = sha256(json.dumps({"digest": digest, "reports":
    //     [asdict(r) for r in winning]}, sort_keys=True))  — CPython
    // default separators, reproduced by jsoncanon::dumps_default.
    let receipt_payload = JVal::Map(vec![
        ("digest".into(), JVal::Str(digest.clone())),
        (
            "reports".into(),
            JVal::List(winning.iter().map(|r| r.to_jval()).collect()),
        ),
    ]);
    let receipt = sha256_hex(&dumps_default(&receipt_payload));

    AggregateResult {
        artifact_digest: digest,
        accepted,
        status,
        report_count: valid.len(),
        quorum_required: required,
        matching_reports: winning.len(),
        independent_kernel_reports: independent,
        signed_reports: signed,
        reports: valid,
        dissent,
        receipt,
        explanation: if accepted {
            "Independent prover quorum reached.".into()
        } else {
            "Evidence quorum not reached; status remains open.".into()
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn requires_independent_quorum() {
        // Mirrors tests/test_phase8.py::test_multi_prover_requires_independent_quorum
        let reports = vec![
            ProofReport::with_flags("a", "d", "proven", true, true),
            ProofReport::with_flags("b", "d", "proven", true, true),
            ProofReport::with_flags("c", "d", "proven", false, true),
        ];
        let result = aggregate(&reports, 2, true);
        assert!(result.accepted);
        assert_eq!(result.independent_kernel_reports, 2);
        assert_eq!(result.status, "proven");
        // Golden receipt from the Python reference for this scenario.
        assert_eq!(
            result.receipt,
            "3d3dcc432341bae68287f2c33e87ee261acc3a890e544a2a6e5162a7af7cb7a1"
        );
    }

    #[test]
    fn retains_dissent() {
        // Mirrors tests/test_phase8.py::test_multi_prover_retains_dissent.
        // Note the Python tie-break: equal counts pick the larger digest
        // ("other" > "d"), so the "d" report becomes the dissent.
        let reports = vec![
            ProofReport::with_flags("a", "d", "proven", true, false),
            ProofReport::with_flags("b", "other", "derived", true, false),
        ];
        let result = aggregate(&reports, 2, true);
        assert!(!result.accepted);
        assert_eq!(result.artifact_digest, "other");
        assert_eq!(result.dissent.len(), 1);
        assert_eq!(result.dissent[0].artifact_digest, "d");
        assert_eq!(result.status, "open");
        assert_eq!(
            result.receipt,
            "878c321459835ee4267297c652c0be8687fb0479aca89d402488eae2d8c16905"
        );
    }

    #[test]
    fn accepted_status_is_the_minimum_of_the_winning_set() {
        // The SAMO section 3.2 bind law: aggregation never upgrades
        // above the weakest supplied evidence.
        let reports = vec![
            ProofReport::with_flags("a", "d", "proven", true, true),
            ProofReport::with_flags("b", "d", "derived", true, false),
        ];
        let result = aggregate(&reports, 2, true);
        assert!(result.accepted);
        assert_eq!(result.status, "derived");
        // The stronger report counts as dissent against the final
        // (minimum) status, exactly as in Python.
        assert_eq!(result.dissent.len(), 1);
        assert_eq!(result.dissent[0].prover_id, "a");
        assert_eq!(
            result.receipt,
            "48b0192f7bc8b96a0cefad789a5e46ddc060eb50c127a1186bc6c9119dbb5083"
        );
    }

    #[test]
    fn invalid_reports_are_filtered_before_quorum() {
        let reports = vec![
            ProofReport::with_flags("a", "d", "certain", true, true), // bad status
            ProofReport::with_flags("", "d", "proven", true, true),   // no prover
            ProofReport::with_flags("b", "", "proven", true, true),   // no digest
        ];
        let result = aggregate(&reports, 2, true);
        assert_eq!(result.report_count, 0);
        assert!(!result.accepted);
        assert_eq!(result.artifact_digest, "");
    }

    #[test]
    fn single_independent_kernel_is_not_a_quorum() {
        let reports = vec![
            ProofReport::with_flags("a", "d", "proven", true, true),
            ProofReport::with_flags("b", "d", "proven", false, true),
        ];
        let result = aggregate(&reports, 2, true);
        assert!(!result.accepted);
        // ... but the same set passes when independence is not required.
        let relaxed = aggregate(&reports, 2, false);
        assert!(relaxed.accepted);
    }
}
