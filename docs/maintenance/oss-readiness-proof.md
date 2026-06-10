# OSS Readiness Proof

This page is the top-level maintainer-oriented proof path for the public OSS
readiness story of `l40s-llm-bench`.

It bundles the major CPU-only proof packs into one repeatable artifact set so a
teacher, reviewer, or program contact can inspect one entry point instead of
several separate workflows.

## Run It

```bash
python scripts/run_oss_readiness_proof.py
```

Default output directory:

- `results/oss-readiness-proof/`

Key generated files:

- `results/oss-readiness-proof/oss_readiness_proof.md`
- `results/oss-readiness-proof/oss_readiness_proof.json`
- `results/oss-readiness-proof/packs/reviewer-smoke-proof/reviewer_smoke_proof.md`
- `results/oss-readiness-proof/packs/community-entry-proof/community_entry_proof.md`
- `results/oss-readiness-proof/packs/feedback-triage-proof/feedback_triage_proof.md`
- `results/oss-readiness-proof/packs/submission-review-proof/submission_review_proof.md`

## What A Pass Means

A passing pack means:

- the repo can generate a reviewer-oriented reproducibility proof pack
- the repo can generate a community-entry proof pack for README routing, issue chooser links, and starter flows
- the repo can generate a maintainer-oriented feedback-triage proof pack
- the repo can generate a maintainer-oriented submission-review proof pack
- all of those flows can be packaged into one top-level public evidence bundle

## What A Pass Does Not Mean

- It is not real external feedback.
- It is not a real L40S/vLLM hardware artifact.
- It does not complete G9 or G10 by itself.

## Why This Helps

This gives `l40s-llm-bench` one obvious public evidence entrypoint for
application, teacher, or reviewer sharing. It turns several separate workflow
artifacts into a single OSS-readiness pack without changing the underlying
claims.

## Related Docs

- `docs/maintenance/reviewer-smoke-proof.md`
- `docs/maintenance/community-entry-proof.md`
- `docs/maintenance/feedback-triage-proof.md`
- `docs/maintenance/submission-review-proof.md`
- `docs/maintenance/current-maintainer-readiness.md`
