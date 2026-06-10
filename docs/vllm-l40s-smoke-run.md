# vLLM L40S Smoke-Run Profile

This profile is intended for future real L40S/vLLM measurements. It does not
include real GPU performance results until an artifact bundle with raw events,
summary, manifest, environment notes, and GPU metrics is published.

Use this path only after the dry-run and fake-server smoke paths are working.
The goal is a small, reviewable first real-server run, not a leaderboard entry.

## Profile Files

| File | Purpose |
| --- | --- |
| `configs/workloads/vllm-l40s-smoke.yaml` | Small benchmark matrix for a vLLM OpenAI-compatible endpoint. |
| `configs/backends/vllm-openai-compatible.yaml` | Backend metadata and server notes. |
| `scripts/run_vllm_smoke_profile.sh` | Bounded helper for dry validation or a real endpoint run. |
| `examples/evidence-bundles/real-l40s-placeholder/README.md` | Placeholder explaining what a real artifact must contain. |

## Dry Validation

Run the profile without a GPU, model download, or vLLM server:

```bash
bash scripts/run_vllm_smoke_profile.sh
```

This uses `--dry-run --stream` and writes synthetic records under `results/`.
The output validates config loading, result schema compatibility, summary
generation, and the profile's request shape only. It is not real vLLM evidence.

## Real vLLM Smoke Path

Start a real vLLM OpenAI-compatible server with a small open model:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model <small-open-model-id> \
  --host 127.0.0.1 \
  --port 8000
```

Then run the smoke profile against that endpoint:

```bash
VLLM_SMOKE_DRY_RUN=0 \
VLLM_SMOKE_RUN_ID=l40s-vllm-smoke-YYYYMMDD \
bash scripts/run_vllm_smoke_profile.sh
```

The default endpoint is:

```text
http://127.0.0.1:8000/v1/chat/completions
```

Change it in `configs/workloads/vllm-l40s-smoke.yaml` only after documenting
the endpoint and redacting any private hostnames.

## Workload Shape

The profile keeps the first real run intentionally small:

| Case | Streaming | Repeats | Concurrency | Prompt target | Output target |
| --- | --- | ---: | ---: | ---: | ---: |
| `vllm_l40s_smoke_short_stream` | yes | 1 | 1 | 128 | 32 |
| `vllm_l40s_smoke_concurrent_stream` | yes | 1 | 2 | 256 | 64 |

The model label is `vllm-l40s-smoke-model`. It is a placeholder label in
`configs/models.yaml`; replace the underlying `model_id` or document the actual
served model before publishing a real artifact.

## Schema Notes

- `ttft_ms` is measured by the client as time from request start to first
  streamed token event. It depends on prompt shape, server queueing, model load
  state, and streaming behavior.
- `tpot_ms` is derived from total request latency after the first token divided
  by observed output token events minus one. Very short outputs can make this
  noisy.
- `output_token_events` counts streamed output events observed by the client. It
  is not tokenizer-verified tokenization.
- `output_tokens_per_second` is calculated from observed output events and
  request latency. It is a smoke-run clue, not a universal throughput claim.
- Error records should remain in raw JSONL. HTTP errors, timeouts, connection
  failures, and OOM-adjacent failures are part of the evidence.
- `prompt_tokens` and `output_tokens` are config targets until tokenizer-verified
  counting is added later.

## Required Context For A Real Artifact

Before sharing real L40S/vLLM numbers, publish an evidence bundle that includes:

- raw request JSONL
- summary JSON or CSV
- run manifest
- environment notes
- benchmark and backend config
- model identifier and revision
- vLLM version
- Python version
- CUDA version
- driver version
- GPU model and GPU count
- GPU metrics CSV and summary
- known limitations and failed/skipped cases

Use `docs/reproducibility-evidence-bundle.md` and `docs/gpu-metrics.md` before
opening a PR with real data.
If the raw run artifacts already exist, use
`docs/evidence_bundle_quickstart.md` and `scripts/build_evidence_bundle.py` to
package them into a reviewable bundle for issue `#17`.
