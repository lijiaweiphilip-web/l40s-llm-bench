# Real L40S/vLLM Artifact Needed

Public issue: https://github.com/lijiaweiphilip-web/l40s-llm-bench/issues/17

No real L40S/vLLM artifact exists in the repository yet. This document records
the expected artifact shape so future contributors can provide useful evidence
without overclaiming.

If you already have real raw JSONL, config, environment notes, and optional GPU
metrics files, use `scripts/build_evidence_bundle.py` to package them into a
bundle that matches this expected shape.

## Required Files

```text
examples/evidence-bundles/l40s-vllm-smoke-YYYYMMDD/
  README.md
  manifest.json
  config.json
  environment.json
  raw-events.jsonl
  summary.json
  gpu-metrics.csv
  gpu-metrics-summary.json
  limitations.md
```

## Required Metadata

- exact benchmark command
- repo commit hash
- workload config and backend config
- model identifier and revision
- vLLM version
- Python version
- CUDA version
- NVIDIA driver version
- GPU model and GPU count
- raw request JSONL
- summary JSON/CSV
- run manifest
- environment notes
- GPU metrics CSV and summary
- known limitations, including failed, skipped, timeout, and OOM cases

## Safe Wording

```text
This is a first public smoke artifact intended to validate the evidence bundle
format and collection workflow. It is not a leaderboard result or a
comprehensive performance claim.
```

## Redaction Boundary

Do not include private hostnames, usernames, cluster paths, job IDs, API keys,
private endpoints, or confidential dataset names.
