# Real L40S/vLLM Evidence Placeholder

No real L40S/vLLM artifact is included in this repository yet.

This placeholder documents the expected location and file shape for the first
real smoke artifact. Do not add synthetic files here and do not rename synthetic
fixtures as real GPU output.

Expected future layout:

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

A future artifact should be described as a smoke artifact that validates the
collection workflow, not as a leaderboard result or broad performance claim.
