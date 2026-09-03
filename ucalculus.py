"""Universal-calculus intermediate language for readable claim declarations.

Example::

    claim Stability:
      given drive u >= dissipation gamma
      given gamma >= continuity_floor
      infer u >= continuity_floor
      source: Harmonia Praestabilita

The compiler emits a typed JSON IR and a Lean theorem skeleton. It intentionally
emits proof obligations rather than pretending that an unproved inference is a
kernel theorem.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import re
from pathlib import Path

_STATUS = {"open", "conjectured", "axiomatic", "derived", "proven"}

@dataclass(frozen=True)
class Premise:
    text: str
    normalized: str

@dataclass(frozen=True)
class Claim:
    name: str
    premises: tuple[Premise, ...]
    conclusion: str
    source: str | None = None
    status: str = "open"
    tags: tuple[str, ...] = ()

@dataclass(frozen=True)
class ArgumentIR:
    language: str
    version: str
    claim: Claim
    fingerprint: str
    proof_obligations: tuple[str, ...]

class SyntaxError(ValueError):
    pass

def _normalize(text: str) -> str:
    return re.sub(r"\\s+", " ", text.strip())

def parse(text: str) -> Claim:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("claim ") or not lines[0].endswith(":"):
        raise SyntaxError("expected `claim Name:` as the first declaration")
    name = lines[0][6:-1].strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise SyntaxError(f"invalid claim name: {name}")
    premises: list[Premise] = []
    conclusion: str | None = None
    source: str | None = None
    status = "open"
    tags: list[str] = []
    for line in lines[1:]:
        if line.startswith("given "):
            body = _normalize(line[6:])
            if not body:
                raise SyntaxError("a given clause cannot be empty")
            premises.append(Premise(text=body, normalized=body.replace(">=", " ≥ ").replace("->", " → ")))
        elif line.startswith("infer "):
            if conclusion is not None:
                raise SyntaxError("a claim may have only one infer clause")
            conclusion = _normalize(line[6:])
        elif line.startswith("source:"):
            source = line[7:].strip()
        elif line.startswith("status:"):
            status = line[7:].strip().lower()
            if status not in _STATUS:
                raise SyntaxError(f"unknown status {status!r}; expected one of {sorted(_STATUS)}")
        elif line.startswith("tag:"):
            tags.extend(tag.strip() for tag in line[4:].split(",") if tag.strip())
        else:
            raise SyntaxError(f"unrecognized clause: {line}")
    if conclusion is None:
        raise SyntaxError("missing `infer ...` conclusion")
    return Claim(name=name, premises=tuple(premises), conclusion=conclusion,
                 source=source, status=status, tags=tuple(tags))

def compile_claim(claim: Claim) -> ArgumentIR:
    payload = json.dumps(asdict(claim), sort_keys=True, ensure_ascii=False).encode()
    fingerprint = hashlib.sha256(payload).hexdigest()
    obligations = tuple([*(premise.text for premise in claim.premises), claim.conclusion])
    return ArgumentIR(language="Leibniz Universal Calculus", version="0.1", claim=claim,
                      fingerprint=fingerprint, proof_obligations=obligations)

def emit_lean(ir: ArgumentIR) -> str:
    c = ir.claim
    assumptions = "\n".join(f"  (h{i} : {p.text})" for i, p in enumerate(c.premises, 1))
    source = f"\nSource: {c.source}" if c.source else ""
    return (f"/-- Generated from Universal Calculus IR {ir.fingerprint}.{source} -/\n"
            f"theorem {c.name}{' ' if assumptions else ''}{assumptions} : {c.conclusion} := by\n"
            f"  sorry\n")

def compile_text(text: str) -> dict:
    ir = compile_claim(parse(text))
    result = asdict(ir)
    result["lean"] = emit_lean(ir)
    return result

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Compile a Leibniz universal-calculus claim")
    parser.add_argument("path", type=Path)
    parser.add_argument("--emit-lean", type=Path)
    args = parser.parse_args()
    result = compile_text(args.path.read_text())
    if args.emit_lean:
        args.emit_lean.write_text(result.pop("lean"))
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
