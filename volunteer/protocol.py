"""Versioned, signed work units for transcription, translation, and proof tasks."""
from __future__ import annotations
import base64
import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any
PROTOCOL_VERSION = 1
class JobType:
    HTR_TRANSCRIPTION = "htr-transcription"
    LATIN_TRANSLATION = "latin-translation"
    BOUNDED_PROOF_SEARCH = "bounded-proof-search"
    LEAN4_PROOF_CHECK = "lean4-proof-check"
ALLOWED_JOB_TYPES = frozenset((JobType.HTR_TRANSCRIPTION, JobType.LATIN_TRANSLATION, JobType.BOUNDED_PROOF_SEARCH, JobType.LEAN4_PROOF_CHECK))
@dataclass(frozen=True)
class WorkUnit:
    unit_id: str
    kind: str
    payload: dict[str, Any]
    schema_version: int = PROTOCOL_VERSION
    def canonical_bytes(self) -> bytes:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
    def digest(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()
def sign_work_unit(unit: WorkUnit, private_key: Any) -> str:
    return base64.urlsafe_b64encode(private_key.sign(unit.canonical_bytes())).decode("ascii")
def verify_work_unit(unit: WorkUnit, signature: str, public_key: Any) -> bool:
    try:
        public_key.verify(base64.urlsafe_b64decode(signature.encode("ascii")), unit.canonical_bytes())
        return True
    except Exception:
        return False
def to_json(unit: WorkUnit) -> str:
    return json.dumps(asdict(unit), sort_keys=True, indent=2)
