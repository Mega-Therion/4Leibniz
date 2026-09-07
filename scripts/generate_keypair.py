#!/usr/bin/env python3
"""Generate an Ed25519 keypair locally, without putting the private key on the wire.

Replaces the disabled-by-default `/api/security/keypair` route (release
assessment finding B-03: a network endpoint must never return a private key).
Run this on the machine that will hold the key.

    python3 scripts/generate_keypair.py

Prints the public key to stdout and writes the private key to a file with
0600 permissions instead of printing it, so it doesn't land in shell history
or a terminal scrollback buffer.
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from security import generate_keypair


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("leibniz_private_key.txt"),
                         help="file to write the private key to (default: ./leibniz_private_key.txt)")
    args = parser.parse_args()

    if args.out.exists():
        print(f"refusing to overwrite existing {args.out}", file=sys.stderr)
        return 1

    private, public = generate_keypair()
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(private + "\n")

    print(f"private key written to {args.out} (0600)")
    print(f"public key: {public}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
