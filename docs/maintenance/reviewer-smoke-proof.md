# Reviewer Smoke Proof

Date: 2026-06-04

Repository: https://github.com/lijiaweiphilip-web/l40s-llm-bench

This document describes the reviewer-oriented CPU-only proof pack for
`l40s-llm-bench`.

## Why This Exists

The repository already has CI, tests, dry-run validation, example evidence
bundles, GPU telemetry fixtures, and a dry-validatable vLLM/L40S profile.
Before this proof pack, those signals were spread across workflow logs, release
notes, and maintenance docs. The reviewer smoke proof pack ties them into one
repeatable public artifact.

## How To Run

Local:

```bash
python scripts/run_reviewer_smoke_pack.py
```

GitHub Actions:

- Workflow file: `.github/workflows/reviewer-smoke-proof.yml`
- Artifact directory: `results/reviewer-smoke-proof/`

## What The Pack Covers

- environment capture
- `python -m pytest -q`
- CPU-only dry run
- dry-run summary generation
- JSONL compatibility check
- run manifest creation
- packaged evidence bundle validation
- sample GPU metrics summarization
- vLLM/L40S smoke-profile dry run and record validation
- fake-server sanity checks

The output pack includes logs, raw JSONL, summary tables, a run manifest, a GPU
sample summary, and a top-level reviewer report in both JSON and Markdown.

## What This Proves

- A clean CPU-only environment can install the repository and run the public
  validation path end to end.
- The reproducibility contract is inspectable without GPU access.
- The benchmark harness, evidence validator, telemetry parser, and vLLM smoke
  profile remain wired together after changes to `main`.

## What This Does Not Prove

- It does not add real L40S, vLLM, model-server, or GPU benchmark evidence.
- It does not count as independent external feedback or adoption.
- It does not replace issue #17 or a real hardware artifact bundle.

## Reviewer Path

1. Open the latest release and README.
2. Open the reviewer smoke proof workflow or download its artifact bundle.
3. Check `reviewer_smoke_proof.md` for pass/fail status and artifact paths.
4. Inspect the attached raw JSONL, summary files, manifest, and logs if a claim
   needs verification.

## Related Public Links

- Latest release: https://github.com/lijiaweiphilip-web/l40s-llm-bench/releases/tag/v0.1.2
- Early tester issue: https://github.com/lijiaweiphilip-web/l40s-llm-bench/issues/12
- Hardware-needed issue: https://github.com/lijiaweiphilip-web/l40s-llm-bench/issues/17

## Positioning

This proof pack is an honest strengthening step for maintainer readiness. It
improves public reproducibility evidence, but it does not close the remaining
world-contact gaps:

- G9 independent external feedback
- G10 one real L40S/vLLM artifact bundle
