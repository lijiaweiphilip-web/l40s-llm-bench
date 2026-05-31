from __future__ import annotations

from collections import defaultdict
from statistics import mean, median
from typing import Any

from l40s_bench.errors import (
    ERROR_KIND_TO_SUMMARY_COLUMN,
    ERROR_SUMMARY_COLUMNS,
    OTHER_ERROR_SUMMARY_COLUMN,
)


GROUP_KEYS = (
    "case_id",
    "framework",
    "model",
    "prompt_tokens",
    "output_tokens",
    "batch_size",
    "concurrency",
)


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[tuple(record[key] for key in GROUP_KEYS)].append(record)

    rows: list[dict[str, Any]] = []
    for group, group_records in sorted(groups.items()):
        error_kind_counts = {kind: 0 for kind in ERROR_KIND_TO_SUMMARY_COLUMN}
        other_error_runs = 0
        for item in group_records:
            if item.get("status") == "ok":
                continue
            error_kind = item.get("error_kind")
            if error_kind in error_kind_counts:
                error_kind_counts[error_kind] += 1
            else:
                other_error_runs += 1
        latencies = [
            float(item["latency_ms"])
            for item in group_records
            if item.get("latency_ms") is not None and item.get("status") == "ok"
        ]
        ttfts = [
            float(item["ttft_ms"])
            for item in group_records
            if item.get("ttft_ms") is not None and item.get("status") == "ok"
        ]
        tpots = [
            float(item["tpot_ms"])
            for item in group_records
            if item.get("tpot_ms") is not None and item.get("status") == "ok"
        ]
        token_rates = [
            float(item["output_tokens_per_second"])
            for item in group_records
            if item.get("output_tokens_per_second") is not None
            and item.get("status") == "ok"
        ]
        row = dict(zip(GROUP_KEYS, group, strict=True))
        row.update(
            {
                "runs": len(group_records),
                "ok_runs": sum(1 for item in group_records if item.get("status") == "ok"),
                "error_runs": sum(
                    1 for item in group_records if item.get("status") != "ok"
                ),
                "median_latency_ms": round(median(latencies), 3) if latencies else None,
                "p95_latency_ms": (
                    round(percentile(latencies, 0.95), 3) if latencies else None
                ),
                "median_ttft_ms": round(median(ttfts), 3) if ttfts else None,
                "median_tpot_ms": round(median(tpots), 3) if tpots else None,
                "avg_output_tokens_per_second": (
                    round(mean(token_rates), 3) if token_rates else None
                ),
            }
        )
        row.update(
            {
                column: error_kind_counts[kind]
                for kind, column in ERROR_KIND_TO_SUMMARY_COLUMN.items()
            }
        )
        row[OTHER_ERROR_SUMMARY_COLUMN] = other_error_runs
        rows.append(row)
    return rows


def rows_to_markdown(rows: list[dict[str, Any]]) -> str:
    headers = [
        "case_id",
        "framework",
        "model",
        "prompt_tokens",
        "output_tokens",
        "batch_size",
        "concurrency",
        "runs",
        "ok_runs",
        "error_runs",
        "median_latency_ms",
        "p95_latency_ms",
        "median_ttft_ms",
        "median_tpot_ms",
        "avg_output_tokens_per_second",
        *ERROR_SUMMARY_COLUMNS,
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines) + "\n"
