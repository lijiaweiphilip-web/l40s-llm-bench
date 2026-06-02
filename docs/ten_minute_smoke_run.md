# 10-Minute Smoke Run

This guide gives a first-time reader one safe path through the benchmark
scaffold. It is a measurement-harness check, not a GPU benchmark.

Use it before spending L40S or other GPU time.

## What This Proves

- The benchmark client can write raw JSONL records.
- Streaming TTFT and TPOT measurement works against a controlled server.
- Summaries, workload reports, and run manifests can be generated from the
  same evidence bundle.

## What This Does Not Prove

- It does not measure any real model.
- It does not compare vLLM, llama.cpp, TensorRT-LLM, or other serving stacks.
- It does not justify a public benchmark claim about any GPU.

## Step 1: Install

```bash
python -m pip install -r requirements-dev.txt
```

## Step 2: Dry Run

```bash
python scripts/bench_openai_compatible.py --dry-run
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
```

Expected artifacts:

- `results/raw/dry_run.jsonl`
- `results/tables/summary.csv`
- `results/tables/summary.md`

If this step fails, stop here and work through
`docs/first_run_troubleshooting.md` before attempting a fake or real server.

## Step 3: Controlled Streaming Check

Start a fake OpenAI-compatible server in one terminal:

```bash
python scripts/fake_openai_server.py --port 18000 --ttft-ms 120 --tpot-ms 25 --tokens 8
```

In another terminal, run the benchmark:

```bash
python scripts/bench_openai_compatible.py --config configs/fake_server_matrix.yaml --models-config configs/models.yaml --output results/raw/fake_server_streaming.jsonl --stream
python scripts/summarize_results.py --input results/raw/fake_server_streaming.jsonl --output-dir results/tables
```

The fake server is configured with:

- `ttft_ms = 120`
- `tpot_ms = 25`
- `tokens = 8`

The measured summary should be close to those values. Small desktop timing
deviations are normal.

If `ttft_ms`, `tpot_ms`, or `output_token_events` do not look plausible, use
`docs/first_run_troubleshooting.md` to separate streaming-measurement issues
from serving-stack issues.

## Step 4: Scenario Suite

```bash
python scripts/run_sanity_checks.py
```

This creates a compact report covering baseline streaming, concurrent
streaming, high TTFT, slow TPOT, and HTTP error handling.

Expected artifacts:

- `results/raw/sanity_checks.jsonl`
- `results/tables/sanity_checks.md`

## Step 5: Evidence Manifest

```bash
python scripts/build_run_manifest.py --run-id fake-server-smoke-run --config configs/fake_server_matrix.yaml --raw results/raw/fake_server_streaming.jsonl --summary results/tables/summary.csv
```

Expected artifacts:

- `results/manifests/fake-server-smoke-run.json`
- `results/manifests/fake-server-smoke-run.md`

The manifest records artifact paths, file sizes, SHA256 hashes, missing
required files, and the run scope note.

## Optional Real vLLM Placeholder

Only use this after the fake-server path works. Start a vLLM OpenAI-compatible
server with a small model, then use the dedicated vLLM/L40S smoke profile in
`docs/vllm-l40s-smoke-run.md`.

```bash
python -m vllm.entrypoints.openai.api_server --model <small-open-model> --host 127.0.0.1 --port 8000
```

Then run:

```bash
VLLM_SMOKE_DRY_RUN=0 bash scripts/run_vllm_smoke_profile.sh
```

Do not publish latency or throughput numbers until the model, framework
version, hardware, driver, raw logs, config, and repeated-run policy are all
recorded.
