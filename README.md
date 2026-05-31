# l40s-llm-bench

Minimal scaffold for reproducible LLM inference benchmark experiments.

This repository is intentionally starting with the parts that can be built and
verified without GPU access: configuration, dry-run execution, raw result
schemas, summarization, environment capture, and tests. It does not claim
performance results yet.

## Purpose

- Run small LLM inference benchmark experiments against OpenAI-compatible
  servers.
- Record raw JSONL logs for each request and benchmark case.
- Summarize latency, throughput, errors, and environment metadata.
- Keep benchmark claims tied to reproducible commands and versioned configs.

## Quickstart

```bash
python -m pip install -r requirements-dev.txt
python scripts/bench_openai_compatible.py --dry-run
python scripts/summarize_results.py --input results/raw/dry_run.jsonl --output-dir results/tables
python -m pytest
```

The dry run writes synthetic records only. It does not contact a model server,
download a model, or use a GPU.

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

## Experiment Roadmap

See `docs/benchmark_landscape.md` for the current list of reference projects,
borrowed ideas, and small experiments to run before spending GPU time.

## Current Status

The scaffold now supports dry runs, streaming sanity checks, workload profiles,
summary reports, regression comparison, error taxonomy counts, and JSONL
compatibility checks. It can also create workload profile reports for review.
No real GPU benchmark results are claimed yet.

## Next Steps

- Add a real vLLM server run against a small open model.
- Add GPU metric capture around real runs.
- Add llama.cpp once the vLLM path is stable.

## Limitations

This is not yet a complete benchmark suite. Early results, when added, should
be treated as local measurements rather than universal claims about any GPU,
model, or inference framework.
