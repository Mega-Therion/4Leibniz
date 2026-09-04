import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from multiprover import ProofReport, aggregate
from governance import GovernanceVote, evaluate

class Phase8Tests(unittest.TestCase):
    def test_multi_prover_requires_independent_quorum(self):
        reports=[ProofReport('a','d','proven',True,True),ProofReport('b','d','proven',True,True),ProofReport('c','d','proven',False,True)]
        result=aggregate(reports, required=2)
        self.assertTrue(result['accepted']); self.assertEqual(result['independent_kernel_reports'],2)
    def test_multi_prover_retains_dissent(self):
        result=aggregate([ProofReport('a','d','proven',True),ProofReport('b','other','derived',True)], required=2)
        self.assertFalse(result['accepted']); self.assertEqual(len(result['dissent']),1)
    def test_governance_veto_blocks_even_with_quorum(self):
        votes=[GovernanceVote('a',True,2),GovernanceVote('b',True,2),GovernanceVote('c',False,1,veto=True)]
        result=evaluate('p','rotate-key',votes)
        self.assertFalse(result['accepted']); self.assertTrue(result['veto'])
    def test_governance_acceptance_is_timelocked(self):
        result=evaluate('p','admit-peer',[GovernanceVote('a',True,2),GovernanceVote('b',True,1)], quorum=0.66, timelock_seconds=600)
        self.assertTrue(result['accepted']); self.assertEqual(result['timelock_seconds'],600)

if __name__=='__main__': unittest.main()
