# First-Run Troubleshooting and Result Interpretation

This guide is for first-time contributors and maintainers who can validate only
the CPU-only dry-run and fake-server paths. It helps separate harness issues
from model-serving issues before anyone spends GPU time or publishes a result.

## Start With the Safest Path

Use the paths in this order:

1. `--dry-run` confirms the benchmark client, raw JSONL writing, and summary
   scripts can complete without contacting a server.
2. `fake_openai_server.py` confirms the client can measure streaming TTFT and
   TPOT against controlled delays.
3. A real OpenAI-compatible server run is only worth attempting after the
   first two paths behave as expected.

If the dry run fails, do not interpret later failures as serving-stack issues.
If the dry run succeeds but the fake server fails, focus on request/streaming
mechanics before suspecting model quality or GPU performance.

## Common First-Run Failure Patterns

### Install and Environment Setup

Symptoms:

- `pip` cannot install requirements.
- `pytest` fails before benchmark scripts run.
- Commands import the wrong Python environment.

Checks:

```bash
python --version
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

If those fail, fix the local Python environment first. The benchmark harness
cannot be trusted until the development dependencies and test suite pass.

### Dry-Run Path Fails

Symptoms:

- `python scripts/bench_openai_compatible.py --dry-run` exits with an error.
- `results/raw/dry_run.jsonl` is missing or empty.
- `summarize_results.py` cannot read the generated JSONL.

Checks:

```bash
python scripts/bench_openai_compatible.py --dry-run --output results/raw/dry_run.jsonl
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
python scripts/check_jsonl_compat.py --input results/raw/dry_run.jsonl --output results/tables/jsonl_compat.md
```

Interpretation:

- A dry-run failure usually means a harness, schema, or local environment
  problem, not a server connectivity problem.
- A compatibility failure means the raw records need inspection before any
  summary or manifest should be treated as reliable.

### Endpoint or Configuration Mistakes

Symptoms:

- Real or fake-server runs fail immediately.
- `status=error` dominates the JSONL.
- `http_status` is `404`, `401`, `403`, or `500` for most requests.

Checks:

- Confirm the benchmark config points at the expected OpenAI-compatible
  endpoint path such as `/v1/chat/completions`.
- Confirm the port, host, and any required auth environment variables match
  the intended server.
- Use the fake-server config first to prove the client path works without a
  real model in the loop.

Interpretation:

- Repeated `404` usually means the path or port is wrong.
- Repeated `401` or `403` usually means auth is missing or invalid.
- Repeated `500` may still be a serving-stack problem, but only after the
  dry-run and fake-server paths are known-good.

### Streaming Confusion

Symptoms:

- `ttft_ms`, `tpot_ms`, or `output_token_events` are `null`.
- Throughput fields look empty even though the request succeeded.
- Results look slower or simpler than expected.

Checks:

- Confirm the benchmark command used `--stream` when the scenario expects
  token-event timing.
- Confirm the target endpoint actually emits streaming token events in the
  OpenAI-compatible shape the harness expects.
- Run the controlled fake server before reasoning about real-server TTFT/TPOT.

Interpretation:

- `null` TTFT/TPOT fields on non-streaming runs are expected.
- Non-null latency with null TTFT/TPOT often means the request completed, but
  no token-event stream was observed.
- Streaming validation against the fake server checks harness mechanics only;
  it does not validate model quality or GPU throughput.

### Summary, Manifest, or Artifact Mismatch

Symptoms:

- Summary tables do not match the raw JSONL.
- A manifest references missing files.
- Reviewers cannot tell which raw logs support a result.

Checks:

```bash
python scripts/summarize_results.py --input results/raw/<run>.jsonl --output-dir results/tables
python scripts/build_run_manifest.py --run-id <run-id> --raw results/raw/<run>.jsonl --summary results/tables/summary.csv
```

Interpretation:

- Treat the raw JSONL as the primary evidence artifact.
- Treat the summary and manifest as derived views that must point back to the
  exact raw file and config used for the run.

## How To Read First-Run Results

These fields are the most useful for a first-pass interpretation:

| Field | What it tells you on a first run |
| --- | --- |
| `status` | Whether a request finished (`ok`) or failed (`error`). Start here before comparing timings. |
| `error_kind` | The coarse failure category, such as HTTP, timeout, connection, or URL-level problems. |
| `http_status` | The server's HTTP status when available. Useful for spotting auth and endpoint mistakes. |
| `latency_ms` | End-to-end request time. This is the safest timing field to compare across dry-run, fake-server, and real-server paths. |
| `ttft_ms` | Time to first token when streaming works. If this is `null`, verify that the run and endpoint actually used streaming. |
| `tpot_ms` | Time per output token when streaming token events are observed. Interpret only after fake-server validation passes. |
| `output_tokens_per_second` | Derived throughput for one request. Useful for local comparisons, but not a standalone benchmark claim. |

Keep these boundaries in mind:

- Dry-run output proves the pipeline, not model or GPU behavior.
- Fake-server output proves timing mechanics against controlled delays, not
  real inference performance.
- Real-server output may still reflect prompt shape, server settings, network
  path, retries, or timeouts more than GPU capability.

## What To Attach When Asking For Help

When opening an issue or asking a maintainer for review, attach:

- the exact command you ran;
- the config path or inline parameters used;
- whether the run was dry-run, fake-server, or real-server;
- the raw JSONL file or a small redacted excerpt;
- the generated summary path;
- the run manifest path, if available;
- the observed `status`, `error_kind`, and `http_status` patterns;
- any redacted endpoint or serving-stack notes needed to reproduce the issue.

Do not include API keys, bearer tokens, private endpoint URLs, internal
hostnames, or confidential hardware inventory.
