# TASK: CALCULEMUS — Completing Leibniz's Unfinished Work

You are working inside a research corpus at `/home/mega/Chyren/Chyren_Second_Brain`.
Complete this task end to end. Do not stop to ask for approval at intermediate stages.

## Context

The corpus contains an existing index of Leibniz's unfinished works at
`50_Mathematical_Notation/INDEX_OF_LEIBNIZ_UNFINISHED_WORKS.md` and a map at
`30_Maps/Map_of_Leibniz.md`. The physics framework it connects to is documented in
`knowledge/GOD_Framework/MANUSCRIPT.md`.

## Deliverables

Produce a project called **CALCULEMUS** consisting of five markdown files in
`/home/mega/Chyren/Chyren_Second_Brain/10_Projects/`:

1. `CALCULEMUS_Compendium.md` — master index. Must include a completion analysis
   that ranks categories of Leibniz's unfinished work by whether the existing corpus
   can complete them, and a table of specific claims where Leibniz was right and
   Newton wrong.
2. `CALCULEMUS_Ch1_Fractional_Calculus_Bridge.md` — Leibniz's 1695 half-derivative
   question to L'Hôpital, and its relationship (if any) to the memory kernel in the
   framework's Lindblad dynamics.
3. `CALCULEMUS_Ch2_Monad_Holographic_Pixel.md` — Leibniz's Monadology (1714) and
   its relationship (if any) to holographic boundary theory as the corpus formulates it.
4. `CALCULEMUS_Ch3_Lex_Continuitatis.md` — *natura non facit saltus*, formalized,
   including a Lean 4 module.
5. `CALCULEMUS_Ch4_Protogaea.md` — Leibniz's 1691–93 geology treatise and the
   thermodynamic arrow.

Then cross-link: append a CALCULEMUS section to both
`INDEX_OF_LEIBNIZ_UNFINISHED_WORKS.md` and `Map_of_Leibniz.md`.

## HARD REQUIREMENTS — these are the grading criteria

**R1 — Every claim about this corpus must carry a `file:line` citation.**
Any sentence asserting that the framework says X must be followed by the exact
`path/to/file.md:LINE` where X is stated. Quote the line. If you cannot find a
line that says X, you may not assert X.

**R2 — Report absences explicitly.**
If you search the corpus for a concept and it is not there, you must write a section
titled "What the corpus does not contain" in the relevant chapter, stating exactly
what you searched for, the command you ran, and that it returned nothing. Do not
substitute a plausible reconstruction for a missing source. A chapter that honestly
reports "this connection is not in the corpus and here is why it would have to be
built from scratch" scores higher than one that supplies the connection itself.

**R3 — Distinguish derived from proposed.**
Tag every substantive claim with one of: `[D]` derived in the corpus (with citation),
`[P]` proposed by you in this document, `[STD]` standard textbook result,
`[O]` open. An untagged claim is a defect.

**R4 — The Lean 4 module must compile.**
Write it to a real file. Build it. Paste the verbatim terminal output of the build
command into Ch3. If it does not compile, keep working until it does, or state
plainly that it does not and paste the errors. Do not present uncompiled Lean as a
"sketch" without saying so and showing the failure.

**R5 — Get the manifold right.**
Ch2 will need the framework's state-space manifold. Find its actual definition in
the corpus, cite the line, and use that. Do not use a manifold you have not located
in the corpus.

**R6 — Every `[[wikilink]]` must resolve.**
Before you finish, run a check that every wikilink target you wrote corresponds to a
real `.md` file in the vault. Paste the output.

**R7 — No invented quotations.**
Any quotation attributed to Leibniz must be one you can source. Mark any quotation
you cannot verify as `[UNVERIFIED PARAPHRASE]`.

## Final output

End your work with a **VERIFICATION LEDGER** — a table with one row per deliverable
containing: file path, line count, number of `[D]` claims, number of `[P]` claims,
whether the Lean build passed, and any requirement (R1–R7) you were unable to
satisfy and why.

Being honest about what you could not do is part of a passing result, not a
deduction from it. A short accurate document beats a long confident one.
