"""Latin morphological helpers for the manuscript HTR pipeline.

Split out from the pipeline so the linguistic rules can be tested directly
against real Latin rather than only through an end-to-end run.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Abbreviation expansion
# ---------------------------------------------------------------------------
# NOTE ON THE PATTERNS. These deliberately have NO trailing \b.
#
# `\b` is a transition between a word and a non-word character. Every one of
# these abbreviations ENDS in a non-word character -- `}` or `.` -- so a
# trailing `\b` requires the next character to be a word character. In real
# text an abbreviation is followed by a space or end-of-string, so the boundary
# never exists and the pattern can never match.
#
# The original version of this table carried `\bq_{d}\b` and friends. Measured:
# it was a no-op on 6 out of 6 inputs, including the exact strings it was
# written for. Expansion had never once run.
LATIN_ABBREVIATIONS: Dict[str, str] = {
    r"\bq_\{d\}": "quod",
    r"\bp_\{t\}": "praeter",
    r"\be\.g\.": "exempli gratia",
    r"\bm\.s\.": "manuscriptum",
}


def expand_abbreviations(text: str) -> str:
    """Expand editorial abbreviations. Returns the text unchanged if none apply."""
    for pattern, replacement in LATIN_ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)
    return text


# ---------------------------------------------------------------------------
# Enclitic stripping
# ---------------------------------------------------------------------------
# Latin appends -que, -ve, -ne as enclitics ("senatus populusque"). Stripping
# them helps lexicon matching, but a naive suffix strip mutilates ordinary words
# that merely END in those letters.
#
# The previous exception list held 8 entries and a `len <= 4` guard. Measured
# against common Latin, it corrupted 8 of 14 test words, including some of the
# most frequent words in the language:
#
#   neque -> ne      atque -> at      quoque -> quo     usque  -> us
#   quinque -> quin  namque -> nam    cumque -> cum     carne  -> car
#
# `neque`, `atque` and `quoque` are top-100 words in classical prose, so this
# was not an edge case. The list below is the closed class of words ending in
# -que/-ve/-ne that are NOT enclitic constructions.
ENCLITIC_EXCEPTIONS = frozenset({
    # -que words that are lexical, not enclitic
    "itaque", "utrique", "plerique", "undique", "ubique", "denique", "absque",
    "quousque", "quinque", "usque", "neque", "atque", "namque", "quoque",
    "cumque", "quicumque", "quaecumque", "quodcumque", "utcumque", "plerumque",
    "susque", "deque", "obliquisque",
    # -ve words
    "sive", "seu", "nave", "gravé", "suave", "breve", "leve", "nove",
    # -ne words
    "bene", "sine", "omne", "carne", "carmine", "nomine", "ordine", "origine",
    "virgine", "homine", "lumine", "flumine", "semine", "germine", "agmine",
    "certamine", "examine", "crimine", "culmine", "fine", "plene", "digne",
})

MIN_STEM_LENGTH = 3
"""A stripped stem shorter than this is almost certainly a false positive."""


def strip_enclitics(token: str) -> str:
    """Remove a trailing -que/-ve/-ne enclitic, conservatively.

    Refuses to strip when the token is a known lexical exception, when the token
    is short enough that stripping is unlikely to be right, or when the
    resulting stem would be implausibly short. Under-stripping costs a missed
    lexicon match; over-stripping silently corrupts the word.
    """
    lower = token.lower()
    if lower in ENCLITIC_EXCEPTIONS or len(lower) <= 4:
        return token
    for enclitic in ("que", "ve", "ne"):
        if lower.endswith(enclitic):
            stem = token[: -len(enclitic)]
            if len(stem) < MIN_STEM_LENGTH:
                return token
            return stem
    return token


# ---------------------------------------------------------------------------
# Leibnizian core lexicon
# ---------------------------------------------------------------------------
# Declension of `vis` (force), third declension, irregular:
#   sg. vis / vim / vi        pl. vires / virium / viribus
#
# The inherited pattern was `v(is|im|iri?|iribus)`. Two problems, both found by
# testing it against real forms rather than by reading it:
#   - `vi` (ablative singular) was MISSING, and it is the commonest form in a
#     dynamics text -- "vi viva" is "by living force". "vi mortua" did not match.
#   - `iri?` matches `vir` and `viri`, which are forms of `vir` (man), not `vis`.
#     That is a false-positive source and matches no real form of this noun.
_VIS = r"\bv(is|im|i|ires|irium|iribus)"

CORE_LEXICON_SCHEMA: List[Tuple[str, str, List[str]]] = [
    ("vis viva", "living force", [_VIS + r"\s+viv(a|ae|am|arum|is|as)\b"]),
    ("vis mortua", "dead force", [_VIS + r"\s+mortu(a|ae|am|arum|is|as)\b"]),
    ("conatus", "endeavor", [r"\bconat(us|um|ui|o|ibus|uum)\b"]),
    ("monas", "monad", [r"\bmona(s|dos|di|dem|de|des|dum|dibus)\b",
                        r"\bmonad(es|ibus|is|em|e|um)\b"]),
    ("calculus ratiocinator", "calculus ratiocinator",
     [r"\bcalcul(us|i|o|um)\s+ratiocinator(is|i|em|e)?\b"]),
    ("aggregatum", "aggregate", [r"\baggregat(um|i|o|a|orum|is)\b"]),
    ("actionis quantitas", "quantity of action",
     [r"\baction(is|i|em|e)\s+quantita(s|tis|ti|tem|te)\b"]),
]


def extract_matching_terms(latin_text: str) -> List[Tuple[str, str]]:
    """Return the (canonical, english) lexicon pairs present in the text."""
    tokens = [strip_enclitics(t) for t in re.findall(r"\w+|[^\w\s]", latin_text)]
    clean_text = " ".join(tokens).lower()
    raw_lower = latin_text.lower()

    matched: List[Tuple[str, str]] = []
    for canonical, translation, patterns in CORE_LEXICON_SCHEMA:
        for pattern in patterns:
            if re.search(pattern, raw_lower) or re.search(pattern, clean_text):
                matched.append((canonical, translation))
                break
    return sorted(set(matched), key=lambda x: x[0])
