"""Phase 9 signed peer admission policy."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, time
from security import SignedProposal, verify_proposal
@dataclass(frozen=True)
class PeerRecord:
    node_id: str
    public_key: str
    capabilities: tuple[str, ...] = ()
    weight: int = 1
    admitted_at: int = 0
    expires_at: int = 0
    revoked: bool = False

def receipt(record): return hashlib.sha256(json.dumps(asdict(record),sort_keys=True).encode()).hexdigest()
def admit(proposal: SignedProposal, capabilities=(), weight=1, ttl=86400, now=None):
    now = int(time.time()) if now is None else int(now)
    if not verify_proposal(proposal) or proposal.payload.get('kind') != 'peer_admission': return {'accepted':False,'reason':'invalid signed admission'}
    if proposal.payload.get('node_id') != proposal.node_id: return {'accepted':False,'reason':'identity mismatch'}
    record = PeerRecord(proposal.node_id, proposal.public_key, tuple(sorted(capabilities)), max(1,int(weight)), now, now+int(ttl), False)
    return {'accepted':True,'record':asdict(record),'receipt':receipt(record)}
def is_active(record, now=None):
    now = int(time.time()) if now is None else int(now)
    return bool(record and not record.get('revoked') and record.get('admitted_at',0) <= now < record.get('expires_at',0))
def revoke(record, reason='governance decision'):
    updated = dict(record); updated['revoked']=True; updated['revocation_reason']=reason; updated['receipt']=receipt(PeerRecord(updated['node_id'],updated['public_key'],tuple(updated.get('capabilities',())),updated.get('weight',1),updated.get('admitted_at',0),updated.get('expires_at',0),True)); return updated
