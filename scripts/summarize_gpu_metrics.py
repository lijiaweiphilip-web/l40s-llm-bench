from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from statistics import mean
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent


REQUIRED_COLUMNS = (
    "timestamp",
    "gpu_name",
    "gpu_uuid",
    "driver_version",
    "cuda_version",
    "power.draw",
    "power.limit",
    "temperature.gpu",
    "utilization.gpu",
    "utilization.memory",
    "memory.used",
    "memory.total",
    "clocks.sm",
    "clocks.mem",
    "pcie.link.gen.current",
    "pcie.link.width.current",
)

METRIC_COLUMNS = {
    "power_draw_w": "power.draw",
    "power_limit_w": "power.limit",
    "temperature_gpu_c": "temperature.gpu",
    "utilization_gpu_percent": "utilization.gpu",
    "utilization_memory_percent": "utilization.memory",
    "memory_used_mib": "memory.used",
    "memory_total_mib": "memory.total",
    "clocks_sm_mhz": "clocks.sm",
    "clocks_mem_mhz": "clocks.mem",
    "pcie_link_gen_current": "pcie.link.gen.current",
    "pcie_link_width_current": "pcie.link.width.current",
}

MISSING_VALUES = {"", "N/A", "[N/A]", "Not Supported", "None"}


@dataclass(frozen=True)
class GpuGroup:
    gpu_uuid: str
    rows: list[dict[str, str]]


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    stripped = value.strip()
    if stripped in MISSING_VALUES:
        return None
    for suffix in (" MiB", " W", " C", " MHz", "%"):
        if stripped.endswith(suffix):
            stripped = stripped[: -len(suffix)].strip()
    try:
        return float(stripped)
    except ValueError:
        return None


def summarize_numbers(values: Iterable[float | None]) -> dict[str, float | int | None]:
    parsed = [value for value in values if value is not None]
    if not parsed:
        return {"count": 0, "min": None, "avg": None, "max": None}
    return {
        "count": len(parsed),
        "min": round(min(parsed), 3),
        "avg": round(mean(parsed), 3),
        "max": round(max(parsed), 3),
    }


def read_gpu_metrics_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"missing required GPU metric columns: {', '.join(missing)}")
        return [dict(row) for row in reader]


def group_by_gpu(rows: list[dict[str, str]]) -> list[GpuGroup]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for index, row in enumerate(rows):
        gpu_uuid = row.get("gpu_uuid") or f"missing-gpu-uuid-{index}"
        grouped[gpu_uuid].append(row)
    return [GpuGroup(gpu_uuid, grouped[gpu_uuid]) for gpu_uuid in sorted(grouped)]


def summarize_group(group: GpuGroup) -> dict[str, Any]:
    rows = group.rows
    first = rows[0]
    summary: dict[str, Any] = {
        "gpu_uuid": group.gpu_uuid,
        "gpu_name": first.get("gpu_name"),
        "driver_version": first.get("driver_version"),
        "cuda_version": first.get("cuda_version"),
        "sample_count": len(rows),
        "timestamp_start": rows[0].get("timestamp"),
        "timestamp_end": rows[-1].get("timestamp"),
    }
    for output_name, column in METRIC_COLUMNS.items():
        summary[output_name] = summarize_numbers(
            parse_number(row.get(column)) for row in rows
        )
    return summary


def summarize_gpu_metrics(path: str | Path) -> dict[str, Any]:
    rows = read_gpu_metrics_csv(path)
    groups = group_by_gpu(rows)
    return {
        "input_file": str(path),
        "schema_version": "0.1",
        "sample_count": len(rows),
        "gpu_count": len(groups),
        "required_columns": list(REQUIRED_COLUMNS),
        "gpus": [summarize_group(group) for group in groups],
        "limitations": [
            "GPU metrics provide context only and do not validate benchmark quality.",
            "Synthetic sample files are parser fixtures, not real GPU measurements.",
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize nvidia-smi GPU metrics CSV artifacts.",
    )
    parser.add_argument("input", help="nvidia-smi CSV file to summarize.")
    parser.add_argument(
        "--output",
        help="Optional JSON output path. Prints to stdout when omitted.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = summarize_gpu_metrics(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output = json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True)
    if args.output:
        target = ensure_parent(args.output)
        target.write_text(output + "\n", encoding="utf-8")
        print(f"wrote GPU metrics summary to {target}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
