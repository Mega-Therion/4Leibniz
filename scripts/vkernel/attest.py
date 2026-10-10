#!/usr/bin/env python3
"""V-KERNEL attest: build a Lean project, audit named theorems, emit a signed record.

What a record certifies: the signer ran `lake build` and a Lean probe on the exact
committed sources **inside an isolated sandbox** (no network, read-only root, writable
project only, resource- and wall-clock-limited), re-checked the stored declarations with
leanchecker in a **separate** sandboxed process, and Lean reported these axiom sets and
statement/definition commitments. With `--challenge` it also records whether each
theorem's elaborated-statement hash matches a trusted challenge (structural identity).

It does NOT certify a theorem means what its name says beyond that hash comparison, it
does NOT run a second independent kernel (leanchecker is the same kernel re-run), and it
does NOT promote anything to [P]; consumers apply their own policy with verify.py.

Usage: attest.py <project_dir> <config.json> <out_record.json> [--unsigned] [--challenge <file>]
config: {"imports": ["Leibniz"], "theorems": [...], "axiom_policy": "standard-3",
         "check_modules": ["Leibniz.VisViva"], "checker_fresh": false}
Signing key: $VKERNEL_SIGNING_KEY (path to 32-byte raw Ed25519 seed), never in the repo.
"""
import datetime
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from nacl.signing import SigningKey

import sandbox
from vkcanon import PROTOCOL, canon, payload_digest, signing_message, strict_load  # noqa: F401

POLICIES = {"standard-3": {"propext", "Classical.choice", "Quot.sound"}}
HERE = Path(__file__).resolve().parent
BUILD_TIMEOUT = int(os.environ.get("VKERNEL_BUILD_TIMEOUT", "1800"))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def source_commitment(root: Path) -> str:
    h = hashlib.sha256()
    files = sorted(p for p in root.rglob("*.lean") if ".lake" not in p.parts)
    files += [p for p in (root / "lean-toolchain", root / "lake-manifest.json") if p.exists()]
    for p in files:
        h.update(str(p.relative_to(root)).encode() + b"\0" + sha(p.read_bytes()).encode() + b"\n")
    return h.hexdigest()


def main() -> int:
    argv = sys.argv
    root, cfg_path, out = Path(argv[1]).resolve(), Path(argv[2]), Path(argv[3])
    cfg = json.loads(cfg_path.read_text())
    allowed = POLICIES[cfg["axiom_policy"]]
    unsigned = "--unsigned" in argv
    challenge = None
    if "--challenge" in argv:
        challenge = strict_load(Path(argv[argv.index("--challenge") + 1]).read_bytes())
    key_path = os.environ.get("VKERNEL_SIGNING_KEY")
    if not key_path and not unsigned:
        print("VKERNEL_SIGNING_KEY not set (use --unsigned in CI)", file=sys.stderr)
        return 2
    sk = None if unsigned else SigningKey(Path(key_path).read_bytes())

    # 1. untrusted build, sandboxed.
    build = sandbox.run(["lake", "build"], cwd=str(root), writable=[str(root)], timeout=BUILD_TIMEOUT)

    # 2. the probe, same sandbox profile, separate process.
    template = (HERE / "Probe.lean.in").read_text()
    probe_src = template.replace("@IMPORTS@", "\n".join(f"import {m}" for m in cfg["imports"])) \
                        .replace("@THEOREMS@", ", ".join(f"`{t}" for t in cfg["theorems"]))
    with tempfile.NamedTemporaryFile("w", suffix=".lean", dir=root, delete=False) as f:
        f.write(probe_src)
        probe = Path(f.name)
    try:
        # The probe's full stdout is parsed (one JSON object per theorem), so it needs a
        # large capture cap; a 47-theorem project easily exceeds the tight default.
        run = sandbox.run(["lake", "env", "lean", str(probe)], cwd=str(root), writable=[str(root)],
                          timeout=BUILD_TIMEOUT, max_output=64 * 1024 * 1024)
    finally:
        probe.unlink()

    # 3. recheck: leanchecker replays the stored declarations in a SEPARATE sandboxed process,
    #    outside the build above. Fail on nonzero exit OR any output (a clean run is silent).
    checks = []
    recheck_iso = "not-run"
    for mod in cfg.get("check_modules", []):
        args = ["lake", "env", "leanchecker"] + (["--fresh"] if cfg.get("checker_fresh") else []) + [mod]
        c = sandbox.run(args, cwd=str(root), writable=[str(root)], timeout=BUILD_TIMEOUT)
        recheck_iso = c["isolation"]
        txt = (c["stdout"] + c["stderr"]).strip()
        checks.append({"module": mod, "exit": c["returncode"], "clean_output": txt == "",
                       "ok": c["returncode"] == 0 and txt == ""})

    theorems = []
    for line in run["stdout"].splitlines():
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        axioms = sorted(r["axioms"])
        st_hash = sha(r["statement"].encode())
        t = {
            "name": r["theorem"],
            "statement_hash": st_hash,
            "statement_text": r["statement"],
            "def_closure_hash": sha("\n".join(r["def_closure"]).encode()),
            "def_closure_size": len(r["def_closure"]),
            "axioms": axioms,
            "axiom_policy_ok": set(axioms) <= allowed,
        }
        if challenge is not None:
            want = (challenge.get("theorems") or {}).get(r["theorem"])
            t["challenge_match"] = bool(want) and want.get("statement_hash") == st_hash and (
                "def_closure_hash" not in want or want["def_closure_hash"] == t["def_closure_hash"])
        theorems.append(t)
    found = {t["name"] for t in theorems}
    missing = [t for t in cfg["theorems"] if t not in found]

    if challenge is None:
        statement_match, relation = "not-checked", None
    else:
        matched = theorems and all(t.get("challenge_match") for t in theorems) and not missing
        statement_match = "structural-match" if matched else "mismatch"
        relation = "structural-hash-identity"

    checks_ok = all(c["ok"] for c in checks) if checks else True
    accepted = (build["returncode"] == 0 and run["returncode"] == 0 and not missing
                and all(t["axiom_policy_ok"] for t in theorems) and checks_ok
                and statement_match != "mismatch")

    payload = {
        "protocol": PROTOCOL,
        "evidence_mode": "ci-unsigned" if unsigned else "signed-service",
        "ci_run": os.environ.get("GITHUB_SERVER_URL", "") + "/" + os.environ.get("GITHUB_REPOSITORY", "")
                  + "/actions/runs/" + os.environ["GITHUB_RUN_ID"] if os.environ.get("GITHUB_RUN_ID") else None,
        "issued_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lean_toolchain": (root / "lean-toolchain").read_text().strip(),
        "source_commitment": source_commitment(root),
        "build_exit": build["returncode"],
        "probe_exit": run["returncode"],
        "build_isolation": build["isolation"],
        "network_blocked": sandbox.net_blocked(build["isolation"]),
        "recheck_isolation": recheck_iso,
        "axiom_policy": cfg["axiom_policy"],
        "theorems": theorems,
        "missing_theorems": missing,
        "statement_match": statement_match,
        "comparison_relation": relation,
        "nonvacuity": "not-established",
        "independent_checker": ("leanchecker" + (" --fresh" if cfg.get("checker_fresh") else "")) if checks else "not-run",
        "checker_runs": checks,
        "formal_result": "accepted" if accepted else "rejected",
        "signer": None if unsigned else sk.verify_key.encode().hex(),
    }
    digest = payload_digest(payload)
    sig = None if unsigned else sk.sign(signing_message(digest)).signature.hex()
    record = {"payload": payload, "payload_digest": digest, "signature": sig}
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"formal_result={payload['formal_result']} build={build['returncode']} probe={run['returncode']} "
          f"isolation={build['isolation']} net_blocked={payload['network_blocked']} "
          f"theorems={len(theorems)} missing={len(missing)} statement_match={statement_match}")
    if build["returncode"]:
        print((build["stderr"] or build["stdout"])[-1500:], file=sys.stderr)
    if run["returncode"]:
        print((run["stderr"] or run["stdout"])[-1500:], file=sys.stderr)
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())
