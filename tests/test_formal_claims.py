"""Contract tests for the v1 formal-claims catalog (issue #11).

These tests do NOT require the Lean toolchain: they validate the schema, the
fixtures, the committed artifact, and the generator's pure decision logic.
The proof-grounded generation itself runs in CI (lean job) and locally via
scripts/generate_formal_claims.py.
"""
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts/schema/v1/formal-claims.schema.json"
ARTIFACT_PATH = ROOT / "artifacts/v1/formal-claims.json"
FIXTURE_DIR = ROOT / "tests/fixtures/formal_claims"
BRIDGE_PATH = ROOT / "integration/4leibniz_bridge.json"

STATUSES = {"proved", "conditional", "informal", "open_problem"}


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_formal_claims", ROOT / "scripts/generate_formal_claims.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator(schema):
    return Draft202012Validator(schema)


@pytest.fixture(scope="module")
def artifact():
    assert ARTIFACT_PATH.is_file(), (
        "artifacts/v1/formal-claims.json is missing — generate it with "
        "scripts/generate_formal_claims.py (CI must never skip this)")
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gen():
    return _load_generator()


class TestSchemaContract:
    def test_valid_fixture_passes(self, validator):
        catalog = json.loads((FIXTURE_DIR / "valid_catalog.json").read_text())
        errors = sorted(validator.iter_errors(catalog), key=lambda e: e.path)
        assert not errors, [e.message for e in errors]

    @pytest.mark.parametrize("bad_fixture", [
        "invalid_proved_missing_verification.json",
        "invalid_proved_with_sorry.json",
        "invalid_conditional_without_assumptions.json",
    ])
    def test_invalid_fixtures_rejected(self, validator, bad_fixture):
        catalog = json.loads((FIXTURE_DIR / bad_fixture).read_text())
        errors = list(validator.iter_errors(catalog))
        assert errors, f"{bad_fixture} must fail schema validation"

    def test_status_enum_is_locked(self, schema):
        enum = schema["$defs"]["claim"]["properties"]["status"]["enum"]
        assert set(enum) == STATUSES
        assert len(enum) == 4

    def test_proved_requires_verification_and_zero_sorries(self, schema):
        claim = schema["$defs"]["claim"]
        gates = {item["if"]["properties"]["status"]["const"]: item["then"]
                 for item in claim["allOf"]}
        assert "verification" in gates["proved"]["required"]
        assert gates["proved"]["properties"]["verification"]["properties"]["sorries"]["const"] == 0
        assert "conditional_on" in gates["conditional"]["required"]


class TestCommittedArtifact:
    def test_validates_against_schema(self, validator, artifact):
        errors = sorted(validator.iter_errors(artifact), key=lambda e: list(e.path))
        assert not errors, [e.message for e in errors]

    def test_pinned_source(self, artifact):
        source = artifact["source"]
        assert source["repository"] == "Mega-Therion/4Leibniz"
        assert len(source["commit"]) == 40
        assert source["lean_toolchain"] == "leanprover/lean4:v4.34.0-rc2"

    def test_claims_sorted_and_unique(self, artifact):
        ids = [c["claim_id"] for c in artifact["claims"]]
        assert ids == sorted(ids), "claims must be sorted by claim_id"
        assert len(ids) == len(set(ids)), "claim_id must be unique"

    def test_controlled_statuses_only(self, artifact):
        for claim in artifact["claims"]:
            assert claim["status"] in STATUSES

    def test_every_proved_claim_is_really_verified(self, artifact):
        for claim in artifact["claims"]:
            if claim["status"] != "proved":
                continue
            v = claim["verification"]
            assert v["sorries"] == 0
            assert set(v["axioms"]) <= {"propext", "Classical.choice", "Quot.sound"}, (
                f"{claim['claim_id']}: proved with non-standard axioms "
                f"{sorted(set(v['axioms']) - {'propext', 'Classical.choice', 'Quot.sound'})}")

    def test_generated_artifact_grounded_in_lean(self, artifact):
        record = artifact["verification_record"]
        assert record["lean_available"] is True, (
            "the committed artifact must come from a toolchain-grounded run")
        assert record["lake_build_exit_code"] == 0

    def test_rytt_bridge_theorems_are_catalogued(self, artifact):
        bridge = json.loads(BRIDGE_PATH.read_text(encoding="utf-8"))
        by_id = {c["claim_id"]: c for c in artifact["claims"]}
        for thm in bridge["source_theorems"]:
            assert thm in by_id, f"bridge theorem {thm} missing from catalog"
            assert by_id[thm]["status"] == "proved", (
                f"bridge theorem {thm} is {by_id[thm]['status']}, expected proved")


class TestGeneratorGate:
    """A failed Lean check can never produce `proved`."""

    def test_failed_report_excludes(self, gen):
        status, _ = gen.decide_status(
            {"ok": False, "axioms": [], "error": "elaboration failed"}, 0, 0)
        assert status is None

    def test_nonzero_module_exit_excludes(self, gen):
        status, _ = gen.decide_status({"ok": True, "axioms": []}, 1, 0)
        assert status is None

    def test_sorry_axiom_never_proves(self, gen):
        status, assumptions = gen.decide_status(
            {"ok": True, "axioms": ["propext", "sorryAx"]}, 0, 0)
        assert status == "conditional"
        assert any("sorry" in a for a in assumptions)

    def test_module_sorry_never_proves(self, gen):
        status, _ = gen.decide_status({"ok": True, "axioms": ["propext"]}, 0, 3)
        assert status != "proved"

    def test_repo_axiom_never_proves(self, gen):
        status, assumptions = gen.decide_status(
            {"ok": True, "axioms": ["propext", "Leibniz.VisViva.ghost_force_positive"]}, 0, 0)
        assert status == "conditional"
        assert assumptions

    def test_clean_check_proves(self, gen):
        status, assumptions = gen.decide_status(
            {"ok": True, "axioms": ["propext", "Classical.choice", "Quot.sound"]}, 0, 0)
        assert (status, assumptions) == ("proved", [])

    def test_unavailable_toolchain_yields_no_proved_claims(self, gen, tmp_path):
        """With the toolchain unavailable the catalog contains open problems and
        axioms but never a proved theorem."""
        built = gen.build_claims("0" * 40, "leanprover/lean4:v4.34.0-rc2", use_lean=False)
        assert built["verification_record"]["lean_available"] is False
        assert built["verification_record"]["lake_build_exit_code"] is None
        assert all(c["status"] != "proved" for c in built["claims"])
        assert all(c["status"] != "informal" for c in built["claims"])
        # axioms (conditional) and open problems are extracted statically
        statuses = {c["status"] for c in built["claims"]}
        assert statuses == {"conditional", "open_problem"}
        assert built["excluded"], "theorems must be excluded, not downgraded"


class TestDeterminismAndStableIds:
    def test_catalog_is_a_pure_function_of_the_checkout(self, gen):
        import json as _json
        a, b = (gen.build_claims("0" * 40, "leanprover/lean4:v4.34.0-rc2", use_lean=False)
                for _ in range(2))
        assert _json.dumps(a, sort_keys=True) == _json.dumps(b, sort_keys=True)

    def test_claim_ids_are_stable(self, gen):
        a = gen.build_claims("0" * 40, "leanprover/lean4:v4.34.0-rc2", use_lean=False)
        b = gen.build_claims("1" * 40, "leanprover/lean4:v4.34.0-rc2", use_lean=False)
        ids_a = [c["claim_id"] for c in a["claims"]]
        ids_b = [c["claim_id"] for c in b["claims"]]
        assert ids_a == ids_b, "claim ids must not depend on the commit"

    def test_axioms_keep_their_fully_qualified_names(self, gen):
        built = gen.build_claims("0" * 40, "leanprover/lean4:v4.34.0-rc2", use_lean=False)
        ids = {c["claim_id"] for c in built["claims"]}
        for expected in [
            "Leibniz.Calculemus.holonomy_path_ordered",
            "Leibniz.Calculemus.entropy_nonnegative",
            "Leibniz.Harmonia.lindblad_trace_preserving",
            "Leibniz.VisViva.ghost_force_positive",
        ]:
            assert expected in ids, f"expected axiom {expected} in catalog"

    def test_open_problem_ids_are_stable(self, gen):
        built = gen.build_claims("0" * 40, "leanprover/lean4:v4.34.0-rc2", use_lean=False)
        ids = {c["claim_id"] for c in built["claims"]}
        for expected in [
            "Leibniz.OpenProblems.chiral-floor",
            "Leibniz.OpenProblems.lindblad-cp",
            "Leibniz.OpenProblems.wilson-loop",
        ]:
            assert expected in ids
