from frontier.rytt_geometric_calculus import balanced_ternary, interpret_dyas


def test_balanced_ternary_roundtrip_shape():
    assert balanced_ternary(0) == (0,)
    assert balanced_ternary(2) == (1, -1)
    assert all(d in (-1, 0, 1) for d in balanced_ternary(42, 8))


def test_frontier_interpretation_is_deterministic():
    result = interpret_dyas((-1, 0, 1), ("Characteristica.tensio_symm",))
    assert result.holonomy_mod_24 == 2
    assert result.stiefel_coset == "SO(5)/SO(3)"
    assert len(result.digest()) == 64
