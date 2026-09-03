import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from api import app
from explanations import explain_result
from proof_engine import search
from ucalculus import parse

TEXT = (Path(__file__).parents[1] / 'examples' / 'monadology_argument.uc').read_text()

class ExplanationAndReplTests(unittest.TestCase):
    def setUp(self): self.client = app.test_client()

    def test_english_and_latin_are_deterministic(self):
        result = search(parse(TEXT))
        rendered = explain_result(result)
        self.assertIn('transitivity', rendered['en'][0].lower())
        self.assertIn('transitivitatem', rendered['la'][0])

    def test_prove_response_contains_both_languages(self):
        response = self.client.post('/api/prove', json={'text': TEXT})
        self.assertEqual(response.status_code, 200)
        self.assertIn('en', response.json['explanations'])
        self.assertIn('la', response.json['explanations'])

    def test_repl_help_and_prove(self):
        self.assertIn('prove', self.client.post('/api/repl', json={}).json['commands'])
        response = self.client.post('/api/repl', json={'action': 'prove', 'text': TEXT})
        self.assertEqual(response.json['kind'], 'prove')
        self.assertEqual(response.json['search']['outcome'], 'proved')

if __name__ == '__main__': unittest.main()
