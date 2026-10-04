#!/usr/bin/env python3
"""Assert the vendored formal-claims snapshot matches upstream 4Leibniz.

tests/formal-claims-contract.ts already proves the snapshot is internally sound:
commit-pinned, proved-implies-verification, controlled statuses, and the consumer
gate that only `proved` entries can earn a badge.

What nothing checked is whether the snapshot still matches the catalog 4Leibniz
actually publishes. A snapshot can be perfectly self-consistent and months stale,
and a stale catalog is exactly how a "proved" badge outlives the proof behind it.

Upstream had a real instance of this: its CI freshness assertion could never pass,
because the generator pinned `rev-parse HEAD` -- committing the artifact changed
the very commit the artifact recorded. Fixed upstream 2026-09-14; this is the
consumer-side half.

Network-free by default: compares against a local 4Leibniz checkout when one is
reachable, else skips with a clear message rather than inventing confidence.
Set FOURLEIBNIZ_PATH to point at the checkout.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LOCAL = HERE / "content" / "formal-claims-v1.json"

CANDIDATES = [
    os.environ.get("FOURLEIBNIZ_PATH"),
    str(Path.home() / "4Leibniz"),
    str(HERE.parent / "4Leibniz"),
]


def find_upstream() -> Path | None:
    for c in CANDIDATES:
        if not c:
            continue
        p = Path(c) / "artifacts" / "v1" / "formal-claims.json"
        if p.is_file():
            return p
    return None


def main() -> int:
    if not LOCAL.is_file():
        print(f"FAIL: {LOCAL} missing", file=sys.stderr)
        return 1
    up = find_upstream()
    if up is None:
        print("SKIP: no local 4Leibniz checkout found; set FOURLEIBNIZ_PATH to "
              "compare. This is a SKIP, not a pass -- freshness is unverified.")
        return 0

    local = json.loads(LOCAL.read_text())
    upstream = json.loads(up.read_text())

    lc = {c["proof_source"]["commit"] for c in local["claims"] if "proof_source" in c}
    uc = {c["proof_source"]["commit"] for c in upstream["claims"] if "proof_source" in c}

    if local["claims"] != upstream["claims"]:
        print(f"FAIL: vendored snapshot differs from upstream {up}", file=sys.stderr)
        print(f"  local:    {len(local['claims'])} claims, pins {sorted(lc)}", file=sys.stderr)
        print(f"  upstream: {len(upstream['claims'])} claims, pins {sorted(uc)}", file=sys.stderr)
        print("  Regenerate upstream, then refresh this snapshot. A stale catalog "
              "means a displayed 'proved' badge may outlive its proof.", file=sys.stderr)
        return 1

    print(f"PASS: snapshot matches upstream ({len(local['claims'])} claims, "
          f"pinned at {sorted(lc)[0][:8]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
