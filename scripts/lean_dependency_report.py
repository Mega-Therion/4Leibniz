"""Report source-level Lean imports and declarations; not a full elaborated proof graph."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)", re.M)
DECL_RE = re.compile(r"^\s*(theorem|lemma|def|abbrev|example|structure|inductive|class)\s+([A-Za-z0-9_'.]+)", re.M)

def report(root: Path) -> dict:
    files = sorted(root.glob("Leibniz/**/*.lean"))
    modules = []
    all_names = {}
    for path in files:
        source = path.read_text(encoding="utf-8")
        module = ".".join(path.with_suffix("").relative_to(root).parts)
        imports = IMPORT_RE.findall(source)
        declarations = [{"kind": kind, "name": name} for kind, name in DECL_RE.findall(source)]
        theorem_like = [item for item in declarations if item["kind"] in {"theorem", "lemma", "example"}]
        modules.append({"file": str(path.relative_to(root)), "module": module, "imports": imports, "declarations": declarations, "theorem_like_count": len(theorem_like)})
        for item in declarations: all_names[f"{module}.{item['name']}"] = item["kind"]
    edges = [{"module": item["module"], "imports": item["imports"]} for item in modules]
    return {"schema": "4leibniz.lean-dependencies.v1", "scope": "source-level imports and declaration inventory; elaborated theorem-to-theorem dependencies require Lean environment tracing", "module_count": len(modules), "declaration_count": len(all_names), "theorem_like_count": sum(item["theorem_like_count"] for item in modules), "modules": modules, "import_graph": edges}

def markdown(data: dict) -> str:
    lines = ["# Lean dependency report", "", f"- Modules: {data['module_count']}", f"- Declarations: {data['declaration_count']}", f"- Theorem-like declarations: {data['theorem_like_count']}", "", "> This is a reproducible source-level import/declaration inventory. It does not claim a full elaborated theorem-to-theorem dependency graph.", "", "## Module inventory", "", "| Module | Imports | Theorem-like declarations |", "|---|---|---:|"]
    for item in data["modules"]: lines.append(f"| `{item['module']}` | {', '.join(f'`{x}`' for x in item['imports']) or '—'} | {item['theorem_like_count']} |")
    lines += ["", "## Declaration details", ""]
    for item in data["modules"]:
        lines.append(f"### `{item['module']}`")
        for declaration in item["declarations"]: lines.append(f"- `{declaration['kind']}` `{declaration['name']}`")
        lines.append("")
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=Path(".")); parser.add_argument("--json", type=Path, default=Path("lean-dependency-report.json")); parser.add_argument("--markdown", type=Path, default=Path("docs/LEAN_DEPENDENCY_REPORT.md")); args = parser.parse_args()
    data = report(args.root); args.json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8"); args.markdown.parent.mkdir(parents=True, exist_ok=True); args.markdown.write_text(markdown(data) + "\n", encoding="utf-8"); print(json.dumps({"modules": data["module_count"], "declarations": data["declaration_count"], "theorem_like": data["theorem_like_count"]}, indent=2))
if __name__ == "__main__": main()
