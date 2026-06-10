# Synthetic Fake-Server Result Fixture

This directory contains a tiny synthetic fake-server submission example. It is
small enough for schema, tooling, and documentation tests, while still showing
the expected relationship between:

- raw JSONL
- generated summary output
- run manifest

Every record is synthetic and produced as a fake-server fixture. It is not a
model benchmark, GPU benchmark, hardware comparison, or performance claim.

Markers used by `scripts/validate_result.py --require-synthetic-fake-server`:

- `synthetic: true`
- `server: "fake-server"`
- `benchmark_claim: false`

Included example artifacts:

- `raw.jsonl`
- `summary.csv`
- `summary.md`
- `run_manifest.json`
- `run_manifest.md`

For a copy-and-paste issue example using this bundle, see
`docs/result_submission_example.md`.
