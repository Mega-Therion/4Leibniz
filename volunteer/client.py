"""One-shot or bounded daemon volunteer client."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
try:
    from .protocol import WorkUnit
    from .worker import execute, run_json
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from volunteer.protocol import WorkUnit
    from volunteer.worker import execute, run_json

def process_once(database: str, worker_id: str, root: str = ".") -> dict:
    from coordinator.queue_manager import QueueManager
    queue = QueueManager(database); job = queue.claim(worker_id)
    if job is None: return {"status": "idle", "processed": 0}
    result = execute(WorkUnit(job["unit_id"], job["kind"], job["payload"]), root)
    queue.record_response(job["unit_id"], worker_id, result)
    consensus = queue.consensus(job["unit_id"])
    if consensus["status"] in {"canonical", "expert-review"}:
        queue.finalize(job["unit_id"], consensus)
    return {"status": "processed", "processed": 1, "unit_id": job["unit_id"], "result": result, "consensus": consensus}

def main() -> None:
    parser = argparse.ArgumentParser(description="Run one work unit or a bounded 4Leibniz queue daemon")
    parser.add_argument("work_unit", nargs="?", type=Path)
    parser.add_argument("--root", default="."); parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--database", default="coordinator/job_queue.sqlite"); parser.add_argument("--worker-id", default="local-worker")
    parser.add_argument("--max-jobs", type=int, default=1); parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if args.daemon:
        for _ in range(max(0, args.max_jobs)):
            result = process_once(args.database, args.worker_id, args.root); print(json.dumps(result, sort_keys=True), flush=True)
            if result["status"] == "idle": break
            if args.interval: time.sleep(args.interval)
    else:
        if args.work_unit is None: parser.error("work_unit is required unless --daemon is used")
        print(run_json(args.work_unit.read_text(encoding="utf-8"), args.root))
if __name__ == "__main__": main()
