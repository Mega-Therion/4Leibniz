"""Analyze candidate OCR conservatively; output is never canonical corpus text."""
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path

BINARY_RE = re.compile(r"(?<![A-Za-z0-9])([01](?:\s*[01]){2,})(?:\s+)(\d{1,4})(?!\d)")

def normalize_bits(raw: str) -> str:
    return re.sub(r"\s+", "", raw)

def binary_rows(lines: list[str], start: int, end: int) -> list[dict]:
    rows = []
    for number, line in enumerate(lines[start - 1:end], start):
        for match in BINARY_RE.finditer(line):
            bits, decimal = normalize_bits(match.group(1)), int(match.group(2))
            value = int(bits, 2)
            rows.append({"line": number, "binary": bits, "claimed_decimal": decimal, "computed_decimal": value, "consistent": value == decimal})
    return rows

def analyze(path: Path, start: int = 23, end: int = 760) -> dict:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = lines[start - 1:end]
    text = "\n".join(selected)
    replacement = text.count("�")
    non_ascii = sum(1 for char in text if ord(char) > 127)
    blanks = sum(1 for line in selected if not line.strip())
    token_counts = Counter(re.findall(r"\S+", text))
    suspicious_tokens = [token for token, count in token_counts.items() if any(ch in token for ch in "�^\\|{}[]<>♦■") or sum(ch.isdigit() for ch in token) >= 3]
    rows = binary_rows(lines, 23, 760)
    return {"range": [start, end], "line_count": len(selected), "blank_lines": blanks, "blank_ratio": round(blanks / max(1, len(selected)), 3), "replacement_characters": replacement, "non_ascii_characters": non_ascii, "suspicious_token_count": len(suspicious_tokens), "suspicious_token_examples": suspicious_tokens[:40], "binary_rows": rows}

def translation_tables(lines: list[str]) -> list[dict]:
    rows = []
    for number, line in enumerate(lines, 1):
        bits = re.findall(r"(?<![A-Za-z0-9])(?:[01]\s*){3,}(?![A-Za-z0-9])", line)
        for raw in bits:
            normalized = normalize_bits(raw)
            if len(normalized) >= 3:
                rows.append({"line": number, "binary": normalized, "computed_decimal": int(normalized, 2)})
    return rows

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("path", type=Path); parser.add_argument("--start", type=int, default=23); parser.add_argument("--end", type=int, default=760); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); lines = args.path.read_text(encoding="utf-8", errors="replace").splitlines()
    report = analyze(args.path, args.start, args.end); report["translation_binary_rows"] = translation_tables(lines); report["source_sha256"] = __import__("hashlib").sha256(args.path.read_bytes()).hexdigest()
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output: args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
if __name__ == "__main__": main()
