"""Quality audit for HTR output.

The audit's job is to decide whether a transcription is usable evidence. It
therefore has to consider provenance, not only confidence: fixture text can
carry any confidence its author typed.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .engine import LineTranscription, Provenance

CONFIDENCE_THRESHOLD = 0.75
MAX_FLAGGED_FRACTION = 0.25


def audit_transcription(lines: List[LineTranscription], doc_id: str) -> Dict[str, Any]:
    """Audit a folio's lines.

    Returns status SIMULATED_NOT_EVIDENCE when any line is fixture output. That
    check comes FIRST and is not overridable by confidence, because the previous
    version of this audit returned PASSED at 0.866 average confidence on five
    blank white images -- the confidence numbers were simply the ones the
    fixture author had written down.
    """
    total = len(lines)
    if total == 0:
        return {"doc_id": doc_id, "status": "FAILED", "reason": "Zero lines segmented"}

    simulated = [i + 1 for i, ln in enumerate(lines) if ln.provenance is Provenance.SIMULATED]
    if simulated:
        return {
            "doc_id": doc_id,
            "status": "SIMULATED_NOT_EVIDENCE",
            "reason": (
                f"{len(simulated)} of {total} lines are fixture output, not a "
                "transcription of these pixels. Confidence scores on simulated "
                "lines are authored constants and carry no information about "
                "the image. This document must not be promoted to the corpus."
            ),
            "simulated_lines": simulated,
            "total_lines": total,
        }

    flagged: List[Dict[str, Any]] = []
    confidences: List[float] = []
    for idx, ln in enumerate(lines):
        confidences.append(ln.confidence)
        issues: List[str] = []
        if ln.confidence < CONFIDENCE_THRESHOLD:
            issues.append(f"Confidence {ln.confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}")
        words = ln.text.split()
        if len(words) > 4 and len(set(words)) <= len(words) // 2:
            issues.append("Repetition loop detected in beam output")
        if issues:
            flagged.append({"line_index": idx + 1, "text": ln.text,
                            "confidence": ln.confidence, "issues": issues})

    avg = sum(confidences) / len(confidences)
    ok = (len(flagged) / total) < MAX_FLAGGED_FRACTION and avg >= CONFIDENCE_THRESHOLD
    return {
        "doc_id": doc_id,
        "status": "PASSED" if ok else "REQUIRES_AGENT_REVIEW",
        "provenance": Provenance.TRANSCRIBED.value,
        "total_lines": total,
        "average_confidence": round(avg, 4),
        "flagged_line_count": len(flagged),
        "flagged_lines": flagged,
    }


def audit_translation_compliance(
    english_translation: str,
    mandatory_terms: List[Tuple[str, str]],
    *,
    translation_provenance: Provenance,
) -> Dict[str, Any]:
    """Check that required lexicon terms appear in a translation.

    `translation_provenance` is required, and not decorative. The earlier
    version compared a hard-coded English string against terms extracted from a
    hard-coded Latin string and reported 100% compliance -- an audit whose
    inputs were both fixtures cannot fail, and reporting a score for it invites
    the number to be quoted as if something had been checked.
    """
    missing = [
        {"canonical_latin": canonical, "expected_english": expected}
        for canonical, expected in mandatory_terms
        if expected.lower() not in english_translation.lower()
    ]
    score = 1.0 if not mandatory_terms else (len(mandatory_terms) - len(missing)) / len(mandatory_terms)
    result: Dict[str, Any] = {
        "lexicon_compliance_score": round(score, 2),
        "missing_terms": missing,
        "compliant": not missing,
        "translation_provenance": translation_provenance.value,
    }
    if translation_provenance is Provenance.SIMULATED:
        result["meaningful"] = False
        result["caveat"] = (
            "Both sides of this comparison are fixtures. The score describes the "
            "fixtures agreeing with each other and says nothing about any model."
        )
    else:
        result["meaningful"] = True
    return result
