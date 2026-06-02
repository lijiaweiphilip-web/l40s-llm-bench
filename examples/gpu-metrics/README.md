# GPU Metrics Examples

This directory contains synthetic telemetry fixtures for documentation and
parser tests. The values are intentionally small and deterministic. They are not
real GPU, L40S, vLLM, or model benchmark results.

Validate the CSV parser with:

```bash
python scripts/summarize_gpu_metrics.py examples/gpu-metrics/nvidia-smi-sample.csv
```

The `.prom` file shows the shape of optional DCGM exporter samples. DCGM is not
required for CI or for first smoke-run evidence bundles.
