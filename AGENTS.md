# Base44 Development Setup

## What this project is

4Leibniz is a self-contained Python/Flask web app for formal verification in Lean 4.
The Flask app (`api.py`) serves a single-page frontend (`web/index.html`) at `/`
and exposes ~40 JSON API endpoints under `/api/*`. It is single-origin — the
frontend calls same-origin `/api/*` endpoints, no separate API service needed.

## How it runs

- **Compose file**: `docker-compose.base44.yml` (single `web` service)
- **Base image**: `python:3.12-slim` + `uv` (installed via pip in `Dockerfile.base44`)
- **Dependencies**: `uv sync --frozen` from `uv.lock` at container startup, then
  `flask run --host 0.0.0.0 --port 3000` (debug mode OFF)
- **Source**: bind-mounted at `/app`; Python edits need a service restart
  (`docker compose -f docker-compose.base44.yml restart web`) or `reload_preview`
- **Port**: 3000 (mapped directly, no proxy needed)
- **Healthcheck**: `curl -f http://localhost:3000/`

## External services (all optional)

The app boots and works with zero external credentials:

- **Telemetry**: PostHog is off by RY's decision (2026-09-26). Never add a PostHog key; the app runs without
  analytics in every mode.
- **OpenAI** (`OPENAI_API_KEY`, `OPENAI_API_BASE`): AI premise suggestions. Falls
  back to a deterministic local mode without credentials.
- **LEIBNIZ_API_TOKEN**: gates mutation endpoints. Without it, mutation routes
  return 503 (secure-by-default). Read-only endpoints work without it.

## Verification

```bash
# App is serving
curl http://localhost:3000/                          # frontend HTML
curl http://localhost:3000/api/modules               # module list JSON
curl http://localhost:3000/api/epistemic/lattice     # lattice JSON

# Run the test suite
docker compose -f docker-compose.base44.yml exec web uv run pytest tests/
```
