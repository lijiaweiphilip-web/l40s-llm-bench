# Community Entry Proof Pack

This page is the maintainer-oriented proof path for the public newcomer and
community-entry flow.

It packages the README route, GitHub issue chooser links, starter generators,
and example review helpers into one repeatable CPU-only artifact set.

## Run It

```bash
python scripts/run_community_entry_proof.py
```

Default output directory:

- `results/community-entry-proof/`

Key generated files:

- `results/community-entry-proof/community_entry_proof.md`
- `results/community-entry-proof/community_entry_proof.json`
- `results/community-entry-proof/audit/community_entry_audit.md`
- `results/community-entry-proof/review/example_smoke_feedback_review.md`
- `results/community-entry-proof/review/example_result_review.md`
- `results/community-entry-proof/smoke-feedback-starter/README.md`
- `results/community-entry-proof/submission-starter/README.md`

## What A Pass Means

A passing pack means:

- the public newcomer route is still discoverable from README and the issue chooser
- the smoke-feedback starter path still scaffolds correctly
- the benchmark-result starter path still scaffolds correctly
- the checked-in example packets are still accepted by the maintainer-side review helpers

## What A Pass Does Not Mean

- It is not independent external feedback.
- It is not a real L40S or vLLM artifact bundle.
- It does not replace issue `#12`, issue `#17`, or a real outside signal.

## Good Next Docs

After the pack passes, the best next docs are:

- `docs/ten_minute_smoke_run.md`
- `docs/contributor-self-check.md`
- `docs/smoke_feedback_starter.md`
- `docs/result_submission_starter.md`
- `docs/maintenance/current-maintainer-readiness.md`
