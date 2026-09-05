"""Versioned, signed work units for volunteer transcription/proof tasks."""
from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

PROTOCOL_VERSION = 1

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
    """Return a URL-safe Ed25519 signature; the key object is supplied by the caller."""
    signature = private_key.sign(unit.canonical_bytes())
    return base64.urlsafe_b64encode(signature).decode("ascii")


def verify_work_unit(unit: WorkUnit, signature: str, public_key: Any) -> bool:
    try:
        public_key.verify(base64.urlsafe_b64decode(signature.encode("ascii")), unit.canonical_bytes())
        return True
    except Exception:
        return False


def to_json(unit: WorkUnit) -> str:
    return json.dumps(asdict(unit), sort_keys=True, indent=2)
