from __future__ import annotations

from typing import Any


REQUIRED_RESULT_FIELDS = {
    "schema_version",
    "timestamp_utc",
    "run_id",
    "case_id",
    "framework",
    "model",
    "prompt_tokens",
    "output_tokens",
    "batch_size",
    "repeat_index",
    "dry_run",
    "status",
    "latency_ms",
    "output_tokens_per_second",
}

OPTIONAL_RESULT_FIELDS = {
    "ttft_ms": None,
    "tpot_ms": None,
    "output_token_events": None,
    "concurrency": None,
    "request_index": None,
    "error": None,
    "error_kind": None,
    "http_status": None,
}

VALID_STATUSES = {"ok", "error", "oom", "skipped"}


def validate_result(record: dict[str, Any]) -> None:
    for key, value in OPTIONAL_RESULT_FIELDS.items():
        record.setdefault(key, value)
    if record["concurrency"] is None:
        record["concurrency"] = record.get("batch_size")
    if record["request_index"] is None:
        record["request_index"] = 0
    missing = REQUIRED_RESULT_FIELDS - set(record)
    if missing:
        raise ValueError(f"result record missing fields: {sorted(missing)}")
    if record["status"] not in VALID_STATUSES:
        raise ValueError(f"invalid status: {record['status']}")
    for key in ("prompt_tokens", "output_tokens", "batch_size", "repeat_index"):
        if int(record[key]) < 0:
            raise ValueError(f"{key} must be non-negative")
    if record["latency_ms"] is not None and float(record["latency_ms"]) < 0:
        raise ValueError("latency_ms must be non-negative or null")
    if record["ttft_ms"] is not None and float(record["ttft_ms"]) < 0:
        raise ValueError("ttft_ms must be non-negative or null")
    if record["tpot_ms"] is not None and float(record["tpot_ms"]) < 0:
        raise ValueError("tpot_ms must be non-negative or null")
    if record["output_token_events"] is not None and int(record["output_token_events"]) < 0:
        raise ValueError("output_token_events must be non-negative or null")
    if int(record["concurrency"]) <= 0:
        raise ValueError("concurrency must be positive")
    if int(record["request_index"]) < 0:
        raise ValueError("request_index must be non-negative")
    if record["http_status"] is not None and not (
        100 <= int(record["http_status"]) <= 599
    ):
        raise ValueError("http_status must be a valid HTTP status or null")
    if (
        record["output_tokens_per_second"] is not None
        and float(record["output_tokens_per_second"]) < 0
    ):
        raise ValueError("output_tokens_per_second must be non-negative or null")
