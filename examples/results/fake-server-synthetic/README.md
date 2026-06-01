# Synthetic Fake-Server Result Fixture

This directory contains a tiny JSONL artifact for schema and tooling tests.
Every record is synthetic and produced as a fake-server fixture. It is not a
model benchmark, GPU benchmark, hardware comparison, or performance claim.

Markers used by `scripts/validate_result.py --require-synthetic-fake-server`:

- `synthetic: true`
- `server: "fake-server"`
- `benchmark_claim: false`
