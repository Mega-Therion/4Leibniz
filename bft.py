"""Phase 7 deterministic BFT decision and incentive accounting.

This is a coordination layer: it does not replace Lean proof checking.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json

@dataclass(frozen=True)
class BFTPeer:
    node_id: str
    weight: int = 1
    reputation: int = 100
    faulty: bool = False

@dataclass(frozen=True)
class BFTVote:
    node_id: str
    proposal_hash: str
    status: str
    round: int = 0
    nonce: str = ""

@dataclass(frozen=True)
class Incentive:
    node_id: str
    delta: int
    reason: str

STATUSES = ("open", "conjectured", "axiomatic", "derived", "proven")

def _hash(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def decide(peers, votes, fault_tolerance=1, threshold=2/3):
    peers = tuple(peers); votes = tuple(votes)
    weights = {p.node_id: max(0, p.weight) for p in peers}
    total = sum(weights.values())
    # One vote per node and proposal; duplicate/conflicting votes are Byzantine evidence.
    by_node = {}
    equivocations = []
    for vote in votes:
        if vote.node_id not in weights or vote.status not in STATUSES:
            continue
        prior = by_node.setdefault(vote.node_id, {})
        key = (vote.proposal_hash, vote.round)
        if key in prior and (prior[key].status != vote.status or prior[key].proposal_hash != vote.proposal_hash):
            equivocations.append(vote.node_id)
        elif prior and key not in prior:
            equivocations.append(vote.node_id)
        else:
            prior[key] = vote
    valid = [v for node in by_node.values() for v in node.values()]
    tally = {s: 0 for s in STATUSES}
    for vote in valid: tally[vote.status] += weights[vote.node_id]
    winning_status, quorum = max(tally.items(), key=lambda item: item[1]) if tally else ("open", 0)
    required = max(1, int(total * threshold + 0.999999))
    classical_bft_required = 3 * fault_tolerance + 1
    accepted = len(peers) >= classical_bft_required and quorum >= required and not equivocations
    proposal_hash = _hash({'votes': [asdict(v) for v in valid]}) if valid else ''
    incentives = []
    for peer in peers:
        own = [v for v in valid if v.node_id == peer.node_id]
        if peer.node_id in equivocations:
            incentives.append(Incentive(peer.node_id, -10, 'equivocation detected'))
        elif own and own[0].status == winning_status and accepted:
            incentives.append(Incentive(peer.node_id, 1, 'vote aligned with accepted quorum'))
        elif own:
            incentives.append(Incentive(peer.node_id, 0, 'honest dissent or insufficient quorum'))
    return {'proposal_hash': proposal_hash, 'status': winning_status, 'accepted': accepted,
            'quorum_weight': quorum, 'total_weight': total, 'required_weight': required,
            'fault_tolerance': fault_tolerance, 'minimum_nodes': classical_bft_required,
            'equivocations': sorted(set(equivocations)), 'votes': [asdict(v) for v in valid],
            'incentives': [asdict(i) for i in incentives],
            'explanation': ('BFT quorum accepted.' if accepted else
                           'Decision withheld: insufficient BFT quorum or equivocation detected.')}
