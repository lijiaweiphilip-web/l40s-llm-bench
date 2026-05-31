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
python scripts/summarize_results.py --input results/raw --output-dir results/tables
python -m pytest
```

The dry run writes synthetic records only. It does not contact a model server,
download a model, or use a GPU.

## MVP Scope

- Framework path one: vLLM through an OpenAI-compatible endpoint.
- Framework path two: llama.cpp after the vLLM path is working.
- First model target: one small open model.
- First metrics: latency, output tokens per second, error status, and
  environment notes.
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

## Current Status

Starting repository. No benchmark results are claimed yet.

## Next Steps

- Add a real vLLM server run against a small open model.
- Add streaming support for time-to-first-token measurements.
- Add GPU metric capture around real runs.
- Add llama.cpp once the vLLM path is stable.

## Limitations

This is not yet a complete benchmark suite. Early results, when added, should
be treated as local measurements rather than universal claims about any GPU,
model, or inference framework.
