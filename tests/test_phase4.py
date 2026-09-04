import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from ai_assist import suggest
from benchmarks.runner import run
from consensus import Peer, Vote, reach_consensus

class Phase4Tests(unittest.TestCase):
    def test_offline_ai_suggestions_are_unverified(self):
        result = suggest('claim C:\n  infer a >= b')
        self.assertFalse(result['verified'])
        self.assertTrue(result['suggestions'])
        self.assertEqual(result['suggestions'][0]['status'], 'unverified')

    def test_weighted_consensus_retains_dissent(self):
        result = reach_consensus(
            [Peer('alpha', 2), Peer('beta', 1), Peer('gamma', 1)],
            [Vote('alpha', 'p', 'derived'), Vote('beta', 'p', 'derived'), Vote('gamma', 'p', 'open')])
        self.assertTrue(result.accepted)
        self.assertEqual(result.status, 'derived')
        self.assertEqual(len(result.dissent), 1)

    def test_benchmark_is_reproducible_and_complete(self):
        result = run()
        self.assertEqual(result['summary']['total'], 8)
        self.assertEqual(result['summary']['correct'], 8)
        self.assertTrue(all('source' not in case for case in result['cases']))

if __name__ == '__main__': unittest.main()
