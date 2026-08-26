# l40s-llm-bench

[![CI](https://github.com/lijiaweiphilip-web/l40s-llm-bench/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lijiaweiphilip-web/l40s-llm-bench/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/lijiaweiphilip-web/l40s-llm-bench)](https://github.com/lijiaweiphilip-web/l40s-llm-bench/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Purpose

`l40s-llm-bench` is a small, reproducible harness for measuring request-level
latency and throughput of OpenAI-compatible LLM servers on local GPU or CPU
setups. It keeps the command, workload, raw JSONL, summary and environment
metadata together so a result can be checked instead of reduced to one number.

## Current status

The public repository contains a tested CPU-only and fake-server path. It does
**not** yet contain a real NVIDIA L40S/vLLM benchmark result. A hardware-backed
result will be added only with an exact model revision, GPU/software disclosure,
serving flags, repeated runs, failures and a hash-verified manifest.

## Quickstart (CPU-only, about ten minutes)

```bash
python -m pip install -r requirements-dev.txt
python scripts/bench_openai_compatible.py --dry-run
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
python -m pytest
```

The dry run is synthetic validation: it does not contact a model server,
download a model or measure GPU performance. For the complete local path see
[`docs/ten_minute_smoke_run.md`](docs/ten_minute_smoke_run.md).

## What is measured

- total request latency and, for streaming endpoints, TTFT and TPOT;
- output-token event count and derived output tokens per second;
- HTTP status, error category, concurrency, repeat and request indices;
- raw JSONL records, summary tables and a run manifest.

Prompt/output token counts are configuration targets unless a tokenizer-backed
measurement is explicitly supplied.

## What is not measured

- No real GPU, model-server or vLLM result is currently included.
- Fake-server timings validate measurement mechanics, not model quality or GPU
  performance.
- GPU utilization, power, memory bandwidth and scheduler effects are outside
  the current client scope.
- This is not a leaderboard and makes no universal claim about a model,
  framework or hardware vendor.

## Reproducibility contract

Shared measurements should include the benchmark command, versioned workload
and model configuration, raw JSONL, a summary, hardware/software disclosure,
repeat policy (including failures, timeouts and OOMs) and a run manifest with
SHA-256 hashes. Missing fields make a result a local observation rather than a
benchmark claim. See [`docs/reproducibility-evidence-bundle.md`](docs/reproducibility-evidence-bundle.md)
and [`docs/result-schema.md`](docs/result-schema.md).

## Hardware run plan

The planned vLLM/L40S smoke profile is documented in
[`docs/vllm-l40s-smoke-run.md`](docs/vllm-l40s-smoke-run.md). Before sharing
real numbers, disclose GPU model and VRAM, CPU/RAM, driver, CUDA, framework,
model identifier/revision, serving flags, prompt profile, concurrency, repeat
policy and all failed cases. Redact private hostnames, usernames, job IDs,
paths, keys and tokens.

## Project map

- `configs/` — workload, backend and hardware templates;
- `l40s_bench/` and `scripts/` — benchmark, parsing and reporting code;
- `tests/` — schema, fake-server and failure-path checks;
- `results/` — synthetic examples and public-safe result schemas;
- `docs/` — methodology, limitations, metrics and reproducibility notes.

## Citation and license

See [`LICENSE`](LICENSE) and the current [GitHub releases](https://github.com/lijiaweiphilip-web/l40s-llm-bench/releases)
for versioned source snapshots. Cite a released repository version when sharing
local measurements, and include the linked config, raw JSONL and manifest.
