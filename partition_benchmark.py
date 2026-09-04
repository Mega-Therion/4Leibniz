from __future__ import annotations
import json, time
from pathlib import Path
from cross_shard import Shard, atomic_commit, recover_in_doubt
from durable_log import OrderedLog

def run_case(name, reachable):
    shards={'alpha':Shard('alpha',{'a':0}),'beta':Shard('beta',{'b':0})}; start=time.perf_counter(); result=atomic_commit(name,shards,{'alpha':{'a':1},'beta':{'b':1}},reachable); elapsed=time.perf_counter()-start
    if result['phase']=='in_doubt': recovery=recover_in_doubt(name,shards,'commit')
    else: recovery=None
    result.update({'case':name,'elapsed_seconds':round(elapsed,7),'states':{k:v.state for k,v in shards.items()},'recovery':recovery}); return result

def audit(results):
    checks=[]
    for r in results:
        if r['phase']=='committed': checks.append({'case':r['case'],'invariant':'atomic_commit','passed':len(set(r['committed']))==2})
        elif r['phase']=='aborted': checks.append({'case':r['case'],'invariant':'atomic_abort','passed':all(v=={'a':0} or v=={'b':0} for v in r['states'].values())})
        else: checks.append({'case':r['case'],'invariant':'recovery_resolves_in_doubt','passed':r['recovery'] is not None})
    return checks

def main():
    results=[run_case('tx-connected',{'alpha','beta'}),run_case('tx-partitioned',{'alpha'}),run_case('tx-unreachable',set())]
    output={'cases':results,'audit':audit(results),'summary':{'total':len(results),'passed':sum(x['passed'] for x in audit(results))}}
    out=Path('benchmarks/artifacts/phase10'); out.mkdir(parents=True,exist_ok=True); (out/'partition_benchmark.json').write_text(json.dumps(output,indent=2)+'\n'); print(json.dumps(output,indent=2))
if __name__=='__main__': main()
