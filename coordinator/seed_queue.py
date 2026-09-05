from __future__ import annotations
import argparse, json
from pathlib import Path
from .auto_ingest import slice_text
from .queue_manager import QueueManager
from volunteer.protocol import JobType

def seed(input_path: str, database: str, source_id: str, limit: int = 0) -> int:
    passages = slice_text(Path(input_path).read_text(encoding="utf-8"), source_id)
    if limit: passages = passages[:limit]
    queue = QueueManager(database)
    for passage in passages:
        queue.enqueue(f"{source_id}-{passage.sequence:04d}", JobType.HTR_TRANSCRIPTION, {"text": passage.text, "sha256": passage.sha256})
    return len(passages)

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("input"); parser.add_argument("--database", default="coordinator/job_queue.sqlite"); parser.add_argument("--source-id", required=True); parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args(); print(json.dumps({"generated": seed(args.input, args.database, args.source_id, args.limit)}))
if __name__ == "__main__": main()
