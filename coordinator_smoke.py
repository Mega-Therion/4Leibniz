"""Run a bounded local pipeline smoke test without mutating canonical corpus files."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from coordinator.auto_ingest import slice_text, write_candidate
from coordinator.harvester import harvest_manifest
from coordinator.queue_manager import QueueManager
from volunteer.protocol import JobType

def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp); manifest = harvest_manifest(root / "harvest_manifest.json")
        passage = slice_text(" " .join(["Veritas"] * 60), "smoke-source")[0]
        candidate = write_candidate(passage, root / "candidates", "SMOKE", "local fixture")
        queue = QueueManager(root / "jobs.sqlite"); queue.enqueue("SMOKE-001", JobType.HTR_TRANSCRIPTION, {"text": passage.text})
        job = queue.claim("smoke-worker")
        result = {"discovered_sources": len(manifest["sources"]), "candidate_file": str(candidate), "claimed_job": job["unit_id"], "queue_counts": queue.counts()}
        print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
