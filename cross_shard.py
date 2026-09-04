"""Phase 10 cross-shard atomic commit and state synchronization reference model."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, time
from durable_log import OrderedLog

def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
@dataclass(frozen=True)
class TxReceipt:
    txid: str
    phase: str
    participants: tuple[str, ...]
    prepared: tuple[str, ...]
    committed: tuple[str, ...]
    aborted: tuple[str, ...]
    reason: str = ''
    receipt: str = ''

class Shard:
    def __init__(self, shard_id, initial=None):
        self.shard_id=shard_id; self.state=dict(initial or {}); self.log=OrderedLog(); self.prepared={}
    def prepare(self, txid, writes):
        if txid in self.prepared: return self.prepared[txid]['digest']==digest(writes)
        if any(k not in self.state and v is None for k,v in writes.items()): return False
        self.prepared[txid]={'writes':dict(writes),'digest':digest(writes),'phase':'prepared'}; return True
    def commit(self, txid):
        item=self.prepared.get(txid)
        if not item: return False
        self.state.update(item['writes']); self.log.append(txid, {'writes':item['writes'],'phase':'commit'}); item['phase']='committed'; return True
    def abort(self, txid):
        item=self.prepared.get(txid)
        if item: item['phase']='aborted'
        return True
    def snapshot(self): return {'shard_id':self.shard_id,'state':dict(self.state),'log':self.log.snapshot(),'state_hash':digest(self.state)}
    def sync(self, snapshot):
        if snapshot.get('shard_id') != self.shard_id: raise ValueError('wrong shard')
        recovered=OrderedLog(snapshot['log']['entries'])
        if digest(snapshot.get('state',{})) != snapshot.get('state_hash'): raise ValueError('state hash mismatch')
        self.state=dict(snapshot.get('state',{})); self.log=recovered; self.prepared={}; return self.snapshot()

def atomic_commit(txid, shards, writes_by_shard, reachable=None):
    reachable=set(shards) if reachable is None else set(reachable); ids=tuple(shards); prepared=[]
    for sid in ids:
        if sid not in reachable or not shards[sid].prepare(txid,writes_by_shard.get(sid,{})):
            for p in prepared: shards[p].abort(txid)
            return asdict(TxReceipt(txid,'aborted',ids,tuple(prepared),(),tuple(prepared),'partition or prepare failure',digest({'txid':txid,'phase':'aborted','prepared':prepared})))
        prepared.append(sid)
    committed=[]
    for sid in ids:
        if sid not in reachable: return asdict(TxReceipt(txid,'in_doubt',ids,tuple(prepared),tuple(committed),tuple(), 'partition during commit', digest({'txid':txid,'phase':'in_doubt','prepared':prepared})))
        shards[sid].commit(txid); committed.append(sid)
    return asdict(TxReceipt(txid,'committed',ids,tuple(prepared),tuple(committed),(),'',digest({'txid':txid,'phase':'committed','committed':committed})))

def recover_in_doubt(txid, shards, decision):
    if decision not in ('commit','abort'): raise ValueError('invalid coordinator decision')
    changed=[]
    for shard in shards.values():
        if txid in shard.prepared:
            (shard.commit if decision=='commit' else shard.abort)(txid); changed.append(shard.shard_id)
    return {'txid':txid,'decision':decision,'resolved_shards':changed,'receipt':digest({'txid':txid,'decision':decision,'resolved':changed})}
