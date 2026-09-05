#!/usr/bin/env python3
r"""Measure the Lean kernel's actual shape. Nothing here is hardcoded.

Leibniz/Calculemus.lean:60 carries a struct literal:

    { build := true, theoremCount := 18, sorryCount := 0, metadataCount := 12 }

Those are numbers somebody typed, not results of running anything, and the README
quoted them as if they were measurements. This script produces the real values,
so a claim in the README can cite a command instead of a literal.

  python3 scripts/measure_kernel.py            # human summary
  python3 scripts/measure_kernel.py --json     # machine-readable
  python3 scripts/measure_kernel.py --check    # exit 1 if any sorry is present

`--check` runs `lake env lean` per module and reads the ELABORATOR's output.
Source-text grepping is not sufficient: Lean reports `declaration uses \`sorry\``
as a WARNING and exits 0, and a sorry can also arrive through an import.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEIBNIZ = ROOT / "Leibniz"
DECL = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*"
                  r"(theorem|lemma|def|instance|abbrev|structure|inductive)\s+([A-Za-z_][\w'.]*)",
                  re.M)
# Lean 4 emits backticks; older docs show single quotes. Accept either.
SORRY = re.compile(r"uses ['`]sorry['`]")
AXIOMS = re.compile(r"depends on axioms: \[([^\]]*)\]")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}


def modules() -> list[Path]:
    mods = sorted(LEIBNIZ.glob("*.lean"))
    root = ROOT / "Leibniz.lean"
    if root.is_file():
        mods.append(root)
    return mods


def count_decls(paths: list[Path]) -> dict[str, int]:
    tally: dict[str, int] = {}
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        # strip block and line comments so prose is not counted as code
        text = re.sub(r"/-.*?-/", "", text, flags=re.S)
        text = re.sub(r"--.*$", "", text, flags=re.M)
        for kind, _name in DECL.findall(text):
            tally[kind] = tally.get(kind, 0) + 1
    return tally


def elaborate(paths: list[Path]) -> dict:
    """Run the real elaborator per module. Slow but authoritative."""
    sorries: list[str] = []
    nonstandard: list[str] = []
    failed: list[str] = []
    for p in paths:
        rel = p.relative_to(ROOT)
        proc = subprocess.run(["lake", "env", "lean", str(rel)],
                              cwd=ROOT, capture_output=True, text=True)
        out = proc.stdout + proc.stderr
        if proc.returncode != 0:
            failed.append(f"{rel} (exit {proc.returncode})")
        if SORRY.search(out):
            sorries.append(str(rel))
        for match in AXIOMS.findall(out):
            extra = {a.strip() for a in match.split(",")} - STANDARD
            if extra:
                nonstandard.append(f"{rel}: {sorted(extra)}")
    return {"sorry_modules": sorries, "nonstandard_axioms": nonstandard,
            "failed_modules": failed}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="elaborate every module; exit 1 on any sorry or failure")
    args = ap.parse_args()

    mods = modules()
    tally = count_decls(mods)
    report = {
        "modules_under_Leibniz": len(list(LEIBNIZ.glob("*.lean"))),
        "modules_total": len(mods),
        "declarations": tally,
        "theorems_and_lemmas": tally.get("theorem", 0) + tally.get("lemma", 0),
        "toolchain": (ROOT / "lean-toolchain").read_text().strip()
        if (ROOT / "lean-toolchain").is_file() else "unknown",
    }

    if args.check:
        report.update(elaborate(mods))

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"toolchain            {report['toolchain']}")
        print(f"modules under Leibniz/  {report['modules_under_Leibniz']}")
        print(f"modules total           {report['modules_total']}  (incl. root Leibniz.lean)")
        print(f"theorems + lemmas       {report['theorems_and_lemmas']}")
        for kind, n in sorted(tally.items()):
            print(f"  {kind:<10} {n}")
        if args.check:
            print(f"\nmodules with sorry      {len(report['sorry_modules'])} {report['sorry_modules']}")
            print(f"non-standard axioms     {len(report['nonstandard_axioms'])} {report['nonstandard_axioms']}")
            print(f"modules failing to build {len(report['failed_modules'])} {report['failed_modules']}")

    if args.check:
        bad = report["sorry_modules"] or report["nonstandard_axioms"] or report["failed_modules"]
        if bad:
            print("\nRESULT: FAIL", file=sys.stderr)
            return 1
        print("\nRESULT: PASS — every module elaborates, zero sorry, standard axioms only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
