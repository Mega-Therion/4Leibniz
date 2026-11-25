//! Deterministic BFT decision and incentive accounting.
//!
//! Faithful port of `4leibniz/bft.py::decide` (Phase 7). Per the Python
//! module docstring: "This is a coordination layer: it does not replace
//! Lean proof checking."
//!
//! SAMO relevance (spec §6.5): BFT accounting slashes provable
//! equivocation (`-10`) while assigning `0` penalty to honest minority
//! dissent — the Proof-of-Work-Inversion rule that bare majority votes
//! cannot sanction a peer. Both behaviors are preserved exactly,
//! including the Python quirks documented inline:
//!
//! * a vote for a *second* proposal hash or round from the same node is
//!   treated as Byzantine evidence (equivocation), not as a new vote;
//! * an identical duplicate vote is silently re-recorded (no penalty);
//! * votes from unknown nodes or with non-canonical statuses are
//!   ignored before any accounting;
//! * peers that cast no valid vote receive no incentive entry at all.

use crate::epistemic::{Status, STATUSES};
use crate::jsoncanon::{dumps_compact, sha256_hex, JVal};

/// Mirrors `bft.BFTPeer`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BFTPeer {
    pub node_id: String,
    pub weight: i64,
    /// Carried for structural parity with the Python dataclass;
    /// `decide` does not read it (as in Python).
    pub reputation: i64,
    /// Carried for structural parity; `decide` does not read it.
    pub faulty: bool,
}

impl BFTPeer {
    pub fn new(node_id: impl Into<String>) -> Self {
        BFTPeer {
            node_id: node_id.into(),
            weight: 1,
            reputation: 100,
            faulty: false,
        }
    }

    pub fn with_weight(node_id: impl Into<String>, weight: i64) -> Self {
        BFTPeer {
            weight,
            ..BFTPeer::new(node_id)
        }
    }
}

/// Mirrors `bft.BFTVote`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BFTVote {
    pub node_id: String,
    pub proposal_hash: String,
    /// Canonical status name (see [`Status`]).
    pub status: String,
    pub round: i64,
    pub nonce: String,
}

impl BFTVote {
    pub fn new(
        node_id: impl Into<String>,
        proposal_hash: impl Into<String>,
        status: impl Into<String>,
    ) -> Self {
        BFTVote {
            node_id: node_id.into(),
            proposal_hash: proposal_hash.into(),
            status: status.into(),
            round: 0,
            nonce: String::new(),
        }
    }

    fn to_jval(&self) -> JVal {
        // dataclasses.asdict field set; jsoncanon sorts keys, matching
        // json.dumps(..., sort_keys=True).
        JVal::Map(vec![
            ("node_id".into(), JVal::Str(self.node_id.clone())),
            ("nonce".into(), JVal::Str(self.nonce.clone())),
            (
                "proposal_hash".into(),
                JVal::Str(self.proposal_hash.clone()),
            ),
            ("round".into(), JVal::Int(self.round)),
            ("status".into(), JVal::Str(self.status.clone())),
        ])
    }
}

/// Mirrors `bft.Incentive`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Incentive {
    pub node_id: String,
    pub delta: i64,
    pub reason: String,
}

/// The decision record returned by [`decide`]; mirrors the dict returned
/// by `bft.decide` field-for-field.
#[derive(Debug, Clone, PartialEq)]
pub struct BFTDecision {
    /// SHA-256 of the canonical votes payload; empty when no valid
    /// votes were cast (as in Python).
    pub proposal_hash: String,
    /// Winning status name (the taint ceiling of the decision).
    pub status: String,
    pub accepted: bool,
    pub quorum_weight: i64,
    pub total_weight: i64,
    pub required_weight: i64,
    pub fault_tolerance: i64,
    /// `3 * fault_tolerance + 1` — the classical BFT minimum.
    pub minimum_nodes: usize,
    /// Sorted, deduplicated equivocating node ids.
    pub equivocations: Vec<String>,
    /// Valid votes, in Python dict-insertion order (node first-seen,
    /// then vote first-seen).
    pub votes: Vec<BFTVote>,
    pub incentives: Vec<Incentive>,
    pub explanation: String,
}

/// `bft._hash`: SHA-256 over `json.dumps(v, sort_keys=True,
/// separators=(",", ":"))`.
fn hash_payload(v: &JVal) -> String {
    sha256_hex(&dumps_compact(v))
}

/// Port of `bft.decide` with the Python defaults
/// (`fault_tolerance=1`, `threshold=2/3`).
pub fn decide_default(peers: &[BFTPeer], votes: &[BFTVote]) -> BFTDecision {
    decide(peers, votes, 1, 2.0 / 3.0)
}

/// Port of `bft.decide(peers, votes, fault_tolerance, threshold)`.
pub fn decide(
    peers: &[BFTPeer],
    votes: &[BFTVote],
    fault_tolerance: i64,
    threshold: f64,
) -> BFTDecision {
    // weights = {p.node_id: max(0, p.weight)} — a later duplicate peer
    // overwrites an earlier one, as in a Python dict comprehension.
    let mut weight_order: Vec<String> = Vec::new();
    let mut weights: Vec<i64> = Vec::new();
    for p in peers {
        match weight_order.iter().position(|n| n == &p.node_id) {
            Some(i) => weights[i] = p.weight.max(0),
            None => {
                weight_order.push(p.node_id.clone());
                weights.push(p.weight.max(0));
            }
        }
    }
    let weight_of = |node: &str| -> Option<i64> {
        weight_order
            .iter()
            .position(|n| n == node)
            .map(|i| weights[i])
    };
    let total: i64 = weights.iter().sum();

    // One vote per node and proposal; duplicate/conflicting votes are
    // Byzantine evidence. Insertion order is preserved to mirror the
    // Python dicts (and therefore the `votes` list and proposal hash).
    let mut by_node: Vec<(String, Vec<((String, i64), BFTVote)>)> = Vec::new();
    let mut equivocations: Vec<String> = Vec::new();
    for vote in votes {
        if weight_of(&vote.node_id).is_none() || Status::from_name(&vote.status).is_none() {
            continue;
        }
        let node_idx = match by_node.iter().position(|(n, _)| n == &vote.node_id) {
            Some(i) => i,
            None => {
                by_node.push((vote.node_id.clone(), Vec::new()));
                by_node.len() - 1
            }
        };
        let prior = &mut by_node[node_idx].1;
        let key = (vote.proposal_hash.clone(), vote.round);
        match prior.iter().position(|(k, _)| k == &key) {
            Some(existing) => {
                let prior_vote = &prior[existing].1;
                if prior_vote.status != vote.status
                    || prior_vote.proposal_hash != vote.proposal_hash
                {
                    equivocations.push(vote.node_id.clone());
                } else {
                    prior[existing].1 = vote.clone();
                }
            }
            None => {
                if !prior.is_empty() {
                    // A second proposal/round from the same node is
                    // equivocation evidence in the Python rules.
                    equivocations.push(vote.node_id.clone());
                } else {
                    prior.push((key, vote.clone()));
                }
            }
        }
    }

    let valid: Vec<BFTVote> = by_node
        .iter()
        .flat_map(|(_, node_votes)| node_votes.iter().map(|(_, v)| v.clone()))
        .collect();

    // tally over STATUSES in canonical order; Python's max() keeps the
    // first maximal item, i.e. the earliest status in STATUSES order.
    let mut tally: Vec<(Status, i64)> = STATUSES.iter().map(|s| (*s, 0)).collect();
    for vote in &valid {
        let status = Status::from_name(&vote.status).expect("valid votes have canonical status");
        let w = weight_of(&vote.node_id).expect("valid votes come from known peers");
        for entry in tally.iter_mut() {
            if entry.0 == status {
                entry.1 += w;
            }
        }
    }
    let (winning_status, quorum) =
        tally
            .iter()
            .fold((Status::Open, 0i64), |(best_s, best_w), (s, w)| {
                if *w > best_w {
                    (*s, *w)
                } else {
                    (best_s, best_w)
                }
            });

    // required = max(1, int(total * threshold + 0.999999))
    let required = ((total as f64 * threshold + 0.999999) as i64).max(1);
    let classical_bft_required = 3 * fault_tolerance + 1;
    let accepted = (peers.len() as i64) >= classical_bft_required
        && quorum >= required
        && equivocations.is_empty();

    let proposal_hash = if valid.is_empty() {
        String::new()
    } else {
        hash_payload(&JVal::Map(vec![(
            "votes".into(),
            JVal::List(valid.iter().map(|v| v.to_jval()).collect()),
        )]))
    };

    let mut incentives = Vec::new();
    for peer in peers {
        let own: Vec<&BFTVote> = valid.iter().filter(|v| v.node_id == peer.node_id).collect();
        if equivocations.contains(&peer.node_id) {
            incentives.push(Incentive {
                node_id: peer.node_id.clone(),
                delta: -10,
                reason: "equivocation detected".into(),
            });
        } else if !own.is_empty() && own[0].status == winning_status.name() && accepted {
            incentives.push(Incentive {
                node_id: peer.node_id.clone(),
                delta: 1,
                reason: "vote aligned with accepted quorum".into(),
            });
        } else if !own.is_empty() {
            // Spec §6.5: zero penalty for honest dissent.
            incentives.push(Incentive {
                node_id: peer.node_id.clone(),
                delta: 0,
                reason: "honest dissent or insufficient quorum".into(),
            });
        }
    }

    let mut equiv_sorted = equivocations;
    equiv_sorted.sort();
    equiv_sorted.dedup();

    BFTDecision {
        proposal_hash,
        status: winning_status.name().to_string(),
        accepted,
        quorum_weight: quorum,
        total_weight: total,
        required_weight: required,
        fault_tolerance,
        minimum_nodes: classical_bft_required as usize,
        equivocations: equiv_sorted,
        votes: valid,
        incentives,
        explanation: if accepted {
            "BFT quorum accepted.".into()
        } else {
            "Decision withheld: insufficient BFT quorum or equivocation detected.".into()
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn peers4() -> Vec<BFTPeer> {
        (0..4).map(|i| BFTPeer::new(format!("n{}", i))).collect()
    }

    #[test]
    fn accepts_four_honest_nodes_and_rewards_aligned_votes() {
        // Mirrors tests/test_phase7.py::test_bft_accepts_four_honest_nodes_and_rewards_aligned_votes
        let votes: Vec<BFTVote> = (0..4)
            .map(|i| BFTVote::new(format!("n{}", i), "p", "proven"))
            .collect();
        let result = decide(&peers4(), &votes, 1, 2.0 / 3.0);
        assert!(result.accepted);
        assert_eq!(result.incentives.iter().map(|i| i.delta).sum::<i64>(), 4);
        // Golden hash from the Python reference for this exact scenario.
        assert_eq!(
            result.proposal_hash,
            "7dd7aa715f08d4751f67f18d546835edbc34babbc5322810d329a0a2fbabe8da"
        );
        assert_eq!(result.required_weight, 3);
        assert_eq!(result.minimum_nodes, 4);
    }

    #[test]
    fn withholds_on_equivocation() {
        // Mirrors tests/test_phase7.py::test_bft_withholds_on_equivocation
        let votes = vec![
            BFTVote::new("n0", "p", "proven"),
            BFTVote::new("n0", "p", "open"),
            BFTVote::new("n1", "p", "proven"),
            BFTVote::new("n2", "p", "proven"),
            BFTVote::new("n3", "p", "proven"),
        ];
        let result = decide(&peers4(), &votes, 1, 2.0 / 3.0);
        assert!(!result.accepted);
        assert_eq!(result.equivocations, vec!["n0".to_string()]);
        // Spec section 6.5 accounting: -10 for the equivocator, 0 for
        // honest participants when the decision is withheld.
        assert_eq!(result.incentives[0].delta, -10);
        assert!(result.incentives[1..].iter().all(|i| i.delta == 0));
    }

    #[test]
    fn second_proposal_from_same_node_is_equivocation() {
        // Python branch: `elif prior and key not in prior` — voting on a
        // different proposal hash is Byzantine evidence, and the second
        // vote is not recorded.
        let votes = vec![
            BFTVote::new("n0", "p1", "proven"),
            BFTVote::new("n0", "p2", "proven"),
            BFTVote::new("n1", "p1", "proven"),
            BFTVote::new("n2", "p1", "proven"),
            BFTVote::new("n3", "p1", "proven"),
        ];
        let result = decide(&peers4(), &votes, 1, 2.0 / 3.0);
        assert!(!result.accepted);
        assert_eq!(result.equivocations, vec!["n0".to_string()]);
        assert_eq!(result.votes.len(), 4);
    }

    #[test]
    fn weighted_votes_below_threshold_are_withheld() {
        // Golden scenario computed with the Python reference.
        let peers = vec![
            BFTPeer::with_weight("a", 2),
            BFTPeer::with_weight("b", 1),
            BFTPeer::with_weight("c", 1),
            BFTPeer::with_weight("d", 1),
        ];
        let votes = vec![
            BFTVote::new("a", "h", "derived"),
            BFTVote::new("b", "h", "derived"),
            BFTVote::new("c", "h", "open"),
        ];
        let result = decide(&peers, &votes, 1, 2.0 / 3.0);
        assert!(!result.accepted);
        assert_eq!(result.status, "derived");
        assert_eq!(result.quorum_weight, 3);
        assert_eq!(result.total_weight, 5);
        assert_eq!(result.required_weight, 4);
        assert_eq!(
            result.proposal_hash,
            "0c9e0da5144a4e2b24798b57afdc545976374a243304126016d6238b5bce818a"
        );
        // Peer "d" cast no vote and receives no incentive entry.
        assert_eq!(result.incentives.len(), 3);
    }

    #[test]
    fn unknown_nodes_and_bad_statuses_are_ignored() {
        let votes = vec![
            BFTVote::new("ghost", "p", "proven"),
            BFTVote::new("n0", "p", "certain"),
        ];
        let result = decide(&peers4(), &votes, 1, 2.0 / 3.0);
        assert!(result.votes.is_empty());
        assert_eq!(result.proposal_hash, "");
        assert!(!result.accepted);
    }
}
