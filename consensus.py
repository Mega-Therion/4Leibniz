"""Deterministic decentralized-consensus primitives for proof collaboration.

The current implementation is transport-agnostic. Nodes exchange signed-looking
content hashes and votes; production deployments should bind signatures to a
real identity and append accepted proposals to durable storage.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json
from typing import Iterable

STATUSES = ("open", "conjectured", "axiomatic", "derived", "proven")

@dataclass(frozen=True)
class Peer:
    node_id: str
    weight: int = 1
    capabilities: tuple[str, ...] = ("lean", "search")

@dataclass(frozen=True)
class Vote:
    node_id: str
    proposal_hash: str
    status: str
    rationale: str = ""

@dataclass(frozen=True)
class ConsensusResult:
    proposal_hash: str
    status: str
    accepted: bool
    quorum_weight: int
    total_weight: int
    votes: tuple[Vote, ...]
    dissent: tuple[Vote, ...]
    explanation: str

def proposal_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()

def reach_consensus(peers: Iterable[Peer], votes: Iterable[Vote], threshold: float = 2/3) -> ConsensusResult:
    peers = tuple(peers); votes = tuple(votes)
    weights = {p.node_id: p.weight for p in peers}
    total = sum(weights.values())
    valid = tuple(v for v in votes if v.node_id in weights and v.status in STATUSES)
    tally = {s: 0 for s in STATUSES}
    for vote in valid: tally[vote.status] += weights[vote.node_id]
    status, quorum = max(tally.items(), key=lambda item: item[1]) if tally else ("open", 0)
    required = max(1, int(total * threshold + 0.999999))
    accepted = quorum >= required and total > 0
    winning = tuple(v for v in valid if v.status == status)
    dissent = tuple(v for v in valid if v.status != status)
    return ConsensusResult(
        proposal_hash=valid[0].proposal_hash if valid else "",
        status=status, accepted=accepted, quorum_weight=quorum, total_weight=total,
        votes=valid, dissent=dissent,
        explanation=(f"{quorum}/{total} weighted votes support {status}; "
                     f"{'quorum reached' if accepted else 'quorum not reached'} at {threshold:.0%}."))

def result_json(result: ConsensusResult) -> dict:
    return asdict(result)
