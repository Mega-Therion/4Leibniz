from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from performance import run

ROOT = Path(__file__).parents[1]
OUT = ROOT/'benchmarks'/'artifacts'

def generate():
    OUT.mkdir(exist_ok=True)
    data=run(); (OUT/'performance.json').write_text(json.dumps(data,indent=2))
    available=[row for row in data['backend_results'] if row.get('mean_ms') is not None]
    names=[row['name'] for row in available]; values=[row['mean_ms'] for row in available]
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,ax=plt.subplots(figsize=(10,5.5)); bars=ax.barh(names,values,color=['#c99a4a','#6da58b','#7894b8'])
    ax.set_xscale('log'); ax.set_xlabel('Mean wall-clock time (ms, logarithmic scale)'); ax.set_title('4Leibniz Phase 5 solver-backend performance')
    for bar,value in zip(bars,values): ax.text(value,bar.get_y()+bar.get_height()/2,f' {value:.3f} ms',va='center')
    fig.tight_layout(); fig.savefig(OUT/'performance.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,5.5)); ids=[r['id'] for r in data['cases']]; proof=[r['proof_search_ms'] for r in data['cases']]; model=[r['bounded_model_ms'] for r in data['cases']]; x=range(len(ids)); width=.38
    ax.bar([i-width/2 for i in x],proof,width,label='Proof search',color='#c99a4a'); ax.bar([i+width/2 for i in x],model,width,label='Bounded model search',color='#6da58b'); ax.set_xticks(list(x),ids,rotation=35,ha='right'); ax.set_ylabel('Wall-clock time (ms)'); ax.set_title('Per-case timing comparison'); ax.legend(); fig.tight_layout(); fig.savefig(OUT/'per_case_performance.png',dpi=160); plt.close(fig)
    unavailable=[row['name'] for row in data['backend_results'] if row.get('mean_ms') is None]
    md=['# 4Leibniz Phase 5 Performance Report','',f"Corpus: `{data['corpus']}`",'',data['methodology'],'','## Backend summary','', '| Backend | Status | Mean time (ms) |','|---|---:|---:|']
    for row in data['backend_results']: md.append(f"| {row['name']} | {row['status']} | {row.get('mean_ms','—')} |")
    md += ['', '![Backend timing comparison](performance.png)','', '![Per-case timing comparison](per_case_performance.png)','', '## Interpretation','', 'The chart compares only backends that were actually available in this environment. Wall-clock measurements are local regression signals, not portable claims about absolute performance. Unavailable SMT backends are retained as explicit gaps rather than being assigned fabricated timings.', '', f"Unavailable backends: {', '.join(unavailable) if unavailable else 'none'}."]
    (OUT/'PERFORMANCE_REPORT.md').write_text('\n'.join(md)+'\n')
    return data

if __name__=='__main__': generate()
