import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from api import app
from proof_engine import SemanticPatch, search
from ucalculus import parse

ROOT = Path(__file__).parents[1]

class ProofSearchTests(unittest.TestCase):
    def setUp(self):
        self.claim_text = (ROOT / 'examples' / 'monadology_argument.uc').read_text()
        self.claim = parse(self.claim_text)

    def test_transitive_philosophical_argument_is_found(self):
        result = search(self.claim)
        self.assertEqual(result.outcome, 'proved')
        self.assertEqual(result.steps[0].rule, 'transitivity')
        self.assertEqual(len(result.steps[0].from_premises), 2)

    def test_open_argument_reports_obligation(self):
        claim = parse('claim Unknown:\n  given A >= B\n  infer A >= C')
        result = search(claim)
        self.assertEqual(result.outcome, 'open')
        self.assertIn('A >= C', result.remaining_obligations)

    def test_semantic_patch_preserves_structure(self):
        patch = SemanticPatch('p1', 'add missing premise', 'add_premise', '', 'C >= D')
        patched = patch.apply(self.claim)
        self.assertEqual(len(patched.premises), 3)
        self.assertEqual(patched.conclusion, self.claim.conclusion)

class Phase2ApiTests(unittest.TestCase):
    def setUp(self): self.client = app.test_client()

    def test_prove_endpoint(self):
        text = (ROOT / 'examples' / 'monadology_argument.uc').read_text()
        response = self.client.post('/api/prove', json={'text': text})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['search']['outcome'], 'proved')

    def test_patch_endpoint(self):
        text = (ROOT / 'examples' / 'monadology_argument.uc').read_text()
        response = self.client.post('/api/patch', json={'text': text, 'patch': {
            'id': 'rename', 'description': 'rename', 'operation': 'rename',
            'target': 'SufficientReason', 'replacement': 'PrincipleOfSufficientReason'}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['claim']['name'], 'PrincipleOfSufficientReason')

    def test_visualization_endpoints(self):
        lattice = self.client.get('/api/epistemic/lattice').json
        graph = self.client.get('/api/arguments/graph').json
        self.assertEqual(len(lattice['nodes']), 5)
        self.assertTrue(any(e['relation'] == 'depends_on' for e in graph['edges']))

if __name__ == '__main__': unittest.main()
