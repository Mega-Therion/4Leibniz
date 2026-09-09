import json
from pathlib import Path

from coordinator.auto_ingest import slice_text, write_candidate
from coordinator.queue_manager import QueueManager
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from volunteer.protocol import JobType, WorkUnit, sign_work_unit


def test_slicer_and_candidate_header(tmp_path):
    text = " ".join(["Latin"] * 101)
    passages = slice_text(text, "analysis-situs-1679")
    assert len(passages) == 2
    target = write_candidate(passages[0], tmp_path, "LH XXXV, 1, 9", "Gerhardt vol. 5")
    content = target.read_text()
    assert "status: candidate-review" in content
    assert "normalization_policy: diplomatic-literal" in content


def test_queue_requires_three_matching_workers(tmp_path):
    """Three INDEPENDENT workers, evidenced by three distinct admitted keys.

    This test previously supplied three unsigned responses under three
    self-chosen worker_id strings and asserted "canonical" -- which encoded the
    Sybil hole as correct behaviour. Its name said "three matching workers", but
    nothing established that the three strings were three parties; one actor
    could satisfy it alone. See tests/test_consensus_sybil.py.

    Independence is now what the test actually supplies.
    """
    keys = {f"worker-{c}": Ed25519PrivateKey.generate() for c in "abc"}
    queue = QueueManager(tmp_path / "jobs.sqlite",
                         admitted_keys={w: k.public_key() for w, k in keys.items()})
    queue.enqueue("LH-001", JobType.HTR_TRANSCRIPTION, {"text": "Veritas"})
    job = queue.claim("worker-a")
    assert job["unit_id"] == "LH-001"

    response = {"text": "Veritas"}
    for worker, key in keys.items():
        signature = sign_work_unit(
            WorkUnit(unit_id="LH-001", kind="response", payload=response), key)
        queue.record_response("LH-001", worker, response, signature=signature)

    result = queue.consensus("LH-001")
    assert result["status"] == "canonical"
    assert result["agreement"] == 1.0
    assert result["distinct_verified_keys"] == 3
    queue.finalize("LH-001", result)
    assert queue.counts()["canonical"] == 1


def test_queue_rejects_unsigned_responses(tmp_path):
    """The behaviour the old version of the test above asserted must now fail."""
    queue = QueueManager(tmp_path / "jobs.sqlite")
    queue.enqueue("LH-002", JobType.HTR_TRANSCRIPTION, {"text": "Veritas"})
    for worker in ("worker-a", "worker-b", "worker-c"):
        queue.record_response("LH-002", worker, {"text": "Veritas"})
    assert queue.consensus("LH-002")["status"] != "canonical"
