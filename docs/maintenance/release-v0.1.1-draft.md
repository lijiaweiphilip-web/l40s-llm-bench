# v0.1.1 Release Readiness Draft

Prepared: 2026-06-01

Status: release-preparation note for the `v0.1.1` patch release.

## Source of Truth

- Previous release: `v0.1.0`, published as `v0.1.0 - OSS readiness baseline`.
- Candidate head inspected: `origin/main` at the post-PR #11 merge commit.
- Candidate range inspected: `v0.1.0^{}..origin/main`.
- No local or remote `v0.1.1` tag was found during this check.
- `CHANGELOG.md` now records the `0.1.1` maintenance patch.

## Merged Factual Changes Since v0.1.0

- `49358ef8106413b4c01b7824ac10316143199a6c` records the published
  `v0.1.0` OSS readiness baseline in the README and maintenance docs, points
  maintenance planning at the `v0.2.0` milestone and issues #2 through #7, and
  keeps real GPU benchmark results out of scope.
- PR #8, merged as `030a624350b5eb3f577f8ca95b5a4679d34852bb`, adds
  `docs/first_run_troubleshooting.md` and links it from the README and
  `docs/ten_minute_smoke_run.md`. The guide covers install/environment setup,
  dry-run failures, endpoint and configuration mistakes, streaming confusion,
  summary/manifest mismatches, first-run field interpretation, and what to
  attach when asking for help. It closes issue #6.
- PR #9 adds synthetic fake-server result fixtures, a lightweight validator,
  validator tests, `AGENTS.md`, and a maintainer playbook. It closes or
  materially addresses issue #7 without adding real benchmark claims.
- PR #10 adds the application readiness scorecard and conservative Codex for
  OSS form text variants.
- PR #11 adds the first-user smoke-test feedback workflow, bilingual outreach
  templates, a smoke-run feedback issue template, and an outreach target
  template.
- Issue #12 publicly invites early testers to try only the dry-run and
  fake-server paths. It is an invitation, not adoption evidence.
- No real model-server validation, adoption metrics, or real L40S/GPU
  performance claims were added.

## Readiness Checklist

- [x] Inspect `CHANGELOG.md`.
- [x] Inspect the existing `v0.1.0` release notes and published release state.
- [x] Inspect post-`v0.1.0` commits on `origin/main`.
- [x] Inspect likely incoming PR branch state, including the local
  `review/pr-8-troubleshooting` branch and GitHub PR #8.
- [x] Confirm PR #8 is merged into `origin/main`.
- [x] Confirm PRs #9, #10, and #11 are merged into `origin/main`.
- [x] Confirm issue #12 is open as a truthful early-tester invitation.
- [x] Confirm no `v0.1.1` tag exists locally or on `origin`.
- [x] Keep draft notes limited to merged factual changes.
- [x] Exclude unmerged `v0.2.0` roadmap work from the patch release notes.
- [ ] Confirm CI is green on the exact final commit to tag.
- [x] Add a `CHANGELOG.md` entry for `0.1.1`.
- [ ] If this readiness note should be part of the tagged source, merge
  `release/v0.1.1-draft` before tagging.
- [ ] Ensure the tag is cut from the final release commit after this PR merges.

## Must Merge Before Tagging v0.1.1

For the patch scope inspected here, the tagged commit should include PRs #8,
#9, #10, #11, and this release-preparation PR with the changelog entry.

Do not include or mention these as `v0.1.1` release contents unless they are
merged before the tag:

- open `v0.2.0` roadmap issues #2, #3, #4, #5, and #7;
- any real GPU, vLLM, L40S, adoption, usage, or downstream-user claims.

## Verification Run While Drafting

Run from the release-preparation worktree:

```powershell
python -m pytest -q
```

Result before final release prep: `21 passed`.

```powershell
python scripts\bench_openai_compatible.py --dry-run --output $env:TEMP\l40s-v011-dry-run.jsonl
python scripts\summarize_results.py --input $env:TEMP\l40s-v011-dry-run.jsonl --output-dir $env:TEMP\l40s-v011-tables
```

Result: dry run wrote 4 records; summary wrote 2 rows.

## Draft GitHub Release Notes

Title: `v0.1.1 - first-run troubleshooting docs`

Body:

```markdown
## v0.1.1

`v0.1.1` is a documentation, validation, and maintenance patch over `v0.1.0`.

### Changed

- Added a first-run troubleshooting and result-interpretation guide for the
  existing dry-run and fake-server validation paths.
- Linked the troubleshooting guide from the README and the 10-minute smoke-run
  guide.
- Added synthetic fake-server example result fixtures plus a lightweight
  validator and tests.
- Added AGENTS instructions and a maintainer playbook.
- Added an application readiness scorecard with conservative Codex for OSS
  text variants.
- Added a first-user smoke-test feedback workflow, bilingual outreach template,
  smoke-run feedback issue template, and outreach target template.

### Validation

- GitHub Actions `CPU quality checks` passed on PRs #8, #9, #10, and #11
- `python -m pytest -q` -> 24 passed on the validator branch
- Result validator -> PASS on the synthetic fake-server fixture
- Dry-run benchmark check -> wrote 4 records
- Dry-run summary check -> wrote 2 rows

### Scope and limitations

- This release does not add real model-server validation, adoption metrics, or
  real L40S/GPU performance claims.
- Synthetic and fake-server artifacts remain harness-validation examples only,
  not hardware or model performance evidence.
```
