"""Safe local execution for one explicitly supplied work unit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .protocol import WorkUnit

ALLOWED_KINDS = frozenset({"transcription-check", "proof-check"})


def execute(unit: WorkUnit, root: str | Path = ".") -> dict[str, Any]:
    """Execute only deterministic, bounded checks; never eval arbitrary payload code."""
    if unit.kind not in ALLOWED_KINDS:
        raise ValueError(f"unsupported work-unit kind: {unit.kind}")
    payload = unit.payload
    if unit.kind == "transcription-check":
        text = str(payload.get("text", ""))
        return {"unit_id": unit.unit_id, "digest": hashlib.sha256(text.encode()).hexdigest(), "characters": len(text)}
    path = Path(root, str(payload.get("path", ""))).resolve()
    root_path = Path(root).resolve()
    if root_path not in path.parents and path != root_path:
        raise ValueError("proof path escapes worker root")
    if path.suffix != ".lean" or not path.is_file():
        raise ValueError("proof-check requires an existing .lean file inside worker root")
    source = path.read_text(encoding="utf-8")
    return {"unit_id": unit.unit_id, "digest": hashlib.sha256(source.encode()).hexdigest(), "bytes": len(source.encode())}


def run_json(work_unit_json: str, root: str = ".") -> str:
    raw = json.loads(work_unit_json)
    unit = WorkUnit(**raw)
    return json.dumps(execute(unit, root), sort_keys=True)
