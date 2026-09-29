# ledger-api

> A small Python/Flask service that runs on my self-hosted Kubernetes platform.
> Today it's a production-shaped skeleton; it will grow into a double-entry
> ledger API that every later project (supply chain, resilience, cloud) protects.

## Why this exists
A platform needs something real to run. `ledger-api` is deliberately small so the
focus stays on the platform around it, but it's built the way a production service
should be: health checks, metrics, a non-root container, and a pipeline that won't
publish an image unless lint and tests pass.

It's deployed by GitOps from the [`platform`](https://github.com/esoung11/platform)
repo. This repo builds the image; `platform` decides what runs
([ADR-0003](https://github.com/esoung11/platform/blob/main/docs/adr/0003-manifests-in-config-repo.md)).

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness/readiness probe target. Returns `{"status": "ok"}` |
| `GET` | `/metrics` | Prometheus metrics (e.g. `ledger_health_checks_total`) |

## Pipeline
Every push runs three stages in self-hosted GitLab CI:

1. **lint:** `ruff check .`
2. **test:** `pytest`
3. **dockerize:** build the image and push `ledger-api:<short-sha>` to the GitLab
   registry, plus `:latest` on `main` only.

Images are deployed by their immutable SHA tag, never `:latest`
([ADR-0006](https://github.com/esoung11/platform/blob/main/docs/adr/0006-pin-images-by-sha-tag.md)).

## Container
- `python:3.12-slim` base, served by `gunicorn` on port 8000.
- Runs as an unprivileged user (UID 1000). The Kubernetes Deployment also enforces
  `runAsNonRoot`, with CPU/memory requests and limits.

## Run it locally
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt pytest
pytest -q
python app.py            # then: curl localhost:8000/health
```

Or with Docker:
```bash
docker build -t ledger-api .
docker run --rm -p 8000:8000 ledger-api
```

## A bug the tests missed
`/metrics` was served with a misspelled header (`Cotent-Type`), so responses went
out with the wrong content type. The existing test only checked that the metric
name appeared in the body, so it passed. Prometheus 3 can reject scrapes that lack
a valid content type, so this would have surfaced as a silent monitoring gap.
Fixed, and `test_metrics_content_type` now guards it; it fails against the old code.

## Roadmap
- **Ledger:** accounts, transfers and balances in PostgreSQL, using double-entry
  bookkeeping, idempotency keys on writes, and an append-only audit log.
- **Supply chain:** Kaniko builds, a CycloneDX SBOM per image, and cosign signatures.
- **Observability:** SLOs such as "p99 transfer latency under 300ms" and "zero
  double-applied transfers".
