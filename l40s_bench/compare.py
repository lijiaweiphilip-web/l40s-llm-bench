from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from l40s_bench.errors import ERROR_SUMMARY_COLUMNS
from l40s_bench.summary import GROUP_KEYS


LOWER_IS_BETTER = {
    "error_runs",
    *ERROR_SUMMARY_COLUMNS,
    "median_latency_ms",
    "p95_latency_ms",
    "median_ttft_ms",
    "median_tpot_ms",
}

HIGHER_IS_BETTER = {
    "ok_runs",
    "avg_output_tokens_per_second",
}

COMPARE_METRICS = tuple(sorted(LOWER_IS_BETTER | HIGHER_IS_BETTER))


def read_summary_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(key, "")) for key in GROUP_KEYS)


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    return float(text)


def delta_pct(baseline: float | None, candidate: float | None) -> float | None:
    if baseline is None or candidate is None or baseline == 0:
        return None
    return ((candidate - baseline) / baseline) * 100.0


def metric_status(
    metric: str,
    baseline: float | None,
    candidate: float | None,
    max_regression_pct: float,
) -> str:
    if baseline is None and candidate is None:
        return "unchanged-missing"
    if baseline is None:
        return "new-value"
    if candidate is None:
        return "missing-value"
    if baseline == 0 and candidate != 0:
        if metric in LOWER_IS_BETTER and candidate > baseline:
            return "regression"
        if metric in HIGHER_IS_BETTER and candidate < baseline:
            return "regression"
        return "ok"
    change = delta_pct(baseline, candidate)
    if change is None:
        return "unchanged"
    if metric in LOWER_IS_BETTER:
        return "regression" if change > max_regression_pct else "ok"
    if metric in HIGHER_IS_BETTER:
        return "regression" if -change > max_regression_pct else "ok"
    return "unknown"


def compare_summaries(
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    max_regression_pct: float,
) -> list[dict[str, Any]]:
    baseline_by_key = {row_key(row): row for row in baseline_rows}
    candidate_by_key = {row_key(row): row for row in candidate_rows}
    all_keys = sorted(set(baseline_by_key) | set(candidate_by_key))

    comparisons: list[dict[str, Any]] = []
    for key in all_keys:
        baseline = baseline_by_key.get(key)
        candidate = candidate_by_key.get(key)
        key_data = dict(zip(GROUP_KEYS, key, strict=True))
        if baseline is None:
            comparisons.append({**key_data, "metric": "*row*", "status": "new-row"})
            continue
        if candidate is None:
            comparisons.append({**key_data, "metric": "*row*", "status": "missing-row"})
            continue
        for metric in COMPARE_METRICS:
            baseline_value = parse_number(baseline.get(metric))
            candidate_value = parse_number(candidate.get(metric))
            change = delta_pct(baseline_value, candidate_value)
            comparisons.append(
                {
                    **key_data,
                    "metric": metric,
                    "baseline": baseline_value,
                    "candidate": candidate_value,
                    "delta_pct": round(change, 3) if change is not None else None,
                    "status": metric_status(
                        metric,
                        baseline_value,
                        candidate_value,
                        max_regression_pct=max_regression_pct,
                    ),
                }
            )
    return comparisons


def comparison_to_markdown(rows: list[dict[str, Any]]) -> str:
    headers = [
        "case_id",
        "framework",
        "model",
        "concurrency",
        "metric",
        "baseline",
        "candidate",
        "delta_pct",
        "status",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def has_regression(rows: list[dict[str, Any]]) -> bool:
    return any(
        row.get("status") in {"regression", "missing-row", "missing-value"}
        for row in rows
    )
