#!/usr/bin/env python3
"""Vacuity screen: classify named Lean theorems by the vacuity patterns seen in practice.

Usage: vacuity_screen.py <project_dir> <config.json> <out.json> [--preamble FILE.lean]
config: {"imports": ["Mod"], "theorems": ["Ns.thm", ...], "prefixes": ["Ns"]}   (vkernel-compatible)

Writes a JSON sidecar. It is NOT part of a vkernel/0.1 record and never sets
`nonvacuity`: a PASS only means none of the screened patterns fired. Classes are
documented in VacuityScreen.lean.in. One Lean process per project, so Mathlib loads once.
"""
import json, re, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from attest import source_commitment  # same commitment a vkernel record uses

TOOL = "vacuity_screen/0.1"
LINE = re.compile(r"VACUITY\|([^|\n]+)\|([^|\n]+)\|([^\n]*)")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root, cfg_path, out = Path(args[0]).resolve(), Path(args[1]), Path(args[2])
    preamble = ""
    if "--preamble" in sys.argv:
        preamble = Path(sys.argv[sys.argv.index("--preamble") + 1]).read_text()
    cfg = json.loads(cfg_path.read_text())
    thms = cfg.get("theorems", [])
    cmds = [f"#vacuity_screen {' '.join(thms[i:i + 15])}" for i in range(0, len(thms), 15)]
    cmds += [f"#vacuity_screen_prefix {p}" for p in cfg.get("prefixes", [])]
    # Import only tactic modules whose oleans the project has built (a project that
    # never built the Mathlib.Tactic umbrella cannot import it without a long build).
    mbuild = root / ".lake/packages/mathlib/.lake/build/lib/lean/Mathlib"
    if (mbuild / "Tactic.olean").exists():
        tactic_mods, missing = ["Mathlib.Tactic"], []
    else:
        want = ["Mathlib.Tactic.Ring", "Mathlib.Tactic.FieldSimp", "Mathlib.Tactic.NormNum", "Mathlib.Tactic.Linarith"]
        tactic_mods = [m for m in want if (mbuild / (m.split(".", 1)[1].replace(".", "/") + ".olean")).exists()]
        missing = [m for m in want if m not in tactic_mods]
    src = (HERE / "VacuityScreen.lean.in").read_text() \
        .replace("@IMPORTS@", "\n".join(f"import {m}" for m in cfg["imports"])) \
        .replace("@TACTIC_IMPORTS@", "\n".join(f"import {m}" for m in tactic_mods)) \
        .replace("@PREAMBLE@", preamble).replace("@COMMANDS@", "\n".join(cmds))
    with tempfile.NamedTemporaryFile("w", suffix=".lean", prefix="VacuityProbe_", dir=root, delete=False) as f:
        f.write(src)
        probe = Path(f.name)
    t0 = time.time()
    # Build first: `lake env lean` reads whatever oleans exist, which can predate the sources.
    real_imports = [m for m in cfg["imports"]]
    build = subprocess.run(["lake", "build", *real_imports], cwd=root, capture_output=True, text=True, timeout=7200)
    try:
        run = subprocess.run(["lake", "env", "lean", str(probe)], cwd=root, capture_output=True, text=True,
                             timeout=7200)
    finally:
        probe.unlink()
    text = run.stdout + run.stderr
    results = [{"theorem": m.group(1), "statement": m.group(2), "conjuncts": m.group(3).split(",")}
               for m in LINE.finditer(text)]
    errors = [l for l in text.splitlines() if ": error" in l][:20]
    rec = {
        "tool": TOOL,
        "project": root.name,
        "source_commitment": source_commitment(root),
        "config": cfg,
        "preamble_used": bool(preamble),
        "tactic_imports": tactic_mods,
        "tactic_imports_missing": missing,
        "lake_build_exit": build.returncode,
        "lean_exit": run.returncode,
        "lean_errors": errors,
        "seconds": round(time.time() - t0, 1),
        "nonvacuity": "not-established",
        "results": results,
    }
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    counts = {}
    for r in results:
        counts[r["statement"]] = counts.get(r["statement"], 0) + 1
    print(f"lean_exit={run.returncode} screened={len(results)} errors={len(errors)} {counts}")
    for e in errors[:5]:
        print("  ", e[:200])
    return 0 if run.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
