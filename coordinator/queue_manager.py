"""SQLite queue, bounded leasing, and independent-response consensus."""
from __future__ import annotations
import argparse, json, sqlite3, time
from pathlib import Path
from typing import Any
JOB_TYPES = frozenset({"htr-transcription", "latin-translation", "bounded-proof-search", "lean4-proof-check"})
class QueueManager:
    def __init__(self, database: str | Path, admitted_keys: dict[str, Any] | None = None):
        """Create a queue.

        `admitted_keys` maps worker_id -> Ed25519 public key, normally sourced
        from `peer_admission`. When supplied, a response is only counted toward
        consensus if it carries a signature that verifies against the key
        admitted for that worker.

        When it is NOT supplied, responses are still recorded but are stored
        with `verified_key = NULL`, and `consensus()` refuses to promote them.
        That is deliberate: the previous design counted rows keyed by a
        caller-supplied worker_id string with no authentication anywhere, so one
        actor submitting under three self-chosen ids drove arbitrary text to
        status "canonical" at agreement 1.0. Reproduced against the committed
        code before this change.
        """
        self.database = str(database); Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self.admitted_keys = dict(admitted_keys or {})
        with self._connect() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', lease_owner TEXT, result TEXT, created_at REAL NOT NULL); CREATE TABLE IF NOT EXISTS responses (job_id TEXT NOT NULL, worker_id TEXT NOT NULL, response TEXT NOT NULL, created_at REAL NOT NULL, verified_key TEXT, PRIMARY KEY (job_id, worker_id));""")
            # Older databases predate verified_key; add it rather than requiring a rebuild.
            cols = {r["name"] for r in db.execute("PRAGMA table_info(responses)")}
            if "verified_key" not in cols:
                db.execute("ALTER TABLE responses ADD COLUMN verified_key TEXT")
    def _connect(self):
        db = sqlite3.connect(self.database); db.row_factory = sqlite3.Row; return db
    def enqueue(self, unit_id: str, kind: str, payload: dict[str, Any]) -> None:
        if kind not in JOB_TYPES: raise ValueError(f"unknown job type: {kind}")
        with self._connect() as db: db.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, 'pending', NULL, NULL, ?)", (unit_id, kind, json.dumps(payload, sort_keys=True), time.time()))
    def claim(self, worker_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE status='pending' ORDER BY created_at LIMIT 1").fetchone()
            if row is None: return None
            db.execute("UPDATE jobs SET status='leased', lease_owner=? WHERE id=?", (worker_id, row['id']))
            return {"unit_id": row['id'], "kind": row['kind'], "payload": json.loads(row['payload'])}
    def requeue_unfinalized(self) -> int:
        with self._connect() as db:
            result = db.execute("UPDATE jobs SET status='pending', lease_owner=NULL WHERE status='leased'")
            return result.rowcount
    def record_response(self, job_id: str, worker_id: str, response: dict[str, Any],
                        signature: str | None = None) -> None:
        """Record a worker's response, verifying its signature when possible.

        The response is stored either way. What a signature buys is the right to
        COUNT toward consensus: `verified_key` is set only when the signature
        verifies against the key admitted for this worker, and `consensus()`
        counts distinct verified keys rather than rows.

        A worker_id is a self-chosen string. Treating it as an identity is what
        made the previous consensus Sybil-open.
        """
        verified_key: str | None = None
        if signature is not None and worker_id in self.admitted_keys:
            from volunteer.protocol import WorkUnit, verify_work_unit
            unit = WorkUnit(unit_id=job_id, kind="response", payload=response)
            if verify_work_unit(unit, signature, self.admitted_keys[worker_id]):
                verified_key = self._key_fingerprint(worker_id)
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?, ?)",
                       (job_id, worker_id, json.dumps(response, sort_keys=True), time.time(), verified_key))

    def _key_fingerprint(self, worker_id: str) -> str:
        """Stable identifier for an admitted key.

        Deliberately derived from the KEY, not the worker_id, so two ids backed
        by the same key collapse to one voice.
        """
        from hashlib import sha256
        key = self.admitted_keys[worker_id]
        try:
            from cryptography.hazmat.primitives import serialization
            raw = key.public_bytes(encoding=serialization.Encoding.Raw,
                                   format=serialization.PublicFormat.Raw)
        except Exception:
            raw = repr(key).encode()
        return sha256(raw).hexdigest()[:32]
    def finalize(self, job_id: str, result: dict[str, Any]) -> None:
        with self._connect() as db: db.execute("UPDATE jobs SET status=?, result=? WHERE id=?", (result['status'], json.dumps(result, sort_keys=True), job_id))
    def counts(self) -> dict[str, int]:
        with self._connect() as db: return {row['status']: row['count'] for row in db.execute("SELECT status, COUNT(*) count FROM jobs GROUP BY status")}
    def consensus(self, job_id: str, minimum_workers: int = 3, threshold: float = 0.95) -> dict[str, Any]:
        """Decide whether a job's responses agree well enough to promote.

        Counts DISTINCT VERIFIED KEYS, not rows. Unsigned responses -- or ones
        whose signature did not verify -- are recorded but can never reach
        "canonical", however many of them arrive.

        Before this, `minimum_workers` counted rows keyed by a caller-supplied
        worker_id with no authentication. Reproduced against the committed code:
        one actor submitting under three self-chosen ids produced
        {"status": "canonical", "responses": 3, "agreement": 1.0,
         "text": "FORGED TEXT"}.
        """
        with self._connect() as db:
            rows = db.execute(
                "SELECT response, worker_id, verified_key FROM responses WHERE job_id=? ORDER BY worker_id",
                (job_id,)).fetchall()

        verified_rows = [r for r in rows if r["verified_key"]]
        unverified_count = len(rows) - len(verified_rows)

        # One vote per KEY. Two worker_ids sharing a key are one voice.
        by_key: dict[str, Any] = {}
        for r in verified_rows:
            by_key.setdefault(r["verified_key"], json.loads(r["response"]))
        responses = list(by_key.values())

        if len(responses) < minimum_workers:
            return {"status": "pending-review",
                    "responses": len(responses),
                    "distinct_verified_keys": len(by_key),
                    "unverified_responses": unverified_count,
                    "reason": ("minimum independent workers not reached; only signatures "
                               "verified against admitted keys are counted")}
        if any(response.get("status") == "candidate-review" for response in responses): return {"status": "expert-review", "responses": len(responses), "reason": "candidate OCR requires philological review before promotion"}
        texts = [str(response.get('text', '')) for response in responses]
        best = max(set(texts), key=texts.count)
        agreement = sum(1 for text in texts if text == best) / len(texts)
        return {"status": "canonical" if agreement >= threshold else "expert-review",
                "responses": len(responses),
                "distinct_verified_keys": len(by_key),
                "unverified_responses": unverified_count,
                "agreement": agreement,
                "text": best if agreement >= threshold else None}
def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect or requeue a 4Leibniz SQLite work queue"); parser.add_argument("--database", default="coordinator/job_queue.sqlite"); parser.add_argument("--requeue-leased", action="store_true"); args = parser.parse_args(); queue = QueueManager(args.database)
    if args.requeue_leased: print(json.dumps({"requeued": queue.requeue_unfinalized()}))
    print(json.dumps(queue.counts(), sort_keys=True))
if __name__ == "__main__": main()
