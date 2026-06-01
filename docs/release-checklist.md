# Release Checklist

Target release: `v0.1.0`

Status: draft release preparation only. Do not create tags or GitHub releases
from this checklist without maintainer approval.

## Scope

- [x] Keep release preparation limited to `CHANGELOG.md`,
  `docs/release-checklist.md`, and
  `docs/maintenance/release-v0.1.0-draft.md`.
- [x] Treat v0.1.0 as an early-stage OSS readiness release, not a validated GPU
  performance publication.
- [x] Include dry-run validation, fake-server streaming validation, workload
  profiles, and run manifests in the release notes.
- [x] Note OSS-facing governance/support files and CI documentation when present.
- [x] Do not create tags, GitHub releases, or release assets from local git.
- [x] Record that `gh` CLI is unavailable and draft/manual release mode is
  expected.

## Local Verification

Run these checks before promoting the draft:

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

Maintainer placeholders before final release:

- [ ] Confirm CI is green on the release branch or PR.
- [ ] Confirm repository metadata, description, topics, and license display are
  correct on GitHub.
- [ ] Confirm no private paths, credentials, unpublished benchmark results, or
  local-only artifacts are included in the release diff.
- [ ] Confirm whether any generated sample outputs should be attached, ignored,
  or regenerated for the final release.
- [ ] Confirm final version/date in `CHANGELOG.md`.

## Release Notes Checklist

- [x] State that this is harness validation, not real model performance.
- [x] Mention dry-run validation over generated workload profiles.
- [x] Mention local fake OpenAI-compatible streaming server validation.
- [x] Mention run manifest support for evidence bundles and artifact hashes.
- [x] Mention docs for methodology, limitations, result schema, workload
  profiles, fake-server validation, CI, and project rationale.
- [x] Mention governance/support files present in the repository.
- [x] Mention `gh` CLI unavailable locally.
- [x] Mention tags/releases were not created.

## Risks

- Synthetic dry-run and fake-server checks can validate harness behavior but do
  not prove GPU throughput, latency, memory use, or model-serving correctness.
- CI is documented as CPU-only; it does not exercise vLLM, GPUs, remote APIs, or
  production-like model servers.
- Release publishing remains manual because `gh` is unavailable in this
  environment.

