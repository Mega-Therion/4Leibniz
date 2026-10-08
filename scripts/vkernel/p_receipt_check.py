#!/usr/bin/env python3
"""[P] receipt check: does every proved-tier row have a verifying vkernel record?

Usage: p_receipt_check.py ROWS.json RECORDS_DIR SOURCE_DIR [--trusted trusted_signers.json] [--md OUT.md]

ROWS.json: {"rows": [{"row", "tier", "modules": [...], "named_in_row": bool, "prefixes": [...]}, ...]}
For each record RECORDS_DIR/*.json (sidecars *.vacuity.json excluded): run verify.py with
--source SOURCE_DIR --require-checker; a record covers the modules in its checker_runs.
A row passes when it names its modules (or they are inferred and say so), every module is
covered by a record that verifies, and the record is fresh (source commitment matches).
The vacuity sidecar's classes for the row's theorems are reported, never used as a pass.
Exit 0 if every "[P]" row passes, 1 otherwise. "[P/O]" rows are reported but do not fail.
"""
import json, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rows_path, rec_dir, src = Path(args[0]), Path(args[1]), Path(args[2])
    opts = sys.argv
    trusted = Path(opts[opts.index("--trusted") + 1]) if "--trusted" in opts else HERE / "trusted_signers.json"
    rows = json.loads(rows_path.read_text())["rows"]
    records = []
    for f in sorted(rec_dir.glob("*.json")):
        if f.name.endswith(".vacuity.json") or f.name == rows_path.name:
            continue
        try:
            rec = json.loads(f.read_text())
            payload = rec["payload"]
        except (ValueError, KeyError):
            continue
        r = subprocess.run([sys.executable, str(HERE / "verify.py"), str(f), str(trusted), "--source", str(src),
                            "--require-checker"], capture_output=True, text=True)
        mods = {c["module"] for c in payload.get("checker_runs", []) if c.get("ok")}
        side = f.with_name(f.stem + ".vacuity.json")
        vac = {}
        if side.exists():
            try:
                vac = {x["theorem"]: x["statement"] for x in json.loads(side.read_text())["results"]}
            except (ValueError, KeyError):
                pass
        records.append({"file": f.name, "verified": r.returncode == 0, "modules": mods, "vacuity": vac,
                        "why": " ".join(r.stdout.split())[:160] if r.returncode else ""})
    out = ["| row | tier | module named in row | modules | receipt | verifies | vacuity screen (row's theorems) |",
           "|---|---|---|---|---|---|---|"]
    failed = 0
    for row in rows:
        mods = row.get("modules", [])
        cover = {m: [r for r in records if m in r["modules"]] for m in mods}
        ok_mods = all(any(r["verified"] for r in cover[m]) for m in mods) if mods else False
        files = sorted({r["file"] for m in mods for r in cover[m]})
        vac = Counter()
        for r in records:
            for t, s in r["vacuity"].items():
                if any(t.startswith(p) for p in row.get("prefixes", [])):
                    vac[s] += 1
        vtxt = ", ".join(f"{k} {n}" for k, n in sorted(vac.items())) or "-"
        named = "yes" if row.get("named_in_row") else ("no (inferred)" if mods else "no")
        verifies = "-" if not mods else ("yes" if ok_mods else "NO")
        passed = bool(mods) and ok_mods
        if row["tier"] == "[P]" and not passed:
            failed += 1
        out.append(f"| {row['row']} | {row['tier']} | {named} | {', '.join(mods) or '(none)'} | "
                   f"{', '.join(files) or 'none'} | {verifies} | {vtxt} |")
    bad = [r for r in records if not r["verified"]]
    if bad:
        out += ["", "Records that do not verify:"] + [f"- `{r['file']}`: {r['why']}" for r in bad]
    out += ["", f"[P] rows without a verifying receipt: {failed} of {sum(1 for r in rows if r['tier'] == '[P]')}."]
    text = "\n".join(out)
    if "--md" in opts:
        Path(opts[opts.index("--md") + 1]).write_text(text + "\n")
    print(text)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
