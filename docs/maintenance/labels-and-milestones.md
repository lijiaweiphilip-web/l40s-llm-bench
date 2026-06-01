# Labels and Milestones

This maintenance note records the labels, milestone, and roadmap issues created
after the `v0.1.0` OSS readiness release.

## Milestone

`v0.2.0`

GitHub milestone: https://github.com/lijiaweiphilip-web/l40s-llm-bench/milestone/1

Purpose:

- First real-server reproducibility hardening.
- Concrete L40S/vLLM smoke-run path.
- GPU metrics guidance.
- One scoped second-backend decision.
- Better first-run interpretation and submission examples.

Non-goals:

- Public leaderboard claims.
- Governance or release-process changes.
- CI expansion.
- Broad backend matrix implementation.

## Suggested Labels

| Label | Use |
| --- | --- |
| `backend` | Backend integration or backend selection work. |
| `benchmark` | Benchmark harness, workload, summary, manifest, or result-review work. |
| `benchmark-result` | Submitted benchmark-result issues that need reproducibility review. |
| `bug` | Broken commands, incorrect reports, schema failures, or unexpected behavior. |
| `ci` | GitHub Actions and local quality-check parity. |
| `docs` | Documentation-only or documentation-led work. |
| `documentation` | Documentation-only or documentation-led work. |
| `enhancement` | New project capability or workflow improvement. |
| `fixtures` | Sample data, tiny result bundles, or example artifacts. |
| `good first issue` | Small, bounded tasks suitable for a new contributor. |
| `gpu-metrics` | GPU telemetry, hardware/runtime notes, or metrics capture. |
| `help wanted` | Useful scoped tasks where outside implementation or testing would help. |
| `l40s` | Work specifically tied to L40S hardware interpretation or setup. |
| `needs-decision` | Maintainer decision required before implementation. |
| `question` | Clarification requests about scope, reproducibility, or interpretation. |
| `reproducibility` | Evidence bundle, manifest, schema, or repeatability work. |
| `release` | Release preparation, checklist, tag, or notes work. |
| `schema` | Raw JSONL, summary fields, or compatibility behavior. |
| `security` | Secret handling, private endpoint redaction, or vulnerability reporting. |
| `usability` | First-run experience, troubleshooting, or result interpretation. |
| `vllm` | vLLM-specific profile, server, or result interpretation work. |

## Issue Mapping

| Issue | Suggested labels | Milestone |
| --- | --- | --- |
| #2 Harden v0.2 reproducibility evidence bundle | `enhancement`, `reproducibility`, `documentation` | `v0.2.0` |
| #3 Add a real vLLM L40S smoke-run profile and schema notes | `enhancement`, `vllm`, `l40s`, `schema` | `v0.2.0` |
| #4 Write GPU metrics collection guide for nvidia-smi and DCGM | `documentation`, `gpu-metrics`, `reproducibility` | `v0.2.0` |
| #5 Define the next backend path: llama.cpp or TensorRT-LLM | `enhancement`, `backend`, `needs-decision` | `v0.2.0` |
| #6 Improve first-run troubleshooting and result interpretation | `documentation`, `good first issue`, `usability` | `v0.2.0` |
| #7 Add sample fixtures and result submission examples | `documentation`, `good first issue`, `fixtures` | `v0.2.0` |
