import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from security import commit_private_premise, generate_keypair, sign_proposal, verify_proposal
from benchmarks.performance import run

class SecurityTests(unittest.TestCase):
    def test_signed_proposal_verifies_and_tampering_fails(self):
        private, _ = generate_keypair()
        proposal = sign_proposal('node-a', {'claim': 'C', 'status': 'derived'}, private)
        self.assertTrue(verify_proposal(proposal))
        tampered = type(proposal)(proposal.node_id, {'claim': 'D', 'status': 'derived'}, proposal.public_key, proposal.signature, proposal.digest)
        self.assertFalse(verify_proposal(tampered))

    def test_private_premise_is_explicitly_not_zk(self):
        receipt = commit_private_premise('private observation', b'fixed nonce for test')
        self.assertFalse(receipt.verified)
        self.assertIn('not a zero-knowledge proof', receipt.note)
        self.assertNotEqual(receipt.commitment, receipt.statement_digest)

class BenchmarkTests(unittest.TestCase):
    def test_performance_result_keeps_unavailable_backends_explicit(self):
        result = run()
        self.assertEqual(len(result['cases']), 8)
        names = {b['name']: b for b in result['backend_results']}
        self.assertEqual(names['Z3 SMT']['status'], 'unavailable')
        self.assertIn(names['universal-calculus proof search']['status'], ('available', 'unavailable'))

if __name__ == '__main__': unittest.main()
