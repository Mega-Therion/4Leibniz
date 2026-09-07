"""Phase 7 signed envelopes and replay protection.

Signatures authenticate canonical content; ReplayGuard additionally enforces a
freshness window and one-time nonce use. These controls do not establish proof truth.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import base64, hashlib, json, os, sqlite3, time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

def _b64(data: bytes) -> str: return base64.urlsafe_b64encode(data).decode().rstrip('=')
def _unb64(text: str) -> bytes: return base64.urlsafe_b64decode(text + '=' * (-len(text) % 4))
def canonical(payload: dict) -> bytes: return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()

@dataclass(frozen=True)
class SignedProposal:
    node_id: str
    payload: dict
    public_key: str
    signature: str
    digest: str
    timestamp: int = 0
    nonce: str = ""

class ReplayGuard:
    """Tracks seen (node_id, nonce) pairs within a freshness window.

    Default storage is an in-process dict, which is lost on restart -- flagged
    as B-05 in the 2026-09-07 release assessment. Passing `db_path` switches
    to a SQLite-backed table so the window survives a process restart on a
    single node. That is still not the multi-node, transactional store a
    clustered deployment needs (see docs/PRODUCTION_READINESS.md, Phase 3);
    it closes the "state vanishes on redeploy" gap for a single instance.
    """
    def __init__(self, max_age_seconds: int = 300, db_path: str | None = None):
        self.max_age_seconds = max_age_seconds
        self._seen: dict[str, int] = {}
        self._db: sqlite3.Connection | None = None
        if db_path:
            self._db = sqlite3.connect(db_path, check_same_thread=False)
            self._db.execute('CREATE TABLE IF NOT EXISTS replay_seen (key TEXT PRIMARY KEY, seen_at INTEGER NOT NULL)')
            self._db.commit()

    def accept(self, node_id: str, nonce: str, timestamp: int, now: int | None = None) -> bool:
        now = int(time.time()) if now is None else int(now)
        key = f'{node_id}:{nonce}'
        if not nonce or abs(now - int(timestamp)) > self.max_age_seconds:
            return False
        if self._db is not None:
            self._db.execute('DELETE FROM replay_seen WHERE ? - seen_at > ?', (now, self.max_age_seconds))
            if self._db.execute('SELECT 1 FROM replay_seen WHERE key = ?', (key,)).fetchone() is not None:
                self._db.commit()
                return False
            self._db.execute('INSERT INTO replay_seen (key, seen_at) VALUES (?, ?)', (key, now))
            self._db.commit()
            return True
        self._seen = {k: v for k, v in self._seen.items() if now - v <= self.max_age_seconds}
        if key in self._seen:
            return False
        self._seen[key] = now
        return True

@dataclass(frozen=True)
class PrivatePremiseCommitment:
    commitment: str
    statement_digest: str
    protocol: str = 'phase5-commitment-boundary'
    verified: bool = False
    note: str = 'Commitment is not a zero-knowledge proof; replace verifier with an audited circuit.'

def generate_keypair() -> tuple[str, str]:
    private = Ed25519PrivateKey.generate()
    return (_b64(private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())),
            _b64(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)))

def sign_proposal(node_id: str, payload: dict, private_key: str, timestamp: int | None = None, nonce: str | None = None) -> SignedProposal:
    timestamp = int(time.time()) if timestamp is None else int(timestamp)
    nonce = nonce or _b64(os.urandom(16))
    envelope = {'node_id': node_id, 'payload': payload, 'timestamp': timestamp, 'nonce': nonce}
    message = canonical(envelope)
    private = Ed25519PrivateKey.from_private_bytes(_unb64(private_key))
    return SignedProposal(node_id, payload,
        _b64(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)),
        _b64(private.sign(message)), hashlib.sha256(message).hexdigest(), timestamp, nonce)

def verify_proposal(proposal: SignedProposal) -> bool:
    try:
        envelope = {'node_id': proposal.node_id, 'payload': proposal.payload, 'timestamp': proposal.timestamp, 'nonce': proposal.nonce}
        message = canonical(envelope)
        Ed25519PublicKey.from_public_bytes(_unb64(proposal.public_key)).verify(_unb64(proposal.signature), message)
        return proposal.digest == hashlib.sha256(message).hexdigest()
    except Exception:
        return False

def verify_fresh_proposal(proposal: SignedProposal, guard: ReplayGuard, now: int | None = None) -> bool:
    return verify_proposal(proposal) and guard.accept(proposal.node_id, proposal.nonce, proposal.timestamp, now)

def commit_private_premise(statement: str, nonce: bytes | None = None) -> PrivatePremiseCommitment:
    nonce = nonce or os.urandom(32)
    return PrivatePremiseCommitment(hashlib.sha256(nonce + statement.encode()).hexdigest(), hashlib.sha256(statement.encode()).hexdigest())
def receipt_json(receipt) -> dict: return asdict(receipt)
