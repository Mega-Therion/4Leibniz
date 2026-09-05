"""Discover and download archival candidates without silently canonizing them."""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ARCHIVE_API = "https://archive.org/advancedsearch.php"
ALLOWED_HOSTS = {"archive.org", "ia801*.us.archive.org", "gallica.bnf.fr"}

@dataclass(frozen=True)
class SourceSpec:
    id: str
    title: str
    shelfmark: str
    edition: str
    query: str
    language: str = "la"

PRIORITY_SOURCES = (
    SourceSpec("analysis-situs-1679", "Analysis situs", "LH XXXV, 1, 9", "Gerhardt, vol. 5, pp. 139–183", "Leibniz Analysis situs Gerhardt"),
    SourceSpec("initia-rerum-mathematicarum-metaphysica-1715", "Initia rerum mathematicarum metaphysica", "LH XXXV, 1, 15", "Gerhardt, vol. 7, pp. 17–29", "Leibniz Initia rerum mathematicarum metaphysica"),
    SourceSpec("de-progressione-dyadica-1679", "De progressione dyadica", "LH XXXV, 3, 2", "Gerhardt, vol. 5", "Leibniz De progressione dyadica"),
)

def _json_get(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "4Leibniz/1.0 archival-harvester"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def discover_archive(spec: SourceSpec, rows: int = 20) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"q": spec.query, "fl[]": ["identifier", "title", "year", "mediatype"], "rows": rows, "output": "json"}, doseq=True)
    data = _json_get(f"{ARCHIVE_API}?{params}")
    return data.get("response", {}).get("docs", [])

def harvest_manifest(output: str | Path, sources: tuple[SourceSpec, ...] = PRIORITY_SOURCES) -> dict[str, Any]:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for spec in sources:
        try:
            candidates = discover_archive(spec)
            error = None
        except Exception as exc:
            candidates, error = [], str(exc)
        records.append({**asdict(spec), "candidates": candidates, "error": error, "status": "candidate-only"})
    manifest = {"schema": "4leibniz.harvest.v1", "policy": "Network discoveries are candidates until a human verifies a witness.", "sources": records}
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest

def hash_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description="Discover public archival candidates for 4Leibniz")
    parser.add_argument("--output", default="coordinator/harvest_manifest.json")
    args = parser.parse_args()
    manifest = harvest_manifest(args.output)
    print(json.dumps({"sources": len(manifest["sources"]), "output": args.output}, indent=2))

if __name__ == "__main__":
    main()
