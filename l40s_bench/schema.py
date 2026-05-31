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

VALID_STATUSES = {"ok", "error", "oom", "skipped"}


def validate_result(record: dict[str, Any]) -> None:
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
    if (
        record["output_tokens_per_second"] is not None
        and float(record["output_tokens_per_second"]) < 0
    ):
        raise ValueError("output_tokens_per_second must be non-negative or null")
