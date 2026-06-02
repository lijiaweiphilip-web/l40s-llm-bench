# Feedback Triage Policy

This policy explains how maintainers handle early feedback for
`l40s-llm-bench`. It is meant to keep usability feedback, synthetic harness
checks, and real benchmark evidence separate.

## What Counts As Feedback

Valid early feedback can be:

- a public comment on issue #12 after reading the README or first-user guide
- a smoke-run feedback issue using the GitHub issue template
- a small PR fixing docs, setup friction, or unclear commands
- a failure report from the dry-run or local fake-server path

It does not need to be positive. Critical notes about confusing steps are more
useful than praise.

## What Does Not Count

Do not record these as external validation:

- maintainer comments
- Codex-generated personas or invented feedback
- private praise copied without consent
- stars, forks, or reactions requested as favors
- synthetic files renamed as real user reports
- real benchmark claims without raw artifacts and metadata

## Triage Buckets

| Bucket | Use when | Maintainer action |
| --- | --- | --- |
| Documentation friction | A command, term, or expected file is unclear. | Patch docs or open a docs issue. |
| Setup failure | Install, Python version, shell, or dependency behavior blocks the path. | Reproduce if possible and add troubleshooting notes. |
| Harness failure | Dry-run, fake-server, summarizer, validator, or schema behavior fails. | Create a bug issue with exact command and output. |
| Artifact gap | A tester cannot tell which files should be attached. | Improve checklist, issue template, or evidence bundle docs. |
| Real-run request | A tester wants to run a real model/GPU path. | Route to issue #17 and require complete metadata. |
| Out of scope | Feedback asks for leaderboard claims, private endpoints, or unsupported results. | Reframe as a metadata or scope request. |

## Response Rules

- Thank the tester without inflating the feedback into adoption evidence.
- Do not say the project is validated by a tester unless the public evidence
  supports that exact claim.
- Convert actionable feedback into a follow-up issue or small PR.
- Keep secrets and private infrastructure details out of public replies.
- Preserve failed, partial, and confusing outcomes; they are useful evidence.

## Closeout Rule

A tester interaction is counted for the 80-readiness plan only when it is public
and attributable to a real external account through a comment, issue, or PR. A
maintainer should link the interaction in
`docs/maintenance/80-percent-readiness-review.md` before changing G9 status.
