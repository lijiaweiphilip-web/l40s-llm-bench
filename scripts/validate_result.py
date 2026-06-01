from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import read_jsonl
from l40s_bench.schema import validate_result


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    record_index: int | None
    message: str

    def format(self) -> str:
        if self.record_index is None:
            return f"{self.path}: {self.message}"
        return f"{self.path} record {self.record_index}: {self.message}"


@dataclass(frozen=True)
class ValidationReport:
    files: tuple[Path, ...]
    records: int
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def collect_jsonl_paths(inputs: Sequence[str | Path]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for raw_input in inputs:
        path = Path(raw_input)
        if path.is_dir():
            candidates = sorted(path.rglob("*.jsonl"))
        elif path.is_file():
            candidates = [path]
        else:
            raise FileNotFoundError(path)
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved not in seen:
                paths.append(candidate)
                seen.add(resolved)
    if not paths:
        raise ValueError("no JSONL result files found")
    return paths


def validate_synthetic_fake_server_markers(
    record: dict[str, Any],
    path: Path,
    record_index: int,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    expected = {
        "synthetic": True,
        "server": "fake-server",
        "benchmark_claim": False,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            issues.append(
                ValidationIssue(
                    path,
                    record_index,
                    f"expected {key}={value!r} for synthetic fake-server examples",
                )
            )
    return issues


def validate_file(
    path: str | Path,
    require_synthetic_fake_server: bool = False,
) -> ValidationReport:
    target = Path(path)
    issues: list[ValidationIssue] = []
    try:
        records = read_jsonl(target)
    except ValueError as exc:
        return ValidationReport((target,), 0, (ValidationIssue(target, None, str(exc)),))

    for record_index, original in enumerate(records, start=1):
        record = dict(original)
        try:
            validate_result(record)
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(ValidationIssue(target, record_index, str(exc)))
            continue
        if require_synthetic_fake_server:
            issues.extend(
                validate_synthetic_fake_server_markers(
                    original,
                    target,
                    record_index,
                )
            )
    return ValidationReport((target,), len(records), tuple(issues))


def validate_paths(
    inputs: Sequence[str | Path],
    require_synthetic_fake_server: bool = False,
) -> ValidationReport:
    paths = collect_jsonl_paths(inputs)
    issues: list[ValidationIssue] = []
    records = 0
    for path in paths:
        report = validate_file(path, require_synthetic_fake_server)
        records += report.records
        issues.extend(report.issues)
    return ValidationReport(tuple(paths), records, tuple(issues))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate raw benchmark result JSONL files.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        default=["examples/results"],
        help="JSONL file(s) or directories to validate.",
    )
    parser.add_argument(
        "--require-synthetic-fake-server",
        action="store_true",
        help="Require example records to be marked synthetic fake-server fixtures.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_paths(
            args.inputs,
            require_synthetic_fake_server=args.require_synthetic_fake_server,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    marker_note = (
        " with synthetic fake-server markers"
        if args.require_synthetic_fake_server
        else ""
    )
    print(
        f"validated {report.records} record(s) from {len(report.files)} file(s)"
        f"{marker_note}"
    )
    if report.ok:
        print("PASS")
        return 0

    print("FAIL")
    for issue in report.issues:
        print(f"- {issue.format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
