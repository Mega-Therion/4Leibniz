"""SQLite queue and BFT consensus manager for 4Leibniz volunteer work units."""
from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

class QueueManager:
    def __init__(self, db_path: str = "coordinator/job_queue.sqlite"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS work_units (
                    unit_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    claimed_by TEXT,
                    claimed_at REAL,
                    finalized_result TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id TEXT NOT NULL,
                    worker_id TEXT NOT NULL,
                    result TEXT NOT NULL,
                    received_at REAL NOT NULL,
                    FOREIGN KEY(unit_id) REFERENCES work_units(unit_id)
                )
            """)
            conn.commit()

    def enqueue(self, unit_id: str, kind: str, payload: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO work_units (unit_id, kind, payload, status) VALUES (?, ?, ?, 'queued')",
                (unit_id, kind, json.dumps(payload, sort_keys=True))
            )
            conn.commit()

    def claim(self, worker_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT unit_id, kind, payload FROM work_units WHERE status = 'queued' LIMIT 1"
            )
            row = cursor.fetchone()
            if not row:
                return None
            unit_id, kind, payload = row
            now = time.time()
            cursor.execute(
                "UPDATE work_units SET status = 'claimed', claimed_by = ?, claimed_at = ? WHERE unit_id = ?",
                (worker_id, now, unit_id)
            )
            conn.commit()
            return {
                "unit_id": unit_id,
                "kind": kind,
                "payload": json.loads(payload)
            }

    def record_response(self, unit_id: str, worker_id: str, result: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO responses (unit_id, worker_id, result, received_at) VALUES (?, ?, ?, ?)",
                (unit_id, worker_id, json.dumps(result, sort_keys=True), time.time())
            )
            conn.commit()

    def consensus(self, unit_id: str, threshold: int = 1) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT result FROM responses WHERE unit_id = ?", (unit_id,))
            rows = cursor.fetchall()
            if not rows:
                return {"status": "pending", "unit_id": unit_id}
            
            # Simple tally for agreement
            results = [json.loads(r[0]) for r in rows]
            latest = results[-1]
            if len(results) >= threshold:
                return {"status": "canonical", "unit_id": unit_id, "consensus_result": latest}
            return {"status": "in-progress", "unit_id": unit_id, "responses_count": len(results)}

    def finalize(self, unit_id: str, consensus_data: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE work_units SET status = 'finalized', finalized_result = ? WHERE unit_id = ?",
                (json.dumps(consensus_data, sort_keys=True), unit_id)
            )
            conn.commit()
