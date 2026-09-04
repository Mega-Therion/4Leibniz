import pytest
from rytt_geometric_calculus import (
    RYTT_GLYPHS,
    GLYPH_MAP,
    make_leibniz_rytt_theorem,
    RyttProposition
)

def test_glyph_palette_completeness():
    assert len(RYTT_GLYPHS) == 24
    for key, symbol, desc, weight in RYTT_GLYPHS:
        assert weight in (-1, 0, 1)
        assert len(symbol) > 0

def test_holonomy_evaluation_closed():
    thm = make_leibniz_rytt_theorem(
        name="Test_Closure",
        glyph_keys=["aleph", "gimel", "mem", "qoph", "omega"],
        premises=["given a >= b", "given b >= c"],
        conclusion="infer a >= c"
    )
    res = thm.evaluate_holonomy()
    assert res["status"] == "VERIFIED_INVARIANT"
    assert res["normalized_balance"] > 0
    assert 0 <= res["topological_shear"] <= 1.0

def test_holonomy_evaluation_unclosed():
    thm = make_leibniz_rytt_theorem(
        name="Test_Sheared",
        glyph_keys=["he", "ayin"],
        premises=["given a < b"],
        conclusion="infer a >= b"
    )
    res = thm.evaluate_holonomy()
    assert res["normalized_balance"] < 0
