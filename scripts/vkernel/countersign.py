#!/usr/bin/env python3
"""Countersign an unsigned CI record locally, with the key that never leaves this machine.

The signer did NOT run the check; CI did. So evidence_mode becomes
"ci-run-countersigned", and the payload keeps ci_run so a consumer can look up the run.
Countersigning means: "I fetched this record from that CI run and vouch for it."
Usage: countersign.py <unsigned_record.json> <out.json>   (needs $VKERNEL_SIGNING_KEY)
"""
import json
import os
import sys
from pathlib import Path
from nacl.signing import SigningKey
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vkcanon import payload_digest, signing_message, strict_load  # noqa: E402

rec = strict_load(Path(sys.argv[1]).read_bytes())
p = rec["payload"]
if p.get("evidence_mode") != "ci-unsigned" or rec.get("signature"):
    sys.exit("refusing: not an unsigned CI record")
if not p.get("ci_run"):
    sys.exit("refusing: record has no ci_run, so its origin can't be traced")
sk = SigningKey(Path(os.environ["VKERNEL_SIGNING_KEY"]).read_bytes())
p["evidence_mode"] = "ci-run-countersigned"
p["signer"] = sk.verify_key.encode().hex()
digest = payload_digest(p)
out = {"payload": p, "payload_digest": digest, "signature": sk.sign(signing_message(digest)).signature.hex()}
Path(sys.argv[2]).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(f"countersigned {len(p['theorems'])} theorems from {p['ci_run']}; formal_result={p['formal_result']}")
