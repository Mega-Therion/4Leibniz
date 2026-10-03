# CALCULEMUS — correction pass

The five monographs, the cross-links, and the Lean module are accepted. An independent
audit confirmed: all line counts exact, 79/79 wikilinks resolve, all epistemic tag counts
exact, every `file:line` citation lands, every "What the corpus does not contain" negative
report is true, and `lake build LexContinuitatis` returns exit 0 with 0 `sorry`.

Three defects remain, all in the VERIFICATION LEDGER itself. Fix these and nothing else.

## D1 — False Lean status in the ledger

The ledger row for `10_Projects/CALCULEMUS_Compendium.md` reports
`PASSED (0 errors, 0 sorry)` in the Lean 4 Build Status column. That file contains no Lean
code. The value was auto-filled by a filename substring match in your reporting script, not
measured. Correct it to `N/A (Analytical)`.

Then re-check every other row of that column against what was actually built. Only
`CALCULEMUS_Ch3_Lex_Continuitatis.md` may claim a build status.

## D2 — R7 claimed satisfied without evidence

Every ledger row states "R1–R7 Fully Satisfied". R7 requires marking any quotation you
cannot source as `[UNVERIFIED PARAPHRASE]`. No quotation in any of the five documents
carries that marker, and the documents contain numerous Latin and French quotations
attributed to Leibniz that are not present anywhere in this corpus.

For each such quotation, state which of these is true and act accordingly:

- you reproduced it from a verifiable printed edition you can name precisely — leave it,
  and cite the edition;
- you reconstructed or translated it from memory — mark it `[UNVERIFIED PARAPHRASE]`.

Then change the ledger's requirements column to state R7's real status per file rather than
a blanket claim.

## D3 — Internal ledger disagrees with final ledger

The "Epistemic Tag Ledger for Compendium" at the foot of
`10_Projects/CALCULEMUS_Compendium.md` reports `[D]` 8, `[STD]` 14. The final VERIFICATION
LEDGER reports 17 and 23 for the same file. The final ledger is the correct one. Recompute
the in-document ledger by actual count and correct it. Check the other four chapters' in-document
ledgers the same way.

## Verification required before you report back

Run and paste verbatim terminal output for both:

    cd /home/mega/Chyren/Chyren_Second_Brain/50_Mathematical_Notation/formalization && lake build

    wc -l 10_Projects/CALCULEMUS_*.md 50_Mathematical_Notation/INDEX_OF_LEIBNIZ_UNFINISHED_WORKS.md 30_Maps/Map_of_Leibniz.md

The full `lake build` (not just the LexContinuitatis target) has not yet been verified since
you edited `lakefile.lean`. Confirm `GodPipeline` still builds.

## Standing rule for the ledger

No cell in a verification ledger may contain a value you did not measure. If a value cannot
be measured, write `NOT MEASURED` and say why. A ledger reporting a status it did not check
is worse than no ledger, because it is the instrument used to decide whether to trust
everything else in the document.
