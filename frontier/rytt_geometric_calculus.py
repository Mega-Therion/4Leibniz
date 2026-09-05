"""Small, dependency-free bridge from the Leibniz kernel to the RYTT frontier.

This module is an adapter, not a historical claim: the modern structures are
explicitly namespaced and carry the source theorem identifiers they extend.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

BALANCED_TERNARY = (-1, 0, 1)


def balanced_ternary(value: int, width: int = 0) -> tuple[int, ...]:
    if not isinstance(value, int) or value < 0:
        raise ValueError("value must be a non-negative integer")
    digits: list[int] = []
    if value == 0:
        digits.append(0)
    while value:
        remainder = value % 3
        value //= 3
        if remainder == 2:
            digits.append(-1)
            value += 1
        else:
            digits.append(remainder)
    while len(digits) < width:
        digits.append(0)
    if len(digits) > width > 0:
        raise ValueError("width is too small")
    return tuple(reversed(digits))


def base24_holonomy(path: Iterable[int]) -> int:
    """Fold a bounded integer path into a reproducible base-24 residue."""
    residue = 0
    for step in path:
        if not isinstance(step, int) or not 0 <= step < 24:
            raise ValueError("holonomy steps must be integers in [0, 23]")
        residue = (residue * 24 + step) % 24
    return residue


@dataclass(frozen=True)
class FrontierInterpretation:
    source_theorems: tuple[str, ...]
    ternary: tuple[int, ...]
    holonomy_mod_24: int
    stiefel_coset: str = "SO(5)/SO(3)"

    def digest(self) -> str:
        payload = f"{self.source_theorems}|{self.ternary}|{self.holonomy_mod_24}|{self.stiefel_coset}"
        return sha256(payload.encode()).hexdigest()


def interpret_dyas(dyas: Iterable[int], source_theorems: Iterable[str] = ()) -> FrontierInterpretation:
    values = tuple(dyas)
    if any(value not in BALANCED_TERNARY for value in values):
        raise ValueError("RYTT dyads must use balanced ternary values -1, 0, or 1")
    return FrontierInterpretation(tuple(source_theorems), values, base24_holonomy((value + 1) for value in values))
