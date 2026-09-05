import json
from pathlib import Path


def test_bridge_contract_is_explicit_about_provenance():
    contract = json.loads((Path(__file__).parents[1] / "integration" / "4leibniz_bridge.json").read_text())
    assert contract["schema"].endswith("v1")
    assert contract["modern_extensions"]["truth_values"] == [-1, 0, 1]
    assert "does not attribute" in contract["policy"]
    assert len(contract["source_theorems"]) >= 3
