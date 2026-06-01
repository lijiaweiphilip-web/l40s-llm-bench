# Release Checklist

Target release: `v0.1.0`

Status: published on 2026-06-01 after PR #1 passed GitHub Actions.

## Scope

- [x] Keep release preparation limited to `CHANGELOG.md`,
  `docs/release-checklist.md`, and
  `docs/maintenance/release-v0.1.0.md`.
- [x] Treat v0.1.0 as an early-stage OSS readiness release, not a validated GPU
  performance publication.
- [x] Include dry-run validation, fake-server streaming validation, workload
  profiles, and run manifests in the release notes.
- [x] Note OSS-facing governance/support files and CI documentation when present.
- [x] Publish a `v0.1.0` tag and GitHub release after CI is green.

## Local Verification

Run these checks before publishing:

```powershell
python --version
python -m pytest -q
python scripts\bench_openai_compatible.py --config configs\generated_workload_matrix.yaml --dry-run --stream --output $env:TEMP\l40s-workload-profiles-dry-run.jsonl
python scripts\summarize_results.py --input $env:TEMP\l40s-workload-profiles-dry-run.jsonl --output-dir $env:TEMP\l40s-tables
python scripts\run_sanity_checks.py --repeats 1 --output $env:TEMP\l40s-sanity-checks.jsonl --report $env:TEMP\l40s-sanity-checks.md
```

Observed locally on 2026-06-01:

- [x] Python version check: Python 3.12.10
- [x] Unit tests: 21 passed
- [x] Workload profile dry run: wrote 16 records
- [x] Dry-run summary: wrote 5 summary rows
- [x] Fake-server sanity checks: PASS, wrote 8 records and a sanity report

Maintainer checks before final release:

- [x] Confirm CI is green on the release PR.
- [x] Confirm repository metadata, description, topics, and license display are
  correct on GitHub.
- [x] Confirm no private paths, credentials, unpublished benchmark results, or
  local-only artifacts are included in the release diff.
- [x] Confirm generated sample outputs should remain ignored, regenerated, or
  published as CI artifacts rather than committed release assets.
- [x] Confirm final version/date in `CHANGELOG.md`.

## Release Notes Checklist

- [x] State that this is harness validation, not real model performance.
- [x] Mention dry-run validation over generated workload profiles.
- [x] Mention local fake OpenAI-compatible streaming server validation.
- [x] Mention run manifest support for evidence bundles and artifact hashes.
- [x] Mention docs for methodology, limitations, result schema, workload
  profiles, fake-server validation, CI, and project rationale.
- [x] Mention governance/support files present in the repository.
- [x] Mention GitHub Actions validation.
- [x] Mention tag/release scope.

## Risks

- Synthetic dry-run and fake-server checks can validate harness behavior but do
  not prove GPU throughput, latency, memory use, or model-serving correctness.
- CI is documented as CPU-only; it does not exercise vLLM, GPUs, remote APIs, or
  production-like model servers.
- Real L40S results still need a separate evidence bundle before public
  performance claims.
