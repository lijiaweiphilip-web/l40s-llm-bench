from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent
from scripts.review_result_submission import (
    ReviewReport,
    report_to_markdown,
    resolve_inputs,
    review_submission,
)


VERDICT_INTROS = {
    "ready for review": (
        "Thanks for sharing this result. I ran the repository-side review helper, "
        "and the submitted artifact set looks internally consistent enough for "
        "maintainer review."
    ),
    "needs missing artifact": (
        "Thanks for sharing this result. I ran the repository-side review helper, "
        "and the submission still needs one or more required artifacts before it "
        "can be treated as reproducibility evidence."
    ),
    "exploratory only, not ready for benchmark discussion": (
        "Thanks for sharing this result. I ran the repository-side review helper, "
        "and this currently reads as an exploratory artifact set rather than a "
        "ready-for-discussion benchmark submission."
    ),
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a maintainer-style benchmark result review comment draft.",
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
        help="Markdown output path. Defaults to <submission-dir>/result_review_comment.md or results/review/result_review_comment.md.",
    )
    parser.add_argument(
        "--review-summary-output",
        help="Optional path for also writing the structured review summary markdown.",
    )
    return parser.parse_args(argv)


def default_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output) if Path(args.output).is_absolute() else ROOT / args.output
    if args.submission_dir:
        submission_dir = Path(args.submission_dir)
        if not submission_dir.is_absolute():
            submission_dir = ROOT / submission_dir
        return submission_dir / "result_review_comment.md"
    return ROOT / "results" / "review" / "result_review_comment.md"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_comment(report: ReviewReport) -> str:
    intro = VERDICT_INTROS.get(
        report.verdict,
        "Thanks for sharing this result. I ran the repository-side review helper and captured the current review state below.",
    )
    lines = [
        intro,
        "",
        f"Automated verdict: `{report.verdict}`",
        f"Run ID checked: `{report.run_id or 'unknown'}`",
        "",
    ]

    if report.checks_passed:
        lines.extend(["What already looks good:", ""])
        lines.extend(f"- {item}" for item in report.checks_passed)
        lines.append("")

    if report.issues:
        lines.extend(["What should be fixed or clarified next:", ""])
        lines.extend(f"- {item}" for item in report.issues)
        lines.append("")

    lines.extend(["Manual maintainer checks still needed:", ""])
    lines.extend(f"- {item}" for item in report.manual_checks)
    lines.append("")

    if report.verdict == "ready for review":
        lines.extend(
            [
                "Current maintainer note:",
                "",
                "- This means the artifact chain is reviewable, not that the repository is endorsing a broad benchmark claim yet.",
                "- Any performance interpretation still needs to stay tied to the submitted hardware, software stack, and stated limitations.",
            ]
        )
    else:
        lines.extend(
            [
                "Current maintainer note:",
                "",
                "- Until the points above are addressed, this should be treated as a local observation or draft submission rather than a benchmark claim.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    from scripts.review_result_submission import parse_args as parse_review_args

    args = parse_args(argv)
    review_arg_list: list[str] = []
    for name in ("submission_dir", "raw", "summary", "manifest"):
        value = getattr(args, name)
        if value:
            review_arg_list.extend([f"--{name.replace('_', '-')}", value])

    try:
        inputs = resolve_inputs(parse_review_args(review_arg_list))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = review_submission(inputs)
    comment_output = ensure_parent(default_output_path(args))
    comment_output.write_text(build_comment(report), encoding="utf-8")
    print(f"wrote review comment draft to {display_path(comment_output)}")

    if args.review_summary_output:
        summary_output = ensure_parent(
            Path(args.review_summary_output)
            if Path(args.review_summary_output).is_absolute()
            else ROOT / args.review_summary_output
        )
        summary_output.write_text(report_to_markdown(report), encoding="utf-8")
        print(f"wrote review summary to {display_path(summary_output)}")

    print(f"verdict: {report.verdict}")
    return 0 if report.verdict == "ready for review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
