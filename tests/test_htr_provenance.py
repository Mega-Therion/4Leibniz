"""Regression tests for the HTR pipeline's provenance and Latin handling.

Every test here corresponds to a measured defect in the original pipeline. The
comments record what the old behaviour actually was, so a future change that
reintroduces it fails with an explanation rather than a bare assertion.
"""
from __future__ import annotations

import pytest
from PIL import Image

from htr.audit import audit_transcription, audit_translation_compliance
from htr.engine import HTRModelUnavailable, LeibnizHTREngine, LineTranscription, Provenance
from htr.latin_morphology import expand_abbreviations, extract_matching_terms, strip_enclitics


# ── provenance ──────────────────────────────────────────────────────────────

def test_unloadable_model_raises_instead_of_fabricating():
    """A real transcription request that cannot load a model must fail loudly.

    Old behaviour: the load error was swallowed and `force_simulation` was set
    to True, so the caller got fixture Latin at 0.93 confidence with nothing
    recording the substitution. This uses a checkpoint that cannot resolve, so
    the test exercises the failure path whether or not torch is installed.
    """
    with pytest.raises(HTRModelUnavailable):
        LeibnizHTREngine(checkpoint="definitely/not-a-real-checkpoint-xyz", simulate=False)


def test_failed_load_does_not_silently_enable_simulation():
    """The engine must not be usable after a failed load."""
    try:
        LeibnizHTREngine(checkpoint="definitely/not-a-real-checkpoint-xyz", simulate=False)
    except HTRModelUnavailable:
        return
    pytest.fail("engine constructed despite an unloadable checkpoint")


def test_simulated_output_is_labelled_simulated():
    engine = LeibnizHTREngine(simulate=True)
    blanks = [Image.new("RGB", (400, 60), "white") for _ in range(3)]
    for line in engine.transcribe(blanks):
        assert line.provenance is Provenance.SIMULATED
        assert not line.is_evidence


def test_audit_refuses_to_pass_simulated_lines():
    """Blank images must never yield a PASSED audit.

    Old behaviour, measured: five blank white images produced five sentences of
    scholarly Latin and the audit returned PASSED with average confidence 0.866.
    """
    engine = LeibnizHTREngine(simulate=True)
    blanks = [Image.new("RGB", (400, 60), "white") for _ in range(5)]
    report = audit_transcription(engine.transcribe(blanks), "BLANK_FOLIO")
    assert report["status"] == "SIMULATED_NOT_EVIDENCE"
    assert report["status"] != "PASSED"
    assert report["simulated_lines"] == [1, 2, 3, 4, 5]


def test_high_confidence_cannot_launder_simulated_output():
    """Provenance is checked before confidence, so a perfect score cannot pass."""
    lines = [LineTranscription("Monas est substantia simplex.", 1.0, Provenance.SIMULATED)]
    assert audit_transcription(lines, "D")["status"] == "SIMULATED_NOT_EVIDENCE"


def test_transcribed_lines_can_pass():
    lines = [LineTranscription(f"Linea {i} cum verbis pluribus hic scripta.", 0.95,
                               Provenance.TRANSCRIBED) for i in range(5)]
    report = audit_transcription(lines, "REAL")
    assert report["status"] == "PASSED"
    assert report["provenance"] == "transcribed"


def test_simulated_translation_audit_is_marked_not_meaningful():
    """A fixture-vs-fixture comparison scores 1.0; it must not read as evidence."""
    result = audit_translation_compliance(
        "living force and endeavor", [("vis viva", "living force"), ("conatus", "endeavor")],
        translation_provenance=Provenance.SIMULATED,
    )
    assert result["lexicon_compliance_score"] == 1.0
    assert result["meaningful"] is False
    assert "caveat" in result


# ── abbreviation expansion ──────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("hoc q_{d} verum est", "hoc quod verum est"),
    ("p_{t} extensionem", "praeter extensionem"),
    ("e.g. corpus", "exempli gratia corpus"),
    ("m.s. folio 12", "manuscriptum folio 12"),
])
def test_abbreviations_actually_expand(raw, expected):
    """Old behaviour: no-op on 6/6 inputs.

    Every pattern ended in `\\b` after a non-word character (`}` or `.`), which
    requires a following word character. Abbreviations are followed by a space,
    so the boundary never existed and expansion never ran once.
    """
    assert expand_abbreviations(raw) == expected


# ── enclitic stripping ──────────────────────────────────────────────────────

@pytest.mark.parametrize("word", [
    "neque", "atque", "quoque", "usque", "quinque", "namque", "cumque", "carne",
    "sive", "bene", "sine", "omne", "nomine", "ordine", "plerumque",
])
def test_common_latin_words_survive_enclitic_stripping(word):
    """Old behaviour corrupted 8 of 14 tested words:

        neque -> ne    atque -> at    quoque -> quo    usque -> us
        quinque -> quin    namque -> nam    cumque -> cum    carne -> car

    `neque`, `atque` and `quoque` are top-100 words in classical Latin prose.
    """
    assert strip_enclitics(word) == word


@pytest.mark.parametrize("compound,stem", [
    ("populusque", "populus"),
    ("armaque", "arma"),
])
def test_genuine_enclitics_are_still_stripped(compound, stem):
    """The fix must not simply disable stripping."""
    assert strip_enclitics(compound) == stem


def test_lexicon_matches_declined_forms():
    terms = dict(extract_matching_terms("Hinc patet vim vivam a vi mortua differre."))
    assert terms.get("vis viva") == "living force"
    assert terms.get("vis mortua") == "dead force"
