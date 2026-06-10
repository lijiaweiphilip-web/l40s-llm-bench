# Result Submission Starter

This page is for contributors who already have one local benchmark run and want
to package it into a clean, reviewable GitHub issue.

The goal is not to make every submission look identical. The goal is to remove
guesswork around:

- directory layout
- artifact naming
- issue body shape
- minimum disclosure
- redaction and limitation notes

## Why This Helps

Many early benchmark contributions fail review for boring reasons: raw logs are
missing, manifest paths are inconsistent, commands are incomplete, or the issue
body does not say what readers should not infer. A starter kit makes the first
submission easier to review and easier to trust.

## One-Command Starter

Create a starter directory for one run:

```bash
python scripts/init_result_submission.py --run-id l40s-vllm-smoke-YYYYMMDD
```

By default this creates:

```text
results/submissions/l40s-vllm-smoke-YYYYMMDD/
  README.md
  issue_body.md
  commands.sh
  raw/
  tables/
  manifests/
```

Use `--config` if your run used a different config file:

```bash
python scripts/init_result_submission.py \
  --run-id llama-cpp-local-smoke-YYYYMMDD \
  --config configs/workloads/llama-cpp-smoke.yaml
```

## What To Put In The Starter Directory

1. Place raw request records in `raw/raw.jsonl`.
2. Generate summaries into `tables/`.
3. Generate a run manifest into `manifests/`.
4. Edit `issue_body.md` so the wording matches the real run.
5. Open the `Benchmark result` issue template and paste from `issue_body.md`.

## Notes

- The starter does not fabricate artifacts or benchmark claims.
- The generated limitation section is only a placeholder. Replace it with the
  smallest honest caveat for the actual run.
- Remove secrets, private endpoints, internal hostnames, cluster paths, and job
  IDs before posting.

## Related Docs

- Example filled submission: `docs/result_submission_example.md`
- Review expectations: `docs/result_review_checklist.md`
- Community expectations: `docs/community-feedback.md`
