from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from textwrap import dedent
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]


def format_repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def detect_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "<fill-me>"
    return result.stdout.strip() or "<fill-me>"


def build_readme(
    run_id: str,
    config_path: str,
    raw_path: Path,
    summary_csv_path: Path,
    summary_md_path: Path,
    manifest_json_path: Path,
    manifest_md_path: Path,
) -> str:
    return dedent(
        f"""\
        # Result Submission Starter

        This directory is a starter kit for one reproducible benchmark
        submission.

        Run ID: `{run_id}`

        ## Put artifacts here

        - Raw JSONL: `{format_repo_path(raw_path)}`
        - Summary CSV: `{format_repo_path(summary_csv_path)}`
        - Summary Markdown: `{format_repo_path(summary_md_path)}`
        - Run manifest JSON: `{format_repo_path(manifest_json_path)}`
        - Run manifest Markdown: `{format_repo_path(manifest_md_path)}`

        ## Suggested commands

        ```bash
        python scripts/summarize_results.py --input {format_repo_path(raw_path)} --output-dir {format_repo_path(summary_csv_path.parent)}
        python scripts/build_run_manifest.py --run-id {run_id} --config {config_path} --raw {format_repo_path(raw_path)} --summary {format_repo_path(summary_csv_path)} --summary-md {format_repo_path(summary_md_path)} --output {format_repo_path(manifest_json_path)} --markdown {format_repo_path(manifest_md_path)}
        python scripts/validate_result.py {format_repo_path(raw_path.parent)}
        ```

        ## Review checklist

        - Replace placeholders in `issue_body.md` before posting.
        - Confirm secrets, private endpoints, and hostnames are removed.
        - State what readers should not infer from the run.
        - Link the exact config used for the run.
        - If this is synthetic or dry-run-only, say that explicitly.

        ## Related docs

        - `docs/result_submission_starter.md`
        - `docs/result_submission_example.md`
        - `docs/result_review_checklist.md`
        - `docs/community-feedback.md`
        """
    )


def build_issue_body(
    run_id: str,
    commit: str,
    config_path: str,
    raw_path: Path,
    summary_csv_path: Path,
    summary_md_path: Path,
    manifest_json_path: Path,
    manifest_md_path: Path,
) -> str:
    return dedent(
        f"""\
        ## Result summary

        Replace this paragraph with a short, concrete description of what was
        measured and what you want reviewed.

        ## Repository commit

        `{commit}`

        ## Exact commands

        ```bash
        python scripts/summarize_results.py --input {format_repo_path(raw_path)} --output-dir {format_repo_path(summary_csv_path.parent)}
        python scripts/build_run_manifest.py --run-id {run_id} --config {config_path} --raw {format_repo_path(raw_path)} --summary {format_repo_path(summary_csv_path)} --summary-md {format_repo_path(summary_md_path)} --output {format_repo_path(manifest_json_path)} --markdown {format_repo_path(manifest_md_path)}
        python scripts/validate_result.py {format_repo_path(raw_path.parent)}
        ```

        ## Configuration

        - Benchmark config: `{config_path}`
        - Run ID: `{run_id}`
        - Endpoint: <fill-me>
        - Repeats: <fill-me>
        - Concurrency: <fill-me>
        - Output tokens target: <fill-me>

        ## Serving stack

        - Server: <fill-me>
        - Version: <fill-me>
        - Model: <fill-me>
        - Streaming: <fill-me>
        - Batch/concurrency settings: <fill-me>

        ## Hardware and runtime

        - GPU: <fill-me>
        - Driver/runtime: <fill-me>
        - CPU/memory: <fill-me>
        - Deployment context: <fill-me>
        - Power/thermal/shared constraints: <fill-me>

        ## Result artifacts

        - Raw JSONL: `{format_repo_path(raw_path)}`
        - Summary CSV: `{format_repo_path(summary_csv_path)}`
        - Summary Markdown: `{format_repo_path(summary_md_path)}`
        - Run manifest JSON: `{format_repo_path(manifest_json_path)}`
        - Run manifest Markdown: `{format_repo_path(manifest_md_path)}`

        ## Limitations

        - Single environment unless otherwise noted
        - Not a model quality evaluation
        - Replace with the smallest honest caveat for this run
        """
    )


def build_commands_sh(
    run_id: str,
    config_path: str,
    raw_path: Path,
    summary_csv_path: Path,
    summary_md_path: Path,
    manifest_json_path: Path,
    manifest_md_path: Path,
) -> str:
    return dedent(
        f"""\
        #!/usr/bin/env bash
        set -euo pipefail

        python scripts/summarize_results.py --input {format_repo_path(raw_path)} --output-dir {format_repo_path(summary_csv_path.parent)}
        python scripts/build_run_manifest.py --run-id {run_id} --config {config_path} --raw {format_repo_path(raw_path)} --summary {format_repo_path(summary_csv_path)} --summary-md {format_repo_path(summary_md_path)} --output {format_repo_path(manifest_json_path)} --markdown {format_repo_path(manifest_md_path)}
        python scripts/validate_result.py {format_repo_path(raw_path.parent)}
        """
    )


def scaffold_submission(
    output_dir: Path,
    run_id: str,
    config_path: str,
    commit: str,
) -> tuple[Path, ...]:
    raw_dir = output_dir / "raw"
    tables_dir = output_dir / "tables"
    manifests_dir = output_dir / "manifests"
    for directory in (output_dir, raw_dir, tables_dir, manifests_dir):
        directory.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / "raw.jsonl"
    summary_csv_path = tables_dir / "summary.csv"
    summary_md_path = tables_dir / "summary.md"
    manifest_json_path = manifests_dir / "run_manifest.json"
    manifest_md_path = manifests_dir / "run_manifest.md"

    files = {
        output_dir / "README.md": build_readme(
            run_id,
            config_path,
            raw_path,
            summary_csv_path,
            summary_md_path,
            manifest_json_path,
            manifest_md_path,
        ),
        output_dir / "issue_body.md": build_issue_body(
            run_id,
            commit,
            config_path,
            raw_path,
            summary_csv_path,
            summary_md_path,
            manifest_json_path,
            manifest_md_path,
        ),
        output_dir / "commands.sh": build_commands_sh(
            run_id,
            config_path,
            raw_path,
            summary_csv_path,
            summary_md_path,
            manifest_json_path,
            manifest_md_path,
        ),
        raw_dir / ".gitkeep": "",
        tables_dir / ".gitkeep": "",
        manifests_dir / ".gitkeep": "",
    }

    written: list[Path] = []
    for path, content in files.items():
        path.write_text(content, encoding="utf-8", newline="\n")
        written.append(path)
    return tuple(written)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a starter directory for benchmark result submission.",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Identifier for the benchmark run.",
    )
    parser.add_argument(
        "--config",
        default="configs/workloads/vllm-l40s-smoke.yaml",
        help="Config path to reference in the starter files.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to create. Defaults to results/submissions/<run-id>.",
    )
    parser.add_argument(
        "--commit",
        default=detect_commit(),
        help="Commit hash to prefill in the issue body.",
    )
    return parser.parse_args(argv)


def resolve_output_dir(raw_output_dir: str | None, run_id: str) -> Path:
    if raw_output_dir is None:
        return ROOT / "results" / "submissions" / run_id
    path = Path(raw_output_dir)
    if path.is_absolute():
        return path
    return ROOT / path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = resolve_output_dir(args.output_dir, args.run_id)
    written = scaffold_submission(
        output_dir=output_dir,
        run_id=args.run_id,
        config_path=args.config,
        commit=args.commit,
    )

    print(f"created result submission starter at {format_repo_path(output_dir)}")
    for path in written:
        print(f"- {format_repo_path(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
