import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from replicated_coordinator import DecisionVote, ParticipantAck, ReplicatedDecisionLog, AckStore
from replica_membership import issue_member, verify_vote, elect_coordinator, sign_vote
from security import generate_keypair
class Phase12Tests(unittest.TestCase):
    def test_coordinator_snapshot_recovery(self):
        log=ReplicatedDecisionLog('r'); log.record(DecisionVote('r','t','commit','d')); restored=ReplicatedDecisionLog.recover(log.snapshot()); self.assertEqual(restored.snapshot()['log']['last_sequence'],1)
    def test_ack_snapshot_recovery(self):
        store=AckStore(); store.record(ParticipantAck('s','t','prepared','d',1,'k',100)); self.assertEqual(len(AckStore.recover(store.durable_snapshot()).for_transaction('t')),1)
    def test_authenticated_vote_and_failover(self):
        private,_=generate_keypair(); issued=issue_member('r1',private,2,ttl=100,now=100); member=issued['record']; vote=sign_vote('r1','t','commit','d',private,1,100); self.assertTrue(verify_vote(vote,member,100)); self.assertEqual(elect_coordinator([member],7,100)['coordinator_id'],'r1')
    def test_expired_member_cannot_verify_vote(self):
        private,_=generate_keypair(); issued=issue_member('r1',private,2,ttl=1,now=100); vote=sign_vote('r1','t','commit','d',private,1,100); self.assertFalse(verify_vote(vote,issued['record'],102))
if __name__=='__main__': unittest.main()
