#!/usr/bin/env python3
"""V-KERNEL verify: check a record without Lean, Lake or Mathlib.

Checks: signature over the canonical payload, signer is in the trusted list,
formal_result == accepted, every theorem passed the axiom policy, no theorem missing.
Optional --source <dir>: recompute the source commitment and require a match.
Prints what was and was not established; never prints a tier.
Usage: verify.py <record.json> <trusted_signers.json> [--source <project_dir>]
"""
import json, sys
from pathlib import Path
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from attest import canon, source_commitment  # noqa: E402

def main() -> int:
    rec = json.loads(Path(sys.argv[1]).read_text())
    trusted = set(json.loads(Path(sys.argv[2]).read_text())["ed25519"])
    p, fails = rec["payload"], []
    try:
        VerifyKey(bytes.fromhex(p["signer"])).verify(canon(p), bytes.fromhex(rec["signature"]))
    except (BadSignatureError, ValueError):
        fails.append("signature invalid")
    if p["signer"] not in trusted: fails.append("signer not trusted")
    if p["formal_result"] != "accepted": fails.append(f"formal_result={p['formal_result']}")
    if p["missing_theorems"]: fails.append(f"missing {p['missing_theorems']}")
    for t in p["theorems"]:
        if not t["axiom_policy_ok"]: fails.append(f"{t['name']} axioms {t['axioms']} violate {p['axiom_policy']}")
    for c in p.get("checker_runs", []):
        if not c["ok"]: fails.append(f"leanchecker failed on {c['module']}")
    if "--require-checker" in sys.argv and p.get("independent_checker", "not-run") == "not-run":
        fails.append("independent checker required but not run")
    if "--source" in sys.argv:
        src = Path(sys.argv[sys.argv.index("--source") + 1])
        if source_commitment(src) != p["source_commitment"]: fails.append("source commitment mismatch")
    print(json.dumps({"verified": not fails, "failures": fails, "evidence_mode": p["evidence_mode"],
                      "statement_match": p["statement_match"], "nonvacuity": p["nonvacuity"],
                      "independent_checker": p["independent_checker"],
                      "theorems": [t["name"] for t in p["theorems"]]}, indent=2))
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
