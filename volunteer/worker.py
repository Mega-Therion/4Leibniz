"""Safe local execution for bounded, allow-listed work units."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
from .protocol import ALLOWED_JOB_TYPES, JobType, WorkUnit
ALLOWED_KINDS = frozenset({"transcription-check", "proof-check", *ALLOWED_JOB_TYPES})
def _file_digest(path_value: str, root: str | Path) -> tuple[str, int]:
    path = Path(root, path_value).resolve(); root_path = Path(root).resolve()
    if root_path not in path.parents and path != root_path: raise ValueError("proof path escapes worker root")
    if path.suffix != ".lean" or not path.is_file(): raise ValueError("proof work requires an existing .lean file inside worker root")
    content = path.read_bytes(); return hashlib.sha256(content).hexdigest(), len(content)
def execute(unit: WorkUnit, root: str | Path = ".") -> dict[str, Any]:
    if unit.kind not in ALLOWED_KINDS: raise ValueError(f"unsupported work-unit kind: {unit.kind}")
    payload = unit.payload
    if unit.kind in {"transcription-check", JobType.HTR_TRANSCRIPTION}:
        text = str(payload.get("text", ""))
        return {"unit_id": unit.unit_id, "text": text, "digest": hashlib.sha256(text.encode()).hexdigest(), "characters": len(text), "status": "candidate-review"}
    if unit.kind == JobType.LATIN_TRANSLATION:
        return {"unit_id": unit.unit_id, "status": "expert-review", "reason": "no translation model is executed implicitly"}
    if unit.kind == JobType.BOUNDED_PROOF_SEARCH:
        return {"unit_id": unit.unit_id, "status": "expert-review", "reason": "bounded proof search requires an explicit trusted runner"}
    digest, size = _file_digest(str(payload.get("path", "")), root)
    return {"unit_id": unit.unit_id, "digest": digest, "bytes": size, "status": "checked"}
def run_json(work_unit_json: str, root: str = ".") -> str:
    raw = json.loads(work_unit_json); return json.dumps(execute(WorkUnit(**raw), root), sort_keys=True)
