# Result Review Response Templates

This page is for maintainers who want a quick, public-facing response after
reviewing a benchmark-result issue.

The repository now supports two layers:

- `scripts/review_result_submission.py` for artifact consistency checks
- `scripts/build_result_review_comment.py` for a maintainer-style reply draft

## Fastest Path

If the contributor used the starter-kit directory layout:

```bash
python scripts/build_result_review_comment.py \
  --submission-dir results/submissions/<run-id>
```

If you need to keep the automated artifact checks but force a different public
verdict:

```bash
python scripts/build_result_review_comment.py \
  --submission-dir results/submissions/<run-id> \
  --override-verdict "needs claim rewrite"
```

## Verdict Matrix

### `ready for review`

Use when the artifact chain is internally consistent enough for maintainer
review, even if interpretation still needs caution.

### `needs missing artifact`

Use when raw JSONL, summary output, manifest, commands, config details, or
hardware notes are missing.

### `needs redaction`

Use when the issue text or attached artifacts expose secrets, private
endpoints, hostnames, internal paths, job IDs, or other confidential
infrastructure details.

### `needs claim rewrite`

Use when the artifacts are useful but the public wording implies too much:
leaderboard rank, broad hardware superiority, adoption, or unsupported
framework conclusions.

### `exploratory only, not ready for benchmark discussion`

Use when the submission is still a draft or local observation because the
artifact set does not yet support even narrow benchmark discussion.

## Notes

- These templates help with consistency; they do not replace maintainer
  judgment.
- `needs redaction` and `needs claim rewrite` are intentionally supported as
  manual override paths because they depend on public wording and disclosure,
  not only on artifact consistency.
- Keep every public reply tied to the exact hardware, software stack, and
  stated limitations of the submission.
