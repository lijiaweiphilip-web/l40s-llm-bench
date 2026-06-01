# Changelog

All notable release preparation notes for this project are recorded here.

## [0.1.1] - 2026-06-01

Maintenance patch for the early OSS readiness track.

### Added

- First-run troubleshooting and result-interpretation guide for dry-run,
  fake-server, and real-server boundary checks.
- Synthetic fake-server example result fixture and lightweight validator.
- AGENTS instructions and maintainer playbook for safer repeat maintenance.
- Application readiness scorecard with conservative Codex for OSS form text.
- First-user smoke-test feedback workflow, bilingual outreach template, smoke
  feedback issue template, and outreach target template.

### Validation

- GitHub Actions `CPU quality checks` passed on PRs #8, #9, #10, and #11.
- Local validation for PR #9:
  - `python scripts/validate_result.py examples/results --require-synthetic-fake-server` -> PASS
  - `python -m pytest -q` -> 24 passed
- Local validation for PRs #10 and #11:
  - `python -m pytest -q` -> 21 passed

### Known limitations

- This release still does not include real L40S, vLLM, or GPU benchmark
  results.
- Synthetic and fake-server artifacts are examples for validating the workflow,
  not performance evidence.
- The public feedback workflow invites early testers but does not claim that
  users have adopted or validated the project.

## [0.1.0] - 2026-06-01

Early-stage OSS readiness release for `l40s-llm-bench`, a minimal scaffold for
reproducible LLM inference benchmark experiments.

### Added

- OpenAI-compatible benchmark client support for dry-run and streaming
  measurement workflows.
- Local fake OpenAI-compatible streaming server validation for TTFT, TPOT,
  concurrency, slow-token, high-TTFT, and HTTP error handling scenarios.
- Workload profile definitions and generated benchmark matrix support for
  short chat, summarization, code generation, long-context QA, and burst
  concurrency shapes.
- Result summarization, workload profile reporting, JSONL compatibility checks,
  regression comparison utilities, environment collection, and run manifest
  generation.
- Documentation for methodology, limitations, result schema, fake-server
  validation, workload profiles, workload reports, run manifests, CI scope,
  community feedback, and project rationale.
- OSS-facing governance and support files are present in the repository:
  `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, and
  `SUPPORT.md`.
- CPU-only GitHub Actions CI documentation is present; the workflow is described
  as avoiding GPUs, credentials, remote APIs, and external model downloads.

### Validation

- Observed locally on 2026-06-01:
  - `python --version` -> Python 3.12.10
  - `python -m pytest -q` -> 21 passed
  - `python scripts/bench_openai_compatible.py --config configs/generated_workload_matrix.yaml --dry-run --stream --output $env:TEMP/l40s-workload-profiles-dry-run.jsonl` -> wrote 16 records
  - `python scripts/summarize_results.py --input $env:TEMP/l40s-workload-profiles-dry-run.jsonl --output-dir $env:TEMP/l40s-tables` -> wrote 5 summary rows
  - `python scripts/run_sanity_checks.py --repeats 1 --output $env:TEMP/l40s-sanity-checks.jsonl --report $env:TEMP/l40s-sanity-checks.md` -> PASS, wrote 8 records and a sanity report
- Observed in GitHub Actions on PR #1 before merge:
  - `CPU quality checks` -> success

### Known limitations

- This release candidate validates the harness and synthetic workflows, not
  real L40S GPU performance.
- Real model-server, vLLM, GPU, and long-running benchmark validation remain
  out of scope for this early v0.1.0 release unless separately provisioned.
