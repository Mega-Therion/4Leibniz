"""Phase 12 authenticated replica membership and failover reference model."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, time
from security import SignedProposal, sign_proposal, verify_proposal
@dataclass(frozen=True)
class ReplicaMember:
    replica_id: str
    public_key: str
    weight: int = 1
    admitted_at: int = 0
    expires_at: int = 0
    revoked: bool = False

def member_receipt(member): return hashlib.sha256(json.dumps(asdict(member),sort_keys=True).encode()).hexdigest()
def issue_member(replica_id, private_key, weight=1, ttl=86400, now=None):
    now=int(time.time()) if now is None else int(now); proposal=sign_proposal(replica_id,{'kind':'replica_membership','replica_id':replica_id},private_key,timestamp=now)
    return {'proposal':asdict(proposal),'record':asdict(ReplicaMember(replica_id,proposal.public_key,max(1,int(weight)),now,now+int(ttl),False))}
def active(member, now=None):
    now=int(time.time()) if now is None else int(now); return bool(member and not member.get('revoked') and member.get('admitted_at',0)<=now<member.get('expires_at',0))
def sign_vote(replica_id, txid, decision, transaction_digest, private_key, sequence=0, timestamp=None):
    proposal=sign_proposal(replica_id,{'kind':'decision_vote','txid':txid,'decision':decision,'transaction_digest':transaction_digest,'sequence':sequence},private_key,timestamp=timestamp)
    return asdict(proposal)
def verify_vote(envelope, member, now=None):
    if not active(member, now): return False
    try:
        proposal=SignedProposal(**envelope)
        return proposal.payload.get('kind')=='decision_vote' and proposal.node_id==member['replica_id'] and proposal.public_key==member['public_key'] and verify_proposal(proposal)
    except Exception: return False
def elect_coordinator(members, epoch, now=None):
    active_members=[m for m in members if active(m,now)]; active_members.sort(key=lambda m:(-int(m.get('weight',1)),m['replica_id']))
    if not active_members: return {'accepted':False,'reason':'no active replicas','epoch':epoch}
    winner=active_members[0]; return {'accepted':True,'epoch':int(epoch),'coordinator_id':winner['replica_id'],'eligible_replicas':[m['replica_id'] for m in active_members],'receipt':hashlib.sha256(json.dumps({'epoch':epoch,'coordinator':winner['replica_id'],'eligible':[m['replica_id'] for m in active_members]},sort_keys=True).encode()).hexdigest()}
