# Optional DCGM Metrics

DCGM is optional for this project. Use it only when it is already available in
the environment and does not add operational risk to a smoke run. The default
CPU-only CI path and packaged examples do not require DCGM.

## Minimal Exporter Path

If a host already exposes DCGM exporter metrics, capture a short Prometheus
snapshot around the benchmark window:

```bash
curl -fsS http://127.0.0.1:9400/metrics > results/gpu/dcgm-metrics.prom
```

Store the file next to `gpu-metrics.csv`, raw JSONL, summary, manifest, and
environment notes. If the endpoint includes private hostnames or labels, redact
those labels before publishing.

## Useful Fields

The exact field set depends on the DCGM exporter configuration. For this
project, the most useful optional fields are:

| Metric | Use |
| --- | --- |
| `DCGM_FI_DEV_GPU_UTIL` | GPU utilization context. |
| `DCGM_FI_DEV_MEM_COPY_UTIL` | Memory copy utilization context. |
| `DCGM_FI_DEV_FB_USED` | Framebuffer memory used. |
| `DCGM_FI_DEV_FB_FREE` | Framebuffer memory free. |
| `DCGM_FI_DEV_POWER_USAGE` | Power draw context. |
| `DCGM_FI_DEV_POWER_LIMIT` | Power limit context. |
| `DCGM_FI_DEV_GPU_TEMP` | Temperature context. |
| `DCGM_FI_DEV_SM_CLOCK` | SM clock context. |
| `DCGM_FI_DEV_MEM_CLOCK` | Memory clock context. |
| `DCGM_FI_DEV_PCIE_REPLAY_COUNTER` | PCIe reliability clue, when available. |

## Caveats

- DCGM labels may expose hostnames, job labels, pod names, namespaces, or other
  private infrastructure details.
- Exporter sampling may not align exactly with benchmark request timestamps.
- DCGM can help explain a run, but it does not validate benchmark quality by
  itself.
- Keep DCGM optional so contributors without cluster-level tooling can still
  provide useful `nvidia-smi` evidence.
