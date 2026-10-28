"""Bound source statement headers without changing proof authority."""
from __future__ import annotations

import re

BOUNDARY = re.compile(
    r"^[ \t]*(?:@\[[^\]]*\]\s*)?"
    r"(?:private\s+|protected\s+|noncomputable\s+)*"
    r"(?:theorem|axiom|def|abbrev|inductive|structure|class|instance|"
    r"namespace|section|end)\b"
)

def statement_at(lines: list[str], index: int) -> str:
    header = lines[index].strip()
    if ":=" in header:
        return header.split(":=", 1)[0].strip()
    parts = [header]
    for line in lines[index + 1:]:
        if BOUNDARY.match(line):
            break
        if ":=" in line:
            parts.append(line.split(":=", 1)[0].strip())
            break
        if line.strip():
            parts.append(line.strip())
    return "\n".join(parts)
