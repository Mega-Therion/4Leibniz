"""Turn verified local witness text into reviewable corpus fragments."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Passage:
    source_id: str
    sequence: int
    text: str
    sha256: str
    status: str = "candidate-review"

def slice_text(text: str, source_id: str, words_per_slice: int = 75) -> list[Passage]:
    if words_per_slice < 50 or words_per_slice > 100:
        raise ValueError("words_per_slice must be between 50 and 100")
    words = re.findall(r"\S+", text)
    passages = []
    for index in range(0, len(words), words_per_slice):
        chunk = " ".join(words[index:index + words_per_slice]).strip()
        if chunk:
            passages.append(Passage(source_id, index // words_per_slice + 1, chunk, hashlib.sha256(chunk.encode()).hexdigest()))
    return passages

def write_candidate(passage: Passage, output_dir: str | Path, shelfmark: str, edition: str, language: str = "la") -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{passage.source_id}.passage-{passage.sequence:04d}.{language}.md"
    header = f"""---\nsource_id: {passage.source_id}\nshelfmark: {shelfmark}\nsource_edition: {edition}\nlanguage: {language}\nnormalization_policy: diplomatic-literal\nstatus: {passage.status}\nsha256: {passage.sha256}\n---\n\n"""
    target.write_text(header + passage.text + "\n", encoding="utf-8")
    return target

def ingest_file(input_path: str | Path, source_id: str, output_dir: str | Path, shelfmark: str, edition: str) -> list[Path]:
    text = Path(input_path).read_text(encoding="utf-8")
    return [write_candidate(p, output_dir, shelfmark, edition) for p in slice_text(text, source_id)]

def main() -> None:
    parser = argparse.ArgumentParser(description="Slice a locally verified candidate witness")
    parser.add_argument("input")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--shelfmark", required=True)
    parser.add_argument("--edition", required=True)
    parser.add_argument("--output-dir", default="corpus/latin/candidates")
    args = parser.parse_args()
    paths = ingest_file(args.input, args.source_id, args.output_dir, args.shelfmark, args.edition)
    print(json.dumps({"passages": len(paths), "status": "candidate-review"}))

if __name__ == "__main__":
    main()
