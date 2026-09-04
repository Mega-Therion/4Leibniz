"""Phase 11 replicated coordinator decision and acknowledgement model."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, time
from durable_log import OrderedLog

def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
@dataclass(frozen=True)
class DecisionVote:
    replica_id: str
    txid: str
    decision: str
    transaction_digest: str
    sequence: int = 0
    signature_verified: bool = False
@dataclass(frozen=True)
class ParticipantAck:
    shard_id: str
    txid: str
    phase: str
    transaction_digest: str
    sequence: int
    idempotency_key: str
    timestamp: int = 0
class ReplicatedDecisionLog:
    def __init__(self, replica_id): self.replica_id=replica_id; self.log=OrderedLog(); self.votes={}; self.conflicts=[]
    def record(self, vote):
        if vote.decision not in ('commit','abort'): raise ValueError('invalid decision')
        prior=self.votes.get(vote.txid)
        if prior and (prior.decision != vote.decision or prior.transaction_digest != vote.transaction_digest):
            self.conflicts.append({'txid':vote.txid,'replica_id':vote.replica_id,'kind':'equivocation'}); raise ValueError('conflicting decision')
        self.votes[vote.txid]=vote
        self.log.append(vote.txid, {'decision':vote.decision,'transaction_digest':vote.transaction_digest,'replica_id':vote.replica_id})
        return self.log.head

def validate_decision(votes, txid, transaction_digest, fault_tolerance=1):
    votes=tuple(votes); expected=2*int(fault_tolerance)+1
    eligible=[v for v in votes if v.txid==txid and v.transaction_digest==transaction_digest and v.signature_verified]
    conflicts=[asdict(v) for v in votes if v.txid==txid and (v.transaction_digest!=transaction_digest or not v.signature_verified)]
    by_decision={d:[v for v in eligible if v.decision==d] for d in ('commit','abort')}
    winning=max(by_decision, key=lambda d: len(by_decision[d])) if eligible else None
    accepted=winning is not None and len(by_decision[winning])>=expected and not (by_decision.get('commit') and by_decision.get('abort'))
    return {'accepted':accepted,'txid':txid,'decision':winning if accepted else None,'quorum_required':expected,'matching_votes':len(by_decision.get(winning,[])) if winning else 0,'conflicts':conflicts,'votes':[asdict(v) for v in votes],'receipt':digest({'txid':txid,'decision':winning if accepted else None,'votes':[asdict(v) for v in votes]})}
class AckStore:
    def __init__(self): self.acks={}
    def record(self, ack):
        key=ack.idempotency_key; prior=self.acks.get(key)
        if prior and asdict(prior)!=asdict(ack): raise ValueError('acknowledgement conflict')
        self.acks[key]=ack; return {'accepted':True,'idempotent':prior is not None,'ack':asdict(ack),'receipt':digest(asdict(ack))}
    def for_transaction(self, txid): return [asdict(a) for a in self.acks.values() if a.txid==txid]
    def durable_snapshot(self): return {'acks':[asdict(a) for a in self.acks.values()]}
