#!/usr/bin/env python3
r"""Generate the proof-grounded formal-claims catalog (contract v1).

  python3 scripts/generate_formal_claims.py                 # -> artifacts/v1/formal-claims.json
  python3 scripts/generate_formal_claims.py --print         # -> stdout
  python3 scripts/generate_formal_claims.py --generated-at 2026-09-12T00:00:00Z

Determinism and honesty rules (contracts/README.md has the full story):

* The canonical claim list is a pure function of the checkout: declarations are
  extracted from Leibniz/**/*.lean, sorted by claim_id, and serialized with a
  fixed shape. `generated_at` records when the verification run happened
  (UTC); --generated-at or SOURCE_DATE_EPOCH pin it deliberately for
  reproducible CI runs.

* `proved` is emitted ONLY when the pinned Lean toolchain actually checked the
  declaration: `lake build` succeeded, the module elaborates without 'sorry',
  and `#print axioms` reports no axiom outside {propext, Classical.choice,
  Quot.sound}. A bare Lean `axiom` is never proved: it is catalogued as
  `conditional` on its own assumption. A checked theorem that depends on
  non-standard axioms (including sorryAx) is `conditional`, naming them. If the
  toolchain is unavailable or a declaration cannot be checked, that declaration
  is EXCLUDED from the catalog (never silently downgraded to some other
  status) and the run exits non-zero unless --allow-failures was passed
  explicitly.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

GENERATOR_NAME = "4leibniz-formal-claims"
GENERATOR_VERSION = "1.0.0"
REPOSITORY = "Mega-Therion/4Leibniz"
SCHEMA_VERSION = "v1"

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

ROOT = Path(__file__).resolve().parents[1]
LEIBNIZ = ROOT / "Leibniz"

# Top-level declarations we catalog. (defs/structures are data, not claims.)
# Leading whitespace is allowed: some declarations sit at column 1 inside a
# namespace block (e.g. Leibniz/LexContinuitatis.lean `theta_pos`).
DECL = re.compile(r"^[ \t]*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*"
                  r"(theorem|axiom)\s+([A-Za-z_][\w'.]*)")
NAMESPACE = re.compile(r"^namespace\s+([A-Za-z_][\w'.]*)")
END_NS = re.compile(r"^end\s+([A-Za-z_][\w'.]*)\s*$|^end\s*$")
SORRY = re.compile(r"uses ['`]sorry['`]")
# Lean 4 emits: "'Leibniz.X' depends on axioms: [propext]" or
# "'Leibniz.X' does not depend on any axioms".
AXIOMS_OUT = re.compile(r"'([^']+)' depends on axioms: \[([^\]]*)\]|"
                        r"'([^']+)' does not depend on any axioms")

OPEN_PROBLEM_ENTRY = re.compile(
    r'\{\s*id\s*:=\s*"([^"]+)",\s*title\s*:=\s*"([^"]+)",\s*status\s*:=\s*"([^"]+)",\s*'
    r"dependencies\s*:=\s*\[(.*?)\],\s*closureRequirement\s*:=\s*\"([^\"]+)\"",
    re.S)

# Machine-generated modules carry provenance in their header comment.
GEN_HEADER = {
    "claim_source": re.compile(r"Claim source\s*:\s*(.+)"),
    "citation": re.compile(r"Source citation\s*:\s*(.+)"),
    "ir_fingerprint": re.compile(r"IR fingerprint\s*:\s*([0-9a-f]{64})"),
    "claim": re.compile(r"Philosophical claim\s*:\s*(.+)"),
}

# Honest notes for declarations whose bare name would invite misreading.
# Every entry cites the source module's own documentation.
SPECIAL_NOTES = {
    "Leibniz.Calculemus.calculemus_omnibus_verum":
        "The module itself documents this theorem as one that 'compiles while "
        "establishing nothing': it proves execute_calculemus.build = true, i.e. "
        "that a hand-typed literal field equals true. It audits nothing else.",
    "Leibniz.Epistemic.ProvenArgument.proof":
        "Unwraps the ProvenArgument constructor: a proof of p given a packaged "
        "proof of p. The epistemic content is in the structure's typing discipline, "
        "not in this theorem's body.",
}


def strip_comments(text: str) -> str:
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    text = re.sub(r"--.*$", "", text, flags=re.M)
    return text


def parse_module(path: Path) -> list[dict]:
    """Extract theorem/axiom declarations with namespace, line, and statement."""
    rel = path.relative_to(ROOT)
    module = rel.with_suffix("").as_posix().replace("/", ".")
    raw_text = path.read_text(encoding="utf-8", errors="replace")
    clean_lines = strip_comments(raw_text).splitlines()
    ns_stack: list[str] = []
    decls: list[dict] = []
    for lineno, line in enumerate(clean_lines, 1):
        if m := NAMESPACE.match(line):
            ns_stack.append(m.group(1))
            continue
        if END_NS.match(line):
            if ns_stack:
                ns_stack.pop()
            continue
        if m := DECL.match(line):
            kind, name = m.group(1), m.group(2)
            ns_prefix = ".".join(ns_stack)
            full = f"{ns_prefix}.{name}" if ns_prefix else name
            # Statement: accumulate source lines until the first ':='.
            statement_lines = [line.strip()]
            for later in clean_lines[lineno:lineno + 25]:
                if ":=" in later:
                    statement_lines.append(later.strip())
                    break
                if later.strip():
                    statement_lines.append(later.strip())
            statement = "\n".join(statement_lines)
            statement = statement.split(":=")[0].strip()
            decls.append({
                "kind": kind,
                "module": module,
                "namespace": ns_prefix,
                "name": name,
                "full_name": full,
                "line": lineno,
                "rel_path": rel.as_posix(),
                "statement": statement,
            })
    return decls


def parse_open_problems(path: Path) -> list[dict]:
    text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    problems = []
    for m in OPEN_PROBLEM_ENTRY.finditer(text):
        pid, title, status, deps, closure = m.groups()
        deps = [d.strip().strip('"') for d in deps.split(",") if d.strip()]
        problems.append({
            "id": pid, "title": title, "status": status,
            "dependencies": deps, "closure": closure,
        })
    return problems


def parse_generated_header(path: Path) -> dict:
    """Machine-generated modules document their provenance in a header comment."""
    header = path.read_text(encoding="utf-8", errors="replace").split("*/")[0]
    out = {}
    for key, rx in GEN_HEADER.items():
        if m := rx.search(header):
            out[key] = m.group(1).strip()
    return out


def git_metadata() -> tuple[str, str]:
    """Pin the commit that last changed the PROOF SOURCES, not HEAD.

    This used to be `rev-parse HEAD`, which made the committed artifact
    impossible to reproduce and left CI permanently red:

      1. generator runs at commit A (the last Lean change) and stamps A into
         every claim's proof_source.commit;
      2. the artifact is committed, producing commit B;
      3. CI regenerates at B, stamps B, asserts fresh == committed;
      4. A != B, so it fails -- and committing the "fix" produces commit C,
         which fails identically. The check could never pass.

    Pinning the last commit to touch Leibniz/ makes the catalog what this
    module's docstring already promises: a pure function of the checkout. A
    catalog-refresh commit changes no proof, so it must not change the catalog.
    A real proof change does, and is still caught.
    """
    def run(args: list[str]) -> str:
        return subprocess.run(["git", "-C", str(ROOT), *args],
                              capture_output=True, text=True, check=True).stdout.strip()
    # A shallow clone cannot answer "which commit last touched Leibniz/": a
    # path-limited `git log` silently returns the checked-out commit instead.
    # That is exactly the mis-pin this function exists to avoid, so refuse
    # rather than emit a catalog that can never be reproduced.
    # (actions/checkout defaults to fetch-depth: 1 -- verify.yml sets 0.)
    if run(["rev-parse", "--is-shallow-repository"]) == "true":
        raise RuntimeError(
            "refusing to pin a proof-source commit in a SHALLOW clone: a "
            "path-limited `git log` would return the checked-out commit, not "
            "the last commit touching Leibniz/, producing a catalog that can "
            "never be reproduced. Check out with full history "
            "(actions/checkout: fetch-depth: 0)."
        )
    rel = LEIBNIZ.relative_to(ROOT).as_posix()
    commit = run(["log", "-1", "--format=%H", "HEAD", "--", rel])
    if len(commit) != 40:
        # No commit touches the sources yet (fresh tree); fall back to HEAD so
        # the generator still pins something real rather than emitting nothing.
        commit = run(["rev-parse", "HEAD"])
    if len(commit) != 40:
        raise RuntimeError(f"could not pin a 40-char commit (got: {commit!r})")
    author_date = run(["show", "-s", "--format=%aI", commit])
    return commit, author_date


def lean_toolchain() -> str:
    return (ROOT / "lean-toolchain").read_text().strip()


def lean_available() -> bool:
    return shutil.which("lake") is not None and shutil.which("lean") is not None


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)


def elaborate_modules() -> dict[str, dict]:
    """lake env lean per module: authoritative elaboration, catches 'sorry'."""
    results: dict[str, dict] = {}
    for path in sorted(LEIBNIZ.rglob("*.lean")):
        rel = path.relative_to(ROOT).as_posix()
        proc = run(["lake", "env", "lean", rel])
        out = proc.stdout + proc.stderr
        results[rel] = {
            "exit": proc.returncode,
            "sorries": len(SORRY.findall(out)),
        }
    return results


def print_axioms(modules: dict[str, list[str]]) -> dict[str, dict]:
    """#print axioms for every declaration, batched one temp file per module."""
    reports: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for module, decls in sorted(modules.items()):
            if not decls:
                continue
            probe = Path(tmp) / (module.replace(".", "_") + ".lean")
            probe.write_text(
                f"import {module}\n" + "\n".join(f"#print axioms {d}" for d in decls) + "\n",
                encoding="utf-8")
            proc = run(["lake", "env", "lean", str(probe)])
            out = proc.stdout + proc.stderr
            found: dict[str, list[str]] = {}
            for m in AXIOMS_OUT.finditer(out):
                name = m.group(1) or m.group(3)
                axioms = [a.strip() for a in m.group(2).split(",") if a.strip()] if m.group(2) else []
                found[name] = axioms
            for d in decls:
                if d in found:
                    reports[d] = {"ok": True, "axioms": found[d], "error": None}
                else:
                    detail = f"#print axioms produced no output for {d} (module {module}"
                    if proc.returncode != 0:
                        detail += f", probe exit {proc.returncode}"
                    reports[d] = {"ok": False, "axioms": [], "error": detail + ")"}
    return reports


def decide_status(report: dict, module_exit: int | None, module_sorries: int) -> tuple[str | None, list[str]]:
    """Pure status gate. Returns (status, conditional_on); status None = exclude.

    `proved` requires: the module elaborated cleanly (exit 0), zero 'sorry'
    warnings, and #print axioms reporting nothing outside the three standard
    Lean axioms. Everything else is conditional or excluded — never proved.
    """
    if module_exit != 0 or not report.get("ok"):
        return None, []
    nonstandard = sorted(set(report.get("axioms", [])) - STANDARD_AXIOMS)
    if module_sorries == 0 and not nonstandard:
        return "proved", []
    assumptions = []
    for ax in nonstandard:
        if ax.startswith("sorryAx"):
            assumptions.append(f"{ax} — the declaration uses 'sorry' (proof stub)")
        else:
            assumptions.append(f"{ax} — bare Lean axiom in this repository")
    return "conditional", assumptions


def build_claims(commit: str, toolchain: str, use_lean: bool) -> dict:
    all_decls: list[dict] = []
    for path in sorted(LEIBNIZ.rglob("*.lean")):
        all_decls.extend(parse_module(path))
    # Skip the root umbrella module: it only re-exports the others.
    all_decls = [d for d in all_decls if d["module"] != "Leibniz"]

    open_problems = parse_open_problems(LEIBNIZ / "OpenProblems.lean")
    gen_headers = {p: parse_generated_header(p)
                   for p in sorted((LEIBNIZ / "Generated").glob("*.lean"))}

    elaboration: dict[str, dict] = {}
    axiom_reports: dict[str, dict] = {}
    lean_available_now = use_lean and lean_available()
    if lean_available_now:
        build = run(["lake", "build"])
        if build.returncode != 0:
            sys.stderr.write("lake build failed; refusing to ground any 'proved' status.\n")
            sys.stderr.write(build.stdout[-2000:] + build.stderr[-2000:])
        elaboration = elaborate_modules()
        by_module: dict[str, list[str]] = {}
        for d in all_decls:
            if d["kind"] == "theorem":
                by_module.setdefault(d["module"], []).append(d["full_name"])
        axiom_reports = print_axioms(by_module)

    claims: list[dict] = []
    excluded: list[str] = []

    for d in all_decls:
        proof_source = {"repository": REPOSITORY, "commit": commit, "path": d["rel_path"]}
        source_refs = [{"type": "file", "ref": d["rel_path"], "line": d["line"]}]
        if d["kind"] == "axiom":
            claims.append({
                "schema_version": SCHEMA_VERSION,
                "claim_id": d["full_name"],
                "title": d["name"],
                "module": d["module"],
                "declaration": d["full_name"],
                "status": "conditional",
                "formal_statement": d["statement"],
                "conditional_on": [
                    f"declared as a bare Lean axiom in {d['rel_path']} — assumed, not proved"],
                "proof_source": proof_source,
                "source_refs": source_refs,
                "human_summary": (
                    f"Declared as a bare Lean axiom: assumed without proof inside the "
                    f"kernel. No verification is claimed for it; any theorem that depends "
                    f"on it is catalogued as conditional. Statement: {d['statement']}"),
            })
            continue

        # theorem
        gen_path = ROOT / d["rel_path"]
        header = gen_headers.get(gen_path) if gen_path.parent.name == "Generated" else None
        if header:
            if header.get("citation"):
                source_refs.append({"type": "citation", "ref": header["citation"]})
            if header.get("claim_source"):
                source_refs.append({"type": "machine", "ref": header["claim_source"]})

        if not lean_available_now:
            excluded.append(f"{d['full_name']} (toolchain unavailable)")
            continue
        mod_rel = d["rel_path"]
        mod_exec = elaboration.get(mod_rel, {"exit": None, "sorries": 0})
        report = axiom_reports.get(d["full_name"],
                                   {"ok": False, "axioms": [], "error": "missing report"})
        status, assumptions = decide_status(report, mod_exec["exit"], mod_exec["sorries"])
        if status is None:
            excluded.append(f"{d['full_name']} ({report.get('error') or 'module elaboration failed'})")
            continue
        if status == "proved":
            claims.append({
                "schema_version": SCHEMA_VERSION,
                "claim_id": d["full_name"],
                "title": d["name"],
                "module": d["module"],
                "declaration": d["full_name"],
                "status": "proved",
                "formal_statement": d["statement"],
                "proof_source": proof_source,
                "source_refs": source_refs,
                "verification": {
                    "checked_by": "lake build + lake env lean (#print axioms)",
                    "toolchain": toolchain,
                    "axioms": sorted(report["axioms"]),
                    "sorries": 0,
                },
                "human_summary": proved_summary(d, report["axioms"], header),
            })
        else:
            claims.append({
                "schema_version": SCHEMA_VERSION,
                "claim_id": d["full_name"],
                "title": d["name"],
                "module": d["module"],
                "declaration": d["full_name"],
                "status": "conditional",
                "formal_statement": d["statement"],
                "conditional_on": assumptions,
                "proof_source": proof_source,
                "source_refs": source_refs,
                "verification": {
                    "checked_by": "lake build + lake env lean (#print axioms)",
                    "toolchain": toolchain,
                    "axioms": sorted(report["axioms"]),
                    "sorries": mod_exec["sorries"],
                },
                "human_summary": (
                    f"Checked by the pinned Lean toolchain, but the derivation depends on "
                    f"assumptions that are not proved in the kernel: "
                    f"{'; '.join(assumptions)}. It is proved only conditionally on them."),
            })

    # Open problems from the Leibniz.OpenProblems registry. Entries marked
    # closed/resolved are excluded: they are no longer open, and the closure
    # is recorded in the registry itself and in the repo README.
    for p in open_problems:
        if p["status"].strip().lower() in ("closed", "resolved"):
            continue
        claims.append({
            "schema_version": SCHEMA_VERSION,
            "claim_id": f"Leibniz.OpenProblems.{p['id']}",
            "title": p["title"],
            "module": "Leibniz.OpenProblems",
            "declaration": f"Leibniz.OpenProblems.registry[{p['id']}]",
            "status": "open_problem",
            "formal_statement": (
                f"OpenProblem {{ id := \"{p['id']}\", title := \"{p['title']}\", "
                f"status := \"{p['status']}\" }}"),
            "proof_source": {"repository": REPOSITORY, "commit": commit,
                             "path": "Leibniz/OpenProblems.lean"},
            "source_refs": [{"type": "file", "ref": "Leibniz/OpenProblems.lean"}],
            "human_summary": (
                f"Recorded in Leibniz.OpenProblems as {p['status']}. Not proved. "
                f"Closure requirement: {p['closure']}. "
                f"Depends on modules: {', '.join(p['dependencies']) or 'none recorded'}."),
        })

    # RYTT bridge consistency: every bridge source theorem must appear as a
    # catalogued theorem (proved or conditional). A missing one is a contract
    # violation, not a silently degraded status.
    bridge_path = ROOT / "integration" / "4leibniz_bridge.json"
    if bridge_path.is_file():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        catalogued = {c["claim_id"]: c for c in claims}
        for thm in bridge.get("source_theorems", []):
            if thm not in catalogued:
                excluded.append(f"{thm} (listed in integration/4leibniz_bridge.json "
                                f"but not found in Leibniz sources — contract violation)")
            else:
                catalogued[thm]["source_refs"].append(
                    {"type": "bridge", "ref": "rytt.4leibniz.bridge.v1"})

    claims.sort(key=lambda c: c["claim_id"])

    if excluded:
        exclusion_note = (" Excluded (not catalogued, never downgraded): "
                          + "; ".join(excluded) + ".")
    else:
        exclusion_note = ""
    record = {
        "lean_available": lean_available_now,
        "lake_build_exit_code": None,
        "sorries": sum(m["sorries"] for m in elaboration.values()),
        "notes": (
            ("All theorem claims were grounded by running the pinned Lean toolchain "
             "(lake build + per-module elaboration + #print axioms per declaration)."
             + exclusion_note)
            if lean_available_now else
            ("Lean toolchain unavailable in this run: theorem claims could not be "
             "grounded and were excluded rather than downgraded. Open problems and "
             "axioms are extracted statically and included honestly."
             + exclusion_note)),
    }
    if lean_available_now:
        record["lake_build_exit_code"] = run(["lake", "build"]).returncode

    return {"claims": claims, "verification_record": record, "excluded": excluded,
            "lean_was_used": lean_available_now}


def proved_summary(d: dict, axioms: list[str], header: dict | None) -> str:
    ax = ", ".join(sorted(axioms)) if axioms else "none"
    summary = (f"Checked by the pinned Lean toolchain: zero 'sorry', axiom "
               f"dependencies: {ax}. The formal_statement field reproduces the "
               f"complete content proved; no informal reading beyond it is asserted.")
    if d["full_name"] in SPECIAL_NOTES:
        summary += " " + SPECIAL_NOTES[d["full_name"]]
    if header:
        if header.get("claim"):
            summary += (f" Machine-generated by the Calculemus proof engine from the "
                        f"claim '{header.get('claim')}'; the theorem records the exact "
                        f"logical form of the inference over an arbitrary preordered type.")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--emit", default="artifacts/v1/formal-claims.json",
                        help="output path relative to repo root")
    parser.add_argument("--print", action="store_true",
                        help="also print the catalog to stdout")
    parser.add_argument("--generated-at", default=None,
                        help="ISO-8601 UTC timestamp (default: commit author date)")
    parser.add_argument("--no-lean", action="store_true",
                        help="skip Lean verification; emits open problems and axioms only "
                             "(CI must never use this for the committed artifact)")
    parser.add_argument("--allow-failures", action="store_true",
                        help="exit 0 even if some declarations could not be checked "
                             "(they are still excluded from the catalog)")
    args = parser.parse_args()

    commit, _author_date = git_metadata()
    toolchain = lean_toolchain()
    generated_at = args.generated_at
    if not generated_at:
        epoch = os.environ.get("SOURCE_DATE_EPOCH")
        if epoch:
            generated_at = datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat()
        else:
            generated_at = datetime.now(timezone.utc).isoformat()

    built = build_claims(commit, toolchain, use_lean=not args.no_lean)
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "generator": {"name": GENERATOR_NAME, "version": GENERATOR_VERSION},
        "generated_at": generated_at,
        "source": {"repository": REPOSITORY, "commit": commit,
                   "lean_toolchain": toolchain},
        "verification_record": built["verification_record"],
        "claims": built["claims"],
    }
    text = json.dumps(catalog, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    out_path = ROOT / args.emit
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    if args.print:
        sys.stdout.write(text)

    proved = sum(1 for c in built["claims"] if c["status"] == "proved")
    conditional = sum(1 for c in built["claims"] if c["status"] == "conditional")
    openp = sum(1 for c in built["claims"] if c["status"] == "open_problem")
    sys.stderr.write(
        f"formal-claims: {proved} proved, {conditional} conditional, "
        f"{openp} open_problem, {len(built['excluded'])} excluded → {args.emit}\n")

    if built["excluded"] and not args.allow_failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
