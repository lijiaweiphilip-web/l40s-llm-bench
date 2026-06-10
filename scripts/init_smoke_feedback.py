from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SmokePathSpec:
    key: str
    label: str
    summary: str
    commands: str
    expected_artifacts: tuple[str, ...]


SMOKE_PATHS = {
    "dry-run": SmokePathSpec(
        key="dry-run",
        label="Dry run only",
        summary="Use this when the tester only ran the synthetic dry-run path.",
        commands=dedent(
            """\
            python -m pip install -r requirements-dev.txt
            python scripts/collect_env.py --output {env_output}
            python scripts/bench_openai_compatible.py --dry-run --run-id {feedback_id} --output {dry_raw}
            python scripts/summarize_results.py --input {dry_raw} --output-dir {tables_dir}
            """
        ),
        expected_artifacts=(
            "raw/dry_run.jsonl",
            "tables/summary.csv",
            "tables/summary.md",
            "env/environment.json",
        ),
    ),
    "sanity": SmokePathSpec(
        key="sanity",
        label="Fake-server sanity suite only",
        summary="Use this when the tester only ran the one-command fake-server sanity suite.",
        commands=dedent(
            """\
            python -m pip install -r requirements-dev.txt
            python scripts/collect_env.py --output {env_output}
            python scripts/run_sanity_checks.py --repeats 1 --output {sanity_raw} --report {sanity_md}
            """
        ),
        expected_artifacts=(
            "raw/sanity_checks.jsonl",
            "tables/sanity_checks.md",
            "env/environment.json",
        ),
    ),
    "both": SmokePathSpec(
        key="both",
        label="Dry run and fake-server sanity suite",
        summary="Use this when the tester ran the normal first-user path through both dry-run and sanity checks.",
        commands=dedent(
            """\
            python -m pip install -r requirements-dev.txt
            python scripts/collect_env.py --output {env_output}
            python scripts/bench_openai_compatible.py --dry-run --run-id {feedback_id} --output {dry_raw}
            python scripts/summarize_results.py --input {dry_raw} --output-dir {tables_dir}
            python scripts/run_sanity_checks.py --repeats 1 --output {sanity_raw} --report {sanity_md}
            """
        ),
        expected_artifacts=(
            "raw/dry_run.jsonl",
            "tables/summary.csv",
            "tables/summary.md",
            "raw/sanity_checks.jsonl",
            "tables/sanity_checks.md",
            "env/environment.json",
        ),
    ),
    "manual-fake-server": SmokePathSpec(
        key="manual-fake-server",
        label="Manual two-terminal fake-server path",
        summary="Use this when the tester followed the two-terminal fake-server walkthrough instead of the one-command sanity suite.",
        commands=dedent(
            """\
            python -m pip install -r requirements-dev.txt
            python scripts/collect_env.py --output {env_output}

            # Terminal 1
            python scripts/fake_openai_server.py --port 18000 --ttft-ms 120 --tpot-ms 25 --tokens 8

            # Terminal 2
            python scripts/bench_openai_compatible.py --config configs/fake_server_matrix.yaml --output {manual_raw} --stream
            python scripts/summarize_results.py --input {manual_raw} --output-dir {tables_dir}
            """
        ),
        expected_artifacts=(
            "raw/fake_server_streaming.jsonl",
            "tables/summary.csv",
            "tables/summary.md",
            "env/environment.json",
        ),
    ),
}


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


def render_commands(spec: SmokePathSpec, feedback_id: str, output_dir: Path) -> str:
    raw_dir = output_dir / "raw"
    tables_dir = output_dir / "tables"
    env_dir = output_dir / "env"
    commands = spec.commands.format(
        feedback_id=feedback_id,
        env_output=format_repo_path(env_dir / "environment.json"),
        dry_raw=format_repo_path(raw_dir / "dry_run.jsonl"),
        sanity_raw=format_repo_path(raw_dir / "sanity_checks.jsonl"),
        manual_raw=format_repo_path(raw_dir / "fake_server_streaming.jsonl"),
        sanity_md=format_repo_path(tables_dir / "sanity_checks.md"),
        tables_dir=format_repo_path(tables_dir),
    )
    return commands.rstrip()


def build_readme(output_dir: Path, feedback_id: str, spec: SmokePathSpec, commit: str) -> str:
    lines = [f"- `{path}`" for path in spec.expected_artifacts]
    commands = render_commands(spec, feedback_id, output_dir).splitlines()
    body = [
        "# Smoke Feedback Starter",
        "",
        "This directory is a starter kit for one first-user smoke-feedback report.",
        "",
        f"Feedback ID: `{feedback_id}`",
        f"Repository commit: `{commit}`",
        f"Smoke-test path: `{spec.label}`",
        "",
        spec.summary,
        "",
        "## Expected artifacts",
        "",
        *lines,
        "",
        "## Suggested commands",
        "",
        "```bash",
        *commands,
        "```",
        "",
        "## Before Posting",
        "",
        "- Replace placeholders in `issue_body.md`.",
        "- Remove private usernames, hostnames, endpoint URLs, cluster paths, job IDs, and tokens.",
        "- Keep this as usability feedback only, not GPU benchmark evidence.",
        "- If a command failed, keep the smallest useful redacted excerpt.",
        "",
        "## Related docs",
        "",
        "- `docs/first-user-smoke-test.md`",
        "- `docs/smoke_feedback_starter.md`",
        "- `docs/feedback-triage-policy.md`",
        "- `docs/community-feedback.md`",
    ]
    return "\n".join(body)


def build_issue_body(output_dir: Path, feedback_id: str, spec: SmokePathSpec, commit: str) -> str:
    lines = [f"- `{path}`" for path in spec.expected_artifacts]
    commands = render_commands(spec, feedback_id, output_dir).splitlines()
    body = [
        "## Repository commit",
        "",
        f"`{commit}`",
        "",
        "## Smoke-test path",
        "",
        f"`{spec.label}`",
        "",
        "## Commands run",
        "",
        "```bash",
        *commands,
        "```",
        "",
        "## Environment",
        "",
        "- OS: <fill-me>",
        "- Python version: <fill-me>",
        "- Shell or terminal: <fill-me>",
        "- Install method: <fill-me>",
        f"- Optional environment file: `{format_repo_path(output_dir / 'env' / 'environment.json')}`",
        "",
        "## Expected artifacts",
        "",
        *lines,
        "",
        "## What happened?",
        "",
        "- Worked / failed / partially worked: <fill-me>",
        "- First confusing step: <fill-me>",
        "- First failure, if any: <fill-me>",
        "",
        "## Approximate time spent",
        "",
        "<fill-me>",
        "",
        "## Short redacted output, if useful",
        "",
        "```text",
        "<fill-me>",
        "```",
        "",
        "## Suggested improvements",
        "",
        "- <fill-me>",
        "",
        "## Safety checks",
        "",
        "- [ ] I only used dry-run or local fake-server commands for this report.",
        "- [ ] I removed API keys, bearer tokens, private endpoint URLs, private hostnames, job IDs, and confidential data.",
        "- [ ] I understand this report is usability feedback, not a real GPU benchmark result.",
    ]
    return "\n".join(body)


def build_commands_sh(output_dir: Path, feedback_id: str, spec: SmokePathSpec) -> str:
    return dedent(
        f"""\
        #!/usr/bin/env bash
        set -euo pipefail

        {render_commands(spec, feedback_id, output_dir)}
        """
    )


def scaffold_feedback(output_dir: Path, feedback_id: str, spec: SmokePathSpec, commit: str) -> tuple[Path, ...]:
    raw_dir = output_dir / "raw"
    tables_dir = output_dir / "tables"
    env_dir = output_dir / "env"
    for directory in (output_dir, raw_dir, tables_dir, env_dir):
        directory.mkdir(parents=True, exist_ok=True)

    files = {
        output_dir / "README.md": build_readme(output_dir, feedback_id, spec, commit),
        output_dir / "issue_body.md": build_issue_body(output_dir, feedback_id, spec, commit),
        output_dir / "commands.sh": build_commands_sh(output_dir, feedback_id, spec),
        raw_dir / ".gitkeep": "",
        tables_dir / ".gitkeep": "",
        env_dir / ".gitkeep": "",
    }

    written: list[Path] = []
    for path, content in files.items():
        path.write_text(content, encoding="utf-8", newline="\n")
        written.append(path)
    return tuple(written)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a starter directory for first-user smoke feedback.",
    )
    parser.add_argument(
        "--feedback-id",
        required=True,
        help="Identifier for the feedback packet.",
    )
    parser.add_argument(
        "--smoke-path",
        choices=tuple(SMOKE_PATHS.keys()),
        default="both",
        help="Which smoke-test path the starter should target.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to create. Defaults to results/feedback/<feedback-id>.",
    )
    parser.add_argument(
        "--commit",
        default=detect_commit(),
        help="Commit hash to prefill in the issue body.",
    )
    return parser.parse_args(argv)


def resolve_output_dir(raw_output_dir: str | None, feedback_id: str) -> Path:
    if raw_output_dir is None:
        return ROOT / "results" / "feedback" / feedback_id
    path = Path(raw_output_dir)
    if path.is_absolute():
        return path
    return ROOT / path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = resolve_output_dir(args.output_dir, args.feedback_id)
    spec = SMOKE_PATHS[args.smoke_path]
    written = scaffold_feedback(
        output_dir=output_dir,
        feedback_id=args.feedback_id,
        spec=spec,
        commit=args.commit,
    )

    print(f"created smoke feedback starter at {format_repo_path(output_dir)}")
    for path in written:
        print(f"- {format_repo_path(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
