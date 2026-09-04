"""Phase 8 multi-prover evidence aggregation.

Aggregation coordinates independent verifier reports; it never upgrades a claim
above the strongest evidence actually supplied by an authorized verifier.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json

STATUSES = ("open", "conjectured", "axiomatic", "derived", "proven")
@dataclass(frozen=True)
class ProofReport:
    prover_id: str
    artifact_digest: str
    status: str
    independent_kernel: bool = False
    signature_verified: bool = False
    rationale: str = ""

def aggregate(reports, required=2, require_independent=True):
    reports = tuple(reports)
    valid = [r for r in reports if r.status in STATUSES and r.artifact_digest and r.prover_id]
    by_digest = {}
    for r in valid: by_digest.setdefault(r.artifact_digest, []).append(r)
    ranked = sorted(by_digest.items(), key=lambda item: (len(item[1]), item[0]), reverse=True)
    digest, winning = ranked[0] if ranked else ("", [])
    independent = sum(1 for r in winning if r.independent_kernel)
    signed = sum(1 for r in winning if r.signature_verified)
    accepted = bool(winning) and len(winning) >= required and (not require_independent or independent >= 2)
    status = min((r.status for r in winning), key=STATUSES.index) if accepted else "open"
    dissent = [asdict(r) for r in valid if r.artifact_digest != digest or (accepted and r.status != status)]
    return {'artifact_digest': digest, 'accepted': accepted, 'status': status,
            'report_count': len(valid), 'quorum_required': required,
            'matching_reports': len(winning), 'independent_kernel_reports': independent,
            'signed_reports': signed, 'reports': [asdict(r) for r in valid],
            'dissent': dissent,
            'receipt': hashlib.sha256(json.dumps({'digest':digest,'reports':[asdict(r) for r in winning]}, sort_keys=True).encode()).hexdigest(),
            'explanation': ('Independent prover quorum reached.' if accepted else 'Evidence quorum not reached; status remains open.')}
