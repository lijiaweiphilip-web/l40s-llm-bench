# Result Schema

Raw benchmark records are written as JSONL: one JSON object per request. The
current schema version is `0.1`.

## Record Fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Raw record schema version. |
| `timestamp_utc` | UTC timestamp when the record was created. |
| `run_id` | Identifier shared by records from one benchmark run. |
| `case_id` | Benchmark case identifier from the config. |
| `framework` | Serving framework label from the config. |
| `model` | Model label from the config. |
| `endpoint` | OpenAI-compatible endpoint used by the case, when applicable. |
| `prompt_tokens` | Configured prompt token target. |
| `output_tokens` | Configured output token target. |
| `batch_size` | Batch size field from the benchmark case. |
| `concurrency` | Number of concurrent requests issued for the case. |
| `repeat_index` | Repeat number within a case. |
| `request_index` | Request number within a concurrent repeat. |
| `dry_run` | Whether the record came from synthetic dry-run mode. |
| `status` | `ok` or `error`. |
| `latency_ms` | Total observed request latency in milliseconds. |
| `ttft_ms` | Streaming time to first token in milliseconds, or `null`. |
| `tpot_ms` | Streaming time per output token in milliseconds, or `null`. |
| `output_token_events` | Count of streamed output token events, or `null`. |
| `output_tokens_per_second` | Calculated output-token throughput for the request, or `null`. |
| `error` | Error message for failed requests, or `null`. |
| `error_kind` | Normalized error category for failed requests, or `null`. |
| `http_status` | HTTP status code when available, or `null`. |

## Interpretation Notes

- `prompt_tokens` and `output_tokens` are config targets, not tokenizer-verified
  counts.
- `ttft_ms`, `tpot_ms`, and `output_token_events` are meaningful only when
  streaming is enabled and the endpoint emits token events.
- Dry-run records are synthetic and exist only to validate the pipeline.
- Fake-server records validate timing mechanics against controlled delays; they
  are not model or GPU measurements.
- Error records should stay in the raw JSONL and summary path so failure rates
  are visible.

## Synthetic Example Artifacts

Packaged example artifacts live under `examples/results/` and are fixtures for
schema, documentation, and validator checks. They are not benchmark claims.

Every packaged example record must include these extra markers:

| Field | Required value | Meaning |
| --- | --- | --- |
| `synthetic` | `true` | The record is a synthetic fixture. |
| `server` | `fake-server` | The source is the local fake OpenAI-compatible server. |
| `benchmark_claim` | `false` | The record must not be presented as a real model, GPU, or hardware result. |

Validate packaged examples with:

```bash
python scripts/validate_result.py examples/results --require-synthetic-fake-server
```

The included `examples/results/fake-server-synthetic/raw.jsonl` artifact covers
one successful streaming record and one HTTP-error record from the fake-server
path. The values are intentionally small synthetic fixtures for tooling tests.

## Compatibility

Use the JSONL compatibility check before comparing or publishing records:

```bash
python scripts/check_jsonl_compat.py --input results/raw --output results/tables/jsonl_compat.md
```

The compatibility report summarizes schema versions, invalid records, and
missing optional fields.

## Sharing Checklist

Do not share a summary table by itself. Pair it with the raw JSONL, benchmark
config, hardware notes, and run manifest so readers can inspect the evidence
behind the numbers.
