# Reproducibility Evidence Bundle

An evidence bundle is the minimum artifact package that should accompany any
shared benchmark result from this project. It is meant to let another maintainer
inspect the command, config, raw events, summary, environment notes, and known
limitations before treating a result as evidence.

The included bundle at
`examples/evidence-bundles/fake-server-smoke/` is synthetic. It validates the
measurement and packaging path only. It is not a model benchmark, GPU benchmark,
hardware comparison, or L40S/vLLM performance claim.

## Bundle Layout

```text
examples/evidence-bundles/<run-id>/
  README.md
  manifest.json
  config.json
  summary.json
  raw-events.jsonl
  environment.json
```

Real GPU bundles may add files such as `gpu-metrics.csv`,
`gpu-metrics-summary.json`, server logs, or scheduler notes. Those additions are
useful, but the core files above are required.

## Required Manifest Fields

| Field | Meaning |
| --- | --- |
| `run_id` | Stable identifier shared by all bundle files. |
| `created_at` | UTC timestamp for the bundle. |
| `project_version` | Project release, tag, or commit label used for the run. |
| `git_commit` | Repository commit used for the run. |
| `benchmark_command` | Exact public command or script used to generate the data. |
| `backend` | Serving backend label, for example `vllm` or `fake-openai-compatible`. |
| `endpoint_type` | Endpoint family, such as `openai-compatible`. |
| `model` | Model label or fixture label used in the run. |
| `workload_profile` | Workload profile or scenario name. |
| `request_count` | Number of raw request records. |
| `success_count` | Raw records with `status: "ok"`. |
| `failure_count` | Raw records with any non-`ok` status. |
| `streaming` | Whether the run used streaming measurement. |
| `ttft_ms_summary` | Summary of time-to-first-token values, if present. |
| `tpot_ms_summary` | Summary of time-per-output-token values, if present. |
| `raw_event_file` | Relative path to the raw JSONL file. |
| `summary_file` | Relative path to the summary JSON file. |
| `manifest_file` | Relative path to the manifest JSON file. |
| `environment_file` | Relative path to environment notes. |
| `hardware.synthetic` | `true` only for synthetic or fake-server fixtures. |
| `hardware.gpu_model` | GPU model for real runs, or `null` for synthetic fixtures. |
| `hardware.gpu_count` | GPU count for real runs, or `0` for synthetic fixtures. |
| `limitations` | Non-empty list of known limitations and interpretation boundaries. |

## Validation

Validate all packaged bundles with:

```bash
python scripts/validate_evidence_bundle.py examples/evidence-bundles
```

Validate one bundle with:

```bash
python scripts/validate_evidence_bundle.py examples/evidence-bundles/fake-server-smoke
```

The validator checks the required files, manifest fields, file references, raw
JSONL schema, synthetic fake-server markers, and request counts. For synthetic
bundles, every raw record must include:

```text
synthetic: true
server: "fake-server"
benchmark_claim: false
```

## Interpretation Rule

Do not publish a summary table by itself. A benchmark claim should point to the
complete bundle and should state what the run does not prove. Synthetic bundles
validate tooling. Real GPU bundles are still smoke artifacts unless they include
the full environment, GPU metrics, repeated-run policy, and limitations needed
for broader comparison.
