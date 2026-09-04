from __future__ import annotations
import json, shutil, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from proof_engine import search_text
from counterexample import find
from ucalculus import parse


def timed(fn):
    started = time.perf_counter(); value = fn(); return value, round((time.perf_counter()-started)*1000, 3)

def run(*, lean_timeout: int = 5) -> dict:
    corpus = json.loads((ROOT/'benchmarks/leibniz_benchmark.json').read_text())
    rows=[]
    for case in corpus['cases']:
        text=case['text']; claim=parse(text)
        _, proof_ms=timed(lambda: search_text(text))
        _, model_ms=timed(lambda: find(claim, 3))
        rows.append({'id':case['id'],'work':case['work'],'proof_search_ms':proof_ms,'bounded_model_ms':model_ms})
    lean_available=shutil.which('lake') is not None
    lean_ms=None; lean_ok=None
    if lean_available:
        try:
            proc, lean_ms=timed(lambda: subprocess.run(['lake','build'],cwd=ROOT,capture_output=True,text=True,timeout=lean_timeout))
            lean_ok=proc.returncode==0
        except subprocess.TimeoutExpired:
            lean_ms=None; lean_ok=False; lean_available=False
    backends=[{'name':'universal-calculus proof search','status':'available','mean_ms':round(sum(r['proof_search_ms'] for r in rows)/len(rows),3)},
              {'name':'bounded integer model search','status':'available','mean_ms':round(sum(r['bounded_model_ms'] for r in rows)/len(rows),3)},
              {'name':'Lean kernel build','status':'available' if lean_available else 'unavailable','mean_ms':lean_ms,'ok':lean_ok},
              {'name':'Z3 SMT','status':'unavailable','mean_ms':None,'reason':'not installed in benchmark environment'},
              {'name':'CVC5 SMT','status':'unavailable','mean_ms':None,'reason':'not installed in benchmark environment'}]
    return {'corpus':corpus['corpus'],'backend_results':backends,'cases':rows,'methodology':'Wall-clock local timings; compare only within the same environment. Unavailable backends are not imputed.','environment':{'python':sys.version.split()[0],'platform':sys.platform}}

if __name__=='__main__': print(json.dumps(run(),indent=2))
