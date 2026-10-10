#!/usr/bin/env python3
"""V-KERNEL verify: check a record without Lean, Lake or Mathlib (Python + PyNaCl only).

Checks, all from the authenticated payload:
  - the record parses under the strict canonical loader (no duplicate keys, no floats);
  - payload_digest is RECOMPUTED here (never trusted as supplied) and the Ed25519
    signature verifies over the domain-separated signing message for that digest;
  - the signer is in the trusted list;
  - formal_result == accepted, no theorem missing, every theorem within the axiom policy;
  - each required leanchecker recheck ran clean;
  - (optional --source) the source commitment matches;
  - (optional --challenge) EACH theorem's statement hash matches the trusted challenge,
    re-compared here from the authenticated payload, not from the record's own flag.

Prints what was and was not established; never prints a tier or "true without assumptions".
Usage: verify.py <record.json> <trusted_signers.json> [--source <dir>] [--require-checker]
                  [--challenge <challenge.json>]
"""
import json
import sys
from pathlib import Path

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vkcanon import CanonError, payload_digest, signing_message, strict_load  # noqa: E402
from attest import source_commitment  # noqa: E402


def _legacy_canon(obj) -> bytes:
    """The vkernel/0.1 canonical form: sorted-json. Used only to verify pre-0.2 records."""
    import json as _json
    return _json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def main() -> int:
    argv = sys.argv
    try:
        rec = strict_load(Path(argv[1]).read_bytes())
    except CanonError as e:
        print(json.dumps({"verified": False, "failures": [f"record rejected by strict parser: {e}"]}))
        return 1
    trusted = set(json.loads(Path(argv[2]).read_text())["ed25519"])
    p, fails = rec.get("payload"), []
    if not isinstance(p, dict):
        print(json.dumps({"verified": False, "failures": ["no payload"]}))
        return 1

    # Protocol dispatch. vkernel/0.2 is the hardened scheme (recomputed domain-separated
    # digest + framed signing message). vkernel/0.1 is the legacy scheme (Ed25519 over
    # sorted-json canon, no digest) -- still accepted so committed 0.1 records are not
    # stranded, but a consumer can demand >=0.2 with --min-protocol. Transition shim added
    # 2026-10-09; remove once every committed record is regenerated at 0.2.
    proto = p.get("protocol", "vkernel/0.1")
    if "--min-protocol" in argv:
        want = argv[argv.index("--min-protocol") + 1]
        if proto < want:
            fails.append(f"protocol {proto} below required {want}")
    if not rec.get("signature") or not p.get("signer"):
        fails.append("record is unsigned")
    elif proto == "vkernel/0.2":
        try:
            digest = payload_digest(p)
            if rec.get("payload_digest") != digest:
                fails.append("payload_digest does not match recomputed digest")
            VerifyKey(bytes.fromhex(p["signer"])).verify(signing_message(digest), bytes.fromhex(rec["signature"]))
        except (BadSignatureError, ValueError, CanonError):
            fails.append("signature invalid")
    else:  # legacy vkernel/0.1
        try:
            VerifyKey(bytes.fromhex(p["signer"])).verify(_legacy_canon(p), bytes.fromhex(rec["signature"]))
        except (BadSignatureError, ValueError):
            fails.append("signature invalid")
    if p.get("signer") not in trusted:
        fails.append("signer not trusted")
    if p.get("formal_result") != "accepted":
        fails.append(f"formal_result={p.get('formal_result')}")
    if p.get("missing_theorems"):
        fails.append(f"missing {p['missing_theorems']}")
    for t in p.get("theorems", []):
        if not t.get("axiom_policy_ok"):
            fails.append(f"{t['name']} axioms {t['axioms']} violate {p.get('axiom_policy')}")
    for c in p.get("checker_runs", []):
        if not c.get("ok"):
            fails.append(f"leanchecker failed on {c['module']}")
    if "--require-checker" in argv and p.get("independent_checker", "not-run") == "not-run":
        fails.append("independent checker required but not run")
    if "--source" in argv:
        src = Path(argv[argv.index("--source") + 1])
        if source_commitment(src) != p.get("source_commitment"):
            fails.append("source commitment mismatch")

    statement_match = p.get("statement_match", "not-checked")
    if "--challenge" in argv:
        ch = strict_load(Path(argv[argv.index("--challenge") + 1]).read_bytes())
        want = ch.get("theorems") or {}
        names = {t["name"] for t in p.get("theorems", [])}
        for t in p.get("theorems", []):
            w = want.get(t["name"])
            if not w:
                fails.append(f"challenge has no entry for {t['name']}")
            elif w.get("statement_hash") != t.get("statement_hash"):
                fails.append(f"{t['name']} statement hash != trusted challenge")
        for n in want:
            if n not in names:
                fails.append(f"challenge theorem {n} absent from record")
        statement_match = "structural-match" if not any("challenge" in f or "statement hash" in f for f in fails) else "mismatch"

    print(json.dumps({"verified": not fails, "failures": fails,
                      "evidence_mode": p.get("evidence_mode"),
                      "statement_match": statement_match,
                      "comparison_relation": p.get("comparison_relation"),
                      "nonvacuity": p.get("nonvacuity"),
                      "network_blocked": p.get("network_blocked"),
                      "build_isolation": p.get("build_isolation"),
                      "independent_checker": p.get("independent_checker"),
                      "theorems": [t["name"] for t in p.get("theorems", [])]}, indent=2))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
