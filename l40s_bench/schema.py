from __future__ import annotations

import math
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


def _finite_number(value: Any, field: str, *, allow_none: bool = True) -> float | None:
    if value is None:
        if allow_none:
            return None
        raise ValueError(f"{field} must be numeric")
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric, not boolean")
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    return numeric


def _strict_bool(value: Any, field: str) -> None:
    if type(value) is not bool:
        raise ValueError(f"{field} must be boolean")


def _integer_value(value: Any, field: str, *, allow_none: bool = True) -> int | None:
    numeric = _finite_number(value, field, allow_none=allow_none)
    if numeric is None:
        return None
    if not numeric.is_integer():
        raise ValueError(f"{field} must be an integer")
    return int(numeric)


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
    _strict_bool(record["dry_run"], "dry_run")
    for key in ("synthetic", "benchmark_claim"):
        if key in record:
            _strict_bool(record[key], key)
    if record["status"] not in VALID_STATUSES:
        raise ValueError(f"invalid status: {record['status']}")
    for key in ("prompt_tokens", "output_tokens", "batch_size", "repeat_index"):
        integer = _integer_value(record[key], key, allow_none=False)
        if integer is not None and integer < 0:
            raise ValueError(f"{key} must be non-negative")
    for key in ("latency_ms", "ttft_ms", "tpot_ms", "output_tokens_per_second"):
        numeric = _finite_number(record[key], key)
        if numeric is not None and numeric < 0:
            raise ValueError(f"{key} must be non-negative or null")
    if record["output_token_events"] is not None:
        integer = _integer_value(record["output_token_events"], "output_token_events")
        if integer is not None and integer < 0:
            raise ValueError("output_token_events must be non-negative or null")
    concurrency = _integer_value(record["concurrency"], "concurrency", allow_none=False)
    if concurrency is not None and concurrency <= 0:
        raise ValueError("concurrency must be positive")
    request_index = _integer_value(record["request_index"], "request_index", allow_none=False)
    if request_index is not None and request_index < 0:
        raise ValueError("request_index must be non-negative")
    if record["http_status"] is not None:
        http_status = _integer_value(record["http_status"], "http_status")
        if http_status is None or not (100 <= http_status <= 599):
            raise ValueError("http_status must be a valid HTTP status or null")
