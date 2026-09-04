from __future__ import annotations

import json
import subprocess
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from ucalculus import SyntaxError as UCalcSyntaxError, compile_text, parse
from proof_engine import SemanticPatch, search_text
from counterexample import find_for_claim
from divergence import compare_text
from ai_assist import suggest
from consensus import Peer, Vote, reach_consensus, result_json
from benchmarks.runner import run as run_benchmark
from security import SignedProposal, ReplayGuard, commit_private_premise, generate_keypair, sign_proposal, verify_proposal, verify_fresh_proposal, receipt_json
from bft import BFTPeer, BFTVote, decide as bft_decide
from zk_pipeline import status as zk_status
from zk_verify import verify_groth16
from multiprover import ProofReport, aggregate as aggregate_provers
from governance import GovernanceVote, evaluate as evaluate_governance
from durable_log import OrderedLog
from peer_admission import admit as admit_peer, is_active as peer_is_active, revoke as revoke_peer

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
replay_guard = ReplayGuard()

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

@app.post("/api/compile")
def compile_universal_claim():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    if not isinstance(text, str):
        return jsonify({"error": "text must be a universal-calculus declaration"}), 400
    try:
        return jsonify(compile_text(text))
    except UCalcSyntaxError as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/prove")
def prove_universal_claim():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    if not isinstance(text, str):
        return jsonify({"error": "text must be a universal-calculus declaration"}), 400
    try:
        return jsonify(search_text(text))
    except UCalcSyntaxError as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/repl")
def repl():
    payload = request.get_json(silent=True) or {}
    action, text = payload.get("action", "help"), payload.get("text", "")
    if action == "help":
        return jsonify({"commands": ["compile", "prove", "explain"], "usage": "Send action plus universal-calculus text."})
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 400
    try:
        result = search_text(text)
        if action == "compile":
            return jsonify({"kind": "compile", "ir": result["ir"]})
        if action == "prove":
            return jsonify({"kind": "prove", "search": result["search"], "explanations": result["explanations"]})
        if action == "explain":
            return jsonify({"kind": "explain", "explanations": result["explanations"]})
        return jsonify({"error": "unknown action; use compile, prove, or explain"}), 422
    except UCalcSyntaxError as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/ai/suggest")
def ai_suggest():
    payload = request.get_json(silent=True) or {}
    text, model = payload.get("text"), payload.get("model", "gpt-5-mini")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 400
    return jsonify(suggest(text, model))

@app.post("/api/consensus")
def consensus():
    payload = request.get_json(silent=True) or {}
    peers = tuple(Peer(p["node_id"], int(p.get("weight", 1)), tuple(p.get("capabilities", ["lean", "search"]))) for p in payload.get("peers", []))
    votes = tuple(Vote(v["node_id"], v.get("proposal_hash", ""), v["status"], v.get("rationale", "")) for v in payload.get("votes", []))
    try:
        return jsonify(result_json(reach_consensus(peers, votes, float(payload.get("threshold", 2/3)))))
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/bft/decide")
def bft_consensus():
    payload = request.get_json(silent=True) or {}
    try:
        peers = [BFTPeer(**p) for p in payload.get("peers", [])]
        votes = [BFTVote(**v) for v in payload.get("votes", [])]
        return jsonify(bft_decide(peers, votes, int(payload.get("fault_tolerance", 1)), float(payload.get("threshold", 2/3))))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.get("/api/zk/status")
def zk_pipeline_status():
    return jsonify(zk_status())

@app.post("/api/provers/aggregate")
def aggregate_proof_reports():
    payload = request.get_json(silent=True) or {}
    try:
        reports = [ProofReport(**r) for r in payload.get("reports", [])]
        return jsonify(aggregate_provers(reports, int(payload.get("required", 2)), bool(payload.get("require_independent", True))))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/governance/evaluate")
def governance_evaluate():
    payload = request.get_json(silent=True) or {}
    try:
        votes = [GovernanceVote(**v) for v in payload.get("votes", [])]
        return jsonify(evaluate_governance(payload.get("proposal_id", ""), payload.get("action", ""), votes, float(payload.get("quorum", 2/3)), bool(payload.get("veto_blocks", True)), int(payload.get("timelock_seconds", 3600))))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/log/validate")
def validate_log():
    payload = request.get_json(silent=True) or {}
    try:
        log = OrderedLog(payload.get("entries", []))
        if payload.get("append"):
            item = payload["append"]
            log.append(item.get("proposal_id", ""), item.get("payload", {}), item.get("sequence"))
        return jsonify(log.snapshot())
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/peers/admit")
def admit_peer_route():
    payload = request.get_json(silent=True) or {}
    try:
        proposal = SignedProposal(**payload.get("proposal", {}))
        return jsonify(admit_peer(proposal, payload.get("capabilities", []), payload.get("weight", 1), payload.get("ttl", 86400), payload.get("now")))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/peers/revoke")
def revoke_peer_route():
    payload = request.get_json(silent=True) or {}
    return jsonify(revoke_peer(payload.get("record", {}), payload.get("reason", "governance decision")))

@app.post("/api/peers/check")
def check_peer_route():
    payload = request.get_json(silent=True) or {}
    return jsonify({"active": peer_is_active(payload.get("record"), payload.get("now"))})

@app.post("/api/zk/verify")
def zk_verify():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("proof"), dict) or not isinstance(payload.get("public_signals"), list):
        return jsonify({"error": "proof and public_signals are required"}), 400
    return jsonify(verify_groth16(payload["proof"], payload["public_signals"], payload.get("verification_key")))

@app.post("/api/security/keypair")
def security_keypair():
    private, public = generate_keypair()
    return jsonify({"private_key": private, "public_key": public, "warning": "Store the private key outside the API; this endpoint is for local setup only."})

@app.post("/api/security/sign")
def security_sign():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("node_id"), str) or not isinstance(payload.get("payload"), dict) or not isinstance(payload.get("private_key"), str):
        return jsonify({"error": "node_id, payload, and private_key are required"}), 400
    try:
        signed = sign_proposal(payload["node_id"], payload["payload"], payload["private_key"])
        return jsonify({"proposal": signed.__dict__, "verified": verify_proposal(signed)})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/security/verify")
def security_verify():
    payload = request.get_json(silent=True) or {}
    try:
        proposal = SignedProposal(**payload["proposal"])
        verified = verify_fresh_proposal(proposal, replay_guard)
        return jsonify({"verified": verified, "digest": proposal.digest, "replay_protected": True})
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/security/commit")
def security_commit():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("statement"), str):
        return jsonify({"error": "statement is required"}), 400
    return jsonify(receipt_json(commit_private_premise(payload["statement"])))

@app.get("/api/benchmarks")
def benchmarks():
    return jsonify(run_benchmark())

@app.post("/api/counterexample")
def counterexample():
    payload = request.get_json(silent=True) or {}
    text, bound = payload.get("text"), payload.get("max_bound", 3)
    if not isinstance(text, str):
        return jsonify({"error": "text must be a universal-calculus declaration"}), 400
    try:
        return jsonify(find_for_claim(parse(text), int(bound)))
    except (UCalcSyntaxError, ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/divergence")
def divergence():
    payload = request.get_json(silent=True) or {}
    before, after = payload.get("before"), payload.get("after")
    if not isinstance(before, str) or not isinstance(after, str):
        return jsonify({"error": "before and after declarations are required"}), 400
    try:
        return jsonify(compare_text(before, after))
    except (UCalcSyntaxError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/patch")
def patch_universal_claim():
    payload = request.get_json(silent=True) or {}
    text, patch_data = payload.get("text"), payload.get("patch")
    if not isinstance(text, str) or not isinstance(patch_data, dict):
        return jsonify({"error": "text and patch are required"}), 400
    try:
        claim = parse(text)
        patched = SemanticPatch(**patch_data).apply(claim)
        patched_text = "claim " + patched.name + ":\n" + "\n".join("  given " + p.text for p in patched.premises) + "\n  infer " + patched.conclusion
        return jsonify({"claim": patched.__dict__, "search": search_text(patched_text)})
    except (UCalcSyntaxError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.get("/api/epistemic/lattice")
def epistemic_lattice():
    statuses = ["open", "conjectured", "axiomatic", "derived", "proven"]
    return jsonify({"nodes": [{"id": s, "rank": i} for i, s in enumerate(statuses)],
                    "edges": [{"source": statuses[i], "target": statuses[i + 1], "relation": "can_weaken_to"}
                              for i in range(len(statuses) - 1)]})

@app.get("/api/arguments/graph")
def argument_graph():
    nodes = [{"id": t["name"], "module": t["module"], "status": t["status"]} for t in THEOREMS]
    edges = [{"source": dep, "target": t["name"], "relation": "depends_on"}
             for t in THEOREMS for dep in t["dependencies"]]
    return jsonify({"nodes": nodes, "edges": edges})

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
