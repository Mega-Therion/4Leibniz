import json
from coordinator.manifest import register_download

def test_register_download_records_hash_and_role(tmp_path):
    raw = tmp_path / "source.txt"; raw.write_text("candidate", encoding="utf-8")
    manifest = tmp_path / "manifest.json"; manifest.write_text(json.dumps({"sources": [{"id": "x", "status": "candidate-only"}]}))
    artifact = register_download(manifest, "x", raw, "https://archive.org/download/x/source.txt", "mixed-ocr-and-translation")
    saved = json.loads(manifest.read_text())
    assert artifact["sha256"]
    assert saved["sources"][0]["status"] == "candidate-downloaded"
    assert saved["sources"][0]["downloads"][0]["role"] == "mixed-ocr-and-translation"
