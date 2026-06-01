# l40s-llm-bench

Minimal scaffold for reproducible LLM inference benchmark experiments on L40S
and similar single-GPU setups.

This repository is intentionally starting with the parts that can be built and
verified without GPU access: configuration, dry-run execution, raw result
schemas, summarization, environment capture, fake-server validation, and tests.
It does not claim real GPU benchmark results yet.

## Purpose

- Run small LLM inference benchmark experiments against OpenAI-compatible
  servers.
- Record raw JSONL logs for each request and benchmark case.
- Summarize latency, throughput, errors, and environment metadata.
- Keep benchmark claims tied to reproducible commands and versioned configs.

## Why This Exists

LLM benchmark posts often compress too much context into one number. Hardware,
driver versions, serving flags, prompt shapes, concurrency, streaming behavior,
and failed requests can change the story. This project exists to make small
local measurements easier to repeat and harder to overstate.

The first goal is not to crown a winner. The first goal is a public, inspectable
path from config to raw JSONL to summary table to run manifest.

See `docs/project-rationale.md` for the longer rationale and audience.

## Who It Helps

- Practitioners checking whether their local L40S inference setup is behaving
  as expected.
- Researchers who need benchmark artifacts that can be audited after the fact.
- Maintainers comparing changes to a benchmark harness before spending GPU
  time.
- Readers of benchmark results who want enough context to reproduce or question
  a claim.

This is not a leaderboard, hosted benchmark service, or adoption signal for any
model, framework, or hardware vendor.

## Reproducibility Contract

Any shared result should include:

- the command used to run the benchmark
- benchmark config and model config
- raw JSONL output
- summary CSV or Markdown
- run manifest with artifact hashes
- hardware, driver, CUDA, framework, and model revision notes
- repeated-run policy, including failed, skipped, timeout, or OOM cases

If one of those items is missing, treat the result as a local observation rather
than a benchmark claim.

## What Is Measured

The current scaffold records request-level harness data:

- total request latency
- streaming time to first token, when streaming is enabled
- streaming time per output token, when token events are observed
- output token event count for streaming responses
- output tokens per second as calculated from the observed request
- status, HTTP status, and error category
- prompt and output token targets from the benchmark case
- concurrency, repeat index, and request index

See `docs/result-schema.md` for the current raw JSONL schema.

## What Is Not Measured Yet

- No real GPU benchmark results are included in this repository.
- Dry-run numbers are synthetic and test only the pipeline.
- The fake server validates timing measurement mechanics, not model or GPU
  performance.
- GPU utilization, power draw, memory bandwidth, and scheduler effects are not
  captured by the benchmark client yet.
- Token counts are config-level targets, not tokenizer-verified counts.
- No universal claims are made about L40S, vLLM, llama.cpp, or any model.

## Hardware Disclosure

Before sharing real numbers, replace placeholders in
`configs/hardware.example.yaml` or attach equivalent notes. At minimum, disclose
GPU model, GPU count, VRAM, CPU, system RAM, driver version, CUDA version,
framework version, model identifier or revision, and any serving flags that
affect throughput or latency.

Do not publish private cluster paths, hostnames, usernames, job IDs, API keys,
or internal data.

## Quickstart

Start here if you have 10 minutes and want to check the harness before using
GPU time:

```bash
python -m pip install -r requirements-dev.txt
python scripts/bench_openai_compatible.py --dry-run
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
python -m pytest
```

The dry run writes synthetic records only. It does not contact a model server,
download a model, or use a GPU.

For the full guided path through dry-run records, fake-server streaming
validation, summary tables, and run manifests, see
`docs/ten_minute_smoke_run.md`.

## Local Measurement Check

Before spending GPU time, validate streaming TTFT/TPOT measurement against a
controlled fake OpenAI-compatible server:

```bash
python scripts/fake_openai_server.py --port 18000 --ttft-ms 120 --tpot-ms 25 --tokens 8
```

In another terminal:

```bash
python scripts/bench_openai_compatible.py --config configs/fake_server_matrix.yaml --output results/raw/fake_server_streaming.jsonl --stream
python scripts/summarize_results.py --input results/raw/fake_server_streaming.jsonl --output-dir results/tables
```

This checks the benchmark client, not model performance.

For a multi-scenario harness check:

```bash
python scripts/run_sanity_checks.py
```

The sanity suite covers baseline streaming, concurrent streaming, high TTFT,
slow TPOT, and HTTP error handling.

## Workload Profiles

Generate benchmark cases from reusable workload profiles:

```bash
python scripts/generate_matrix.py
python scripts/bench_openai_compatible.py --config configs/generated_workload_matrix.yaml --dry-run --stream --output results/raw/workload_profiles_dry_run.jsonl
```

See `docs/workload_profiles.md` for the current profile set.

Create a scenario-oriented report after summarization:

```bash
python scripts/report_workload_profiles.py --summary results/tables/summary.csv
```

See `docs/workload_profile_report.md` for details.

## Regression Comparison

Compare two summary CSV files and flag metric regressions:

```bash
python scripts/compare_summaries.py --baseline results/baselines/summary.csv --candidate results/tables/summary.csv
```

See `docs/regression_comparison.md` for details.

## Error Taxonomy

Failed requests are tagged with `error_kind` and summarized into HTTP, timeout,
connection, URL-layer, and other error counts.

See `docs/error_taxonomy.md` for details.

## JSONL Compatibility

Check raw result logs for schema versions, missing fields, and invalid records:

```bash
python scripts/check_jsonl_compat.py --input results/raw
```

See `docs/jsonl_compatibility.md` for details.

## Run Manifest

Create a compact evidence bundle for one benchmark run:

```bash
python scripts/build_run_manifest.py --run-id workload-profiles-dry-run
```

See `docs/run_manifest.md` for details.

For a single guided path that ties dry runs, fake-server validation, summaries,
and manifests together, see `docs/ten_minute_smoke_run.md`.

## MVP Scope

- Framework path one: vLLM through an OpenAI-compatible endpoint.
- Framework path two: llama.cpp after the vLLM path is working.
- First model target: one small open model.
- First metrics: latency, TTFT, TPOT, output tokens per second, error status,
  and environment notes.
- First mode: dry run before real GPU runs.

## Project Structure

```text
l40s-llm-bench/
|-- configs/
|-- docs/
|-- l40s_bench/
|-- results/
|-- scripts/
`-- tests/
```

## Result Policy

No benchmark number should be shown without:

- model name and version
- framework name and version
- hardware and driver notes
- config used for the run
- raw log path
- repeated-run policy

Also include a run manifest when possible. It ties artifact paths to file sizes
and SHA256 hashes so readers can tell which files supported a claim.

## How To Cite Or Share Results

This project is early-stage, so cite or share outputs as local measurements,
not as canonical benchmark results. A useful result note should include:

- repository commit or release reference
- benchmark command and config paths
- raw JSONL path and run manifest path
- hardware and software disclosure
- summary table
- short caveat describing what the run does not prove

Suggested wording:

> Local measurement produced with `l40s-llm-bench` on the disclosed hardware and
> software stack. Results are tied to the linked config, raw JSONL, and run
> manifest, and should not be generalized beyond that setup.

For questions, result reports, or requests for missing metadata, see
`docs/community-feedback.md`.

## Experiment Roadmap

See `docs/benchmark_landscape.md` for the current list of reference projects,
borrowed ideas, and small experiments to run before spending GPU time.

## Current Status

The scaffold now supports dry runs, streaming sanity checks, workload profiles,
summary reports, regression comparison, error taxonomy counts, and JSONL
compatibility checks. It can also create workload profile reports for review.
Run manifests tie those artifacts together, and `docs/ten_minute_smoke_run.md`
now provides a 10-minute public entrypoint. No real GPU benchmark results are
claimed yet.

## Next Steps

- Add a real vLLM server run against a small open model.
- Add GPU metric capture around real runs.
- Add llama.cpp once the vLLM path is stable.

## Limitations

This is not yet a complete benchmark suite. Early results, when added, should
be treated as local measurements rather than universal claims about any GPU,
model, or inference framework.
