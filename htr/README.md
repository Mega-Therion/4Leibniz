# HTR pipeline — Leibniz folio transcription

Segments a folio scan into lines, transcribes them, and emits TEI-XML P5 with
facsimile zone alignment.

## The rule this module exists to enforce

**Synthetic text never looks like a transcription.**

`corpus/README.md` says the corpus layer exists so that *"unverified text is not
mistaken for ground truth."* An HTR pipeline is the most direct way to violate
that, so provenance is a first-class value here rather than a convention:

- `Provenance.TRANSCRIBED` — a model read real pixels. Evidence.
- `Provenance.SIMULATED` — fixture text. **Never promotable to `corpus/latin/`.**

Simulation is opt-in (`simulate=True`). When a real transcription is requested
and no model can load, the engine raises `HTRModelUnavailable` rather than
degrading. `audit_transcription` checks provenance **before** confidence and
returns `SIMULATED_NOT_EVIDENCE` for any simulated line, at any confidence.

## Why it is built this way

The original pipeline was measured before being adopted. Five defects:

| # | Defect | Measured |
|---|---|---|
| 1 | Silent simulation fallback | `except Exception: force_simulation = True` — no log, no marker |
| 2 | Audit passed fabricated text | **5 blank white images → 5 Latin sentences → `PASSED`, avg conf 0.866** |
| 3 | Fabrication reached TEI | serialized under `sourceDesc` = *"Gottfried Wilhelm Leibniz Bibliothek (GWLB) Hanover"* |
| 4 | Abbreviation expansion dead | **no-op on 6/6** inputs, including the exact strings it targeted |
| 5 | Enclitic stripper corrupted Latin | **8 of 14** words, incl. `neque→ne`, `atque→at`, `quoque→quo` |

Defect 3 is the serious one: fabricated Latin attributed to a real archive. The
other four are ordinary bugs; that one is a provenance failure.

### Defect 4 — why the regexes never fired

Every pattern ended `\b` after a non-word character (`}` or `.`). A word
boundary needs a word character on one side; abbreviations are followed by a
space, so the boundary never existed. `\bq_{d}\b` cannot match anything.

### Defect 5 — why the stripper corrupted words

Naive suffix stripping of `-que/-ve/-ne` with an 8-entry exception list.
`neque`, `atque` and `quoque` are top-100 words in classical prose.

### Found while testing the fix — the `vis` declension

`v(is|im|iri?|iribus)` misses **`vi`**, the ablative singular, which is the
commonest form in a dynamics text (*"vi viva"* = *by living force*). `vi mortua`
did not match. Worse, `iri?` matches `vir`/`viri` — forms of *vir* (man), not
*vis* (force). Corrected to `v(is|im|i|ires|irium|iribus)`, verified against all
seven forms plus `vir`/`viri` negative cases.

## Usage

```python
from htr.engine import LeibnizHTREngine, Provenance
from htr.audit import audit_transcription

engine = LeibnizHTREngine()                 # raises if no model can load
lines = engine.transcribe(line_crops)
report = audit_transcription(lines, "LH_XXXV_Folio_12r")

engine = LeibnizHTREngine(simulate=True)    # explicit fixtures, audits as
                                            # SIMULATED_NOT_EVIDENCE
```

## Tests

`tests/test_htr_provenance.py` — 29 tests, one per measured defect. Each carries
the old behaviour in its docstring, so a regression fails with an explanation.
