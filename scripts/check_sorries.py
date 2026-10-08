#!/usr/bin/env python3
"""Conservative Lean source hygiene check.

This is intentionally *not* the proof-authority mechanism. Lean elaboration plus
declaration-level "#print axioms" is authoritative for promotion to `proved`.
This script only catches suspicious source tokens early and ignores Lean comments
and string literals so explanatory prose cannot trigger the hygiene gate.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "Leibniz"

TOKEN = re.compile(r"(?<![A-Za-z0-9_'])\b(?:sorry|sorryAx)\b")


def code_without_comments_and_strings(source: str) -> str:
    """Return source with comments/strings blanked while preserving line breaks."""
    out: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    escaped = False

    while i < len(source):
        if block_depth:
            if source.startswith("/-", i):
                block_depth += 1
                out.append("  ")
                i += 2
            elif source.startswith("-/", i):
                block_depth -= 1
                out.append("  ")
                i += 2
            else:
                out.append("\n" if source[i] == "\n" else " ")
                i += 1
            continue

        if in_string:
            if source[i] == "\n":
                # Lean strings normally cannot span raw newlines, but preserve
                # line structure if malformed source is encountered.
                out.append("\n")
                in_string = False
                escaped = False
                i += 1
            elif escaped:
                out.append(" ")
                escaped = False
                i += 1
            elif source[i] == "\\":
                out.append(" ")
                escaped = True
                i += 1
            elif source[i] == '"':
                out.append(" ")
                in_string = False
                i += 1
            else:
                out.append(" ")
                i += 1
            continue

        if source.startswith("--", i):
            while i < len(source) and source[i] != "\n":
                out.append(" ")
                i += 1
            continue

        if source.startswith("/-", i):
            block_depth = 1
            out.extend((" ", " "))
            i += 2
            continue

        if source[i] == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue

        out.append(source[i])
        i += 1

    return "".join(out)


def main() -> int:
    files = sorted(LEAN_ROOT.rglob("*.lean"))
    found = []

    for path in files:
        source = path.read_text(encoding="utf-8", errors="replace")
        code = code_without_comments_and_strings(source)
        for number, line in enumerate(code.splitlines(), 1):
            if TOKEN.search(line):
                original = source.splitlines()[number - 1].strip()
                found.append(f"{path.relative_to(ROOT)}:{number}: {original}")

    if found:
        print("\n".join(found))
        return 1

    print(f"Checked {len(files)} Lean modules: no suspicious sorry tokens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
