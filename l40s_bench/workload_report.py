from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from l40s_bench.errors import ERROR_SUMMARY_COLUMNS


RESULT_HEADERS = [
    "Profile",
    "Framework",
    "Model",
    "Runs",
    "OK",
    "Errors",
    "Median latency ms",
    "P95 latency ms",
    "Median TTFT ms",
    "Median TPOT ms",
    "Output tok/s",
    "Error breakdown",
]


def read_summary_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    return "" if text == "None" else text


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines) + "\n"


def error_breakdown(row: dict[str, Any]) -> str:
    parts = []
    for column in ERROR_SUMMARY_COLUMNS:
        value = row.get(column)
        if value in (None, "", "0", 0):
            continue
        label = column.removesuffix("_runs")
        parts.append(f"{label}={value}")
    return ", ".join(parts) if parts else "none"


def profile_rows(profiles: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            profile["name"],
            profile.get("description", ""),
            profile["prompt_tokens"],
            profile["output_tokens"],
            profile["batch_size"],
            profile["concurrency"],
        ]
        for profile in profiles
    ]


def result_rows(
    profiles: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> tuple[list[list[Any]], list[str], list[str]]:
    profile_order = {profile["name"]: index for index, profile in enumerate(profiles)}
    profile_names = set(profile_order)
    rows_by_profile: dict[str, list[dict[str, Any]]] = {
        profile["name"]: [] for profile in profiles
    }
    unmatched: list[str] = []
    for row in summary_rows:
        case_id = str(row.get("case_id", ""))
        if case_id in rows_by_profile:
            rows_by_profile[case_id].append(row)
        else:
            unmatched.append(case_id)

    result_table_rows = []
    for profile in profiles:
        for row in sorted(
            rows_by_profile[profile["name"]],
            key=lambda item: (str(item.get("framework", "")), str(item.get("model", ""))),
        ):
            result_table_rows.append(
                [
                    row.get("case_id"),
                    row.get("framework"),
                    row.get("model"),
                    row.get("runs"),
                    row.get("ok_runs"),
                    row.get("error_runs"),
                    row.get("median_latency_ms"),
                    row.get("p95_latency_ms"),
                    row.get("median_ttft_ms"),
                    row.get("median_tpot_ms"),
                    row.get("avg_output_tokens_per_second"),
                    error_breakdown(row),
                ]
            )

    covered_profiles = {
        str(row.get("case_id", ""))
        for row in summary_rows
        if str(row.get("case_id", "")) in profile_names
    }
    missing_profiles = [
        profile["name"] for profile in profiles if profile["name"] not in covered_profiles
    ]
    return result_table_rows, missing_profiles, sorted(set(unmatched))


def workload_report_to_markdown(
    profiles_config: dict[str, Any],
    summary_rows: list[dict[str, Any]],
) -> str:
    profiles = profiles_config["profiles"]
    results, missing_profiles, unmatched = result_rows(profiles, summary_rows)
    coverage = len(profiles) - len(missing_profiles)
    lines = [
        "# Workload Profile Report",
        "",
        f"Profiles with summary rows: {coverage}/{len(profiles)}",
        "",
        "## Profile Shapes",
        "",
        markdown_table(
            [
                "Profile",
                "Description",
                "Prompt tokens",
                "Output tokens",
                "Batch size",
                "Concurrency",
            ],
            profile_rows(profiles),
        ),
        "## Summary Results",
        "",
        markdown_table(RESULT_HEADERS, results) if results else "_No summary rows._\n",
    ]
    if missing_profiles:
        lines.extend(["## Missing Profiles", ""])
        lines.extend(f"- `{profile}`" for profile in missing_profiles)
        lines.append("")
    if unmatched:
        lines.extend(["## Unmatched Summary Rows", ""])
        lines.extend(f"- `{case_id}`" for case_id in unmatched)
        lines.append("")
    lines.extend(
        [
            "## Scope Note",
            "",
            "This report compares workload shapes and local run summaries. It does not "
            "prove that one model, server, or GPU is generally better than another.",
            "",
        ]
    )
    return "\n".join(lines)
