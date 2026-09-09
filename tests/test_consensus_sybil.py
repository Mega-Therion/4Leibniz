"""Regression tests for the volunteer consensus Sybil hole.

The pipeline's stated safety property is that a transcription is promoted only
when "at least three independent responses agree exactly". Before this fix,
`minimum_workers` counted ROWS, and rows were keyed by a caller-supplied
`worker_id` string that nothing authenticated.
"""
from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from coordinator.queue_manager import QueueManager
from volunteer.protocol import WorkUnit, sign_work_unit


def _sign(job_id, response, private_key):
    return sign_work_unit(WorkUnit(unit_id=job_id, kind="response", payload=response), private_key)


def test_unsigned_sybil_cannot_reach_canonical(tmp_path):
    """The original attack, reproduced.

    Old behaviour, measured against the committed code: one actor submitting
    under three self-chosen worker_ids produced
    {"status": "canonical", "responses": 3, "agreement": 1.0,
     "text": "FORGED TEXT"}.
    """
    q = QueueManager(tmp_path / "q.sqlite")
    forged = {"status": "checked", "text": "FORGED TEXT"}
    for worker_id in ("alice", "bob", "carol"):
        q.record_response("j1", worker_id, forged)

    result = q.consensus("j1")
    assert result["status"] != "canonical"
    assert result["distinct_verified_keys"] == 0
    assert result["unverified_responses"] == 3


def test_one_key_under_many_ids_counts_once(tmp_path):
    """A holder of ONE admitted key cannot become three voices by renaming.

    Votes are keyed by a fingerprint of the public key, not by worker_id, so
    this collapses to a single response.
    """
    key = Ed25519PrivateKey.generate()
    admitted = {wid: key.public_key() for wid in ("d1", "d2", "d3")}
    q = QueueManager(tmp_path / "q.sqlite", admitted_keys=admitted)

    forged = {"status": "checked", "text": "FORGED TEXT"}
    signature = _sign("j2", forged, key)
    for worker_id in ("d1", "d2", "d3"):
        q.record_response("j2", worker_id, forged, signature=signature)

    result = q.consensus("j2")
    assert result["status"] != "canonical"
    assert result["distinct_verified_keys"] == 1


def test_three_distinct_admitted_keys_promote(tmp_path):
    """The fix must not simply block everything."""
    keys = {f"w{i}": Ed25519PrivateKey.generate() for i in range(3)}
    q = QueueManager(tmp_path / "q.sqlite",
                     admitted_keys={w: k.public_key() for w, k in keys.items()})

    agreed = {"status": "checked", "text": "Monas est substantia simplex."}
    for worker_id, key in keys.items():
        q.record_response("j3", worker_id, agreed, signature=_sign("j3", agreed, key))

    result = q.consensus("j3")
    assert result["status"] == "canonical"
    assert result["distinct_verified_keys"] == 3
    assert result["agreement"] == 1.0
    assert result["text"] == "Monas est substantia simplex."


def test_bad_signature_is_not_counted(tmp_path):
    """A signature from a key that was not admitted for this worker fails."""
    admitted_key = Ed25519PrivateKey.generate()
    attacker_key = Ed25519PrivateKey.generate()
    q = QueueManager(tmp_path / "q.sqlite", admitted_keys={"w0": admitted_key.public_key()})

    payload = {"status": "checked", "text": "x"}
    q.record_response("j4", "w0", payload, signature=_sign("j4", payload, attacker_key))

    assert q.consensus("j4")["distinct_verified_keys"] == 0


def test_tampered_response_fails_verification(tmp_path):
    """Signing one payload and submitting another must not verify."""
    key = Ed25519PrivateKey.generate()
    q = QueueManager(tmp_path / "q.sqlite", admitted_keys={"w0": key.public_key()})

    signature = _sign("j5", {"status": "checked", "text": "original"}, key)
    q.record_response("j5", "w0", {"status": "checked", "text": "TAMPERED"}, signature=signature)

    assert q.consensus("j5")["distinct_verified_keys"] == 0


def test_unsigned_responses_are_still_recorded(tmp_path):
    """Recording is not the same as counting; unsigned work is kept, not promoted."""
    q = QueueManager(tmp_path / "q.sqlite")
    q.record_response("j6", "w0", {"status": "checked", "text": "x"})
    assert q.consensus("j6")["unverified_responses"] == 1
