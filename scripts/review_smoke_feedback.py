from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent

REQUIRED_HEADINGS = (
    "## Repository commit",
    "## Smoke-test path",
    "## Commands run",
    "## Environment",
    "## Expected artifacts",
    "## What happened?",
    "## Approximate time spent",
    "## Suggested improvements",
    "## Safety checks",
)

ALLOWED_SMOKE_PATHS = {
    "Dry run only",
    "Fake-server sanity suite only",
    "Dry run and fake-server sanity suite",
    "Manual two-terminal fake-server path",
}

OUT_OF_SCOPE_PATTERNS = (
    "VLLM_SMOKE_DRY_RUN=0",
    "run_l40s_artifact_capture.sh",
    "vllm serve",
    "tensor parallel",
    "real l40s",
    "gpu benchmark",
)

REDACTION_PATTERNS = (
    ("OpenAI-style key marker", re.compile(r"\bsk-[A-Za-z0-9_-]{10,}\b")),
    ("Bearer token marker", re.compile(r"Bearer\s+[A-Za-z0-9._-]{10,}", re.IGNORECASE)),
    ("Private endpoint hint", re.compile(r"https?://(?!127\.0\.0\.1|localhost)[^\s`]+", re.IGNORECASE)),
)

TRIAGE_BUCKETS = (
    (
        "Setup failure",
        (
            "pip install",
            "module not found",
            "modulenotfounderror",
            "dependency",
            "python version",
            "install failed",
        ),
    ),
    (
        "Harness failure",
        (
            "traceback",
            "assert",
            "schema",
            "sanity_checks",
            "dry_run.jsonl",
            "summary.csv",
            "run_sanity_checks.py",
            "bench_openai_compatible.py",
        ),
    ),
    (
        "Artifact gap",
        (
            "which file",
            "expected artifact",
            "summary.md",
            "manifest",
            "not sure what to attach",
        ),
    ),
    (
        "Documentation friction",
        (
            "unclear",
            "confusing",
            "which document",
            "wording",
            "readme",
            "entry path",
        ),
    ),
    (
        "Real-run request",
        (
            "gpu",
            "vllm",
            "real run",
            "real model",
            "artifact bundle",
            "issue #17",
        ),
    ),
)


@dataclass(frozen=True)
class ReviewInputs:
    issue_body: Path
    environment: Path | None
    output: Path


@dataclass(frozen=True)
class SmokeFeedbackReport:
    verdict: str
    triage_bucket: str
    smoke_path: str | None
    checks_passed: tuple[str, ...]
    issues: tuple[str, ...]
    manual_follow_up: tuple[str, ...]


def format_repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_path(raw_path: str | None) -> Path | None:
    if raw_path is None:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a lightweight review summary for first-user smoke feedback.",
    )
    parser.add_argument(
        "--feedback-dir",
        help="Starter directory containing issue_body.md and optional env/environment.json.",
    )
    parser.add_argument("--issue-body", help="Path to the feedback issue body markdown.")
    parser.add_argument("--environment", help="Optional path to environment JSON.")
    parser.add_argument(
        "--output",
        help="Markdown output path. Defaults to <feedback-dir>/smoke_feedback_review.md or results/review/smoke_feedback_review.md.",
    )
    return parser.parse_args(argv)


def resolve_inputs(args: argparse.Namespace) -> ReviewInputs:
    if args.feedback_dir:
        feedback_dir = resolve_path(args.feedback_dir)
        assert feedback_dir is not None
        issue_body = feedback_dir / "issue_body.md"
        environment = feedback_dir / "env" / "environment.json"
        output = (
            resolve_path(args.output)
            if args.output
            else feedback_dir / "smoke_feedback_review.md"
        )
        assert output is not None
        return ReviewInputs(
            issue_body=issue_body,
            environment=environment if environment.exists() else None,
            output=output,
        )

    if args.issue_body is None:
        raise ValueError("missing required argument without --feedback-dir: --issue-body")
    issue_body = resolve_path(args.issue_body)
    output = (
        resolve_path(args.output)
        if args.output
        else ROOT / "results" / "review" / "smoke_feedback_review.md"
    )
    environment = resolve_path(args.environment) if args.environment else None
    assert issue_body is not None
    assert output is not None
    return ReviewInputs(issue_body=issue_body, environment=environment, output=output)


def section_text(body: str, heading: str) -> str:
    pattern = re.compile(
        rf"{re.escape(heading)}\n+(.*?)(?=\n## |\Z)",
        re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return ""
    return match.group(1).strip()


def classify_bucket(body: str) -> str:
    narrative = "\n".join(
        [
            section_text(body, "## What happened?"),
            section_text(body, "## Suggested improvements"),
        ]
    ).lower()
    for bucket, keywords in TRIAGE_BUCKETS:
        if any(keyword in narrative for keyword in keywords):
            return bucket
    return "Documentation friction"


def review_feedback(inputs: ReviewInputs) -> SmokeFeedbackReport:
    issues: list[str] = []
    checks_passed: list[str] = []

    if not inputs.issue_body.exists():
        return SmokeFeedbackReport(
            verdict="needs missing detail",
            triage_bucket="Documentation friction",
            smoke_path=None,
            checks_passed=(),
            issues=(f"missing required artifact: `{inputs.issue_body}`",),
            manual_follow_up=(
                "Confirm whether the report came from a real external public account before counting it toward G9.",
            ),
        )

    body = inputs.issue_body.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            issues.append(f"missing required section heading: `{heading}`")
    if not issues:
        checks_passed.append("feedback note includes the expected maintainer-review sections")

    if "<fill-me>" in body:
        issues.append("feedback note still contains `<fill-me>` placeholders")
    else:
        checks_passed.append("feedback note does not contain starter placeholders")

    unchecked_safety = re.findall(r"^- \[ \] (.+)$", body, flags=re.MULTILINE)
    if unchecked_safety:
        issues.extend(
            f"unchecked safety item: `{item}`" for item in unchecked_safety
        )
    else:
        checks_passed.append("all listed safety checks are marked complete")

    smoke_path = section_text(body, "## Smoke-test path").strip().strip("`")
    if smoke_path and smoke_path in ALLOWED_SMOKE_PATHS:
        checks_passed.append("smoke-test path stays within the public dry-run/fake-server options")
    else:
        issues.append(
            "smoke-test path is missing or outside the allowed public dry-run/fake-server options"
        )

    commands = section_text(body, "## Commands run")
    if any(pattern.lower() in commands.lower() for pattern in OUT_OF_SCOPE_PATTERNS):
        issues.append("commands section includes a real-run or GPU-path indicator that is out of scope for issue #12")
    elif commands:
        checks_passed.append("commands section stays within the intended smoke-feedback scope")
    else:
        issues.append("commands section is empty")

    for label, pattern in REDACTION_PATTERNS:
        if pattern.search(body):
            issues.append(f"possible sensitive content detected: {label}")
    if not any(issue.startswith("possible sensitive content detected") for issue in issues):
        checks_passed.append("no obvious token or non-local endpoint markers were detected in the markdown")

    if inputs.environment is not None:
        try:
            payload = json.loads(inputs.environment.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"environment JSON is not valid: {exc}")
        else:
            if payload.get("python") and payload.get("platform"):
                checks_passed.append("optional environment JSON is present and parseable")
            else:
                issues.append("environment JSON is present but missing `python` or `platform` fields")

    triage_bucket = classify_bucket(body)

    verdict = "ready for triage"
    if any(issue.startswith("possible sensitive content detected") for issue in issues):
        verdict = "needs redaction"
    elif any("out of scope" in issue for issue in issues):
        verdict = "out of scope for issue #12"
    elif issues:
        verdict = "needs missing detail"

    return SmokeFeedbackReport(
        verdict=verdict,
        triage_bucket=triage_bucket,
        smoke_path=smoke_path or None,
        checks_passed=tuple(checks_passed),
        issues=tuple(issues),
        manual_follow_up=(
            "Confirm whether the public account is genuinely external before counting this toward G9.",
            "Convert the triage bucket into a follow-up doc patch, bug issue, or maintainer reply.",
            "Keep the public wording limited to usability feedback, not benchmark validation.",
        ),
    )


def report_to_markdown(report: SmokeFeedbackReport) -> str:
    lines = [
        "# Smoke Feedback Review Summary",
        "",
        f"Verdict: `{report.verdict}`",
        f"Suggested triage bucket: `{report.triage_bucket}`",
        f"Smoke-test path: `{report.smoke_path or 'unknown'}`",
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

    lines.extend(["", "## Manual Follow-Up", ""])
    lines.extend(f"- {item}" for item in report.manual_follow_up)
    lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        inputs = resolve_inputs(parse_args(argv))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = review_feedback(inputs)
    output = ensure_parent(inputs.output)
    output.write_text(report_to_markdown(report), encoding="utf-8")
    print(f"wrote smoke feedback review to {format_repo_path(output)}")
    print(f"verdict: {report.verdict}")
    print(f"triage bucket: {report.triage_bucket}")
    if report.issues:
        for issue in report.issues:
            print(f"- {issue}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
