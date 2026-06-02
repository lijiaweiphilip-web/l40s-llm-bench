# First-User Smoke Test

This is a low-friction path for early testers who want to check whether the
repository is understandable and runnable before any GPU time is spent.

It uses only synthetic dry-run records and the local fake OpenAI-compatible
server. It is not a model benchmark and should not be reported as L40S, vLLM,
llama.cpp, or GPU performance evidence.

## Before You Start

- You need Python 3.10 or newer.
- You do not need a GPU.
- You do not need a model server.
- Do not paste API keys, private endpoint URLs, private hostnames, cluster job
  IDs, or confidential benchmark data into feedback.

## Step 1: Install

```bash
python -m pip install -r requirements-dev.txt
```

## Step 2: Run The Dry-Run Path

```bash
python scripts/bench_openai_compatible.py --dry-run
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
```

Expected artifacts:

- `results/raw/dry_run.jsonl`
- `results/tables/summary.csv`
- `results/tables/summary.md`

This step checks that the benchmark harness can write and summarize synthetic
records. It does not contact a server.

## Step 3: Run The Fake-Server Path

For the shortest controlled streaming check, run:

```bash
python scripts/run_sanity_checks.py
```

Expected artifacts:

- `results/raw/sanity_checks.jsonl`
- `results/tables/sanity_checks.md`

This starts local fake servers and checks baseline streaming, concurrent
streaming, high TTFT, slow TPOT, and HTTP error handling.

If you prefer the manual two-terminal path, use
`docs/ten_minute_smoke_run.md`.

## Step 4: Send Feedback

Please report the first-run experience, not benchmark numbers. Useful feedback
includes:

- the repository commit you tested
- your OS and Python version
- which command first failed, if any
- whether the expected artifacts appeared
- unclear wording, missing prerequisites, or confusing output
- the approximate time needed to finish the dry-run and fake-server path

You can use either:

- the GitHub issue form named `Smoke-run feedback`
- `docs/feedback-request-template.md` as a copyable prompt
- public issue #12 if you want to leave a short comment instead of opening a
  new issue

Maintainers triage public feedback with `docs/feedback-triage-policy.md`.

## Stop Here

For this first-user feedback pass, please stop after dry-run and fake-server
checks. Real model servers, GPU runs, and public performance claims are outside
this workflow.
