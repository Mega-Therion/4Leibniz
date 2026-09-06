"""Tests for the Calculemus end-to-end machine: synthesis, ledger, kernel."""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from calculemus import (HEADER, install, kernel_verify, lean_ident, pascal,
                        process, synthesize)
from proof_engine import search
from ucalculus import parse

ROOT = Path(__file__).parents[1]
MONADOLOGY = ROOT / "examples" / "monadology_argument.uc"
STABILITY = ROOT / "examples" / "stability.uc"

DIRECT = ("claim Direct:\n"
          "  given light >= darkness\n"
          "  infer light >= darkness\n")


class IdentifierTests(unittest.TestCase):
    def test_lean_ident(self):
        self.assertEqual(lean_ident("contingent event"), "contingentEvent")
        self.assertEqual(lean_ident("continuity_floor"), "continuityFloor")

    def test_pascal(self):
        self.assertEqual(pascal("SufficientReason"), "SufficientReason")


class SynthesisTests(unittest.TestCase):
    def test_transitivity_uses_the_shared_middle_term(self):
        claim = parse(MONADOLOGY.read_text())
        source, theorem = synthesize(claim, search(claim), "examples/x.uc")
        self.assertEqual(theorem, "sufficientReason_transitivity")
        # the chain must run sufficientReason >= intelligibleOrder >= contingentEvent
        self.assertIn("(sufficientReason intelligibleOrder contingentEvent : \u03b1)", source)
        self.assertIn("sufficientReason \u2265 intelligibleOrder", source)
        self.assertIn("intelligibleOrder \u2265 contingentEvent", source)
        self.assertIn("le_trans h1 h2", source)
        self.assertIn("import Mathlib", source)
        self.assertNotIn("sorry", source)
        self.assertNotIn("axiom", source)

    def test_direct_rule(self):
        claim = parse(DIRECT)
        source, theorem = synthesize(claim, search(claim), "examples/x.uc")
        self.assertEqual(theorem, "direct_direct")
        self.assertIn("light \u2265 darkness", source)
        self.assertIn("h1", source.split(":=")[-1])


class LedgerTests(unittest.TestCase):
    def test_dry_run_records_derived_and_open(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            records = [process(MONADOLOGY, dry_run=True, do_install=False, registry=ledger),
                       process(STABILITY, dry_run=True, do_install=False, registry=ledger)]
            lines = [json.loads(l) for l in ledger.read_text().splitlines()]
        self.assertEqual(len(lines), 2)
        self.assertEqual(records[0]["verdict"], "derived")
        self.assertTrue(records[0]["kernel_verified"] is False)
        self.assertEqual(records[1]["verdict"], "open")
        self.assertEqual(records[1]["search_outcome"], "open")
        self.assertIn("No supported proof rule", records[1]["explanation"])
        for r in records:
            self.assertEqual(len(r["fingerprint"]), 64)
            self.assertIn("timestamp", r)

    def test_install_is_idempotent(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, _ = synthesize(parse(MONADOLOGY.read_text()), search(parse(MONADOLOGY.read_text())), "examples/x.uc")
            first = install(source, "SufficientReason", repo_root=root)
            text1 = first.read_text()
            second = install(source, "SufficientReason", repo_root=root)
            self.assertEqual(first, second)
            self.assertEqual(text1, first.read_text())
            self.assertTrue((root / "Leibniz" / "Generated" / "README.md").exists())


@unittest.skipUnless(shutil.which("lake"), "Lean toolchain not available")
class KernelIntegrationTests(unittest.TestCase):
    """The real thing: the Lean 4 kernel must accept the synthesized theorem."""

    def test_monadology_kernel_proven(self):
        source, _ = synthesize(parse(MONADOLOGY.read_text()), search(parse(MONADOLOGY.read_text())), "examples/x.uc")
        ok, output, _ = kernel_verify(source)
        self.assertTrue(ok, f"kernel rejected the flagship theorem: {output}")

    def test_bogus_proof_is_kernel_rejected(self):
        source, _ = synthesize(parse(MONADOLOGY.read_text()), search(parse(MONADOLOGY.read_text())), "examples/x.uc")
        broken = source.replace("le_trans h1 h2", "le_trans h2 h2")
        ok, output, _ = kernel_verify(broken)
        self.assertFalse(ok)
        self.assertTrue(output)


if __name__ == "__main__":
    unittest.main()
