# GPU Metrics Collection

GPU metrics do not make a benchmark valid by themselves, but they help reviewers
understand whether a run had enough hardware context to interpret latency and
throughput numbers. Capture GPU telemetry next to raw JSONL, summaries,
manifests, and environment notes for any real GPU smoke run.

The sample files in `examples/gpu-metrics/` are synthetic fixtures for parser and
documentation tests. They are not real L40S measurements.

## Minimal nvidia-smi Path

For a short smoke run, start metrics collection shortly before launching the
benchmark and stop it shortly after the benchmark exits:

```bash
GPU_METRICS_SAMPLES=120 GPU_METRICS_INTERVAL_SECONDS=1 \
  bash scripts/collect_nvidia_smi_metrics.sh results/gpu/gpu-metrics.csv
```

The script records a bounded number of samples with these fields:

| Field | Why it matters |
| --- | --- |
| `timestamp` | Aligns GPU samples with benchmark JSONL timestamps. |
| `gpu_name` | Identifies the GPU model reported by the driver. |
| `gpu_uuid` | Disambiguates GPUs on multi-GPU hosts. |
| `driver_version` | Captures driver context for reproducibility. |
| `cuda_version` | Captures CUDA runtime context reported by `nvidia-smi`. |
| `power.draw` | Shows observed power draw during the run. |
| `power.limit` | Shows whether a run may be power-limited. |
| `temperature.gpu` | Helps detect thermal throttling risk. |
| `utilization.gpu` | Indicates rough GPU occupancy during sampling. |
| `utilization.memory` | Indicates memory subsystem activity. |
| `memory.used` | Helps detect whether the expected model/workload was resident. |
| `memory.total` | Records visible VRAM. |
| `clocks.sm` | Shows observed SM clock state. |
| `clocks.mem` | Shows observed memory clock state. |
| `pcie.link.gen.current` | Helps detect reduced PCIe generation. |
| `pcie.link.width.current` | Helps detect reduced PCIe link width. |

Summarize a CSV artifact with:

```bash
python scripts/summarize_gpu_metrics.py results/gpu/gpu-metrics.csv \
  --output results/gpu/gpu-metrics-summary.json
```

## Evidence Bundle Placement

For a real GPU evidence bundle, store metrics next to the benchmark artifacts:

```text
examples/evidence-bundles/l40s-vllm-smoke-YYYYMMDD/
  raw-events.jsonl
  summary.json
  manifest.json
  environment.json
  gpu-metrics.csv
  gpu-metrics-summary.json
```

The bundle manifest should mention both `gpu-metrics.csv` and
`gpu-metrics-summary.json` when they are present. If telemetry is missing, the
limitations section should say why.

## Timestamp Alignment

Use UTC timestamps when possible. When comparing telemetry with request records:

1. Record the benchmark start and end time in the run manifest or environment
   notes.
2. Keep the GPU sample interval short enough for the run duration. One second is
   usually enough for a smoke run.
3. Treat samples just before and just after the benchmark as context, not as
   per-request attribution.

## Interpretation Caveats

- Shared hosts can include background utilization from other users or services.
- Thermal limits and power limits can affect clocks without producing a clear
  benchmark error.
- MIG, partitioning, virtualization, or scheduler placement can change visible
  memory and utilization.
- Short smoke runs may not reach steady state.
- GPU utilization alone does not prove model correctness, request quality,
  tokenizer behavior, or benchmark representativeness.
- Missing failed, skipped, timeout, or OOM cases can make telemetry look cleaner
  than the actual run.
