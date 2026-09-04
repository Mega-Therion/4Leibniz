import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from durable_log import OrderedLog
from peer_admission import admit, is_active, revoke
from security import generate_keypair, sign_proposal

class Phase9Tests(unittest.TestCase):
    def test_ordered_log_hash_chain_and_recovery(self):
        log=OrderedLog(); first=log.append('p1',{'x':1}); second=log.append('p2',{'x':2})
        recovered=OrderedLog(log.snapshot()['entries'])
        self.assertEqual(recovered.head.entry_hash, second.entry_hash)
        self.assertEqual(first.sequence,1); self.assertEqual(second.sequence,2)
    def test_ordered_log_rejects_gap_and_corruption(self):
        log=OrderedLog(); log.append('p1',{})
        with self.assertRaises(ValueError): log.append('p3',{},sequence=3)
        snapshot=log.snapshot(); snapshot['entries'][0]['payload']={'tampered':True}
        with self.assertRaises(ValueError): OrderedLog(snapshot['entries'])
    def test_signed_peer_admission_expiry_and_revocation(self):
        private,_=generate_keypair(); proposal=sign_proposal('node-a',{'kind':'peer_admission','node_id':'node-a'},private,timestamp=100,nonce='n')
        result=admit(proposal,['prover'],2,ttl=20,now=100)
        self.assertTrue(result['accepted']); self.assertTrue(is_active(result['record'],110)); self.assertFalse(is_active(result['record'],120))
        self.assertFalse(is_active(revoke(result['record']),110))

if __name__=='__main__': unittest.main()
