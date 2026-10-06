#!/usr/bin/env python3
"""Conservative source hygiene check.

This is intentionally *not* the proof-authority mechanism. Lean elaboration plus
declaration-level "#print axioms" is authoritative for promotion to `proved`.
This script only catches suspicious source tokens early and avoids the old
whitespace-sensitive regex.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "Leibniz"

# Match the Lean identifier/tactic token itself, not surrounding whitespace.
TOKEN = re.compile(r"(?<![A-Za-z0-9_'])\b(?:sorry|sorryAx)\b")

files = sorted(LEAN_ROOT.rglob("*.lean"))
found = []

for path in files:
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if TOKEN.search(line):
            found.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")

if found:
    print("\n".join(found))
    sys.exit(1)

print(f"Checked {len(files)} Lean modules: no suspicious sorry tokens.")
