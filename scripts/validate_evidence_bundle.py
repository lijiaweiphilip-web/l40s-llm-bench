from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_result import validate_file


REQUIRED_FILES = (
    "README.md",
    "manifest.json",
    "config.json",
    "summary.json",
    "raw-events.jsonl",
    "environment.json",
)

REQUIRED_MANIFEST_FIELDS = (
    "run_id",
    "created_at",
    "project_version",
    "git_commit",
    "benchmark_command",
    "backend",
    "endpoint_type",
    "model",
    "workload_profile",
    "request_count",
    "success_count",
    "failure_count",
    "streaming",
    "ttft_ms_summary",
    "tpot_ms_summary",
    "raw_event_file",
    "summary_file",
    "manifest_file",
    "environment_file",
    "hardware.synthetic",
    "hardware.gpu_model",
    "hardware.gpu_count",
    "limitations",
)

REFERENCE_FIELDS = (
    "raw_event_file",
    "summary_file",
    "manifest_file",
    "environment_file",
    "config_file",
)


@dataclass(frozen=True)
class BundleIssue:
    bundle: Path
    message: str

    def format(self) -> str:
        return f"{self.bundle}: {self.message}"


@dataclass(frozen=True)
class BundleReport:
    bundles: tuple[Path, ...]
    issues: tuple[BundleIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing file"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg}"
    if not isinstance(loaded, dict):
        return None, "expected a JSON object"
    return loaded, None


def nested_get(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def nested_present(data: dict[str, Any], dotted_key: str) -> bool:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def discover_bundle_dirs(inputs: Sequence[str | Path]) -> list[Path]:
    bundles: list[Path] = []
    seen: set[Path] = set()
    for raw_input in inputs:
        path = Path(raw_input)
        if path.is_dir() and (path / "manifest.json").exists():
            candidates = [path]
        elif path.is_dir():
            candidates = sorted(
                child for child in path.iterdir() if child.is_dir()
            )
        else:
            raise FileNotFoundError(path)
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved not in seen:
                bundles.append(candidate)
                seen.add(resolved)
    if not bundles:
        raise ValueError("no evidence bundle directories found")
    return bundles


def count_records(raw_records: list[dict[str, Any]]) -> dict[str, int]:
    success_count = sum(1 for record in raw_records if record.get("status") == "ok")
    return {
        "request_count": len(raw_records),
        "success_count": success_count,
        "failure_count": len(raw_records) - success_count,
    }


def compare_count(
    issues: list[BundleIssue],
    bundle: Path,
    source: str,
    data: dict[str, Any],
    key: str,
    expected: int,
) -> None:
    if data.get(key) != expected:
        issues.append(
            BundleIssue(
                bundle,
                f"{source}.{key}={data.get(key)!r}, expected {expected}",
            )
        )


def validate_bundle(path: str | Path) -> BundleReport:
    bundle = Path(path)
    issues: list[BundleIssue] = []
    if not bundle.is_dir():
        return BundleReport((bundle,), (BundleIssue(bundle, "not a directory"),))

    for filename in REQUIRED_FILES:
        if not (bundle / filename).is_file():
            issues.append(BundleIssue(bundle, f"missing required file {filename}"))

    manifest, manifest_error = load_json(bundle / "manifest.json")
    summary, summary_error = load_json(bundle / "summary.json")
    environment, environment_error = load_json(bundle / "environment.json")
    config, config_error = load_json(bundle / "config.json")
    json_errors = {
        "manifest.json": manifest_error,
        "summary.json": summary_error,
        "environment.json": environment_error,
        "config.json": config_error,
    }
    for filename, error in json_errors.items():
        if error:
            issues.append(BundleIssue(bundle, f"{filename}: {error}"))

    if manifest is None:
        return BundleReport((bundle,), tuple(issues))

    for field in REQUIRED_MANIFEST_FIELDS:
        if not nested_present(manifest, field):
            issues.append(BundleIssue(bundle, f"manifest missing {field}"))

    limitations = manifest.get("limitations")
    if not isinstance(limitations, list) or not any(
        isinstance(item, str) and item.strip() for item in limitations
    ):
        issues.append(
            BundleIssue(bundle, "manifest limitations must be a non-empty list")
        )

    for field in REFERENCE_FIELDS:
        reference = manifest.get(field)
        if reference is None:
            continue
        if not isinstance(reference, str) or not reference.strip():
            issues.append(BundleIssue(bundle, f"manifest {field} must be a path string"))
            continue
        if Path(reference).is_absolute():
            issues.append(BundleIssue(bundle, f"manifest {field} must be relative"))
            continue
        if not (bundle / reference).is_file():
            issues.append(
                BundleIssue(bundle, f"manifest {field} target missing: {reference}")
            )

    raw_reference = manifest.get("raw_event_file", "raw-events.jsonl")
    raw_path = (
        bundle / raw_reference
        if isinstance(raw_reference, str)
        else bundle / "raw-events.jsonl"
    )
    synthetic = bool(nested_get(manifest, "hardware.synthetic"))
    if not raw_path.is_file():
        return BundleReport((bundle,), tuple(issues))
    raw_report = validate_file(
        raw_path,
        require_synthetic_fake_server=synthetic,
    )
    for raw_issue in raw_report.issues:
        issues.append(BundleIssue(bundle, raw_issue.format()))

    counts = count_records(
        []
        if raw_report.issues
        else [
            json.loads(line)
            for line in raw_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    )
    if not raw_report.issues:
        for key, expected in counts.items():
            compare_count(issues, bundle, "manifest", manifest, key, expected)
            if summary is not None:
                compare_count(issues, bundle, "summary", summary, key, expected)

    if summary is not None and summary.get("benchmark_claim") is True:
        issues.append(BundleIssue(bundle, "summary benchmark_claim must not be true"))
    if synthetic and summary is not None and summary.get("synthetic") is not True:
        issues.append(
            BundleIssue(bundle, "synthetic bundle summary must set synthetic=true")
        )
    if synthetic and environment is not None:
        env_synthetic = nested_get(environment, "gpu.synthetic")
        if env_synthetic is not True:
            issues.append(
                BundleIssue(
                    bundle,
                    "synthetic bundle environment gpu.synthetic must be true",
                )
            )
    if config is not None and not config:
        issues.append(BundleIssue(bundle, "config.json must not be empty"))

    return BundleReport((bundle,), tuple(issues))


def validate_paths(inputs: Sequence[str | Path]) -> BundleReport:
    bundles = discover_bundle_dirs(inputs)
    issues: list[BundleIssue] = []
    for bundle in bundles:
        report = validate_bundle(bundle)
        issues.extend(report.issues)
    return BundleReport(tuple(bundles), tuple(issues))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate reproducibility evidence bundle directories.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        default=["examples/evidence-bundles"],
        help="Evidence bundle directory or parent directory to validate.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_paths(args.inputs)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"validated {len(report.bundles)} evidence bundle(s)")
    if report.ok:
        print("PASS")
        return 0

    print("FAIL")
    for issue in report.issues:
        print(f"- {issue.format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
