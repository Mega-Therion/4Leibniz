#!/usr/bin/env python3
"""V-KERNEL attest: build a Lean project, audit named theorems, emit a signed record.

What a record certifies: the signer ran `lake build` and a Lean probe on the exact
committed sources, and Lean reported these axiom sets and statement/definition
commitments. It does NOT certify that a theorem means what its name says
(statement_match against a trusted challenge is not checked yet) and it does NOT
promote anything to [P]; consumers apply their own policy.

Usage: attest.py <project_dir> <config.json> <out_record.json>
config: {"imports": ["Leibniz"], "theorems": ["Ns.thm", ...], "axiom_policy": "standard-3"}
Signing key: $VKERNEL_SIGNING_KEY (path to 32-byte raw Ed25519 seed), never in the repo.
"""
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from nacl.signing import SigningKey

PROTOCOL = "vkernel/0.1"
POLICIES = {"standard-3": {"propext", "Classical.choice", "Quot.sound"}}
HERE = Path(__file__).resolve().parent

def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

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
    root, cfg_path, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), Path(sys.argv[3])
    cfg = json.loads(cfg_path.read_text())
    allowed = POLICIES[cfg["axiom_policy"]]
    key_path = os.environ.get("VKERNEL_SIGNING_KEY")
    if not key_path:
        print("VKERNEL_SIGNING_KEY not set", file=sys.stderr); return 2
    sk = SigningKey(Path(key_path).read_bytes())

    build = subprocess.run(["lake", "build"], cwd=root, capture_output=True, text=True)
    template = (HERE / "Probe.lean.in").read_text()
    probe_src = template.replace("@IMPORTS@", "\n".join(f"import {m}" for m in cfg["imports"])) \
                        .replace("@THEOREMS@", ", ".join(f"`{t}" for t in cfg["theorems"]))
    with tempfile.NamedTemporaryFile("w", suffix=".lean", dir=root, delete=False) as f:
        f.write(probe_src); probe = Path(f.name)
    try:
        run = subprocess.run(["lake", "env", "lean", str(probe)], cwd=root, capture_output=True, text=True)
    finally:
        probe.unlink()

    theorems = []
    for line in run.stdout.splitlines():
        if not line.startswith("{"): continue
        r = json.loads(line)
        axioms = sorted(r["axioms"])
        theorems.append({
            "name": r["theorem"],
            "statement_hash": sha(r["statement"].encode()),
            "statement_text": r["statement"],
            "def_closure_hash": sha("\n".join(r["def_closure"]).encode()),
            "def_closure_size": len(r["def_closure"]),
            "axioms": axioms,
            "axiom_policy_ok": set(axioms) <= allowed,
        })
    found = {t["name"] for t in theorems}
    missing = [t for t in cfg["theorems"] if t not in found]

    payload = {
        "protocol": PROTOCOL,
        "evidence_mode": "signed-service",
        "lean_toolchain": (root / "lean-toolchain").read_text().strip(),
        "source_commitment": source_commitment(root),
        "build_exit": build.returncode,
        "probe_exit": run.returncode,
        "axiom_policy": cfg["axiom_policy"],
        "theorems": theorems,
        "missing_theorems": missing,
        "statement_match": "not-checked",   # comparator vs trusted challenge: not wired yet
        "nonvacuity": "not-established",    # never inferred automatically
        "independent_checker": "not-run",   # lean4checker / nanoda: not wired yet
        "formal_result": "accepted" if (build.returncode == 0 and run.returncode == 0 and not missing
                                         and all(t["axiom_policy_ok"] for t in theorems)) else "rejected",
        "signer": sk.verify_key.encode().hex(),
    }
    record = {"payload": payload, "signature": sk.sign(canon(payload)).signature.hex()}
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"formal_result={payload['formal_result']} build_exit={build.returncode} probe_exit={run.returncode} "
          f"theorems={len(theorems)} missing={len(missing)}")
    if run.returncode: print(run.stderr[-2000:] or run.stdout[-2000:], file=sys.stderr)
    return 0 if payload["formal_result"] == "accepted" else 1

if __name__ == "__main__":
    sys.exit(main())
