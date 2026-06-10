# Smoke Feedback Response Templates

This page is the shortest maintainer path for replying to first-user dry-run
and fake-server feedback after running the smoke-feedback review helper.

## Generate A Reply Draft

If the feedback uses the starter-directory layout:

```bash
python scripts/build_smoke_feedback_comment.py --feedback-dir results/feedback/first-user-probe
```

If you also want the structured review summary:

```bash
python scripts/build_smoke_feedback_comment.py \
  --feedback-dir results/feedback/first-user-probe \
  --review-summary-output results/feedback/first-user-probe/smoke_feedback_review.md
```

## Verdicts

- `ready for triage`
- `needs missing detail`
- `needs redaction`
- `out of scope for issue #12`

## Use Them Like This

- `ready for triage`: the note is complete enough for maintainers to route into a doc patch, bug, or follow-up reply
- `needs missing detail`: ask for the missing commands, safety checks, or outcome detail
- `needs redaction`: pause the thread until sensitive content is removed
- `out of scope for issue #12`: redirect real-run or GPU-path discussion to issue `#17`

## Boundary

These drafts are for usability-feedback threads only. They do not prove
independent validation, adoption, or benchmark evidence by themselves.
