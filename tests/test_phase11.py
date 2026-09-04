import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from replicated_coordinator import DecisionVote, ParticipantAck, ReplicatedDecisionLog, validate_decision, AckStore
class Phase11Tests(unittest.TestCase):
    def test_commit_requires_three_verified_votes_for_f_one(self):
        votes=[DecisionVote(str(i),'t','commit','d',signature_verified=True) for i in range(3)]
        result=validate_decision(votes,'t','d',1); self.assertTrue(result['accepted']); self.assertEqual(result['decision'],'commit')
    def test_byzantine_conflict_is_not_accepted(self):
        votes=[DecisionVote('a','t','commit','d',signature_verified=True),DecisionVote('b','t','commit','d',signature_verified=True),DecisionVote('c','t','abort','d',signature_verified=True)]
        result=validate_decision(votes,'t','d',1); self.assertFalse(result['accepted'])
    def test_replica_log_rejects_local_equivocation(self):
        log=ReplicatedDecisionLog('r'); log.record(DecisionVote('r','t','commit','d'))
        with self.assertRaises(ValueError): log.record(DecisionVote('r','t','abort','d'))
    def test_ack_store_is_idempotent_and_conflict_safe(self):
        store=AckStore(); ack=ParticipantAck('s','t','prepared','d',1,'s:t:1',100)
        first=store.record(ack); second=store.record(ack); self.assertFalse(first['idempotent']); self.assertTrue(second['idempotent'])
        with self.assertRaises(ValueError): store.record(ParticipantAck('s','t','committed','d',1,'s:t:1',101))
if __name__=='__main__': unittest.main()
