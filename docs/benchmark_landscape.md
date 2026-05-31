# Benchmark Landscape and Experiment Backlog

This note tracks benchmark and serving projects worth learning from. The goal is
not to clone their scope. The goal is to extract small, testable ideas that can
improve this repository.

## Ten References

| Project / Tool | What it is useful for | Local experiment to copy first |
|---|---|---|
| vLLM benchmark serving | Online serving benchmark with TTFT, TPOT, ITL, latency, and throughput metrics | Match its TTFT/TPOT naming and add concurrency sweeps |
| SGLang benchmark tools | Serving and profiling tools across multiple layers of the stack | Separate online serving checks from lower-level microbenchmarks |
| NVIDIA GenAI-Perf | OpenAI-compatible generative AI benchmark with TTFT, inter-token latency, request throughput, and concurrency | Add structured reports and configurable use-case shapes |
| GuideLLM | Workload-driven benchmark and deployment analysis for OpenAI-compatible and vLLM-native servers | Add workload profiles and regression-friendly reports |
| Ray llmperf | API-level LLM load testing | Keep endpoint/client code provider-agnostic |
| Hugging Face TGI | Production LLM serving system with SSE streaming and continuous batching | Keep streaming parsing and batching assumptions explicit |
| TensorRT-LLM | NVIDIA-focused high-performance inference stack | Keep hardware and driver metadata close to every result |
| llama.cpp / llama-bench | Local and quantized inference benchmarking | Reserve a llama.cpp path with GGUF-specific metadata |
| EleutherAI lm-evaluation-harness | Reproducible model-quality evaluation across many tasks | Separate quality evals from serving performance metrics |
| MLPerf Inference | Standardized inference benchmarking across deployment scenarios | Treat benchmark rules and workload definitions as first-class artifacts |

## Experiment Backlog

| Priority | Experiment | Why it matters | Status |
|---|---|---|---|
| P0 | Fake-server TTFT/TPOT sanity checks | Prevents measurement bugs before GPU runs | Done |
| P0 | Client concurrency sanity checks | Validates request throughput and tail latency handling | Done |
| P1 | Prompt/output shape profiles | Mirrors real use cases such as summary, code, chat, and long context | Planned |
| P1 | Error and timeout taxonomy | Keeps failures visible instead of silently dropping them | Planned |
| P1 | JSONL schema version migration check | Keeps old raw logs readable as metrics evolve | Planned |
| P2 | vLLM smoke run on a small model | First real model-serving path | Deferred until GPU/server access |
| P2 | llama.cpp GGUF metadata path | Makes local quantized inference comparable later | Deferred |
| P2 | Workload profile report | Makes results easier to compare across runs | Planned |

## Current Rule

Every experiment must produce:

- raw JSONL records
- a Markdown or CSV summary
- a test or sanity check
- an explicit statement about what the experiment does not prove

## Sources

- vLLM serving benchmark docs: https://docs.vllm.ai/en/v0.10.2/api/vllm/benchmarks/serve.html
- SGLang benchmark and profiling docs: https://docs.sglang.io/developer_guide/benchmark_and_profiling.html
- NVIDIA GenAI-Perf docs: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_benchmark/genai-perf-README.html
- GuideLLM repository: https://github.com/vllm-project/guidellm
- Ray llmperf repository: https://github.com/ray-project/llmperf
- Hugging Face TGI docs: https://huggingface.co/docs/text-generation-inference/index
- NVIDIA TensorRT-LLM docs: https://docs.nvidia.com/tensorrt-llm/index.html
- LM Evaluation Harness docs: https://lm-evaluation-harness.readthedocs.io/
- MLPerf Inference docs: https://docs.mlcommons.org/inference/index_gh/
