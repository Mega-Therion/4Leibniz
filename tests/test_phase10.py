import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from cross_shard import Shard, atomic_commit, recover_in_doubt
class Phase10Tests(unittest.TestCase):
    def test_connected_commit_is_atomic(self):
        s={'a':Shard('a',{'x':0}),'b':Shard('b',{'y':0})}; r=atomic_commit('t',s,{'a':{'x':1},'b':{'y':1}})
        self.assertEqual(r['phase'],'committed'); self.assertEqual(s['a'].state['x'],1); self.assertEqual(s['b'].state['y'],1)
    def test_partition_aborts_before_commit(self):
        s={'a':Shard('a',{'x':0}),'b':Shard('b',{'y':0})}; r=atomic_commit('t',s,{'a':{'x':1},'b':{'y':1}},reachable={'a'})
        self.assertEqual(r['phase'],'aborted'); self.assertEqual(s['a'].state['x'],0); self.assertEqual(s['b'].state['y'],0)
    def test_in_doubt_recovery_resolves_prepared_work(self):
        s={'a':Shard('a',{'x':0}),'b':Shard('b',{'y':0})}; s['a'].prepare('t',{'x':1}); r=recover_in_doubt('t',s,'commit')
        self.assertEqual(r['resolved_shards'],['a']); self.assertEqual(s['a'].state['x'],1)
    def test_snapshot_sync_validates_hashes(self):
        source=Shard('a',{'x':1}); source.append = None
        snapshot=source.snapshot(); target=Shard('a'); target.sync(snapshot); self.assertEqual(target.state,{'x':1})
if __name__=='__main__': unittest.main()
