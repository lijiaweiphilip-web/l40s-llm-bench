# Result Submission Example

This page shows a small, redacted example of how a contributor could fill the
`Benchmark result` issue template without making unsupported benchmark claims.

The example uses the synthetic fake-server fixture under
`examples/results/fake-server-synthetic/`. It is documentation and review
scaffolding only. It is not a real L40S result, real model result, or
community adoption signal.

## Why This Exists

The result issue template asks for several fields. New contributors often know
what they ran, but not what a complete, safe, reviewable submission should look
like. This example shows the expected shape using non-secret synthetic data.

## Example Issue Body

### Result summary

Synthetic fake-server fixture review only. This is a tiny example submission
that demonstrates the expected artifact layout for raw JSONL, generated
summary, and run manifest files.

### Repository commit

`c4a8cfb`

### Exact commands

```bash
python scripts/summarize_results.py --input examples/results/fake-server-synthetic/raw.jsonl --output-dir examples/results/fake-server-synthetic
python scripts/build_run_manifest.py --run-id synthetic-fake-server-example --config configs/fake_server_matrix.yaml --raw examples/results/fake-server-synthetic/raw.jsonl --summary examples/results/fake-server-synthetic/summary.csv --summary-md examples/results/fake-server-synthetic/summary.md --output examples/results/fake-server-synthetic/run_manifest.json --markdown examples/results/fake-server-synthetic/run_manifest.md
python scripts/validate_result.py examples/results/fake-server-synthetic --require-synthetic-fake-server
```

### Configuration

- Benchmark config: `configs/fake_server_matrix.yaml`
- Endpoint: local fake OpenAI-compatible server example
- Repeats: `2`
- Concurrency: `1`
- Output tokens target: `8`

### Serving stack

- Server: fake OpenAI-compatible server fixture
- Version: repository-local synthetic test path
- Model: `fake-server-model`
- Streaming: represented in fixture data only
- Batch/concurrency settings: single-request illustrative example

### Hardware and runtime

- GPU: not applicable; this is not a real GPU run
- Driver/runtime: not applicable
- CPU/memory: local maintainer environment only; not relevant to interpretation
- Deployment context: synthetic fake-server fixture
- Power/thermal/shared constraints: not applicable

### Result artifacts

- Raw JSONL: `examples/results/fake-server-synthetic/raw.jsonl`
- Summary CSV: `examples/results/fake-server-synthetic/summary.csv`
- Summary Markdown: `examples/results/fake-server-synthetic/summary.md`
- Run manifest JSON: `examples/results/fake-server-synthetic/run_manifest.json`
- Run manifest Markdown: `examples/results/fake-server-synthetic/run_manifest.md`

### Limitations

- Synthetic fixture only
- Not a real L40S or model-server benchmark
- Not a hardware comparison
- Not evidence of community adoption or external validation

## Reviewer Notes

When reviewing a real result submission, check these first:

1. Are the commands concrete and reproducible?
2. Do the raw JSONL, summary, and manifest agree with each other?
3. Are secrets, private endpoints, hostnames, or confidential infrastructure
   details absent?
4. Does the submission clearly state what readers should not infer?

## Related Files

- Starter doc: `docs/result_submission_starter.md`
- Starter script: `scripts/init_result_submission.py`
- Issue template: `.github/ISSUE_TEMPLATE/benchmark_result.yml`
- Example bundle: `examples/results/fake-server-synthetic/`
- Manifest notes: `docs/run_manifest.md`
