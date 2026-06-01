# v0.1.0 Release Notes

This is the maintainer release note for the initial OSS readiness release.

## Summary

`v0.1.0` is an early OSS readiness release for `l40s-llm-bench`. It packages a
small, reproducible benchmark harness for OpenAI-compatible LLM inference
experiments, with emphasis on local validation before any GPU or paid model
time is used.

This release is not a claim about real L40S performance. The validated path is
limited to unit tests, synthetic dry runs, generated workload profiles, local
fake-server streaming checks, and documentation/release hygiene.

## Highlights

- Benchmark dry-run path for checking generated benchmark cases without sending
  real model requests.
- Streaming measurement path for OpenAI-compatible chat-completion servers.
- Local fake-server validation for TTFT, TPOT, concurrent streaming, slow-token,
  high-TTFT, and HTTP error scenarios.
- Workload profiles for short chat, summarization, code generation,
  long-context QA, and burst chat concurrency.
- Run manifest support for recording benchmark inputs, outputs, file hashes,
  missing artifacts, and scope notes.
- Result summarization, workload-profile reporting, JSONL compatibility checks,
  regression comparison, environment collection, and sanity-check utilities.
- Documentation covering methodology, limitations, result schema, fake-server
  validation, workload profiles, workload reports, run manifests, CI scope,
  community feedback, and project rationale.
- OSS-facing governance/support files are present: `LICENSE`,
  `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `SUPPORT.md`.

## Local Validation

Observed on 2026-06-01 before publishing `v0.1.0`:

```powershell
python --version
```

Result: Python 3.12.10

```powershell
python -m pytest -q
```

Result: 21 passed

```powershell
python scripts\bench_openai_compatible.py --config configs\generated_workload_matrix.yaml --dry-run --stream --output $env:TEMP\l40s-workload-profiles-dry-run.jsonl
```

Result: wrote 16 records

```powershell
python scripts\summarize_results.py --input $env:TEMP\l40s-workload-profiles-dry-run.jsonl --output-dir $env:TEMP\l40s-tables
```

Result: wrote 5 summary rows

```powershell
python scripts\run_sanity_checks.py --repeats 1 --output $env:TEMP\l40s-sanity-checks.jsonl --report $env:TEMP\l40s-sanity-checks.md
```

Result: PASS, wrote 8 records and a sanity report

## GitHub Release Text

Title: `v0.1.0 - OSS readiness baseline`

Body:

```markdown
## v0.1.0

Initial OSS readiness release for `l40s-llm-bench`.

This is an early harness release, not a published L40S performance result. It
focuses on reproducible dry runs, OpenAI-compatible streaming measurement,
local fake-server validation, workload profiles, run manifests, and baseline
documentation.

Validated locally:

- Unit tests: 21 passed
- Workload profile dry run: 16 records
- Dry-run summary: 5 summary rows
- Fake-server sanity checks: PASS with 8 records

Known limitations:

- No real GPU/model-server benchmark claims are made in this release.
- Default CI is CPU-only and avoids credentials, GPUs, remote APIs, and model
  downloads.
- Real vLLM/GPU validation should be run separately before publishing any
  performance numbers.
```

## Publishing Notes

- GitHub Actions `CPU quality checks` passed on PR #1 before merge.
- Tag: `v0.1.0`
- This release should remain clearly scoped as harness and documentation
  readiness, not real GPU performance.

## Follow-Up

- Run or verify GitHub Actions on the release branch or PR.
- Decide whether to include generated dry-run artifacts in the release, keep
  them as CI artifacts only, or omit them from the release entirely.
- Add real GPU/model-server validation only after credentials, hardware, model
  selection, and reproducibility expectations are explicitly scoped.
- Recheck that no private paths, credentials, unpublished benchmark claims, or
  local-only artifacts appear in the final release diff.
