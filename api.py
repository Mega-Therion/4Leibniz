from __future__ import annotations

import functools
import json
import os
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
from cross_shard import Shard, atomic_commit, recover_in_doubt
from replicated_coordinator import DecisionVote, ParticipantAck, validate_decision, AckStore, ReplicatedDecisionLog
from replica_membership import issue_member, active as replica_active, verify_vote, elect_coordinator

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)

# --- Minimum-viable access control ------------------------------------------
# This is a stopgap for the research-preview posture, not the identity-aware
# gateway with RBAC/ABAC that a production release needs (see
# docs/PRODUCTION_READINESS.md, Phase 1 vs. Phase 3). It closes the concrete
# gap flagged in the 2026-09-07 release assessment: mutation and
# process-spawning routes must not be callable by any reachable client.
#
# Secure by default: if LEIBNIZ_API_TOKEN is unset, every @require_auth route
# refuses all requests rather than falling open.
API_TOKEN = os.environ.get("LEIBNIZ_API_TOKEN")
ENABLE_BUILD_ENDPOINT = os.environ.get("LEIBNIZ_ENABLE_BUILD_ENDPOINT") == "1"
ENABLE_KEYPAIR_ENDPOINT = os.environ.get("LEIBNIZ_ENABLE_KEYPAIR_ENDPOINT") == "1"

# 1 MiB. Generous for a claim/proposal payload, small enough to bound the
# in-memory JSON parse and blunt trivial request-size abuse (finding B-12).
app.config["MAX_CONTENT_LENGTH"] = 1_000_000

@app.errorhandler(413)
def _payload_too_large(_exc):
    return jsonify({"error": "request body exceeds the 1 MiB limit"}), 413

def require_auth(fn):
    """Gate a mutation/dangerous route behind a bearer token.

    Not a substitute for the RBAC/ABAC gateway the full release blueprint
    calls for -- it has one static token and no per-route scoping -- but it
    means an unauthenticated caller can no longer reach these routes at all,
    which is the Phase 1 exit criterion.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if API_TOKEN is None:
            return jsonify({"error": "server has no LEIBNIZ_API_TOKEN configured; mutation routes are disabled"}), 503
        supplied = request.headers.get("Authorization", "")
        if not supplied.startswith("Bearer ") or supplied[len("Bearer "):] != API_TOKEN:
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)
    return wrapper

replay_guard = ReplayGuard(db_path=os.environ.get("LEIBNIZ_STATE_DB"))
ack_store = AckStore()

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

# Models a caller may request. `model` arrives in the request body, so without
# an allow-list an unauthenticated caller could name an arbitrarily expensive
# model and have this server pay for it (finding F-02).
ALLOWED_SUGGEST_MODELS = frozenset({"gpt-5-mini", "gpt-5", "gpt-4o-mini", "gpt-4o"})
DEFAULT_SUGGEST_MODEL = "gpt-5-mini"

@app.post("/api/ai/suggest")
@require_auth
def ai_suggest():
    """Suggest Lean-checkable premises. Authenticated: this route spends money.

    It was previously public, classified with the read-only/stateless routes.
    It is neither: `suggest()` calls the provider completions API with
    max_completion_tokens=1200 whenever OPENAI_API_KEY and OPENAI_API_BASE are
    set, so an unauthenticated caller could drain the account. It degrades to a
    deterministic fallback when no key is configured, which is exactly why it
    looks harmless in development and in any audit run without credentials --
    safe in the environment it is assessed in, unsafe in the one it runs in.
    """
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    model = payload.get("model", DEFAULT_SUGGEST_MODEL)
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 400
    if not isinstance(model, str) or model not in ALLOWED_SUGGEST_MODELS:
        return jsonify({
            "error": "unsupported model",
            "allowed": sorted(ALLOWED_SUGGEST_MODELS),
        }), 400
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
@require_auth
def governance_evaluate():
    payload = request.get_json(silent=True) or {}
    try:
        votes = [GovernanceVote(**v) for v in payload.get("votes", [])]
        return jsonify(evaluate_governance(payload.get("proposal_id", ""), payload.get("action", ""), votes, float(payload.get("quorum", 2/3)), bool(payload.get("veto_blocks", True)), int(payload.get("timelock_seconds", 3600))))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/replicas/issue")
@require_auth
def replicas_issue():
    payload=request.get_json(silent=True) or {}
    try: return jsonify(issue_member(payload['replica_id'],payload['private_key'],payload.get('weight',1),payload.get('ttl',86400),payload.get('now')))
    except (TypeError,ValueError,KeyError) as exc: return jsonify({'error':str(exc)}),422

@app.post("/api/replicas/elect")
@require_auth
def replicas_elect():
    payload=request.get_json(silent=True) or {}; return jsonify(elect_coordinator(payload.get('members',[]),payload.get('epoch',0),payload.get('now')))

@app.post("/api/replicas/verify-vote")
def replicas_verify_vote():
    payload=request.get_json(silent=True) or {}; return jsonify({'valid':verify_vote(payload.get('vote',{}),payload.get('member',{}),payload.get('now'))})

@app.post("/api/coordinator/recover")
@require_auth
def coordinator_recover():
    payload=request.get_json(silent=True) or {}
    try: return jsonify(ReplicatedDecisionLog.recover(payload['snapshot']).snapshot())
    except (TypeError,ValueError,KeyError) as exc: return jsonify({'error':str(exc)}),422

@app.post("/api/coordinator/validate")
@require_auth
def coordinator_validate():
    payload = request.get_json(silent=True) or {}
    try:
        votes = [DecisionVote(**v) for v in payload.get('votes', [])]
        return jsonify(validate_decision(votes, payload.get('txid',''), payload.get('transaction_digest',''), int(payload.get('fault_tolerance',1))))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({'error':str(exc)}), 422

@app.post("/api/participants/ack")
@require_auth
def participant_ack():
    payload = request.get_json(silent=True) or {}
    try:
        ack = ParticipantAck(**payload['ack'])
        return jsonify(ack_store.record(ack))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({'error':str(exc)}), 422

@app.post("/api/participants/list")
def participant_list():
    payload = request.get_json(silent=True) or {}
    return jsonify({'acks':ack_store.for_transaction(payload.get('txid',''))})

@app.post("/api/shards/atomic-commit")
@require_auth
def shards_atomic_commit():
    payload = request.get_json(silent=True) or {}
    try:
        shards = {s['shard_id']: Shard(s['shard_id'], s.get('state', {})) for s in payload.get('shards', [])}
        return jsonify(atomic_commit(payload.get('txid',''), shards, payload.get('writes', {}), payload.get('reachable')))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({'error':str(exc)}), 422

@app.post("/api/shards/recover")
@require_auth
def shards_recover():
    payload = request.get_json(silent=True) or {}
    try:
        shards = {s['shard_id']: Shard(s['shard_id'], s.get('state', {})) for s in payload.get('shards', [])}
        for s in payload.get('shards', []):
            for txid, item in s.get('prepared', {}).items(): shards[s['shard_id']].prepared[txid] = item
        return jsonify(recover_in_doubt(payload.get('txid',''), shards, payload.get('decision','abort')))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({'error':str(exc)}), 422

@app.post("/api/shards/sync")
@require_auth
def shards_sync():
    payload = request.get_json(silent=True) or {}
    try:
        shard = Shard(payload['snapshot']['shard_id'])
        return jsonify(shard.sync(payload['snapshot']))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({'error':str(exc)}), 422

@app.post("/api/log/validate")
@require_auth
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
@require_auth
def admit_peer_route():
    payload = request.get_json(silent=True) or {}
    try:
        proposal = SignedProposal(**payload.get("proposal", {}))
        return jsonify(admit_peer(proposal, payload.get("capabilities", []), payload.get("weight", 1), payload.get("ttl", 86400), payload.get("now")))
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 422

@app.post("/api/peers/revoke")
@require_auth
def revoke_peer_route():
    payload = request.get_json(silent=True) or {}
    return jsonify(revoke_peer(payload.get("record", {}), payload.get("reason", "governance decision")))

@app.post("/api/peers/check")
def check_peer_route():
    payload = request.get_json(silent=True) or {}
    return jsonify({"active": peer_is_active(payload.get("record"), payload.get("now"))})

@app.post("/api/zk/verify")
@require_auth
def zk_verify():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("proof"), dict) or not isinstance(payload.get("public_signals"), list):
        return jsonify({"error": "proof and public_signals are required"}), 400
    return jsonify(verify_groth16(payload["proof"], payload["public_signals"], payload.get("verification_key")))

@app.post("/api/security/keypair")
@require_auth
def security_keypair():
    # Disabled by default (B-03): a network endpoint that can return a private
    # key is a release blocker regardless of auth. Prefer
    # `python3 scripts/generate_keypair.py`, which never puts the key on the
    # wire. This route exists only for local dev convenience behind an
    # explicit opt-in.
    if not ENABLE_KEYPAIR_ENDPOINT:
        return jsonify({"error": "disabled; run scripts/generate_keypair.py locally, or set LEIBNIZ_ENABLE_KEYPAIR_ENDPOINT=1 for local dev only"}), 404
    private, public = generate_keypair()
    return jsonify({"private_key": private, "public_key": public, "warning": "Store the private key outside the API; this endpoint is for local setup only."})

@app.post("/api/security/sign")
@require_auth
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
@require_auth
def build():
    # Disabled by default (B-02): an unauthenticated, unsandboxed
    # subprocess.run trigger is a release blocker on its own, independent of
    # auth. The real replacement is a queued job with a signed identity,
    # resource limits, and artifact isolation (see
    # docs/PRODUCTION_READINESS.md, Phase 3) -- this flag only restores the
    # old dev-convenience behavior for operators who explicitly ask for it,
    # and even then only to an authenticated caller.
    if not ENABLE_BUILD_ENDPOINT:
        return jsonify({"error": "disabled; run `lake build` locally, or set LEIBNIZ_ENABLE_BUILD_ENDPOINT=1 for local dev only"}), 404
    result = subprocess.run(["lake", "build"], cwd=ROOT, text=True, capture_output=True, timeout=300)
    return jsonify({"ok": result.returncode == 0, "returncode": result.returncode,
                    "output": (result.stdout + result.stderr)[-12000:]})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
