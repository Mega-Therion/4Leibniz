# TRAP: lean4lean exits 0 on incompatible .olean headers

Found 2026-10-08 by an external audit of 4Leibniz (`agent_results/area_0.json`). lean4lean was built at its pinned
v4.33.0-rc2 and run against the project's v4.34.0-rc2 build files. It printed
`failed to read ... VisViva.olean, incompatible header` for every project module, and its process **returned 0**.

Guard in this repo: `.github/workflows/verify.yml` → `independent-kernel` fails on any
`incompatible header|failed to read|error` line (commit 88f519b).

Reproduce: build lean4lean at a toolchain older than the project's, then run
`lake env <lean4lean> Leibniz`. Expected: nonzero exit. Observed: 0.
Not runnable here without a second toolchain download (~3 GB).
