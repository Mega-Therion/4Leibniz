"""SQLite queue, bounded leasing, and independent-response consensus."""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

JOB_TYPES = frozenset({"htr-transcription", "latin-translation", "bounded-proof-search", "lean4-proof-check"})

class QueueManager:
    def __init__(self, database: str | Path):
        self.database = str(database)
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', lease_owner TEXT, result TEXT, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS responses (job_id TEXT NOT NULL, worker_id TEXT NOT NULL, response TEXT NOT NULL, created_at REAL NOT NULL, PRIMARY KEY (job_id, worker_id));
            """)
    def _connect(self):
        db = sqlite3.connect(self.database)
        db.row_factory = sqlite3.Row
        return db
    def enqueue(self, unit_id: str, kind: str, payload: dict[str, Any]) -> None:
        if kind not in JOB_TYPES:
            raise ValueError(f"unknown job type: {kind}")
        with self._connect() as db:
            db.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, 'pending', NULL, NULL, ?)", (unit_id, kind, json.dumps(payload, sort_keys=True), time.time()))
    def claim(self, worker_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE status='pending' ORDER BY created_at LIMIT 1").fetchone()
            if row is None: return None
            db.execute("UPDATE jobs SET status='leased', lease_owner=? WHERE id=?", (worker_id, row['id']))
            return {"unit_id": row['id'], "kind": row['kind'], "payload": json.loads(row['payload'])}
    def record_response(self, job_id: str, worker_id: str, response: dict[str, Any]) -> None:
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?)", (job_id, worker_id, json.dumps(response, sort_keys=True), time.time()))
    def finalize(self, job_id: str, result: dict[str, Any]) -> None:
        with self._connect() as db:
            db.execute("UPDATE jobs SET status=?, result=? WHERE id=?", (result['status'], json.dumps(result, sort_keys=True), job_id))
    def counts(self) -> dict[str, int]:
        with self._connect() as db:
            return {row['status']: row['count'] for row in db.execute("SELECT status, COUNT(*) count FROM jobs GROUP BY status")}
    def consensus(self, job_id: str, minimum_workers: int = 3, threshold: float = 0.95) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT response FROM responses WHERE job_id=? ORDER BY worker_id", (job_id,)).fetchall()
        responses = [json.loads(row['response']) for row in rows]
        if len(responses) < minimum_workers:
            return {"status": "pending-review", "responses": len(responses), "reason": "minimum independent workers not reached"}
        texts = [str(r.get('text', '')) for r in responses]
        best = max(set(texts), key=texts.count)
        agreement = sum(1 for text in texts if text == best) / len(texts)
        return {"status": "canonical" if agreement >= threshold else "expert-review", "responses": len(responses), "agreement": agreement, "text": best if agreement >= threshold else None}

def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a 4Leibniz SQLite work queue")
    parser.add_argument("--database", default="coordinator/job_queue.sqlite")
    args = parser.parse_args()
    print(json.dumps(QueueManager(args.database).counts(), sort_keys=True))

if __name__ == "__main__":
    main()
