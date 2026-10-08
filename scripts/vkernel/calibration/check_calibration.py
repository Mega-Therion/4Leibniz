#!/usr/bin/env python3
"""Run the vacuity screen on the chyren-aeon calibration set and check it against the
frozen expectations: every old (replaced-as-vacuous) statement flagged, every genuine
replacement PASS. Exit 0 only if both hold.  Usage: check_calibration.py [vkernel_dir]"""
import json, subprocess, sys, tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
vk = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else here.parent
exp = json.loads((here / "chyren_aeon_expected.json").read_text())
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "screen.json"
    subprocess.run([sys.executable, str(vk / "vacuity_screen.py"), "/home/mega/Chyren/chyren-aeon/formal",
                    str(here / "chyren_aeon.json"), str(out), "--preamble", str(here / "chyren_aeon_old.lean")],
                   check=False)
    got = {r["theorem"]: r["statement"] for r in json.loads(out.read_text())["results"]}
bad = [f"not flagged: {n} ({got.get(n)})" for n in exp["must_flag"] if got.get(n) in (None, "PASS", "ERROR")]
bad += [f"not PASS: {n} ({got.get(n)})" for n in exp["must_pass"] if got.get(n) != "PASS"]
print("\n".join(bad) if bad else f"calibration OK: {len(exp['must_flag'])} flagged, {len(exp['must_pass'])} pass")
sys.exit(1 if bad else 0)
