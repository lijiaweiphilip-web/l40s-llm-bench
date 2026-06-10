from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = ROOT / "results"

WHAT_IT_PROVES = [
    "The repository can scaffold a first-user smoke-feedback packet in a clean CPU-only environment.",
    "Maintainers can review an example smoke-feedback note for completeness, scope, and redaction risk.",
    "Maintainers can generate a consistent public reply draft without inflating the note into benchmark evidence or external validation.",
]

WHAT_IT_DOES_NOT_PROVE = [
    "This pack does not create or claim genuinely independent external feedback.",
    "This pack is not benchmark evidence and does not replace issue #17 or a real hardware artifact bundle.",
    "The included example feedback packet is workflow-demo material only, not a countable G9 interaction.",
]

NEXT_DOCS = [
    "docs/smoke_feedback_starter.md",
    "docs/smoke_feedback_review.md",
    "docs/smoke_feedback_response_templates.md",
    "docs/feedback-triage-policy.md",
]


@dataclass(frozen=True)
class StepSpec:
    step_id: str
    label: str
    command: list[str]
    artifacts: tuple[Path, ...] = ()


@dataclass(frozen=True)
class StepResult:
    step_id: str
    label: str
    status: str
    command: str
    log_path: str
    duration_seconds: float
    artifacts: tuple[str, ...]
    output_excerpt: tuple[str, ...]


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def command_display(command: list[str]) -> str:
    return subprocess.list2cmdline([str(part) for part in command])


def tail_lines(text: str, limit: int = 8) -> list[str]:
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-limit:]


def write_log(path: Path, command: str, returncode: int, stdout: str, stderr: str) -> None:
    body = [
        f"Command: {command}",
        f"Exit code: {returncode}",
        "",
        "## STDOUT",
        stdout.rstrip(),
        "",
        "## STDERR",
        stderr.rstrip(),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body), encoding="utf-8")


def reset_output_dir(output_dir: Path) -> None:
    resolved = output_dir.resolve()
    results_root = RESULTS_ROOT.resolve()
    resolved.relative_to(results_root)
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def build_steps(output_dir: Path) -> list[StepSpec]:
    python = sys.executable
    env_json = output_dir / "env" / "environment.json"
    starter_dir = output_dir / "smoke-feedback-starter"
    review_dir = output_dir / "review"
    feedback_review = review_dir / "example_smoke_feedback_review.md"
    feedback_comment = review_dir / "example_smoke_feedback_comment.md"
    feedback_comment_summary = review_dir / "example_smoke_feedback_review_summary.md"

    return [
        StepSpec(
            "collect_environment",
            "Collect environment report",
            [python, "scripts/collect_env.py", "--output", str(env_json)],
            (env_json,),
        ),
        StepSpec(
            "pytest_feedback_tools",
            "Run smoke-feedback tool tests",
            [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/test_init_smoke_feedback.py",
                "tests/test_review_smoke_feedback.py",
                "tests/test_smoke_feedback_comment.py",
            ],
        ),
        StepSpec(
            "init_smoke_feedback",
            "Create starter directory for first-user smoke feedback",
            [
                python,
                "scripts/init_smoke_feedback.py",
                "--feedback-id",
                "feedback-triage-proof",
                "--smoke-path",
                "both",
                "--output-dir",
                str(starter_dir),
            ],
            (
                starter_dir / "README.md",
                starter_dir / "issue_body.md",
                starter_dir / "commands.sh",
            ),
        ),
        StepSpec(
            "review_example_smoke_feedback",
            "Review example smoke-feedback packet",
            [
                python,
                "scripts/review_smoke_feedback.py",
                "--feedback-dir",
                "examples/feedback/first-user-sample",
                "--output",
                str(feedback_review),
            ],
            (feedback_review,),
        ),
        StepSpec(
            "draft_example_smoke_feedback_comment",
            "Draft example maintainer comment for smoke feedback",
            [
                python,
                "scripts/build_smoke_feedback_comment.py",
                "--feedback-dir",
                "examples/feedback/first-user-sample",
                "--output",
                str(feedback_comment),
                "--review-summary-output",
                str(feedback_comment_summary),
            ],
            (feedback_comment, feedback_comment_summary),
        ),
    ]


def run_step(step: StepSpec, log_dir: Path) -> StepResult:
    command = command_display(step.command)
    started = time.monotonic()
    child_env = os.environ.copy()
    child_env.setdefault("PYTHONIOENCODING", "utf-8")
    completed = subprocess.run(
        step.command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=child_env,
        check=False,
    )
    duration = time.monotonic() - started
    log_path = log_dir / f"{step.step_id}.log"
    write_log(log_path, command, completed.returncode, completed.stdout, completed.stderr)
    excerpt = tuple(tail_lines("\n".join([completed.stdout, completed.stderr])))
    return StepResult(
        step_id=step.step_id,
        label=step.label,
        status="passed" if completed.returncode == 0 else "failed",
        command=command,
        log_path=repo_relative(log_path),
        duration_seconds=round(duration, 2),
        artifacts=tuple(repo_relative(path) for path in step.artifacts),
        output_excerpt=excerpt,
    )


def skipped_step(step: StepSpec) -> StepResult:
    return StepResult(
        step_id=step.step_id,
        label=step.label,
        status="skipped",
        command=command_display(step.command),
        log_path="",
        duration_seconds=0.0,
        artifacts=tuple(repo_relative(path) for path in step.artifacts),
        output_excerpt=(),
    )


def build_report(output_dir: Path, results: list[StepResult]) -> dict[str, Any]:
    failed = [result for result in results if result.status == "failed"]
    artifacts = []
    seen: set[str] = set()
    for result in results:
        for artifact in result.artifacts:
            if artifact and artifact not in seen:
                seen.add(artifact)
                artifacts.append({"path": artifact, "from_step": result.step_id})
    report_json = repo_relative(output_dir / "feedback_triage_proof.json")
    report_md = repo_relative(output_dir / "feedback_triage_proof.md")
    for path, source in ((report_json, "report"), (report_md, "report")):
        if path not in seen:
            artifacts.append({"path": path, "from_step": source})
    return {
        "schema_version": "0.1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS" if not failed else "FAIL",
        "output_dir": repo_relative(output_dir),
        "what_it_proves": WHAT_IT_PROVES,
        "what_it_does_not_prove": WHAT_IT_DOES_NOT_PROVE,
        "next_docs": NEXT_DOCS,
        "steps": [
            {
                "step_id": result.step_id,
                "label": result.label,
                "status": result.status,
                "command": result.command,
                "log_path": result.log_path,
                "duration_seconds": result.duration_seconds,
                "artifacts": list(result.artifacts),
                "output_excerpt": list(result.output_excerpt),
            }
            for result in results
        ],
        "artifacts": artifacts,
    }


def report_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Feedback Triage Proof Pack",
        "",
        f"Status: `{report['status']}`",
        f"Generated: `{report['generated_utc']}`",
        f"Output directory: `{report['output_dir']}`",
        "",
        "This is a maintainer-oriented CPU-only proof pack for the first-user smoke-feedback workflow in `l40s-llm-bench`.",
        "",
        "## What This Proves",
        "",
    ]
    lines.extend(f"- {item}" for item in report["what_it_proves"])
    lines.extend(["", "## What This Does Not Prove", ""])
    lines.extend(f"- {item}" for item in report["what_it_does_not_prove"])
    lines.extend(
        [
            "",
            "## Step Status",
            "",
            "| Step | Status | Duration (s) | Log | Artifacts |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for step in report["steps"]:
        log_path = step["log_path"] or "-"
        artifacts = ", ".join(f"`{path}`" for path in step["artifacts"]) or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    step["label"],
                    step["status"],
                    f"{step['duration_seconds']:.2f}",
                    f"`{log_path}`" if log_path != "-" else log_path,
                    artifacts,
                ]
            )
            + " |"
        )
    lines.extend(["", "## Next Docs To Open", ""])
    lines.extend(f"- `{path}`" for path in report["next_docs"])
    lines.extend(["", "## Artifact Index", ""])
    lines.extend(
        f"- `{artifact['path']}` (from `{artifact['from_step']}`)"
        for artifact in report["artifacts"]
    )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- A passing pack strengthens the public maintainer story for issue #12, but it does not count as independent external feedback by itself.",
        ]
    )
    failed_steps = [step for step in report["steps"] if step["status"] == "failed"]
    if failed_steps:
        lines.extend(["", "## Failure Excerpts", ""])
        for step in failed_steps:
            lines.append(f"### {step['label']}")
            lines.append("")
            if step["output_excerpt"]:
                lines.extend(f"- {line}" for line in step["output_excerpt"])
            else:
                lines.append("- See the step log for details.")
            lines.append("")
    return "\n".join(lines)


def write_report_files(output_dir: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    report_json = output_dir / "feedback_triage_proof.json"
    report_md = output_dir / "feedback_triage_proof.md"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(report_to_markdown(report), encoding="utf-8")
    return report_json, report_md


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="results/feedback-triage-proof",
        help="Directory where the feedback triage proof pack should be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    reset_output_dir(output_dir)
    log_dir = output_dir / "logs"

    steps = build_steps(output_dir)
    results: list[StepResult] = []
    failure_seen = False
    for index, step in enumerate(steps):
        result = run_step(step, log_dir)
        results.append(result)
        if result.status == "failed":
            failure_seen = True
            for pending_step in steps[index + 1 :]:
                results.append(skipped_step(pending_step))
            break

    if not failure_seen and len(results) < len(steps):
        for pending_step in steps[len(results) :]:
            results.append(skipped_step(pending_step))

    report = build_report(output_dir, results)
    report_json, report_md = write_report_files(output_dir, report)
    print(f"wrote feedback triage proof report to {repo_relative(report_md)}")
    print(f"wrote feedback triage proof metadata to {repo_relative(report_json)}")
    return 1 if failure_seen else 0


if __name__ == "__main__":
    raise SystemExit(main())
