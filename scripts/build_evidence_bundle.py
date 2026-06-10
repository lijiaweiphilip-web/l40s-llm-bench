from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.config import load_yaml
from l40s_bench.io import ensure_parent, read_jsonl
from l40s_bench.schema import validate_result
from scripts.collect_env import collect_environment


def run_command(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a reproducibility evidence bundle from benchmark artifacts.",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--raw", required=True, help="Raw JSONL result file.")
    parser.add_argument("--config", required=True, help="Benchmark config file.")
    parser.add_argument(
        "--environment",
        help="Optional environment JSON file. Use --collect-environment to generate one now.",
    )
    parser.add_argument(
        "--collect-environment",
        action="store_true",
        help="Collect environment metadata from the current machine when --environment is not provided.",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--benchmark-command", required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--endpoint-type", default="openai-compatible")
    parser.add_argument("--model", required=True)
    parser.add_argument("--workload-profile", required=True)
    parser.add_argument("--summary-csv", help="Optional summary CSV to include as an extra file.")
    parser.add_argument("--gpu-metrics-csv", help="Optional GPU metrics CSV to include.")
    parser.add_argument(
        "--gpu-metrics-summary",
        help="Optional GPU metrics summary JSON to include.",
    )
    parser.add_argument("--project-version", default=run_command(["git", "describe", "--tags", "--always"]) or "unknown")
    parser.add_argument("--git-commit", default=run_command(["git", "rev-parse", "HEAD"]) or "unknown")
    parser.add_argument("--gpu-model", help="GPU model for real runs.")
    parser.add_argument("--gpu-count", type=int, default=1)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument(
        "--limitation",
        action="append",
        default=[],
        help="Add one limitation line. Can be repeated.",
    )
    parser.add_argument(
        "--notes",
        action="append",
        default=[],
        help="Add one summary note line. Can be repeated.",
    )
    return parser.parse_args(argv)


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def summarize_metric(records: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [
        float(record[key])
        for record in records
        if record.get("status") == "ok" and record.get(key) is not None
    ]
    if not values:
        return {"median": None, "unit": "ms"}
    return {"median": round(median(values), 3), "unit": "ms"}


def load_and_validate_raw(path: Path) -> list[dict[str, Any]]:
    records = read_jsonl(path)
    for record in records:
        validate_result(record)
    return records


def write_json(path: Path, data: dict[str, Any]) -> None:
    ensure_parent(path).write_text(
        json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def copy_file(source: Path, target: Path) -> None:
    ensure_parent(target)
    shutil.copy2(source, target)


def build_summary(
    records: list[dict[str, Any]],
    run_id: str,
    synthetic: bool,
    notes: list[str],
) -> dict[str, Any]:
    success_count = sum(1 for record in records if record.get("status") == "ok")
    return {
        "benchmark_claim": False,
        "failure_count": len(records) - success_count,
        "latency_ms_summary": summarize_metric(records, "latency_ms"),
        "notes": notes,
        "request_count": len(records),
        "run_id": run_id,
        "schema_version": "0.1",
        "success_count": success_count,
        "synthetic": synthetic,
        "tpot_ms_summary": summarize_metric(records, "tpot_ms"),
        "ttft_ms_summary": summarize_metric(records, "ttft_ms"),
    }


def build_config(
    config_path: Path,
    workload_profile: str,
    model: str,
    backend: str,
) -> dict[str, Any]:
    loaded = load_yaml(config_path)
    return {
        "backend": backend,
        "model": model,
        "profile": workload_profile,
        "source_config_file": relative_to_root(config_path),
        "config": loaded,
    }


def build_environment(
    args: argparse.Namespace,
    environment_data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "gpu": {
            "available": not args.synthetic,
            "gpu_count": 0 if args.synthetic else args.gpu_count,
            "gpu_model": None if args.synthetic else args.gpu_model,
            "synthetic": args.synthetic,
        },
        "notes": [
            "Environment file generated for evidence bundle packaging.",
        ],
        "source_environment": environment_data,
    }


def build_manifest(
    args: argparse.Namespace,
    summary: dict[str, Any],
) -> dict[str, Any]:
    limitations = list(args.limitation)
    if not limitations:
        if args.synthetic:
            limitations = [
                "Synthetic artifact for bundle packaging and validator checks only.",
                "Not a real GPU benchmark, model benchmark, or hardware comparison.",
            ]
        else:
            limitations = [
                "First public smoke artifact intended to validate evidence collection and packaging.",
                "Not a leaderboard result or comprehensive performance claim.",
            ]

    return {
        "backend": args.backend,
        "benchmark_command": args.benchmark_command,
        "config_file": "config.json",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "endpoint_type": args.endpoint_type,
        "environment_file": "environment.json",
        "failure_count": summary["failure_count"],
        "git_commit": args.git_commit,
        "hardware": {
            "gpu_count": 0 if args.synthetic else args.gpu_count,
            "gpu_model": None if args.synthetic else args.gpu_model,
            "synthetic": args.synthetic,
        },
        "limitations": limitations,
        "manifest_file": "manifest.json",
        "model": args.model,
        "project_version": args.project_version,
        "raw_event_file": "raw-events.jsonl",
        "request_count": summary["request_count"],
        "run_id": args.run_id,
        "streaming": any(record.get("ttft_ms") is not None for record in load_and_validate_raw(Path(args.raw))),
        "success_count": summary["success_count"],
        "summary_file": "summary.json",
        "tpot_ms_summary": summary["tpot_ms_summary"],
        "ttft_ms_summary": summary["ttft_ms_summary"],
        "workload_profile": args.workload_profile,
    }


def build_readme(args: argparse.Namespace) -> str:
    if args.synthetic:
        scope = (
            "This bundle is synthetic and exists to validate packaging or review "
            "workflow only. It is not a real GPU benchmark or hardware claim."
        )
    else:
        scope = (
            "This bundle is a first public smoke artifact intended to validate "
            "the evidence collection workflow. It is not a leaderboard result "
            "or broad performance claim."
        )
    return (
        "# Evidence Bundle\n\n"
        f"Run ID: `{args.run_id}`\n\n"
        f"{scope}\n\n"
        "Included files should stay together so reviewers can inspect the raw "
        "events, summary, environment notes, and limitations as one artifact set.\n"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    raw_path = Path(args.raw)
    config_path = Path(args.config)
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    if not args.synthetic and not args.gpu_model:
        print("ERROR: --gpu-model is required for non-synthetic bundles", file=sys.stderr)
        return 2

    if args.environment:
        environment_source = json.loads(Path(args.environment).read_text(encoding="utf-8"))
    elif args.collect_environment:
        environment_source = collect_environment()
    else:
        print("ERROR: provide --environment or --collect-environment", file=sys.stderr)
        return 2

    records = load_and_validate_raw(raw_path)
    summary_notes = list(args.notes)
    if not summary_notes:
        summary_notes = [
            "Generated by scripts/build_evidence_bundle.py.",
        ]
    summary = build_summary(records, args.run_id, args.synthetic, summary_notes)
    config = build_config(config_path, args.workload_profile, args.model, args.backend)
    environment = build_environment(args, environment_source)
    manifest = build_manifest(args, summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    copy_file(raw_path, output_dir / "raw-events.jsonl")
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "config.json", config)
    write_json(output_dir / "environment.json", environment)
    write_json(output_dir / "manifest.json", manifest)
    (output_dir / "README.md").write_text(build_readme(args), encoding="utf-8")

    if args.summary_csv:
        copy_file(Path(args.summary_csv), output_dir / "summary.csv")
    if args.gpu_metrics_csv:
        copy_file(Path(args.gpu_metrics_csv), output_dir / "gpu-metrics.csv")
    if args.gpu_metrics_summary:
        copy_file(Path(args.gpu_metrics_summary), output_dir / "gpu-metrics-summary.json")

    limitations_path = output_dir / "limitations.md"
    limitations = manifest["limitations"]
    limitations_path.write_text(
        "# Limitations\n\n" + "\n".join(f"- {item}" for item in limitations) + "\n",
        encoding="utf-8",
    )

    print(f"built evidence bundle at {relative_to_root(output_dir)}")
    print("validate with:")
    print(f"python scripts/validate_evidence_bundle.py {relative_to_root(output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
