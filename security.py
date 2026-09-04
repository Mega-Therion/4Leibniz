"""Phase 7 signed envelopes and replay protection.

Signatures authenticate canonical content; ReplayGuard additionally enforces a
freshness window and one-time nonce use. These controls do not establish proof truth.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import base64, hashlib, json, os, time
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
    def __init__(self, max_age_seconds: int = 300):
        self.max_age_seconds = max_age_seconds
        self._seen: dict[str, int] = {}
    def accept(self, node_id: str, nonce: str, timestamp: int, now: int | None = None) -> bool:
        now = int(time.time()) if now is None else int(now)
        self._seen = {k: v for k, v in self._seen.items() if now - v <= self.max_age_seconds}
        key = f'{node_id}:{nonce}'
        if not nonce or abs(now - int(timestamp)) > self.max_age_seconds or key in self._seen:
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
