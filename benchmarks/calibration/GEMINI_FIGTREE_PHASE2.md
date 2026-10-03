# FIG TREE — Phase 2: Make the Lean and the TeX Build

Phase 1 produced `/home/mega/Res-Nova/FIG_TREE_ASSET_LEDGER.md`. Read it first.
It is now correct: every line-cited claim was re-read from disk and matched.

This phase is **repair only**. Do not write monograph prose. Do not edit any `.md`
file except the one ledger file named below. Do not create new documents.

## Read this before you touch anything

`/home/mega/AGENTS.md`. Four rules. The one that matters most here: **never clone
over an existing path.** On 2026-09-03 an agent ran
`git clone --depth 1 ... /home/mega/Res-Nova` and destroyed 135 commits of history.
If a repo looks missing, run `repo-guard check`, then `repo-guard repair`. Never clone.

## Task A — resolve the 30 MISSING_INPUT rows

All 30 fail for one reason: Mathlib is absent from
`/home/mega/Res-Nova/05_lean_formalization/.lake`. There is now 16 GB free.

    cd /home/mega/Res-Nova/05_lean_formalization
    lake exe cache get
    lake build

Then build every Lean module in that directory individually and record, per module:
the exact `lake build` command, the integer exit code, and the last 3 lines of output
verbatim.

Do not create symlinks to another project's `.lake`. Do not `rm -rf` any `.lake`
directory. If the build fails, record the failure and move to the next module.

## Task B — fix the 4 TeX compile failures

From `## Gaps` section 2:

1. `01_foundational_action/PAPER_01_MU_DERIVATION_ACTION.tex`
   missing `figs/e8_sigil_codex.pdf`
2. `01_foundational_action/PRD_Relativistic_Extension.tex`
   missing `PRD_supplementary/figures/cmb_power_spectrum.pdf`
3. `01_foundational_action/Res_Nova_Geometrically_Ordered_Dynamics_and_Information_Tension.tex`
   `! Package xcolor Error: Undefined color 'gold'.`
4. `03_observer_jwst/IO_OI_ACADEMIC.tex`
   `! Missing $ inserted.`

For 3 and 4 the fault is in the `.tex` and you may fix it: define the missing colour;
find and close the unmatched math delimiter. Change as little as possible and record
the exact diff.

For 1 and 2 the fault is a missing figure file. **Search the filesystem for it first**
(`find /home/mega -name 'e8_sigil_codex*'`). If the figure exists elsewhere, record
the path — do not copy it into place. If it does not exist anywhere, record that. Do
not generate a replacement figure, do not comment out the `\includegraphics`, do not
switch to draft mode.

## Task C — record what you did

Append one section to `FIG_TREE_ASSET_LEDGER.md` titled `## Phase 2 — Repair Log`,
containing only:

- a table of every Lean module: `module | command | exit_code | output_tail`
- for each of the 4 TeX files: what you changed (diff), or why you did not change it
- the new `lake build` exit code for the whole `05_lean_formalization` package

Do not edit any existing row of the Phase 1 table. Do not edit the `## Gaps` section.
Append only.

## Constraints — read these as strictly as the tasks

**Record measurements, not conclusions.** An exit code is a measurement. "Builds
cleanly", "passes", "verified" are conclusions and are not wanted. If you find yourself
about to characterise a result, print the result instead.

**If a constraint prevents you from reporting something accurately, say so.**
Do not paraphrase, substitute, or rewrite command output, file names, or error text to
fit any rule. Verbatim or an explicit statement that you cannot reproduce it verbatim.
Altering a transcript is a more serious defect than any finding it could hide.

**Do not repair anything not listed above.** If you find another defect, add it to the
repair log as a line beginning `FOUND, NOT FIXED:` and leave it alone.

## Report back with only

- `lake build` exit code for the package
- how many Lean modules built at exit 0, out of how many attempted
- which of the 4 TeX files now compile at exit 0
- the count of `FOUND, NOT FIXED:` lines

No summary. The ledger is the deliverable.
