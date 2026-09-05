"""One-shot volunteer client; suitable for an external scheduler."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .worker import run_json
except ImportError:  # supports: python3 volunteer/client.py ...
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from volunteer.worker import run_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one signed 4Leibniz work unit locally")
    parser.add_argument("work_unit", type=Path, help="JSON work-unit file")
    parser.add_argument("--root", default=".", help="sandbox root for proof checks")
    args = parser.parse_args()
    print(run_json(args.work_unit.read_text(encoding="utf-8"), args.root))


if __name__ == "__main__":
    main()
