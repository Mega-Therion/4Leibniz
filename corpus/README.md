# Layer 1 — Critical Historical Corpus

This directory is the philological layer of 4Leibniz. It is intentionally independent of the Lean kernel and the modern RYTT extensions.

## Data model

- `manuscripts/catalog.json` records archive shelfmarks, dates, edition locators, and transcription status.
- `latin/` contains diplomatic Latin only after a witness has been checked against a scan or critical edition.
- `translations/` contains parallel English translations and historical notes; translations never replace the Latin witness.

The catalog currently identifies the three priority witnesses requested by the project. Their status is explicitly marked `source-identified-transcription-needed` until a scan or critical-edition witness is attached. This prevents unverified text from being mistaken for ground truth.

## Contribution rule

Every text file must carry a header naming the witness, folio or edition page, transcriber, date, and normalization policy. Do not silently modernize spelling, punctuation, abbreviations, or mathematical notation. Put normalized readings in a separate file.
