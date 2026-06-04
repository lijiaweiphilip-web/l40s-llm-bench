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
    "The repository installs in a clean CPU-only environment.",
    "The pytest suite passes alongside the public dry-run, summary, compatibility, and sanity-check paths.",
    "Packaged evidence bundles, sample GPU telemetry parsing, and the vLLM/L40S smoke profile all validate without requiring a GPU.",
]

WHAT_IT_DOES_NOT_PROVE = [
    "No real L40S, vLLM, model-server, or GPU benchmark result is included in this pack.",
    "This pack is not independent external feedback or community adoption evidence.",
    "Synthetic dry-run, fake-server, and GPU sample files remain tooling validation artifacts only.",
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
    dry_raw = output_dir / "raw" / "reviewer_dry_run.jsonl"
    tables_dir = output_dir / "tables"
    summary_csv = tables_dir / "summary.csv"
    summary_md = tables_dir / "summary.md"
    jsonl_md = tables_dir / "jsonl_compat.md"
    manifest_json = output_dir / "manifests" / "run_manifest.json"
    manifest_md = output_dir / "manifests" / "run_manifest.md"
    gpu_summary = tables_dir / "gpu_metrics_summary.json"
    vllm_raw = output_dir / "raw" / "vllm_l40s_profile_dry_run.jsonl"
    sanity_raw = output_dir / "raw" / "sanity_checks.jsonl"
    sanity_md = tables_dir / "sanity_checks.md"

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
                "reviewer-smoke-proof",
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
            "build_run_manifest",
            "Build run manifest",
            [
                python,
                "scripts/build_run_manifest.py",
                "--run-id",
                "reviewer-smoke-proof",
                "--config",
                "configs/benchmark_matrix.yaml",
                "--raw",
                str(dry_raw),
                "--summary",
                str(summary_csv),
                "--summary-md",
                str(summary_md),
                "--environment",
                str(env_json),
                "--output",
                str(manifest_json),
                "--markdown",
                str(manifest_md),
            ],
            (manifest_json, manifest_md),
        ),
        StepSpec(
            "validate_packaged_bundle",
            "Validate packaged evidence bundle example",
            [python, "scripts/validate_evidence_bundle.py", "examples/evidence-bundles"],
        ),
        StepSpec(
            "summarize_gpu_metrics",
            "Summarize sample GPU metrics",
            [
                python,
                "scripts/summarize_gpu_metrics.py",
                "examples/gpu-metrics/nvidia-smi-sample.csv",
                "--output",
                str(gpu_summary),
            ],
            (gpu_summary,),
        ),
        StepSpec(
            "vllm_dry_run",
            "Generate vLLM/L40S profile dry-run records",
            [
                python,
                "scripts/bench_openai_compatible.py",
                "--config",
                "configs/workloads/vllm-l40s-smoke.yaml",
                "--models-config",
                "configs/models.yaml",
                "--dry-run",
                "--stream",
                "--run-id",
                "reviewer-vllm-l40s-profile",
                "--output",
                str(vllm_raw),
            ],
            (vllm_raw,),
        ),
        StepSpec(
            "validate_vllm_profile",
            "Validate vLLM/L40S profile dry-run records",
            [python, "scripts/validate_result.py", str(vllm_raw)],
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
    report_json = repo_relative(output_dir / "reviewer_smoke_proof.json")
    report_md = repo_relative(output_dir / "reviewer_smoke_proof.md")
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
        "# Reviewer Smoke Proof Pack",
        "",
        f"Status: `{report['status']}`",
        f"Generated: `{report['generated_utc']}`",
        f"Output directory: `{report['output_dir']}`",
        "",
        "This is a reviewer-oriented CPU-only proof pack for `l40s-llm-bench`.",
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
    lines.extend(["", "## Artifact Index", ""])
    lines.extend(
        f"- `{artifact['path']}` (from `{artifact['from_step']}`)"
        for artifact in report["artifacts"]
    )
    lines.extend(["", "## Notes", ""])
    lines.append(
        "- A passing pack strengthens public reproducibility evidence, but it does not replace independent tester feedback or a real hardware artifact."
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
    report_json = output_dir / "reviewer_smoke_proof.json"
    report_md = output_dir / "reviewer_smoke_proof.md"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(report_to_markdown(report), encoding="utf-8")
    return report_json, report_md


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="results/reviewer-smoke-proof",
        help="Directory where the reviewer proof pack should be written.",
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
    print(f"wrote reviewer smoke proof report to {repo_relative(report_md)}")
    print(f"wrote reviewer smoke proof metadata to {repo_relative(report_json)}")
    return 1 if failure_seen else 0


if __name__ == "__main__":
    raise SystemExit(main())
