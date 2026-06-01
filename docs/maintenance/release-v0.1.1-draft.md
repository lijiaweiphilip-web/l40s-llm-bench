# v0.1.1 Release Readiness Draft

Prepared: 2026-06-01

Status: draft only. Do not tag or publish from this file alone.

## Source of Truth

- Previous release: `v0.1.0`, published as `v0.1.0 - OSS readiness baseline`.
- Candidate head inspected: `origin/main` at
  `030a624350b5eb3f577f8ca95b5a4679d34852bb`.
- Candidate range inspected: `v0.1.0^{}..origin/main`.
- No local or remote `v0.1.1` tag was found during this check.
- `CHANGELOG.md` currently records `0.1.0` only.

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
- No benchmark behavior, benchmark fixtures, committed result artifacts,
  adoption metrics, real model-server validation, or real L40S/GPU performance
  claims were added.

## Readiness Checklist

- [x] Inspect `CHANGELOG.md`.
- [x] Inspect the existing `v0.1.0` release notes and published release state.
- [x] Inspect post-`v0.1.0` commits on `origin/main`.
- [x] Inspect likely incoming PR branch state, including the local
  `review/pr-8-troubleshooting` branch and GitHub PR #8.
- [x] Confirm PR #8 is merged into `origin/main`.
- [x] Confirm no `v0.1.1` tag exists locally or on `origin`.
- [x] Keep draft notes limited to merged factual changes.
- [x] Exclude open `v0.2.0` roadmap work from the patch release notes unless it
  is separately merged before tagging.
- [ ] Confirm CI is green on the exact final commit to tag.
- [ ] Decide whether to merge a `CHANGELOG.md` entry for `0.1.1`; the current
  changelog stops at `0.1.0`.
- [ ] If this readiness note should be part of the tagged source, merge
  `release/v0.1.1-draft` before tagging.
- [ ] Ensure the tag is cut from `030a624350b5eb3f577f8ca95b5a4679d34852bb` or
  a later intended release commit, not from stale local `main` at
  `49358ef8106413b4c01b7824ac10316143199a6c`.

## Must Merge Before Tagging v0.1.1

For the narrow patch scope inspected here, the only content change that must be
present on the tagged commit is PR #8, the first-run troubleshooting guide.
`origin/main` already contains that merge commit.

Before tagging, merge one of these documentation paths:

- a small `CHANGELOG.md` `0.1.1` entry, if the changelog remains the canonical
  in-repo release log; or
- an explicit maintainer decision that the GitHub release body plus this
  maintenance draft are sufficient for `v0.1.1`.

Do not include or mention these as `v0.1.1` release contents unless they are
merged before the tag:

- `maintain/result-schema-and-fixtures` local worktree changes;
- `docs/application-scorecard`;
- open `v0.2.0` roadmap issues #2, #3, #4, #5, and #7;
- any real GPU, vLLM, L40S, adoption, usage, or downstream-user claims.

## Verification Run While Drafting

Run from the clean `release/v0.1.1-draft` worktree:

```powershell
python -m pytest -q
```

Result: `21 passed`.

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

`v0.1.1` is a documentation and maintenance patch over `v0.1.0`.

### Changed

- Added a first-run troubleshooting and result-interpretation guide for the
  existing dry-run and fake-server validation paths.
- Linked the troubleshooting guide from the README and the 10-minute smoke-run
  guide.
- Updated maintenance docs to record the published `v0.1.0` OSS readiness
  baseline and the scoped `v0.2.0` roadmap issue set.

### Validation

- `python -m pytest -q` -> 21 passed
- Dry-run benchmark check -> wrote 4 records
- Dry-run summary check -> wrote 2 rows

### Scope and limitations

- This release does not add benchmark behavior, real model-server validation,
  committed benchmark results, adoption metrics, or real L40S/GPU performance
  claims.
- Dry-run and fake-server paths remain harness validation only, not hardware or
  model performance evidence.
```
