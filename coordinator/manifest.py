from __future__ import annotations
import hashlib, json
from pathlib import Path

def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def register_download(manifest_path: str | Path, source_id: str, local_path: str | Path, source_url: str, role: str = "candidate") -> dict:
    path = Path(manifest_path); data = json.loads(path.read_text(encoding="utf-8")); artifact = {"local_path": str(local_path), "source_url": source_url, "sha256": sha256_file(local_path), "role": role}
    for source in data["sources"]:
        if source["id"] == source_id:
            source.setdefault("downloads", []).append(artifact); source["status"] = "candidate-downloaded"
            break
    else: raise KeyError(source_id)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return artifact
