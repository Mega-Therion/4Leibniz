# Contributing to 4Leibniz

4Leibniz is organized into three layers. The **corpus** preserves historical witnesses, the **Leibniz** directory contains the Lean proof kernel, and **frontier** contains explicitly modern RYTT extensions. Please do not mix modern interpretations into diplomatic Latin files.

## Latin scholars

Choose a record in `corpus/manuscripts/catalog.json`. Submit the scan or stable edition locator, a diplomatic transcription with the required header, and a separate normalized reading or English translation. Keep uncertain readings marked rather than silently resolving them.

## Lean contributors

Run `./scripts/setup_lean.sh` once, then `lake build`. Add a theorem under the appropriate `Leibniz/` namespace, cite its historical dependency in `Leibniz/Sources.lean`, and run `python3 scripts/check_sorries.py`. New axioms require an explicit justification in the pull request.

## RYTT/frontier contributors

Modern balanced ternary, holonomy, and Stiefel constructions belong under `frontier/`. Use the adapter's `source_theorems` field to identify the kernel results being extended. Do not present an adapter result as a historical claim.

## Volunteer compute

Install the package dependencies, create a JSON work unit, and run one bounded task with `python3 volunteer/client.py work-unit.json --root .`. The worker accepts only the two allow-listed deterministic task kinds and never evaluates arbitrary code. Review the output before submitting it.

## Checks

```bash
python3 -m pytest -q
lake build
python3 scripts/check_sorries.py
python3 scripts/proof_receipt.py
```
