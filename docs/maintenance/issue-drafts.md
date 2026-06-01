# Roadmap Issue Source

These issue drafts were used to create GitHub issues #2 through #7 after the
`v0.1.0` OSS readiness release. They are intentionally scoped to
reproducibility, documentation, and small implementation paths for the next
project milestone. They do not claim external user demand or validated
benchmark results.

## 1. Harden v0.2 reproducibility evidence bundle

Labels: `enhancement`, `reproducibility`, `documentation`

Milestone: `v0.2.0`

Scope:

- Define the minimum evidence bundle expected for a real benchmark run:
  raw JSONL, generated summary, benchmark config, model/server config notes,
  hardware/runtime notes, and run manifest.
- Add a maintainer checklist for confirming that the bundle is internally
  consistent before any result is discussed publicly.
- Clarify which artifacts are required, recommended, or optional for v0.2.

Why it matters:

The current scaffold already writes raw records, summaries, and manifests, but
the v0.2 path needs a clearer reproducibility contract before real L40S results
are collected or reviewed. A small checklist reduces ambiguous result reports
and keeps the project from drifting into unsupported benchmark claims.

Acceptance criteria:

- A v0.2 reproducibility checklist exists in project documentation.
- The checklist names required artifacts and the reason each one is needed.
- The checklist includes a redaction reminder for secrets, private endpoints,
  and confidential infrastructure details.
- The checklist distinguishes dry-run, fake-server, and real-server evidence.
- Maintainers can use the checklist to decide whether a submitted result is
  ready for review, needs more information, or should be treated as exploratory.

Maintainer notes:

- Keep this issue documentation-first unless a code change is clearly needed.
- Align language with the existing result schema, run manifest, and 10-minute
  smoke-run docs.
- Avoid adding a leaderboard or performance-claim workflow in this issue.

## 2. Add a real vLLM L40S smoke-run profile and schema notes

Labels: `enhancement`, `vllm`, `l40s`, `schema`

Milestone: `v0.2.0`

Scope:

- Draft a minimal real vLLM smoke-run profile for a single L40S machine using
  an OpenAI-compatible endpoint.
- Document the expected config fields and result-schema interpretation for a
  real vLLM run.
- Identify which values are measured by the benchmark harness and which values
  must be supplied as run metadata.

Why it matters:

The current smoke-run guide has a placeholder for real vLLM usage after the
fake-server path works. v0.2 should turn that placeholder into a concrete,
reviewable profile so maintainers can test the first real L40S path without
presenting it as a validated public benchmark.

Acceptance criteria:

- A real vLLM smoke-run profile is documented with endpoint, model label,
  streaming mode, concurrency/repeat shape, and output path expectations.
- Schema notes explain how to interpret `ttft_ms`, `tpot_ms`,
  `output_token_events`, `output_tokens_per_second`, and error records for
  real vLLM output.
- The profile includes a warning that prompt and output token fields are config
  targets unless tokenizer-verified counting is added later.
- The smoke-run path records enough server, model, driver, and hardware context
  for another maintainer to attempt reproduction.
- The issue does not require publishing actual L40S numbers.

Maintainer notes:

- Prefer a small model and short run shape for the first real smoke-run.
- Do not block this issue on broader multi-model or multi-GPU benchmarking.
- If a config file is added later, keep example values clearly marked as
  placeholders until a maintainer validates them.

## 3. Write GPU metrics collection guide for nvidia-smi and DCGM

Labels: `documentation`, `gpu-metrics`, `reproducibility`

Milestone: `v0.2.0`

Scope:

- Document a lightweight GPU metrics collection path using `nvidia-smi`.
- Document an optional DCGM-based path for environments where DCGM is already
  available.
- Explain how to align GPU metrics timestamps with benchmark JSONL records and
  run manifests.
- State which metrics should be treated as required, recommended, or
  environment-dependent.

Why it matters:

Latency and throughput numbers are hard to interpret without basic GPU context.
For L40S work, maintainers need a repeatable way to capture utilization,
memory, power, clocks, temperature, driver/runtime versions, and multi-tenant
or throttling clues alongside benchmark artifacts.

Acceptance criteria:

- The guide provides one minimal `nvidia-smi` command path suitable for a smoke
  run.
- The guide provides one optional DCGM path or points to the expected DCGM
  fields without making DCGM mandatory.
- The guide explains how to store metrics artifacts next to raw JSONL,
  summaries, and manifests.
- The guide includes interpretation caveats for shared hosts, thermal limits,
  power limits, MIG or partitioning, and background processes.
- The guide avoids claiming that GPU metrics alone validate benchmark quality.

Maintainer notes:

- Keep commands generic and redaction-safe.
- Avoid environment-specific cloud provider assumptions unless marked as
  examples.
- This issue can be completed as documentation only.

## 4. Define the next backend path: llama.cpp or TensorRT-LLM

Labels: `enhancement`, `backend`, `needs-decision`

Milestone: `v0.2.0`

Scope:

- Choose one second backend path to investigate after vLLM: `llama.cpp` or
  `TensorRT-LLM`.
- Document the smallest viable OpenAI-compatible or adapter-based smoke-run
  path for the chosen backend.
- Record the tradeoffs that led to the choice and defer the non-chosen backend
  unless maintainers decide otherwise.

Why it matters:

The project should not overbuild backend support before the first real vLLM
path is stable. A single, explicit backend decision keeps v0.2 focused while
still leaving a roadmap for broader serving-stack comparison.

Acceptance criteria:

- A short maintainer decision note chooses either `llama.cpp` or
  `TensorRT-LLM` as the next backend path.
- The note explains expected integration shape, minimum testable server path,
  hardware assumptions, and result-schema implications.
- The chosen path includes a minimal smoke-run plan rather than a full
  benchmark matrix.
- The non-chosen backend is documented as deferred, not rejected.
- Any backend-specific limitations are stated before implementation begins.

Maintainer notes:

- `llama.cpp` may be simpler for local reproducibility and broad contributor
  access.
- `TensorRT-LLM` may be more relevant for NVIDIA-optimized L40S inference but
  could require more setup discipline.
- Treat this as a scoping issue first; implementation can follow in a separate
  issue if needed.

## 5. Improve first-run troubleshooting and result interpretation

Labels: `documentation`, `good first issue`, `usability`

Milestone: `v0.2.0`

Scope:

- Add a troubleshooting section for first-time dry-run, fake-server, and real
  OpenAI-compatible server runs.
- Explain common result interpretation questions without overstating what the
  harness proves.
- Cover common setup errors, endpoint mistakes, streaming confusion, empty or
  error-heavy JSONL files, and mismatched summary expectations.

Why it matters:

The current first-run path is deliberately cautious. New maintainers still need
help distinguishing harness problems, server connectivity problems, schema
issues, and real benchmark limitations. Better troubleshooting will reduce
repeated support work and make result review cleaner.

Acceptance criteria:

- Troubleshooting guidance covers install, config, endpoint, streaming,
  summarization, manifest, and compatibility-check failures.
- Result interpretation guidance explains `status`, `error_kind`,
  `http_status`, `ttft_ms`, `tpot_ms`, and throughput fields in practical
  first-run terms.
- The guidance explicitly separates dry-run/fake-server validation from real
  model measurement.
- The guidance includes a small "what to attach when asking for help" section.
- No external user reports or invented failure cases are presented as real.

Maintainer notes:

- Reuse the existing error taxonomy and result-schema language where possible.
- This is a good candidate for a contributor who can run only the dry-run and
  fake-server paths.

## 6. Add sample fixtures and result submission examples

Labels: `documentation`, `good first issue`, `fixtures`

Milestone: `v0.2.0`

Scope:

- Add a small redacted example of a complete result submission using existing
  issue-template fields.
- Add or document a tiny sample fixture bundle that demonstrates raw JSONL,
  summary output, and run manifest relationships.
- Make clear that examples are illustrative scaffold outputs, not validated
  public benchmark results.

Why it matters:

The benchmark result template asks for several artifacts, but contributors and
maintainers benefit from seeing the expected shape of a complete, non-secret
submission. A tiny fixture can also help reviewers spot missing fields or
misaligned artifacts quickly.

Acceptance criteria:

- A result submission example shows commands, config notes, serving-stack
  metadata, hardware/runtime notes, artifact list, and limitations.
- Any sample fixture is small, deterministic, and clearly marked as dry-run or
  fake-server output.
- The example demonstrates how to avoid leaking API keys, private endpoints,
  hostnames, and confidential infrastructure details.
- The example links the raw JSONL, summary, and manifest concepts together.
- The example does not claim external adoption, external users, or validated
  L40S performance.

Maintainer notes:

- Prefer fake-server or dry-run data for fixtures unless maintainers explicitly
  approve publishing real benchmark artifacts.
- If this touches issue templates later, keep it as a separate PR from the
  documentation example.
