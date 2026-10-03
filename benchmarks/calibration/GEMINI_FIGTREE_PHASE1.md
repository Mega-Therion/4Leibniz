# FIG TREE — Phase 1: Asset Inventory

You are building the input ledger for a full-length FIG Tree monograph. This phase is
**inventory only**. Do not write any monograph prose, any summary, any assessment of
quality, or any statement about whether something is correct. You are a surveyor, not
an author or a judge.

## Scope

Repository: `/home/mega/Res-Nova` — these six directories, 109 files:

    01_foundational_action      02_galaxy_dynamics       03_observer_jwst
    04_cosmology                05_lean_formalization    06_unification_and_spin

Also in scope: `/home/mega/Res-Nova/FIG_TREE_MONOGRAPH.md` and
`FIG_TREE_ARCHITECTURE_MAP.md`, and `/home/mega/4Leibniz/Leibniz/*.lean`.

## Deliverable

ONE file: `/home/mega/Res-Nova/FIG_TREE_ASSET_LEDGER.md`

One row per file, grouped by directory. For every file record exactly these fields:

| field | how to fill it |
| --- | --- |
| `path` | repo-relative |
| `lines` | `wc -l` |
| `kind` | tex / lean / python / markdown / data / other |
| `claims` | the single main assertion the file makes, quoted from the file, with the line number. If the file makes no assertion (a utility script, a data loader), write `none`. |
| `pillar` | which FIG Tree pillar it feeds: I (horizon tension / a_0), II (Stiefel V_5,2 / holographic), III (Thorne spin ceiling), IV (Lindblad anti-drift gate), or `unassigned`. Do not force a fit — `unassigned` is a valid and useful answer. |
| `executes` | see below |
| `exit_code` | see below |
| `output_tail` | see below |
| `depends_on` | external data or packages the file needs, if any (e.g. SPARC data files, Mathlib) |

## The `executes` / `exit_code` / `output_tail` fields — read carefully

For every `.py` file: run it. For every `.lean` file: build it with the appropriate
`lake build` target. For every `.tex` file: attempt `pdflatex` twice.

Record:

- `executes`: `yes` if you ran it, `no` if you could not run it (say why in one clause)
- `exit_code`: the literal integer exit code
- `output_tail`: the last 3 lines of stdout/stderr, verbatim, in a code span

**You must not write any of these words in these fields: verified, validated,
confirmed, passing, correct, proven, successful.** Record the exit code and the
output. The exit code is the fact. An interpretation of the exit code is not wanted
and will be treated as a defect.

If a file takes longer than 5 minutes, kill it and record `exit_code: TIMEOUT`.
If a file needs data you do not have, record `exit_code: MISSING_INPUT` and name the
input in `depends_on`.

## Second deliverable — inside the same file

A section `## Gaps` listing, in plain sentences:

1. Every pillar (I, II, III, IV) that has **no** executable asset backing it.
2. Every `.tex` file that fails to compile, with the first error line.
3. Every `.lean` file containing `sorry`, with file and line numbers.
4. Every claim in `FIG_TREE_MONOGRAPH.md` that you could not trace to any file in
   the inventory.

State these flatly. Do not propose fixes. Do not soften. A long `## Gaps` section is
a successful outcome of this phase, not a failure — it is the actual product.

## Rules

- **Write nothing outside `FIG_TREE_ASSET_LEDGER.md`.** Do not edit any existing file.
  Do not create the monograph. Do not "improve" anything you read.
- **Do not summarise the physics.** You are recording what is on disk, not what it means.
- **Do not resolve contradictions you find.** Record both sides and their line numbers.
- If you cannot determine a field, write `UNKNOWN`. Never guess a value into a table.

## When you are done

Report back with only:

- the path to the ledger
- `wc -l` of it
- the count of files inventoried, and how many of those you actually executed
- the number of entries in `## Gaps`

Do not summarise your findings in chat. The file is the deliverable.
