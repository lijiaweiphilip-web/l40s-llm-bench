# Smoke Feedback Review

This page is the maintainer-side review path for first-user dry-run and
fake-server feedback.

Use it after someone shares a smoke-feedback packet locally or when you copy a
public issue body into a local review directory.

## Run The Review Helper

If the feedback uses the starter-directory layout:

```bash
python scripts/review_smoke_feedback.py --feedback-dir results/feedback/first-user-probe
```

Or point directly at a copied issue note:

```bash
python scripts/review_smoke_feedback.py --issue-body path/to/issue_body.md
```

## What It Checks

- required feedback sections are present
- starter placeholders were replaced
- safety checkboxes are marked complete
- the smoke-test path stays inside the public dry-run / fake-server scope
- the commands section does not obviously drift into the real-run / GPU path
- obvious token or non-local endpoint markers are not present
- optional environment JSON parses if attached

## Review Outputs

The helper writes a short markdown summary with:

- verdict
- suggested triage bucket
- automated checks passed
- issues to fix before using the note
- manual follow-up reminders

## Verdicts

- `ready for triage`
- `needs missing detail`
- `needs redaction`
- `out of scope for issue #12`

## Triage Buckets

The helper suggests one of the buckets from
`docs/feedback-triage-policy.md`:

- Documentation friction
- Setup failure
- Harness failure
- Artifact gap
- Real-run request

Treat the suggested bucket as a maintainer aid, not ground truth.

## Important Boundary

A passing review does not prove the feedback came from a genuinely independent
external account. Maintainers still need to confirm that manually before
counting the interaction toward the G9 external-feedback gate.
