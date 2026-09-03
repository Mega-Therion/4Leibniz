"""
4Leibniz — Calculemus Web Oracle
A small Flask presentation layer over the Lean 4 formal verification library.
Serves the project on port 3000 and runs `lake build` (the Lean kernel) on demand.
"""
import glob
import os
import re
import subprocess
import threading
import time

from flask import Flask, jsonify, render_template

app = Flask(__name__)

PROJECT_DIR = "/app"
LEAN_DIR = os.path.join(PROJECT_DIR, "Leibniz")

# ---------------------------------------------------------------------------
# Build runner (the Calculemus oracle)
# ---------------------------------------------------------------------------
_build_lock = threading.Lock()
_build = {
    "status": "idle",        # idle | running | done | timeout | error
    "output": "",
    "exit_code": None,
    "elapsed": None,
    "started_at": None,
    "finished_at": None,
}


def run_build():
    with _build_lock:
        _build.update(
            status="running", output="", exit_code=None, elapsed=None,
            started_at=time.time(), finished_at=None,
        )
    start = time.time()
    try:
        res = subprocess.run(
            ["lake", "build"],
            capture_output=True, text=True, cwd=PROJECT_DIR, timeout=600,
        )
        elapsed = time.time() - start
        output = (res.stdout or "") + (res.stderr or "")
        with _build_lock:
            _build.update(
                status="done", output=output, exit_code=res.returncode,
                elapsed=round(elapsed, 2), finished_at=time.time(),
            )
    except subprocess.TimeoutExpired:
        with _build_lock:
            _build.update(
                status="timeout", output="Build timed out after 600s",
                exit_code=None, elapsed=round(time.time() - start, 2),
                finished_at=time.time(),
            )
    except Exception as e:  # noqa: BLE001
        with _build_lock:
            _build.update(
                status="error", output=str(e), exit_code=None,
                elapsed=round(time.time() - start, 2), finished_at=time.time(),
            )


def _trigger_build():
    t = threading.Thread(target=run_build, daemon=True)
    t.start()


# Kick off the first verification shortly after startup (lets the toolchain
# download while the page loads).
threading.Timer(2.0, run_build).start()


# ---------------------------------------------------------------------------
# Module parsing
# ---------------------------------------------------------------------------
MODULE_META = {
    "Characteristica": {
        "title": "Characteristica Universalis",
        "origin": "De Arte Combinatoria (1666)",
        "subtitle": "Symbolic Grammar \u00b7 Epistemic Stratification \u00b7 Dyas",
    },
    "Dyadica": {
        "title": "Dyadica (Binary Genesis)",
        "origin": "De Progressione Dyadica (1679)",
        "subtitle": "IO/OI Tension \u00b7 Entropy Balance \u00b7 Information Projection",
    },
    "SpatiumRelativum": {
        "title": "Spatium Relativum (Relational Spacetime)",
        "origin": "Leibniz-Clarke Correspondence (1715)",
        "subtitle": "Relational Distance \u00b7 Stiefel Manifold V_m(R^N)",
    },
    "Monadologia": {
        "title": "Monadologia (Perceptual Holography)",
        "origin": "La Monadologie (1714)",
        "subtitle": "Projection Boundaries \u00b7 Holonomic Entanglement",
    },
    "VisViva": {
        "title": "Vis Viva (Living Force)",
        "origin": "Specimen Dynamicum (1695)",
        "subtitle": "Kinetic Invariant E = m\u00b7v\u00b2 \u00b7 Cosmic Horizon",
    },
    "LexContinuitatis": {
        "title": "Lex Continuitatis (Law of Continuity)",
        "origin": "Nova Methodus (1684)",
        "subtitle": "Chiral Invariant Continuity Band",
    },
    "Harmonia": {
        "title": "Harmonia Praestabilita (Stability)",
        "origin": "Syst\u00e8me Nouveau (1695)",
        "subtitle": "Anti-Drift Stabilization Theorem",
    },
    "Calculemus": {
        "title": "Calculemus! (Verification Oracle)",
        "origin": "De Scientia Universali (1680)",
        "subtitle": "Master Verification Evaluation",
    },
}


def parse_modules():
    modules = []
    for path in sorted(glob.glob(os.path.join(LEAN_DIR, "*.lean"))):
        name = os.path.basename(path).replace(".lean", "")
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        theorems = re.findall(r"^theorem\s+(\w+)", content, re.MULTILINE)
        defs = re.findall(r"^(?:def|inductive|structure)\s+(\w+)", content, re.MULTILINE)
        ns_match = re.search(r"^namespace\s+([\w.]+)", content, re.MULTILINE)
        meta = MODULE_META.get(name, {})
        modules.append({
            "file": name,
            "namespace": ns_match.group(1) if ns_match else name,
            "title": meta.get("title", name),
            "origin": meta.get("origin", ""),
            "subtitle": meta.get("subtitle", ""),
            "theorems": theorems,
            "definitions": defs,
            "line_count": len(content.splitlines()),
        })
    return modules


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/modules")
def api_modules():
    return jsonify({"modules": parse_modules()})


@app.route("/api/build")
def api_build():
    with _build_lock:
        snapshot = dict(_build)
    return jsonify(snapshot)


@app.route("/api/build/run", methods=["POST"])
def api_build_run():
    if _build["status"] != "running":
        _trigger_build()
    with _build_lock:
        return jsonify(dict(_build))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)
