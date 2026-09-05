import json
from pathlib import Path

from coordinator.auto_ingest import slice_text, write_candidate
from coordinator.queue_manager import QueueManager
from volunteer.protocol import JobType


def test_slicer_and_candidate_header(tmp_path):
    text = " ".join(["Latin"] * 101)
    passages = slice_text(text, "analysis-situs-1679")
    assert len(passages) == 2
    target = write_candidate(passages[0], tmp_path, "LH XXXV, 1, 9", "Gerhardt vol. 5")
    content = target.read_text()
    assert "status: candidate-review" in content
    assert "normalization_policy: diplomatic-literal" in content


def test_queue_requires_three_matching_workers(tmp_path):
    queue = QueueManager(tmp_path / "jobs.sqlite")
    queue.enqueue("LH-001", JobType.HTR_TRANSCRIPTION, {"text": "Veritas"})
    job = queue.claim("worker-a")
    assert job["unit_id"] == "LH-001"
    for worker in ("worker-a", "worker-b", "worker-c"):
        queue.record_response("LH-001", worker, {"text": "Veritas"})
    result = queue.consensus("LH-001")
    assert result["status"] == "canonical"
    assert result["agreement"] == 1.0
    queue.finalize("LH-001", result)
    assert queue.counts()["canonical"] == 1
