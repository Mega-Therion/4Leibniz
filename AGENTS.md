# 4Leibniz — Base44 Dev Environment

## What this project is
A **Lean 4 formal verification library** (`4Leibniz`), not a web app. It contains 6 formal
modules under `Leibniz/*.lean` with 11 machine-checked theorems. "Running" the project means
`lake build`, which invokes the Lean 4 kernel to verify every proof.

There is no original web frontend. A small Flask presentation layer (`web/`) was added so the
project is visible in the Base44 preview (port 3000). It serves a page describing the modules
and runs the `lake build` verification oracle ("Calculemus") on demand.

## Stack
- **Lean 4** toolchain `leanprover/lean4:v4.33.1`, managed by `elan` (installed in the image).
- **Lake** build system (no external package dependencies — `lake-manifest.json` is empty).
- **Flask** web server (`web/app.py`) on port 3000, serving `web/templates/` + `web/static/`.

## Running
```
docker compose -f docker-compose.base44.yml up -d --build
```
- The `Dockerfile.base44` image is `python:3.12-slim` + `elan` + `flask`.
- Source is bind-mounted at `/app`; Flask runs in debug mode (auto-reloads Python changes).
- On startup, `web/app.py` triggers a background `lake build` (downloads the toolchain on
  first run, ~12s) and caches the result. The page polls `/api/build` for status.

## Key endpoints
- `GET /` — the Calculemus web page.
- `GET /api/modules` — parses `Leibniz/*.lean`, returns module names, theorems, definitions.
- `GET /api/build` — current/cached `lake build` result (status, exit code, output, elapsed).
- `POST /api/build/run` — triggers a fresh `lake build`.

## Verifying it works
- `curl -sf -H "Host: external-preview.example.com" http://localhost:3000/` must return the page.
- `curl -s http://localhost:3000/api/build` → `status: "done"`, `exit_code: 0` means all proofs pass.
- `lake build` inside the container should print `Build completed successfully (9 jobs)`.

## Notes
- The original `scripts/calculemus.py` hardcodes `cwd="/home/mega/4Leibniz"` and is not used by
  the web layer — `web/app.py` runs `lake build` directly in `/app`.
- No external secrets are required.
