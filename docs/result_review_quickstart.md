# Result Review Quickstart

This page is the shortest maintainer path for handling one
`benchmark-result` issue.

Use it when you do not want to reread the full playbook first.

## 3-Minute Flow

1. Check the issue for secrets or private infrastructure details.
2. Identify the run type: dry-run, fake-server, or real-server.
3. Check whether the issue includes:
   - repository commit
   - exact commands
   - raw JSONL
   - summary CSV or Markdown
   - run manifest
   - hardware/runtime notes
   - limitations
4. If the contributor used the repository starter layout, run:

```bash
python scripts/review_result_submission.py \
  --submission-dir results/submissions/<run-id>
```

5. Generate a public-facing reply draft:

```bash
python scripts/build_result_review_comment.py \
  --submission-dir results/submissions/<run-id>
```

6. If the artifact chain is fine but the public wording still overreaches, rerun
   with an override:

```bash
python scripts/build_result_review_comment.py \
  --submission-dir results/submissions/<run-id> \
  --override-verdict "needs claim rewrite"
```

7. Before posting, compare the draft against
   `docs/result_review_examples.md`.

## What To Say First

Default order of concerns:

1. redaction
2. artifact completeness
3. artifact consistency
4. claim discipline
5. only then, limited interpretation

If steps 1 to 4 are not in good shape, do not start by debating the benchmark
number.

## Fast Verdict Guide

- `ready for review`: artifact chain is internally consistent enough for
  maintainer review
- `needs missing artifact`: raw JSONL, commands, manifest, or hardware context
  is missing
- `needs redaction`: the public issue still exposes sensitive information
- `needs claim rewrite`: artifacts are useful but the wording implies too much
- `exploratory only, not ready for benchmark discussion`: still a draft or
  local observation

## Next Links

- Full checklist: `docs/result_review_checklist.md`
- Verdict matrix: `docs/result_review_response_templates.md`
- Example maintainer replies: `docs/result_review_examples.md`
- Maintainer playbook: `docs/maintenance/maintainer-playbook.md`
