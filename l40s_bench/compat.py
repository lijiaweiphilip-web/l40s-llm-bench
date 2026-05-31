from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from l40s_bench.io import read_jsonl
from l40s_bench.schema import OPTIONAL_RESULT_FIELDS, REQUIRED_RESULT_FIELDS, validate_result


def collect_jsonl_inputs(input_path: str | Path) -> list[Path]:
    path = Path(input_path)
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.glob("*.jsonl"))
    raise FileNotFoundError(path)


def check_records(
    records: list[dict[str, Any]],
    source: str = "memory",
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "source": source,
        "records": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "schema_versions": Counter(),
        "missing_required_fields": Counter(),
        "missing_optional_fields": Counter(),
        "invalid_messages": [],
    }
    for index, original in enumerate(records, start=1):
        report["records"] += 1
        original_keys = set(original)
        report["schema_versions"][str(original.get("schema_version", "<missing>"))] += 1
        for field in REQUIRED_RESULT_FIELDS - original_keys:
            report["missing_required_fields"][field] += 1
        for field in OPTIONAL_RESULT_FIELDS:
            if field not in original_keys:
                report["missing_optional_fields"][field] += 1
        record = dict(original)
        try:
            validate_result(record)
        except (TypeError, ValueError, KeyError) as exc:
            report["invalid_records"] += 1
            report["invalid_messages"].append(
                {"source": source, "record_index": index, "error": str(exc)}
            )
        else:
            report["valid_records"] += 1
    return report


def merge_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    merged = check_records([])
    merged["source"] = "aggregate"
    for report in reports:
        merged["records"] += report["records"]
        merged["valid_records"] += report["valid_records"]
        merged["invalid_records"] += report["invalid_records"]
        merged["schema_versions"].update(report["schema_versions"])
        merged["missing_required_fields"].update(report["missing_required_fields"])
        merged["missing_optional_fields"].update(report["missing_optional_fields"])
        merged["invalid_messages"].extend(report["invalid_messages"])
    return merged


def check_jsonl_inputs(input_path: str | Path) -> dict[str, Any]:
    reports = []
    for path in collect_jsonl_inputs(input_path):
        reports.append(check_records(read_jsonl(path), source=str(path)))
    return merge_reports(reports)


def counter_table(counter: Counter[str]) -> str:
    if not counter:
        return "_None._\n"
    lines = ["| Field | Count |", "|---|---|"]
    for key, count in sorted(counter.items()):
        lines.append(f"| {key} | {count} |")
    return "\n".join(lines) + "\n"


def report_to_markdown(report: dict[str, Any]) -> str:
    status = "PASS" if report["invalid_records"] == 0 else "FAIL"
    lines = [
        "# JSONL Compatibility Check",
        "",
        f"Status: {status}",
        "",
        f"Records: {report['records']}",
        f"Valid records: {report['valid_records']}",
        f"Invalid records: {report['invalid_records']}",
        "",
        "## Schema Versions",
        "",
        counter_table(report["schema_versions"]),
        "## Missing Required Fields",
        "",
        counter_table(report["missing_required_fields"]),
        "## Missing Optional Fields",
        "",
        counter_table(report["missing_optional_fields"]),
    ]
    if report["invalid_messages"]:
        lines.extend(["## Invalid Records", ""])
        for item in report["invalid_messages"]:
            lines.append(
                f"- {item['source']} record {item['record_index']}: {item['error']}"
            )
    return "\n".join(lines) + "\n"
