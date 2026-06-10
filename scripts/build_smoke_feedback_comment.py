from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent
from scripts.review_smoke_feedback import (
    ReviewInputs,
    SmokeFeedbackReport,
    parse_args as parse_review_args,
    report_to_markdown,
    resolve_inputs,
    review_feedback,
)


VERDICT_CHOICES = (
    "ready for triage",
    "needs missing detail",
    "needs redaction",
    "out of scope for issue #12",
)

VERDICT_INTROS = {
    "ready for triage": (
        "Thanks for sharing this first-user smoke feedback. I ran the repository-side "
        "feedback review helper, and the note is detailed enough for maintainer triage."
    ),
    "needs missing detail": (
        "Thanks for sharing this first-user smoke feedback. I ran the repository-side "
        "feedback review helper, and the note still needs a bit more detail before "
        "maintainers should act on it."
    ),
    "needs redaction": (
        "Thanks for sharing this first-user smoke feedback. I ran the repository-side "
        "feedback review helper, and the public note needs redaction before we keep "
        "the discussion on the thread."
    ),
    "out of scope for issue #12": (
        "Thanks for sharing this note. I ran the repository-side feedback review helper, "
        "and the current report drifts outside the intended dry-run / fake-server scope "
        "for issue #12."
    ),
}

VERDICT_NOTES = {
    "ready for triage": (
        "- This is useful usability feedback, not benchmark validation or adoption evidence.",
        "- The suggested triage bucket helps maintainers route the next action, but it is not a claim about external validation by itself.",
    ),
    "needs missing detail": (
        "- Once the missing details are filled in, maintainers can rerun the same helper on the updated note.",
    ),
    "needs redaction": (
        "- Please remove secrets, private endpoints, hostnames, cluster paths, or tokens before the thread continues.",
        "- After redaction, maintainers can rerun the helper and continue triage on the same public note.",
    ),
    "out of scope for issue #12": (
        "- Issue #12 is only for dry-run and local fake-server usability feedback.",
        "- Real-run or GPU-path discussion should be redirected to issue #17 with the full artifact and metadata requirements.",
    ),
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a maintainer-style smoke-feedback reply draft.",
    )
    parser.add_argument(
        "--feedback-dir",
        help="Starter directory containing issue_body.md and optional env/environment.json.",
    )
    parser.add_argument("--issue-body", help="Path to the feedback issue body markdown.")
    parser.add_argument("--environment", help="Optional path to environment JSON.")
    parser.add_argument(
        "--output",
        help="Markdown output path. Defaults to <feedback-dir>/smoke_feedback_comment.md or results/review/smoke_feedback_comment.md.",
    )
    parser.add_argument(
        "--review-summary-output",
        help="Optional path for also writing the structured feedback review summary markdown.",
    )
    parser.add_argument(
        "--override-verdict",
        choices=VERDICT_CHOICES,
        help="Force the public reply template to use a specific maintainer verdict.",
    )
    return parser.parse_args(argv)


def default_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output) if Path(args.output).is_absolute() else ROOT / args.output
    if args.feedback_dir:
        feedback_dir = Path(args.feedback_dir)
        if not feedback_dir.is_absolute():
            feedback_dir = ROOT / feedback_dir
        return feedback_dir / "smoke_feedback_comment.md"
    return ROOT / "results" / "review" / "smoke_feedback_comment.md"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_comment(report: SmokeFeedbackReport) -> str:
    intro = VERDICT_INTROS.get(
        report.verdict,
        "Thanks for sharing this first-user smoke feedback. I ran the repository-side helper and captured the current review state below.",
    )
    lines = [
        intro,
        "",
        f"Automated verdict: `{report.verdict}`",
        f"Suggested triage bucket: `{report.triage_bucket}`",
        f"Smoke-test path checked: `{report.smoke_path or 'unknown'}`",
        "",
    ]

    if report.checks_passed:
        lines.extend(["What already looks usable:", ""])
        lines.extend(f"- {item}" for item in report.checks_passed)
        lines.append("")

    if report.issues:
        lines.extend(["What should be fixed or clarified next:", ""])
        lines.extend(f"- {item}" for item in report.issues)
        lines.append("")

    lines.extend(["Manual maintainer follow-up:", ""])
    lines.extend(f"- {item}" for item in report.manual_follow_up)
    lines.append("")

    lines.extend(["Current maintainer note:", ""])
    lines.extend(VERDICT_NOTES.get(report.verdict, VERDICT_NOTES["needs missing detail"]))
    lines.append("")
    return "\n".join(lines)


def apply_override_verdict(
    report: SmokeFeedbackReport,
    verdict: str | None,
) -> SmokeFeedbackReport:
    if verdict is None or verdict == report.verdict:
        return report

    extra_issues: tuple[str, ...] = ()
    if verdict == "needs redaction":
        extra_issues = (
            "public note should be redacted before maintainers continue the thread",
        )
    elif verdict == "out of scope for issue #12":
        extra_issues = (
            "report should stay within dry-run / local fake-server feedback scope for issue #12",
        )

    issues = report.issues + tuple(item for item in extra_issues if item not in report.issues)
    return SmokeFeedbackReport(
        verdict=verdict,
        triage_bucket=report.triage_bucket,
        smoke_path=report.smoke_path,
        checks_passed=report.checks_passed,
        issues=issues,
        manual_follow_up=report.manual_follow_up,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    review_arg_list: list[str] = []
    for name in ("feedback_dir", "issue_body", "environment"):
        value = getattr(args, name)
        if value:
            review_arg_list.extend([f"--{name.replace('_', '-')}", value])

    try:
        inputs: ReviewInputs = resolve_inputs(parse_review_args(review_arg_list))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = review_feedback(inputs)
    report = apply_override_verdict(report, args.override_verdict)
    comment_output = ensure_parent(default_output_path(args))
    comment_output.write_text(build_comment(report), encoding="utf-8")
    print(f"wrote smoke feedback comment draft to {display_path(comment_output)}")

    if args.review_summary_output:
        summary_output = ensure_parent(
            Path(args.review_summary_output)
            if Path(args.review_summary_output).is_absolute()
            else ROOT / args.review_summary_output
        )
        summary_output.write_text(report_to_markdown(report), encoding="utf-8")
        print(f"wrote smoke feedback review summary to {display_path(summary_output)}")

    print(f"verdict: {report.verdict}")
    return 0 if report.verdict == "ready for triage" else 1


if __name__ == "__main__":
    raise SystemExit(main())
