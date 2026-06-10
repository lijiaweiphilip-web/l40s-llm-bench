# Result Review Checklist

This checklist is for maintainers and contributors reviewing a benchmark-result
issue. It keeps result review scoped to reproducibility evidence rather than
broad benchmark claims.

## Fast Path

If the submission artifacts are available locally, generate a review note first:

```bash
python scripts/review_result_submission.py \
  --raw examples/results/fake-server-synthetic/raw.jsonl \
  --summary examples/results/fake-server-synthetic/summary.csv \
  --manifest examples/results/fake-server-synthetic/run_manifest.json
```

If the contributor used the starter-kit directory layout, review the whole
submission directory directly:

```bash
python scripts/review_result_submission.py \
  --submission-dir results/submissions/<run-id>
```

If you want a maintainer-style issue reply draft after that check:

```bash
python scripts/build_result_review_comment.py \
  --submission-dir results/submissions/<run-id>
```

If the artifact chain is fine but the public wording still needs a narrower
maintainer verdict:

```bash
python scripts/build_result_review_comment.py \
  --submission-dir results/submissions/<run-id> \
  --override-verdict "needs claim rewrite"
```

The helper does not replace human review. It only checks artifact presence,
schema validity, summary consistency, and manifest consistency before the
maintainer evaluates redaction, hardware disclosure, and claim wording.
For full example replies, see `docs/result_review_examples.md`.

## Before Reviewing The Number

Check the submission shape first:

1. Is the repository commit or release identified?
2. Are the exact benchmark and summarization commands present?
3. Is the config or non-secret parameter set attached?
4. Are the raw JSONL, summary, and run manifest all present or clearly linked?
5. Are hardware/runtime notes specific enough for another contributor to
   attempt reproduction?

If those are missing, treat the report as incomplete before discussing the
number itself.

## Artifact Consistency Checks

Confirm that:

- the raw JSONL is the primary evidence artifact
- the summary matches the raw JSONL at a high level
- the run manifest points at the same artifact set being discussed
- failed, timeout, skipped, or error-heavy runs are not silently dropped

For a small worked example, see `docs/result_submission_example.md`.

## Safety And Redaction Checks

Reject or ask for edits if the submission exposes:

- API keys
- bearer tokens
- private endpoint URLs
- private hostnames
- confidential cluster paths or job IDs
- confidential infrastructure inventory

## Claim Discipline

Ask the submitter to narrow or rewrite the wording if it implies:

- leaderboard rank
- broad hardware superiority
- community adoption
- framework superiority beyond the submitted evidence
- conclusions that are not supported by the attached artifacts

## Quick Verdict Labels

Use one of these simple reviewer conclusions:

- ready for review
- needs missing artifact
- needs redaction
- needs claim rewrite
- exploratory only, not ready for benchmark discussion

## Current Boundary

This repository still does not treat dry-run or fake-server outputs as real GPU
benchmark claims, and it does not treat maintainer-controlled comments as
external validation.
