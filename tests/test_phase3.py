import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from api import app
from counterexample import find
from divergence import compare
from ucalculus import parse

class CounterexampleTests(unittest.TestCase):
    def test_finds_minimal_integer_witness(self):
        claim = parse('claim FalseBridge:\n  given a >= b\n  infer a >= c\n  status: open')
        result = find(claim, 2)
        self.assertEqual(result.outcome, 'refuted')
        self.assertEqual(result.bound, 1)
        self.assertTrue(result.assignment['a'] >= result.assignment['b'])
        self.assertFalse(result.assignment['a'] >= result.assignment['c'])
        self.assertTrue(result.fingerprint)

    def test_no_witness_is_inconclusive(self):
        claim = parse('claim Tautology:\n  given a >= b\n  given b >= c\n  infer a >= c')
        result = find(claim, 2)
        self.assertEqual(result.outcome, 'no-witness')

class DivergenceTests(unittest.TestCase):
    def test_premise_removal_is_logical_divergence(self):
        before = parse('claim C:\n  given a >= b\n  infer a >= c\n  status: derived')
        after = parse('claim C:\n  infer a >= c\n  status: open')
        result = compare(before, after)
        self.assertIn('logical', result.classes)
        self.assertIn('epistemic', result.classes)
        self.assertEqual(result.logical_impact, 'proof obligations changed')

    def test_source_only_change_is_provenance_divergence(self):
        before = parse('claim C:\n  infer a >= c\n  source: A')
        after = parse('claim C:\n  infer a >= c\n  source: B')
        result = compare(before, after)
        self.assertIn('provenance', result.classes)
        self.assertEqual(result.logical_impact, 'proof obligations preserved')

class Phase3ApiTests(unittest.TestCase):
    def setUp(self): self.client = app.test_client()
    def test_counterexample_and_divergence_routes(self):
        text = 'claim C:\n  given a >= b\n  infer a >= c\n  status: open'
        self.assertEqual(self.client.post('/api/counterexample', json={'text': text}).status_code, 200)
        response = self.client.post('/api/divergence', json={'before': text, 'after': text.replace('status: open','status: conjectured')})
        self.assertEqual(response.status_code, 200)
        self.assertIn('epistemic', response.json['classes'])

if __name__ == '__main__': unittest.main()
