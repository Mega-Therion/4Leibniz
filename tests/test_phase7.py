import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from bft import BFTPeer, BFTVote, decide
from security import ReplayGuard, generate_keypair, sign_proposal, verify_fresh_proposal
from api import app

ROOT = Path(__file__).parents[1]

class Phase7Tests(unittest.TestCase):
    def test_bft_accepts_four_honest_nodes_and_rewards_aligned_votes(self):
        peers = [BFTPeer(f'n{i}') for i in range(4)]
        votes = [BFTVote(f'n{i}', 'p', 'proven') for i in range(4)]
        result = decide(peers, votes, fault_tolerance=1)
        self.assertTrue(result['accepted'])
        self.assertEqual(sum(i['delta'] for i in result['incentives']), 4)

    def test_bft_withholds_on_equivocation(self):
        peers = [BFTPeer(f'n{i}') for i in range(4)]
        votes = [BFTVote('n0','p','proven'), BFTVote('n0','p','open'), BFTVote('n1','p','proven'), BFTVote('n2','p','proven'), BFTVote('n3','p','proven')]
        result = decide(peers, votes, fault_tolerance=1)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['equivocations'], ['n0'])

    def test_replay_guard_accepts_once(self):
        private, _ = generate_keypair()
        proposal = sign_proposal('n1', {'claim':'C'}, private, timestamp=1000, nonce='fixed')
        guard = ReplayGuard(max_age_seconds=300)
        self.assertTrue(verify_fresh_proposal(proposal, guard, now=1000))
        self.assertFalse(verify_fresh_proposal(proposal, guard, now=1000))

    def test_groth16_api_verifies_generated_demo_artifact(self):
        build = ROOT/'circuits'/'build'
        if not (build/'proof.json').exists(): self.skipTest('demo proof artifacts not generated')
        c = app.test_client()
        proof=json.loads((build/'proof.json').read_text()); public=json.loads((build/'public.json').read_text())
        response=c.post('/api/zk/verify', json={'proof':proof,'public_signals':public})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['verified'])

if __name__ == '__main__': unittest.main()
