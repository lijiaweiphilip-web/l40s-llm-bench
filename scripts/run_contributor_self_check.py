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
    "A first-time contributor can run the CPU-only repository path in a clean environment or GitHub Codespaces.",
    "The dry-run harness, fake-server sanity checks, and example evidence bundle validation all work without a GPU.",
    "The result-submission starter and maintainer-side review helper are wired well enough for a newcomer to follow the public docs.",
]

WHAT_IT_DOES_NOT_PROVE = [
    "No real L40S, vLLM, or public GPU benchmark result is created by this pack.",
    "This pack is not independent external feedback or community adoption evidence.",
    "Synthetic dry-run and example artifacts remain tooling-validation material only.",
]

NEXT_DOCS = [
    "docs/first-user-smoke-test.md",
    "docs/smoke_feedback_starter.md",
    "docs/result_submission_starter.md",
    "docs/result_review_quickstart.md",
    "docs/evidence_bundle_quickstart.md",
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
    raw_dir = output_dir / "raw"
    tables_dir = output_dir / "tables"
    review_dir = output_dir / "review"
    starter_dir = output_dir / "submission-starter"
    feedback_dir = output_dir / "smoke-feedback-starter"

    dry_raw = raw_dir / "contributor_dry_run.jsonl"
    summary_csv = tables_dir / "summary.csv"
    summary_md = tables_dir / "summary.md"
    jsonl_md = tables_dir / "jsonl_compat.md"
    sanity_raw = raw_dir / "sanity_checks.jsonl"
    sanity_md = tables_dir / "sanity_checks.md"
    example_review = review_dir / "example_result_review.md"
    example_comment = review_dir / "example_result_comment.md"
    example_summary = review_dir / "example_result_review_summary.md"

    return [
        StepSpec(
            "collect_environment",
            "Collect environment report",
            [python, "scripts/collect_env.py", "--output", str(env_json)],
            (env_json,),
        ),
        StepSpec(
            "pytest",
            "Run pytest suite",
            [python, "-m", "pytest", "-q"],
        ),
        StepSpec(
            "dry_run",
            "Generate CPU-only dry-run records",
            [
                python,
                "scripts/bench_openai_compatible.py",
                "--dry-run",
                "--run-id",
                "contributor-self-check",
                "--output",
                str(dry_raw),
            ],
            (dry_raw,),
        ),
        StepSpec(
            "summarize_dry_run",
            "Summarize dry-run records",
            [
                python,
                "scripts/summarize_results.py",
                "--input",
                str(dry_raw),
                "--output-dir",
                str(tables_dir),
            ],
            (summary_csv, summary_md),
        ),
        StepSpec(
            "check_jsonl_compat",
            "Check JSONL compatibility",
            [
                python,
                "scripts/check_jsonl_compat.py",
                "--input",
                str(dry_raw),
                "--output",
                str(jsonl_md),
            ],
            (jsonl_md,),
        ),
        StepSpec(
            "sanity_checks",
            "Run fake-server sanity checks",
            [
                python,
                "scripts/run_sanity_checks.py",
                "--repeats",
                "1",
                "--output",
                str(sanity_raw),
                "--report",
                str(sanity_md),
            ],
            (sanity_raw, sanity_md),
        ),
        StepSpec(
            "validate_example_bundle",
            "Validate packaged example evidence bundle",
            [python, "scripts/validate_evidence_bundle.py", "examples/evidence-bundles"],
        ),
        StepSpec(
            "review_example_submission",
            "Review example submission pack",
            [
                python,
                "scripts/review_result_submission.py",
                "--raw",
                "examples/results/fake-server-synthetic/raw.jsonl",
                "--summary",
                "examples/results/fake-server-synthetic/summary.csv",
                "--manifest",
                "examples/results/fake-server-synthetic/run_manifest.json",
                "--output",
                str(example_review),
            ],
            (example_review,),
        ),
        StepSpec(
            "draft_example_comment",
            "Draft example maintainer comment",
            [
                python,
                "scripts/build_result_review_comment.py",
                "--raw",
                "examples/results/fake-server-synthetic/raw.jsonl",
                "--summary",
                "examples/results/fake-server-synthetic/summary.csv",
                "--manifest",
                "examples/results/fake-server-synthetic/run_manifest.json",
                "--output",
                str(example_comment),
                "--review-summary-output",
                str(example_summary),
            ],
            (example_comment, example_summary),
        ),
        StepSpec(
            "init_smoke_feedback",
            "Create starter directory for first-user smoke feedback",
            [
                python,
                "scripts/init_smoke_feedback.py",
                "--feedback-id",
                "contributor-self-check",
                "--smoke-path",
                "both",
                "--output-dir",
                str(feedback_dir),
            ],
            (
                feedback_dir / "README.md",
                feedback_dir / "issue_body.md",
                feedback_dir / "commands.sh",
            ),
        ),
        StepSpec(
            "init_submission_starter",
            "Create starter directory for a future contributor result",
            [
                python,
                "scripts/init_result_submission.py",
                "--run-id",
                "contributor-self-check",
                "--output-dir",
                str(starter_dir),
            ],
            (
                starter_dir / "README.md",
                starter_dir / "issue_body.md",
                starter_dir / "commands.sh",
            ),
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
    report_json = repo_relative(output_dir / "contributor_self_check.json")
    report_md = repo_relative(output_dir / "contributor_self_check.md")
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
        "# Contributor Self-Check Pack",
        "",
        f"Status: `{report['status']}`",
        f"Generated: `{report['generated_utc']}`",
        f"Output directory: `{report['output_dir']}`",
        "",
        "This is a contributor-oriented CPU-only validation pack for `l40s-llm-bench`.",
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
            "- A passing pack is useful contributor-entry evidence, but it does not replace independent public feedback or a real hardware artifact.",
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
    report_json = output_dir / "contributor_self_check.json"
    report_md = output_dir / "contributor_self_check.md"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(report_to_markdown(report), encoding="utf-8")
    return report_json, report_md


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="results/contributor-self-check",
        help="Directory where the contributor self-check pack should be written.",
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
    print(f"wrote contributor self-check report to {repo_relative(report_md)}")
    print(f"wrote contributor self-check metadata to {repo_relative(report_json)}")
    return 1 if failure_seen else 0


if __name__ == "__main__":
    raise SystemExit(main())
