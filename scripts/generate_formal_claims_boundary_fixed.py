#!/usr/bin/env python3
"""Compatibility entry point for B3-I07 statement-boundary correction.

Uses the existing generator and its unchanged Lean/axiom authority gates.
Only parse_module's statement field is corrected. Run this entry point
instead of generate_formal_claims.py until the change is integrated there.
The original entry point is deliberately not represented as fixed.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from formal_statement_boundaries import statement_at

_SOURCE = Path(__file__).with_name("generate_formal_claims.py")
_SPEC = importlib.util.spec_from_file_location("formal_claims_original", _SOURCE)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Cannot load the original formal-claims generator")
generator = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(generator)
_original_parse_module = generator.parse_module

def parse_module(path: Path) -> list[dict]:
    declarations = _original_parse_module(path)
    lines = generator.strip_comments(
        path.read_text(encoding="utf-8", errors="replace")
    ).splitlines()
    for declaration in declarations:
        declaration["statement"] = statement_at(lines, declaration["line"] - 1)
    return declarations

generator.parse_module = parse_module

if __name__ == "__main__":
    raise SystemExit(generator.main())
