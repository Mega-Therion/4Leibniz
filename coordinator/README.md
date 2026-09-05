# Automated archival-to-proof pipeline

The coordinator is intentionally **candidate-first**. `harvester.py` discovers public archival records and writes a manifest; it does not treat a network result as a verified witness. `auto_ingest.py` slices a locally supplied witness into 50–100 word fragments with SHA-256 metadata and writes them under a candidate directory. Canonical `corpus/latin/` promotion requires an independently reviewed witness.

`queue_manager.py` stores allow-listed work types in SQLite, leases jobs, records worker responses, and promotes only when at least three independent responses agree exactly at the configured threshold (95% by default). Disagreements remain `expert-review`.

Run a one-time discovery pass:

```bash
PYTHONPATH=. python3 coordinator/harvester.py --output coordinator/harvest_manifest.json
```

Run bounded volunteer processing:

```bash
PYTHONPATH=. python3 volunteer/client.py --daemon --database coordinator/job_queue.sqlite --worker-id workstation-1 --max-jobs 10
```

The daemon never runs arbitrary code or an implicit translation model. Translation and proof-search jobs are recorded for expert review unless an explicit trusted runner is added.
