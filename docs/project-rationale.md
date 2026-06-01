# Project Rationale

`l40s-llm-bench` is an early-stage benchmark scaffold for small, reproducible
LLM inference measurements on L40S and similar local GPU setups.

The project starts with the benchmark evidence chain before it starts with
headline numbers. The current focus is config parsing, dry-run records,
fake-server timing validation, JSONL compatibility checks, summaries, workload
reports, environment capture, and run manifests.

## Why This Exists

Benchmark results are easy to over-read when the surrounding context is missing.
A latency or throughput number depends on the model, framework, revision,
serving flags, prompt shape, output length, concurrency, driver stack, hardware,
and failure policy.

This repository exists to make those assumptions explicit. A result should be
traceable from a command to a config, raw JSONL records, summary tables, and a
manifest with artifact hashes.

## Who It Helps

- Local operators who want a repeatable smoke test before spending GPU time.
- Researchers who need auditable benchmark artifacts for experimental notes.
- Maintainers who want to compare harness behavior across changes.
- Readers who want enough metadata to reproduce, challenge, or contextualize a
  benchmark claim.

## What This Project Is Not

- It is not a public leaderboard.
- It is not a hosted benchmark service.
- It does not contain real GPU benchmark claims yet.
- It does not claim adoption by any community, vendor, or project.
- It does not rank serving frameworks or models.

## Design Principles

- Keep raw records close to every summary.
- Separate harness validation from model or GPU performance.
- Treat missing metadata as a blocker for public claims.
- Preserve failed, skipped, timeout, and OOM cases instead of hiding them.
- Prefer small reproducible runs before large benchmark sweeps.

## Current Stage

The repository is a scaffold. Dry-run and fake-server artifacts are useful for
checking the benchmark machinery, but they are not evidence about real LLM
serving performance.
