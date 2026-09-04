from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
ART=ROOT/'artifacts'/'phase8'
files=sorted(ART.glob('live_*.json'))
rows=[json.loads(p.read_text()) for p in files]
labels=[r['fault_mode'] for r in rows]
throughput=[r['throughput_events_per_second'] for r in rows]
rejected=[r['outcomes'].get('rejected',0) for r in rows]
fig, ax=plt.subplots(figsize=(10,5))
x=range(len(labels)); ax.bar(x, throughput, color='#5b8ff9'); ax.set_xticks(list(x), labels); ax.set_ylabel('Events per second'); ax.set_title('4Leibniz Phase 8 WebSocket load and fault injection'); ax.grid(axis='y', alpha=.2); fig.tight_layout(); fig.savefig(ART/'phase8_performance.png', dpi=160); plt.close(fig)
report=['# Phase 8 WebSocket Load Report','', '| Profile | Clients | Messages/client | Elapsed (s) | Throughput (events/s) | Rejected |', '|---|---:|---:|---:|---:|---:|']
for r in rows: report.append(f"| {r['fault_mode']} | {r['clients']} | {r['messages_per_client']} | {r['elapsed_seconds']:.4f} | {r['throughput_events_per_second']:.2f} | {r['outcomes'].get('rejected',0)} |")
report += ['', 'The measurements are bounded observations from one client host and one public edge path. They are not a capacity SLA. Fault profiles confirm rejection behavior, while production capacity requires sustained tests, backpressure metrics, and regional runners.']
(ART/'PHASE8_LOAD_REPORT.md').write_text('\n'.join(report)+'\n')
(ART/'phase8_summary.json').write_text(json.dumps(rows,indent=2)+'\n')
print(f'Wrote {ART/"phase8_performance.png"}')
