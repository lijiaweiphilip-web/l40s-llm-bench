# Workload Profiles

Workload profiles define benchmark case shapes without tying them to one
specific model server.

The first profile set is based on common LLM serving use cases:

| Profile | Purpose |
|---|---|
| `chat_short` | Short assistant-style interaction |
| `summarization_medium` | Medium input with shorter generated summary |
| `code_generation` | Moderate prompt with long generated code output |
| `long_context_qa` | Long-context prompt with concise answer |
| `burst_chat_concurrency` | Small chat requests under concurrent load |

Generate a benchmark matrix:

```bash
python scripts/generate_matrix.py
```

Run a dry-run validation over the generated matrix:

```bash
python scripts/bench_openai_compatible.py \
  --config configs/generated_workload_matrix.yaml \
  --dry-run \
  --stream \
  --output results/raw/workload_profiles_dry_run.jsonl

python scripts/summarize_results.py \
  --input results/raw/workload_profiles_dry_run.jsonl \
  --output-dir results/tables
```

This is still not a model benchmark. It validates that the benchmark harness can
represent multiple request shapes and concurrency levels consistently.
