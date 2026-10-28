from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from formal_statement_boundaries import statement_at

class StatementBoundaryTests(unittest.TestCase):
    def test_consecutive_axioms(self):
        self.assertEqual(statement_at(["axiom a : True", "axiom b : True"], 0), "axiom a : True")

    def test_next_definition(self):
        self.assertEqual(statement_at(["axiom a : True", "noncomputable def b : Nat := 1"], 0), "axiom a : True")

    def test_inline_theorem(self):
        self.assertEqual(statement_at(["theorem a : True := by trivial", "axiom b : True"], 0), "theorem a : True")

    def test_multiline_theorem(self):
        self.assertEqual(statement_at(["theorem a", "  (x : Nat) :", "  x = x := by", "  rfl"], 0), "theorem a\n(x : Nat) :\nx = x")

    def test_scope_boundary(self):
        self.assertEqual(statement_at(["axiom a : True", "end Demo"], 0), "axiom a : True")

    def test_attributed_declaration(self):
        self.assertEqual(statement_at(["axiom a : True", "@[simp] private theorem b : True := by trivial"], 0), "axiom a : True")

    def test_blank_lines(self):
        self.assertEqual(statement_at(["axiom a :", "", " True", "", "axiom b : True"], 0), "axiom a :\nTrue")

    def test_long_header(self):
        binders = [f"  (x{i} : Nat)" for i in range(30)]
        lines = ["theorem a"] + binders + ["  : True := by trivial"]
        expected = "theorem a\n" + "\n".join(x.strip() for x in binders) + "\n: True"
        self.assertEqual(statement_at(lines, 0), expected)

if __name__ == "__main__":
    unittest.main()
