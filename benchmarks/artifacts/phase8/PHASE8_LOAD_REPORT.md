# Phase 8 WebSocket Load Report

| Profile | Clients | Messages/client | Elapsed (s) | Throughput (events/s) | Rejected |
|---|---:|---:|---:|---:|---:|
| duplicate | 8 | 4 | 4.6043 | 8.69 | 5 |
| equivocation | 8 | 4 | 6.1157 | 6.54 | 13 |
| malformed | 8 | 4 | 4.8052 | 8.32 | 4 |
| none | 8 | 4 | 8.4635 | 4.73 | 0 |
| stale | 8 | 4 | 4.7680 | 8.39 | 6 |

The measurements are bounded observations from one client host and one public edge path. They are not a capacity SLA. Fault profiles confirm rejection behavior, while production capacity requires sustained tests, backpressure metrics, and regional runners.
