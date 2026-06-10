from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent, read_jsonl
from l40s_bench.manifest import sha256_file
from l40s_bench.schema import validate_result
from l40s_bench.summary import summarize_records


@dataclass(frozen=True)
class ReviewInputs:
    raw: Path
    summary: Path
    manifest: Path
    output: Path


@dataclass(frozen=True)
class ReviewReport:
    verdict: str
    run_id: str | None
    raw_records: int
    summary_rows: int
    checks_passed: tuple[str, ...]
    issues: tuple[str, ...]
    manual_checks: tuple[str, ...]


def resolve_path(raw_path: str | None) -> Path | None:
    if raw_path is None:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a lightweight review summary for one benchmark result submission.",
    )
    parser.add_argument(
        "--submission-dir",
        help="Starter-kit submission directory containing raw/, tables/, and manifests/.",
    )
    parser.add_argument("--raw", help="Path to raw JSONL.")
    parser.add_argument("--summary", help="Path to summary CSV.")
    parser.add_argument("--manifest", help="Path to run manifest JSON.")
    parser.add_argument(
        "--output",
        help="Markdown output path. Defaults to <submission-dir>/result_review_summary.md or results/review/result_review_summary.md.",
    )
    return parser.parse_args(argv)


def resolve_inputs(args: argparse.Namespace) -> ReviewInputs:
    if args.submission_dir:
        submission_dir = resolve_path(args.submission_dir)
        assert submission_dir is not None
        raw = submission_dir / "raw" / "raw.jsonl"
        summary = submission_dir / "tables" / "summary.csv"
        manifest = submission_dir / "manifests" / "run_manifest.json"
        output = (
            resolve_path(args.output)
            if args.output
            else submission_dir / "result_review_summary.md"
        )
        return ReviewInputs(raw=raw, summary=summary, manifest=manifest, output=output)

    missing = [
        name
        for name in ("raw", "summary", "manifest")
        if getattr(args, name) is None
    ]
    if missing:
        joined = ", ".join(f"--{name}" for name in missing)
        raise ValueError(
            f"missing required arguments without --submission-dir: {joined}"
        )
    output = (
        resolve_path(args.output)
        if args.output
        else ROOT / "results" / "review" / "result_review_summary.md"
    )
    assert output is not None
    raw = resolve_path(args.raw)
    summary = resolve_path(args.summary)
    manifest = resolve_path(args.manifest)
    assert raw is not None
    assert summary is not None
    assert manifest is not None
    return ReviewInputs(
        raw=raw,
        summary=summary,
        manifest=manifest,
        output=output,
    )


def load_summary_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {key: normalize_cell(value) for key, value in row.items()}


def compare_summary_rows(
    records: list[dict[str, Any]],
    summary_rows: list[dict[str, str]],
) -> tuple[bool, str | None]:
    generated_rows = summarize_records(records)
    normalized_generated = [normalize_row(row) for row in generated_rows]
    if normalized_generated == summary_rows:
        return True, None

    actual_case_ids = [row.get("case_id", "<missing>") for row in summary_rows]
    expected_case_ids = [row.get("case_id", "<missing>") for row in normalized_generated]
    return (
        False,
        "summary.csv does not match the current raw JSONL-derived summary "
        f"(expected case_ids={expected_case_ids}, actual case_ids={actual_case_ids})",
    )


def artifact_by_label(manifest: dict[str, Any], label: str) -> dict[str, Any] | None:
    for artifact in manifest.get("artifacts", []):
        if artifact.get("label") == label:
            return artifact
    return None


def check_manifest_entry(
    manifest: dict[str, Any],
    label: str,
    actual_path: Path,
) -> str | None:
    artifact = artifact_by_label(manifest, label)
    if artifact is None:
        return f"manifest is missing `{label}` entry"
    if not actual_path.exists():
        return f"selected {label} file does not exist: {actual_path}"
    actual_sha = sha256_file(actual_path)
    manifest_sha = artifact.get("sha256")
    if manifest_sha != actual_sha:
        return (
            f"manifest `{label}` SHA256 does not match selected file "
            f"({manifest_sha!r} != {actual_sha!r})"
        )
    return None


def review_submission(inputs: ReviewInputs) -> ReviewReport:
    issues: list[str] = []
    checks_passed: list[str] = []

    for required_path in (inputs.raw, inputs.summary, inputs.manifest):
        if not required_path.exists():
            issues.append(f"missing required artifact: `{required_path}`")

    if issues:
        return ReviewReport(
            verdict="needs missing artifact",
            run_id=None,
            raw_records=0,
            summary_rows=0,
            checks_passed=(),
            issues=tuple(issues),
            manual_checks=(
                "Confirm redaction, hardware disclosure, and claim wording manually.",
            ),
        )

    records = read_jsonl(inputs.raw)
    for index, record in enumerate(records, start=1):
        try:
            validate_result(record)
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(f"raw record {index} failed schema validation: {exc}")
    if not issues:
        checks_passed.append("raw JSONL validates against the public result schema")

    manifest = json.loads(inputs.manifest.read_text(encoding="utf-8"))
    run_ids = sorted({str(record.get("run_id")) for record in records})
    run_id = run_ids[0] if len(run_ids) == 1 else None
    if len(run_ids) != 1:
        issues.append(f"raw JSONL contains multiple run_ids: {run_ids}")
    elif manifest.get("run_id") != run_id:
        issues.append(
            f"manifest run_id {manifest.get('run_id')!r} does not match raw JSONL run_id {run_id!r}"
        )
    else:
        checks_passed.append("manifest run_id matches the raw JSONL run_id")

    if manifest.get("missing_required_artifacts"):
        issues.append(
            "manifest reports missing required artifacts: "
            + ", ".join(str(item) for item in manifest["missing_required_artifacts"])
        )
    elif manifest.get("status") != "complete":
        issues.append(f"manifest status is not complete: {manifest.get('status')!r}")
    else:
        checks_passed.append("manifest reports a complete required artifact set")

    for label, path in (("raw_jsonl", inputs.raw), ("summary_csv", inputs.summary)):
        issue = check_manifest_entry(manifest, label, path)
        if issue:
            issues.append(issue)
    if not any("manifest `" in issue for issue in issues):
        checks_passed.append("manifest hashes match the selected raw JSONL and summary CSV")

    summary_rows = load_summary_rows(inputs.summary)
    summary_ok, summary_issue = compare_summary_rows(records, summary_rows)
    if summary_ok:
        checks_passed.append("summary CSV matches a fresh summary generated from the raw JSONL")
    elif summary_issue:
        issues.append(summary_issue)

    verdict = "ready for review"
    if any(issue.startswith("missing required artifact") for issue in issues):
        verdict = "needs missing artifact"
    elif any("raw record" in issue or "summary.csv does not match" in issue for issue in issues):
        verdict = "exploratory only, not ready for benchmark discussion"
    elif issues:
        verdict = "needs missing artifact"

    return ReviewReport(
        verdict=verdict,
        run_id=run_id,
        raw_records=len(records),
        summary_rows=len(summary_rows),
        checks_passed=tuple(checks_passed),
        issues=tuple(issues),
        manual_checks=(
            "Confirm secrets, private endpoints, hostnames, and cluster identifiers are absent.",
            "Confirm hardware/runtime notes are specific enough for another contributor to attempt reproduction.",
            "Confirm the issue wording does not overstate the result beyond the attached evidence.",
        ),
    )


def report_to_markdown(report: ReviewReport) -> str:
    lines = [
        "# Result Review Summary",
        "",
        f"Verdict: `{report.verdict}`",
        f"Run ID: `{report.run_id or 'unknown'}`",
        f"Raw records checked: `{report.raw_records}`",
        f"Summary rows checked: `{report.summary_rows}`",
        "",
        "## Automated Checks Passed",
        "",
    ]
    if report.checks_passed:
        lines.extend(f"- {item}" for item in report.checks_passed)
    else:
        lines.append("- None")

    lines.extend(["", "## Issues", ""])
    if report.issues:
        lines.extend(f"- {item}" for item in report.issues)
    else:
        lines.append("- None")

    lines.extend(["", "## Manual Checks Still Needed", ""])
    lines.extend(f"- {item}" for item in report.manual_checks)
    lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        inputs = resolve_inputs(parse_args(argv))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = review_submission(inputs)
    output = ensure_parent(inputs.output)
    output.write_text(report_to_markdown(report), encoding="utf-8")
    print(f"wrote review summary to {output}")
    print(f"verdict: {report.verdict}")
    if report.issues:
        for issue in report.issues:
            print(f"- {issue}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
