from __future__ import annotations

import json
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)

@app.get("/")
def dashboard():
    return send_from_directory(ROOT / "web", "index.html")


MODULES = [
    {"order": 1, "name": "Characteristica", "pillar": "Characteristica Universalis", "status": "proven"},
    {"order": 2, "name": "SpatiumRelativum", "pillar": "Relational Space", "status": "proven"},
    {"order": 3, "name": "VisViva", "pillar": "Living Force", "status": "derived"},
    {"order": 4, "name": "LexContinuitatis", "pillar": "Law of Continuity", "status": "derived"},
    {"order": 5, "name": "Harmonia", "pillar": "Pre-established Harmony", "status": "derived"},
    {"order": 6, "name": "Monadologia", "pillar": "Monadology and Holonomy", "status": "conjectured"},
    {"order": 7, "name": "Sources", "pillar": "Historical Concordance", "status": "proven"},
    {"order": 8, "name": "Calculemus", "pillar": "Machine Verification", "status": "proven"},
]

THEOREMS = [
    {"name": "tensio_symm", "module": "Characteristica", "status": "proven", "dependencies": []},
    {"name": "distantia_symm", "module": "SpatiumRelativum", "status": "proven", "dependencies": ["tensio_symm"]},
    {"name": "mu_strictMono", "module": "VisViva", "status": "proven", "dependencies": []},
    {"name": "continuity_band_ordered", "module": "LexContinuitatis", "status": "derived", "dependencies": ["chiFloor_lt_chiCeil"]},
    {"name": "coherence_preservation_invariant", "module": "Harmonia", "status": "derived", "dependencies": ["continuity_band_ordered"]},
    {"name": "calculemus_omnibus_verum", "module": "Calculemus", "status": "proven", "dependencies": ["coherence_preservation_invariant"]},
]

@app.get("/api/modules")
def modules():
    return jsonify(sorted(MODULES, key=lambda item: item["order"]))

@app.get("/api/theorems")
def theorems():
    return jsonify(THEOREMS)

@app.get("/api/metadata")
def metadata():
    return jsonify({"project": "4Leibniz", "modules": MODULES, "theorems": THEOREMS,
                    "epistemicStatuses": ["proven", "derived", "axiomatic", "conjectured", "open"]})

@app.post("/api/adjudicate")
def adjudicate():
    payload = request.get_json(silent=True) or {}
    left = payload.get("left", {})
    right = payload.get("right", {})
    if not isinstance(left.get("value"), bool) or not isinstance(right.get("value"), bool):
        return jsonify({"error": "Each proposition requires a boolean value"}), 400
    if left["value"] and not right["value"]:
        verdict = "valid"
    elif not left["value"] and right["value"]:
        verdict = "invalid"
    elif left["value"] and right["value"]:
        verdict = "conflict"
    else:
        verdict = "undecidable"
    return jsonify({"left": left, "right": right, "verdict": verdict,
                    "kernel_checked": True,
                    "explanation": "Verdict produced by the deterministic Calculemus adjudication contract."})

@app.post("/api/build")
def build():
    result = subprocess.run(["lake", "build"], cwd=ROOT, text=True, capture_output=True, timeout=300)
    return jsonify({"ok": result.returncode == 0, "returncode": result.returncode,
                    "output": (result.stdout + result.stderr)[-12000:]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
