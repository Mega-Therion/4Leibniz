"""Phase 8 auditable governance policy evaluator."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json
@dataclass(frozen=True)
class GovernanceVote:
    node_id: str
    support: bool
    weight: int = 1
    veto: bool = False
    rationale: str = ""

def evaluate(proposal_id, action, votes, quorum=2/3, veto_blocks=True, timelock_seconds=3600):
    votes = tuple(votes); total = sum(max(0, v.weight) for v in votes); yes = sum(max(0,v.weight) for v in votes if v.support); veto = any(v.veto for v in votes)
    accepted = total > 0 and yes / total >= quorum and not (veto_blocks and veto)
    receipt = hashlib.sha256(json.dumps({'proposal_id':proposal_id,'action':action,'votes':[asdict(v) for v in votes]},sort_keys=True).encode()).hexdigest()
    return {'proposal_id':proposal_id,'action':action,'accepted':accepted,'yes_weight':yes,'total_weight':total,'threshold':quorum,'veto':veto,'timelock_seconds':timelock_seconds if accepted else 0,'receipt':receipt,'votes':[asdict(v) for v in votes],'explanation':'Proposal accepted and timelocked.' if accepted else 'Proposal rejected or vetoed.'}
