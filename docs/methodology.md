# Methodology

This project separates benchmark mechanics from benchmark claims.

The dry-run path validates the control plane only: config parsing, request-case
expansion, result schema, JSONL writing, and summary generation. It does not
measure model or GPU performance.

Real benchmark runs should record:

- exact model identifier and revision when available
- inference framework and version
- hardware notes
- driver and CUDA versions
- benchmark config
- raw JSONL output
- repeated-run policy
- failed, skipped, or OOM cases

Do not compare frameworks until the serving parameters are documented well
enough for another person to reproduce the run.
