# Evidence Bundle Checklist

Use this checklist before linking a result in an issue, release, blog post, or
application note.

## Required Files

- [ ] `README.md` explains the run and its scope.
- [ ] `manifest.json` includes command, commit, backend, model, counts, file
      references, hardware disclosure, and limitations.
- [ ] `config.json` or an equivalent config file is included.
- [ ] `summary.json` records request counts and key latency summaries.
- [ ] `raw-events.jsonl` contains one raw request record per line.
- [ ] `environment.json` records runtime, platform, and hardware notes.

## Required Checks

- [ ] `python scripts/validate_evidence_bundle.py <bundle-dir>` passes.
- [ ] Raw records validate against `docs/result-schema.md`.
- [ ] Request counts in `manifest.json`, `summary.json`, and raw JSONL agree.
- [ ] Synthetic bundles are clearly marked as synthetic and have
      `benchmark_claim: false`.
- [ ] Real GPU bundles include GPU model, GPU count, driver, CUDA/runtime notes,
      and telemetry or a clear explanation for missing telemetry.
- [ ] Limitations are explicit enough that a reader cannot confuse a smoke test
      with a leaderboard-style benchmark.

## Publication Boundary

- [ ] No private hostnames, usernames, cluster paths, job IDs, API keys, or
      internal dataset names are included.
- [ ] No unsupported claims are made about L40S, vLLM, llama.cpp, TensorRT-LLM,
      a model, or a hardware vendor.
- [ ] Failed, skipped, timeout, HTTP-error, and OOM cases are preserved or
      explained.
- [ ] The evidence link points to a stable commit, PR, issue, or release.
