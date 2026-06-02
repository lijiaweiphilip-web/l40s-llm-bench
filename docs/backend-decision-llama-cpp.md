# Backend Decision: llama.cpp After vLLM

Date: 2026-06-02

Decision: choose `llama.cpp` as the next backend path to investigate after the
first vLLM/L40S smoke artifact is stable. Defer `TensorRT-LLM`; do not reject
it.

## Why llama.cpp First

`l40s-llm-bench` should not overbuild backend support before the first real
vLLM path is stable. The next backend should be easy for outside contributors
to run locally, easy to dry-document, and compatible with the existing
OpenAI-compatible benchmark client.

`llama.cpp` is the better next scoping target because:

- it has a lightweight OpenAI-compatible HTTP server path through
  `llama-server`;
- it can run small GGUF models in local environments without requiring an
  NVIDIA-optimized deployment stack;
- it is useful for contributors who want to validate the harness before spending
  L40S time;
- its first smoke-run shape can reuse the current result schema, summary, GPU
  metrics, and evidence bundle workflow.

Reference checked while drafting:

- https://www.mintlify.com/ggml-org/llama.cpp/inference/server
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

## Deferred Backend: TensorRT-LLM

`TensorRT-LLM` remains relevant for NVIDIA-optimized L40S inference, but it is
deferred because it likely needs more setup discipline before the project has
published one real vLLM smoke artifact. It should return after the project has:

- one complete real vLLM/L40S evidence bundle;
- a stable GPU metrics collection path;
- a clear policy for failed, timeout, skipped, and OOM cases;
- enough maintainer bandwidth to document a backend-specific setup path.

This is a sequencing decision, not a quality judgment against TensorRT-LLM.

## Expected Integration Shape

The first `llama.cpp` smoke path should use the existing benchmark client
against an OpenAI-compatible endpoint:

```text
http://127.0.0.1:8080/v1/chat/completions
```

The server command should stay an example until validated by a maintainer:

```bash
llama-server -m <small-model>.gguf --host 127.0.0.1 --port 8080
```

The benchmark client should not need a new result schema. A future smoke profile
can reuse:

- `ttft_ms`
- `tpot_ms`
- `output_token_events`
- `output_tokens_per_second`
- `error_kind`
- `http_status`
- evidence bundle files
- GPU metrics files when a GPU is used

## Minimum Testable Smoke Plan

Future implementation issue:

1. Add `configs/workloads/llama-cpp-smoke.yaml`.
2. Add `configs/backends/llama-cpp-openai-compatible.yaml`.
3. Add a small helper script only if it removes real friction.
4. Dry-validate the config with `--dry-run --stream`.
5. If a real server is available, run one short streaming case and one tiny
   concurrent case.
6. Publish only a complete evidence bundle, not a standalone summary table.

## Hardware Assumptions

The first `llama.cpp` path should not require L40S hardware. It can start as a
CPU or local-GPU smoke path because the purpose is backend compatibility and
artifact discipline, not a performance comparison.

If GPU offload is used later, the evidence bundle must disclose the model file,
quantization, offload flags, GPU model/count, driver/CUDA context when
applicable, and GPU metrics.

## Result-Schema Implications

- Prompt and output token fields remain config targets unless tokenizer-verified
  counting is added later.
- Streaming TTFT and TPOT interpretation should mirror the vLLM profile.
- Error records must remain in raw JSONL, especially endpoint, model-loading,
  context-length, timeout, and OOM-adjacent failures.
- A `llama.cpp` result should not be compared to vLLM unless both evidence
  bundles include comparable model, prompt, output, runtime, and hardware
  context.

## Limitations Before Implementation

- The server command may change with llama.cpp releases; re-check upstream docs
  before turning this note into an implementation guide.
- GGUF model choice and quantization can dominate results and must be disclosed.
- CPU-only and GPU-offload runs are not comparable without explicit labels.
- This decision does not add benchmark results or backend support by itself.
