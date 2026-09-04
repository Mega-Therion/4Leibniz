import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from api import app
from zk_pipeline import status

class Phase6Tests(unittest.TestCase):
    def test_zk_status_does_not_claim_unbuilt_proof(self):
        result = status()
        self.assertIn('circuit', result)
        self.assertFalse(result['verified'])
        self.assertIn('not a proof', result['boundary'])

    def test_zk_status_route(self):
        response = app.test_client().get('/api/zk/status')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json['verified'])

    def test_deployment_scaffolding_exists(self):
        root = Path(__file__).parents[1]
        self.assertTrue((root/'circuits/private_premise.circom').exists())
        self.assertTrue((root/'circuits/package.json').exists())
        self.assertTrue((root/'deploy/cloudflare/worker.js').exists())
        self.assertTrue((root/'deploy/cloudflare/wrangler.toml').exists())

if __name__ == '__main__': unittest.main()
