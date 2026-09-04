"""Phase 5 cryptographic collaboration primitives.

Ed25519 signing is production-grade message authentication when keys are managed
safely. The private-premise object is a commitment and transcript boundary, not
an implemented zero-knowledge proof system; a real deployment must replace its
placeholder verifier with a reviewed SNARK/STARK or Sigma-protocol circuit.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import base64, hashlib, json, os
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

@dataclass(frozen=True)
class PrivatePremiseCommitment:
    commitment: str
    statement_digest: str
    protocol: str = 'phase5-commitment-boundary'
    verified: bool = False
    note: str = 'Commitment is not a zero-knowledge proof; replace verifier with an audited circuit.'

def generate_keypair() -> tuple[str, str]:
    private = Ed25519PrivateKey.generate()
    private_bytes = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    public_bytes = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return _b64(private_bytes), _b64(public_bytes)

def sign_proposal(node_id: str, payload: dict, private_key: str) -> SignedProposal:
    private = Ed25519PrivateKey.from_private_bytes(_unb64(private_key))
    message = canonical(payload)
    signature = private.sign(message)
    public_key = _b64(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))
    return SignedProposal(node_id, payload, public_key, _b64(signature), hashlib.sha256(message).hexdigest())

def verify_proposal(proposal: SignedProposal) -> bool:
    try:
        Ed25519PublicKey.from_public_bytes(_unb64(proposal.public_key)).verify(_unb64(proposal.signature), canonical(proposal.payload))
        return proposal.digest == hashlib.sha256(canonical(proposal.payload)).hexdigest()
    except Exception:
        return False

def commit_private_premise(statement: str, nonce: bytes | None = None) -> PrivatePremiseCommitment:
    nonce = nonce or os.urandom(32)
    statement_digest = hashlib.sha256(statement.encode()).hexdigest()
    commitment = hashlib.sha256(nonce + statement.encode()).hexdigest()
    return PrivatePremiseCommitment(commitment, statement_digest)

def receipt_json(receipt) -> dict: return asdict(receipt)
