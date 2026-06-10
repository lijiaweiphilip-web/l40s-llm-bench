# Smoke Feedback Starter

This page is for first-time users who want to leave structured smoke-run
feedback without guessing which details to include.

It complements the GitHub `Smoke-run feedback` issue form with a local starter
directory that can hold commands, redacted notes, and optional CPU-only
artifacts.

## Create A Starter Directory

For the common first-user path:

```bash
python scripts/init_smoke_feedback.py --feedback-id first-user-probe --smoke-path both
```

This creates:

- `results/feedback/first-user-probe/README.md`
- `results/feedback/first-user-probe/issue_body.md`
- `results/feedback/first-user-probe/commands.sh`

## Smoke-Path Options

- `dry-run`
- `sanity`
- `both`
- `manual-fake-server`

Use `both` if the tester followed `docs/first-user-smoke-test.md`.

## Why This Helps

The starter keeps first-user feedback focused on:

- repository commit
- exact commands
- environment notes
- which expected files appeared
- the first confusing step or failure
- the smallest useful redacted output excerpt

That makes issue `#12` and future smoke-feedback reports easier to triage
without inflating them into benchmark evidence.

## Boundaries

- This is for dry-run and local fake-server feedback only.
- It is not a real benchmark submission path.
- It should not contain API keys, private endpoint URLs, private hostnames,
  cluster paths, job IDs, or confidential benchmark data.

## Related Docs

- `docs/first-user-smoke-test.md`
- `docs/community-feedback.md`
- `docs/feedback-triage-policy.md`
- `.github/ISSUE_TEMPLATE/smoke_run_feedback.yml`
