from __future__ import annotations
from pathlib import Path
import json, time, sys
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from proof_engine import search_text

def run(path=Path(__file__).with_name('leibniz_benchmark.json')):
    corpus=json.loads(path.read_text()); results=[]; started=time.perf_counter()
    for case in corpus['cases']:
        result=search_text(case['text'])['search']['outcome']
        results.append({'id':case['id'],'work':case['work'],'expected':case['expected'],'actual':result,'correct':result==case['expected']})
    elapsed_ms=round((time.perf_counter()-started)*1000,3)
    return {'corpus':corpus['corpus'],'cases':results,'summary':{'total':len(results),'correct':sum(r['correct'] for r in results),'elapsed_ms':elapsed_ms}}

if __name__=='__main__': print(json.dumps(run(), indent=2))
