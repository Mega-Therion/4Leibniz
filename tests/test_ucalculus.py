import json
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from ucalculus import SyntaxError, compile_text, parse

EXAMPLE = Path(__file__).parents[1] / "examples" / "stability.uc"

class UniversalCalculusTests(unittest.TestCase):
    def test_parse_example(self):
        claim = parse(EXAMPLE.read_text())
        self.assertEqual(claim.name, "Stability")
        self.assertEqual(len(claim.premises), 2)
        self.assertEqual(claim.status, "derived")

    def test_compile_has_stable_fingerprint_and_lean(self):
        result = compile_text(EXAMPLE.read_text())
        self.assertEqual(len(result["fingerprint"]), 64)
        self.assertIn("theorem Stability", result["lean"])
        self.assertEqual(result["claim"]["source"], "Harmonia Praestabilita")

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(SyntaxError):
            parse("claim X:\n  infer True\n  status: imaginary")

if __name__ == "__main__":
    unittest.main()
