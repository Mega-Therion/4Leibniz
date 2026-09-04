from __future__ import annotations
import json, random
from pathlib import Path
from replicated_coordinator import DecisionVote, ParticipantAck, ReplicatedDecisionLog, AckStore, validate_decision
from replica_membership import elect_coordinator

def run(seed=12, cases=200):
    rng=random.Random(seed); failures=[]; accepted=0; rejected=0; recovered=0
    for i in range(cases):
        txid=f't-{i}'; digest=f'd-{rng.randrange(4)}'; votes=[]
        for j in range(3): votes.append(DecisionVote(str(j),txid,rng.choice(['commit','abort','invalid']),digest if rng.random()>.2 else 'bad',signature_verified=rng.random()>.15))
        try:
            result=validate_decision(votes,txid,digest,1)
            (accepted:=accepted+1) if result['accepted'] else (rejected:=rejected+1)
        except Exception as exc: failures.append({'case':i,'kind':'vote_exception','error':str(exc)})
        log=ReplicatedDecisionLog('r'); ack=AckStore()
        try:
            if rng.random()>.2: log.record(DecisionVote('r',txid,'commit',digest))
            recovered_log=ReplicatedDecisionLog.recover(log.snapshot()); recovered += int(recovered_log.snapshot()['log']['last_sequence']==log.snapshot()['log']['last_sequence'])
            a=ParticipantAck('s',txid,'prepared',digest,1,f's:{txid}',100); ack.record(a); AckStore.recover(ack.durable_snapshot())
        except Exception as exc: failures.append({'case':i,'kind':'recovery_exception','error':str(exc)})
    partition_cases=[]
    for mask in range(8):
        reachable=[i for i in range(3) if mask & (1<<i)]
        partition_cases.append({'mask':mask,'reachable_replicas':reachable,'three_replica_quorum_available':len(reachable)>=3})
    return {'seed':seed,'cases':cases,'accepted_decisions':accepted,'rejected_decisions':rejected,'recovered_logs':recovered,'partition_cases':partition_cases,'failures':failures}

def main():
    out=Path('benchmarks/artifacts/phase12'); out.mkdir(parents=True,exist_ok=True); result=run(); (out/'fuzz_report.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
