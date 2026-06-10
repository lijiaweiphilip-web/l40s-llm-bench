# Contributor Self-Check

This page is the shortest CPU-only path for a first-time contributor who wants
to confirm the repository entry flow before spending GPU time.

It is especially useful in GitHub Codespaces or any small Linux environment.

## What It Covers

The contributor self-check pack runs:

- `pytest`
- the synthetic dry-run harness
- dry-run summarization and JSONL compatibility checks
- the fake-server sanity checks
- example evidence-bundle validation
- example result-review helper output
- starter-directory generation for a future benchmark submission

Everything stays CPU-only.

## Run It

```bash
python scripts/run_contributor_self_check.py
```

Default output directory:

- `results/contributor-self-check/`

Key generated files:

- `results/contributor-self-check/contributor_self_check.md`
- `results/contributor-self-check/contributor_self_check.json`
- `results/contributor-self-check/review/example_result_review.md`
- `results/contributor-self-check/review/example_result_comment.md`
- `results/contributor-self-check/submission-starter/README.md`

## What A Pass Means

A passing pack means:

- the repo installs in a clean CPU-only environment
- the newcomer dry-run and sanity-check path is runnable
- the public submission and review docs line up with the checked-in helper
  scripts
- a future contributor has a generated starter directory to adapt

## What A Pass Does Not Mean

- It is not a real L40S or vLLM benchmark result.
- It is not independent external feedback.
- It does not replace issue `#17` or a real hardware artifact bundle.

## Good Next Docs

After the pack passes, the best next docs are:

- `docs/first-user-smoke-test.md`
- `docs/result_submission_starter.md`
- `docs/result_review_quickstart.md`
- `docs/evidence_bundle_quickstart.md`

## Codespaces Fit

This pack is a good match for GitHub Codespaces because it keeps the workflow
bounded, CPU-only, and artifact-oriented. It is a packaging and onboarding aid,
not a substitute for real hardware evidence.
