"""Phase 9 durable ordered consensus log model.

The local implementation mirrors the invariants expected from a Durable Object:
monotone sequence numbers, hash-linked entries, idempotent recovery, and signed
snapshot metadata. It is not a substitute for a replicated consensus protocol.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json

@dataclass(frozen=True)
class LogEntry:
    sequence: int
    proposal_id: str
    payload: dict
    previous_hash: str
    entry_hash: str

def _digest(sequence, proposal_id, payload, previous_hash):
    body = json.dumps({'sequence':sequence,'proposal_id':proposal_id,'payload':payload,'previous_hash':previous_hash}, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(body.encode()).hexdigest()

class OrderedLog:
    def __init__(self, entries=()):
        self.entries = []
        self.recover(entries)
    @property
    def head(self): return self.entries[-1] if self.entries else None
    def append(self, proposal_id, payload, sequence=None):
        expected = len(self.entries) + 1
        if sequence is not None and sequence != expected: raise ValueError('sequence gap or replay')
        previous = self.head.entry_hash if self.head else '0' * 64
        digest = _digest(expected, proposal_id, payload, previous)
        entry = LogEntry(expected, proposal_id, payload, previous, digest)
        self.entries.append(entry); return entry
    def recover(self, entries):
        self.entries = []
        for raw in entries:
            item = raw if isinstance(raw, LogEntry) else LogEntry(**raw)
            expected = len(self.entries) + 1
            if item.sequence != expected: raise ValueError('non-contiguous log')
            expected_previous = self.entries[-1].entry_hash if self.entries else '0' * 64
            if item.previous_hash != expected_previous or item.entry_hash != _digest(item.sequence,item.proposal_id,item.payload,item.previous_hash): raise ValueError('corrupt log entry')
            self.entries.append(item)
    def snapshot(self):
        return {'last_sequence': len(self.entries), 'head_hash': self.head.entry_hash if self.head else '0'*64, 'entries': [asdict(e) for e in self.entries]}
    def to_json(self): return json.dumps(self.snapshot(), sort_keys=True)
