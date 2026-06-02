# v0.1.2 Release Readiness Draft

Prepared: 2026-06-02

Status: release-preparation note for the `v0.1.2` maintenance release.

## Source of Truth

- Previous release: `v0.1.1`, published as `v0.1.1 - maintenance patch`.
- Candidate head inspected before this release/evidence PR: `origin/main` at
  `ca7292f`, the post-PR #16 merge commit.
- Candidate range inspected conceptually: `v0.1.1..origin/main`.
- `CHANGELOG.md` now records the `0.1.2` maintenance patch.

## Merged Factual Changes Since v0.1.1

- PR #14 added a reproducibility evidence bundle contract, checklist, artifact
  review rubric, synthetic fake-server bundle, validator, tests, and CI
  validation. It closed issue #2.
- PR #15 added GPU metrics guidance, optional DCGM notes, synthetic telemetry
  fixtures, `nvidia-smi` collection helper, GPU metrics summarizer, tests, and
  CI sample validation. It closed issue #4.
- PR #16 added a dry-validatable vLLM/L40S smoke profile, backend config, schema
  interpretation notes, helper script, real-artifact placeholder, tests, and CI
  dry validation. It closed issue #3.
- Issue #17 publicly asks for the first real L40S/vLLM evidence bundle and
  lists required artifacts.
- No real model-server validation, adoption metrics, or real L40S/GPU
  performance claims were added.

## Readiness Checklist

- [x] Confirm PRs #14, #15, and #16 are merged.
- [x] Confirm issues #2, #3, and #4 are closed.
- [x] Confirm issue #12 has no external feedback yet.
- [x] Create issue #17 for the first real L40S/vLLM artifact ask.
- [x] Confirm main CI is green at `ca7292f`.
- [x] Add `CHANGELOG.md` entry for `0.1.2`.
- [x] Update evidence packet and readiness scorecard.
- [ ] Merge the release/evidence PR.
- [ ] Confirm main CI is green on the final release commit.
- [ ] Publish `v0.1.2` from the final release commit.

## Draft GitHub Release Notes

Title: `v0.1.2 - reproducibility evidence and GPU metrics preparation`

Body:

```markdown
## v0.1.2

`v0.1.2` is a maintenance release focused on reproducibility evidence, GPU
telemetry preparation, and a dry-validatable vLLM/L40S smoke profile.

### Added

- Reproducibility evidence bundle docs, checklist, artifact review rubric,
  synthetic fake-server evidence bundle, validator, tests, and CI validation.
- GPU metrics guide for `nvidia-smi`, optional DCGM notes, synthetic telemetry
  fixtures, bounded collection helper, summary parser, tests, and CI sample
  validation.
- vLLM/L40S smoke-run profile, backend config, schema interpretation notes,
  dry-validation helper, real-artifact placeholder, tests, and CI dry
  validation.
- Public hardware-needed issue for the first real L40S/vLLM evidence bundle:
  https://github.com/lijiaweiphilip-web/l40s-llm-bench/issues/17
- Updated Codex for Open Source evidence packet and readiness scorecard.

### Validation

- GitHub Actions `CPU quality checks` passed on PRs #14, #15, and #16.
- Main branch CI passed after those merges.
- `python scripts/validate_evidence_bundle.py examples/evidence-bundles` -> PASS
- `python -m pytest -q` -> 36 passed during release preparation.

### Scope and limitations

- This release does not include real L40S, vLLM, model-server, or GPU benchmark
  results.
- Synthetic fake-server and GPU telemetry files are tooling fixtures, not
  performance evidence.
- Public tester feedback and a real hardware artifact are still pending.
```
