#!/usr/bin/env python3
"""V-KERNEL canonicalization and domain-separated hashing (protocol vkernel/0.2).

The old `canon()` was `json.dumps(sort_keys, separators)` -- the exact "ad hoc sorted
JSON" the V-KERNEL v3 brief warns against: it silently accepts duplicate keys on parse,
accepts floats, and frames nothing. This module replaces it with a strict, bounded
canonical form plus domain-separated hashing, so a tampered or ambiguous record is
rejected before it is ever hashed or trusted.

Profile: "jcs/0.2" -- an RFC 8785 subset. Protocol JSON here is integers, strings,
booleans, null, arrays and objects only; FLOATS ARE FORBIDDEN, so the hard part of JCS
(number canonicalization) does not arise and canonical bytes are unambiguous.

Guarantees:
  canon(obj)      -> bytes: UTF-8, recursively sorted keys, no insignificant whitespace,
                    rejects float/NaN/Inf and out-of-range ints. Deterministic.
  strict_load(s)  -> object: parse untrusted JSON, REJECTING duplicate keys, floats,
                    NaN/Inf, oversized input and over-deep nesting.
  payload_digest(p) -> "sha256:<hex>" over a domain-separated encoding of canon(p).
  signing_message(digest) -> the exact bytes that get signed/verified (framed).
  dsha(tag, *parts) -> domain-separated, length-framed SHA-256 hex.

Self-test: vkcanon.py --selftest  (prints test vectors and checks them).
"""
import hashlib
import json
import sys

PROTOCOL = "vkernel/0.2"
MAX_INT = 2**53 - 1            # safe-integer bound, stated explicitly
MAX_BYTES = 8 * 1024 * 1024    # 8 MiB input ceiling
MAX_DEPTH = 64
MAX_STR = 1 << 20             # 1 MiB per string
US = b"\x1f"                  # unit separator for domain framing


class CanonError(ValueError):
    """A value or document that the canonical form refuses."""


def _check(obj, depth=0):
    if depth > MAX_DEPTH:
        raise CanonError(f"nesting exceeds {MAX_DEPTH}")
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, float):
        raise CanonError("floats are forbidden in protocol JSON")
    if isinstance(obj, int):
        if abs(obj) > MAX_INT:
            raise CanonError(f"integer {obj} outside safe range +/-{MAX_INT}")
        return
    if isinstance(obj, str):
        if len(obj) > MAX_STR:
            raise CanonError("string exceeds length bound")
        return
    if isinstance(obj, list):
        for v in obj:
            _check(v, depth + 1)
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise CanonError("object keys must be strings")
            _check(v, depth + 1)
        return
    raise CanonError(f"unsupported type {type(obj).__name__}")


def canon(obj) -> bytes:
    """Canonical bytes for a protocol object. Raises CanonError on anything ambiguous."""
    _check(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _no_dupes(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise CanonError(f"duplicate key {k!r}")
        d[k] = v
    return d


def _reject_float(_s):
    raise CanonError("floats are forbidden in protocol JSON")


def _reject_const(c):
    raise CanonError(f"{c} is forbidden in protocol JSON")


def strict_load(text):
    """Parse untrusted JSON text, failing closed on duplicate keys, floats, NaN/Inf,
    oversize input and over-deep nesting."""
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    if len(text) > MAX_BYTES:
        raise CanonError("input exceeds size bound")
    obj = json.loads(text, object_pairs_hook=_no_dupes,
                     parse_float=_reject_float, parse_constant=_reject_const)
    _check(obj)
    return obj


def dsha(tag: str, *parts) -> str:
    """Domain-separated, length-framed SHA-256. Each part is bytes or str; its byte
    length is framed in, so H(a,b) can never collide with H(a+b)."""
    h = hashlib.sha256()
    h.update(PROTOCOL.encode() + US + tag.encode() + US)
    for part in parts:
        b = part if isinstance(part, bytes) else str(part).encode("utf-8")
        h.update(str(len(b)).encode() + b":")
        h.update(b)
    return h.hexdigest()


def payload_digest(payload) -> str:
    return "sha256:" + dsha("payload", canon(payload))


def signing_message(digest: str) -> bytes:
    """The exact bytes signed and verified. Frames the digest under its own tag so a
    signature over the payload can never be replayed as a signature over anything else."""
    return PROTOCOL.encode() + US + b"sigmsg" + US + digest.encode("utf-8")


def _selftest() -> int:
    ok = []

    def check(name, cond):
        ok.append(bool(cond))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # canonical order is independent of input key order
    a = canon({"b": 1, "a": [3, {"y": 2, "x": 1}]})
    b = canon({"a": [3, {"x": 1, "y": 2}]} | {"b": 1})
    check("key order does not change canonical bytes", a == b)
    check("canonical vector is exact", a == b'{"a":[3,{"x":1,"y":2}],"b":1}')
    check("floats rejected by canon", _raises(lambda: canon({"x": 1.5})))
    check("big int rejected", _raises(lambda: canon({"n": 2**53})))
    check("duplicate keys rejected on load", _raises(lambda: strict_load('{"a":1,"a":2}')))
    check("NaN rejected on load", _raises(lambda: strict_load('{"x": NaN}')))
    check("float rejected on load", _raises(lambda: strict_load('{"x": 1.5}')))
    check("good doc loads", strict_load('{"a":1,"b":[true,null,"z"]}') == {"a": 1, "b": [True, None, "z"]})
    # domain separation: framed hash of (a,b) differs from hash of concatenation
    check("length framing blocks concat collision", dsha("t", "ab", "c") != dsha("t", "a", "bc"))
    check("different tags give different digests", dsha("x", "p") != dsha("y", "p"))
    d = payload_digest({"evidence_mode": "signed-service", "n": 1})
    check("payload_digest is sha256-prefixed hex", d.startswith("sha256:") and len(d) == 71)
    check("signing_message frames the digest", signing_message(d).startswith(PROTOCOL.encode()) and d.encode() in signing_message(d))
    print(f"vkcanon self-test: {'PASS' if all(ok) else 'FAIL'} ({sum(ok)}/{len(ok)})")
    return 0 if all(ok) else 1


def _raises(fn):
    try:
        fn()
        return False
    except CanonError:
        return True


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else 0)
