# l40s-llm-bench

[![CI](https://github.com/lijiaweiphilip-web/l40s-llm-bench/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lijiaweiphilip-web/l40s-llm-bench/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/lijiaweiphilip-web/l40s-llm-bench)](https://github.com/lijiaweiphilip-web/l40s-llm-bench/releases/tag/v0.1.6)
[![Python 3.10-3.12](https://img.shields.io/badge/python-3.10--3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Small, reproducible tooling for measuring OpenAI-compatible LLM inference
latency and throughput. The public release is a CPU/fake-server harness and
does not contain a real L40S/vLLM result.

## Purpose

The project keeps a measurement trace from a versioned configuration to raw
JSONL, summary tables, and a hash-checked run manifest. It is intended for
small, inspectable experiments rather than a leaderboard or hosted service.

## Current evidence status

Release `v0.1.6` contains package discovery and CPU quality-gate repairs. The
checked-in dry-run and fake-server paths validate the measurement pipeline only;
they are not hardware or model-performance evidence.

## Quickstart

```bash
python -m pip install -e ".[dev]"
python scripts/bench_openai_compatible.py --dry-run
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
python scripts/run_sanity_checks.py
python -m pytest
```

The dry run does not contact a model server, download a model, or use a GPU.
For the guided CPU path, see [`docs/ten_minute_smoke_run.md`](docs/ten_minute_smoke_run.md).

## What is measured

The harness records request-level fields including:

- total latency and streaming time to first token;
- streaming time per output token when token events are available;
- observed output-token count and derived output tokens/second;
- status, HTTP status, error category, concurrency and repeat index;
- prompt/output token targets from the versioned workload case.

The fake server checks measurement mechanics. It does not emulate a model or
GPU.

## What is not measured

- No real L40S/vLLM benchmark result is included in this release.
- Dry-run numbers are synthetic pipeline checks.
- GPU utilization, power, memory bandwidth and scheduler effects are not
  measured by the client.
- Configured token targets are not tokenizer-verified counts.
- No universal claims are made about a model, GPU or serving framework.

## Reproducibility contract

Any shared result should provide the command, benchmark/model configuration,
raw JSONL, summary, run-manifest hashes, hardware/software disclosure and a
policy for repeats, failures, timeouts and OOMs. Without those fields, treat
the output as a local observation rather than a benchmark claim.

Before a real run, disclose GPU model and VRAM, CPU/RAM, driver, CUDA,
framework, model identifier/revision, tokenizer, serving flags and the exact
workload. Do not publish private cluster paths, hostnames, usernames, job IDs,
API keys or internal data.

## CPU and fake-server validation

```bash
python scripts/fake_openai_server.py --port 18000 --ttft-ms 120 --tpot-ms 25 --tokens 8
python scripts/bench_openai_compatible.py --config configs/fake_server_matrix.yaml --output results/raw/fake_server_streaming.jsonl --stream
python scripts/summarize_results.py --input results/raw/fake_server_streaming.jsonl --output-dir results/tables
```

For reusable workload cases:

```bash
python scripts/generate_matrix.py
python scripts/bench_openai_compatible.py --config configs/generated_workload_matrix.yaml --dry-run --stream --output results/raw/workload_profiles_dry_run.jsonl
```

The result schema, JSONL compatibility checks, summaries and manifest helpers
are documented in the [`docs/`](docs/) directory.

## Real L40S reference protocol

The result-free protocol in
[`configs/workloads/l40s-vllm-reference-v1.yaml`](configs/workloads/l40s-vllm-reference-v1.yaml)
fixes short/medium prompt targets, concurrency 1/4/8, one warmup and three
measured repeats. It is executable only after a legal NVIDIA L40S session,
public model revision and serving configuration are fixed. A dry run or fake
server can never satisfy that requirement.

If a real run is completed, publish only sanitized derived artifacts with raw
records, failure counts, environment disclosure and a manifest. Report
median, IQR, minimum, maximum, `n` and failures; do not select a favorable
repeat or infer universal performance.

## Results

There is currently no public hardware-backed result. Existing example outputs
are synthetic or fake-server fixtures and are labeled accordingly.

## Project structure

```text
configs/     versioned workload and hardware templates
docs/        measurement and reproducibility notes
l40s_bench/  small parsing, schema and summary helpers
results/     synthetic examples and local outputs
scripts/     runners, validators and report builders
tests/       CPU and fake-server regression tests
```

## Limitations

This is an early-stage harness, not a complete benchmark suite. Results are
local measurements tied to their disclosed setup and should not be generalized
to other hardware, models or serving frameworks.

## Contributing

Run the CPU test suite, compile check and scoped lint before proposing a
change. Keep raw results, configuration and manifests together, and preserve
failed or skipped cases. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Maintenance

Historical contributor, community, reviewer and maintainer workflows remain in
the repository but are indexed separately in
[`docs/maintenance/INDEX.md`](docs/maintenance/INDEX.md). They are maintenance
tools, not benchmark evidence or application claims.

## Citation

See [`CITATION.cff`](CITATION.cff) and cite the release or commit used for a
reported measurement.
