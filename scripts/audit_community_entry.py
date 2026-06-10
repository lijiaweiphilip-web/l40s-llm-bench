from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]

ROUTE_DOCS = [
    {
        "need": "Understand the shortest benchmark harness path",
        "start": "docs/ten_minute_smoke_run.md",
        "why": "Guided first run before opening an issue.",
    },
    {
        "need": "Run one bounded CPU-only newcomer check",
        "start": "docs/contributor-self-check.md",
        "why": "Packages the contributor entry flow into one repeatable pack.",
    },
    {
        "need": "Prepare first-user smoke feedback",
        "start": "docs/smoke_feedback_starter.md",
        "why": "Scaffolds the issue #12 dry-run and fake-server feedback path.",
    },
    {
        "need": "Prepare a benchmark-result submission draft",
        "start": "docs/result_submission_starter.md",
        "why": "Scaffolds the future result-submission path before a public post.",
    },
    {
        "need": "See the maintainer-side public project status",
        "start": "docs/maintenance/current-maintainer-readiness.md",
        "why": "Explains what the repo does and does not claim right now.",
    },
]

README_REFERENCES = [
    "docs/contributor-self-check.md",
    "docs/smoke_feedback_starter.md",
    "docs/result_submission_starter.md",
    "docs/community-feedback.md",
    "docs/maintenance/current-maintainer-readiness.md",
]

REQUIRED_TEMPLATES = [
    ".github/ISSUE_TEMPLATE/smoke_run_feedback.yml",
    ".github/ISSUE_TEMPLATE/benchmark_result.yml",
]

REQUIRED_CONTACT_LINKS = {
    "Start with the 10-minute smoke run": "docs/ten_minute_smoke_run.md",
    "Result submission example": "docs/result_submission_example.md",
    "Community feedback expectations": "docs/community-feedback.md",
    "Current maintainer readiness": "docs/maintenance/current-maintainer-readiness.md",
}


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def extract_repo_path(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc != "github.com":
        return None
    marker = "/blob/main/"
    if marker not in parsed.path:
        return None
    return parsed.path.split(marker, 1)[1]


def load_issue_config(repo_root: Path) -> dict[str, Any]:
    config_path = repo_root / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def build_report(repo_root: Path) -> dict[str, Any]:
    readme_path = repo_root / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    issue_config = load_issue_config(repo_root)
    contact_links = {
        str(link.get("name", "")): extract_repo_path(str(link.get("url", "")))
        for link in issue_config.get("contact_links", [])
        if isinstance(link, dict)
    }

    checks: list[dict[str, str]] = []

    for route in ROUTE_DOCS:
        doc_path = repo_root / route["start"]
        checks.append(
            {
                "label": f"route doc exists: {route['start']}",
                "status": "pass" if doc_path.exists() else "fail",
                "details": route["why"],
            }
        )

    for path in README_REFERENCES:
        checks.append(
            {
                "label": f"README references {path}",
                "status": "pass" if path in readme_text else "fail",
                "details": "Newcomers should be able to discover this path from the README.",
            }
        )

    for path in REQUIRED_TEMPLATES:
        checks.append(
            {
                "label": f"issue template exists: {path}",
                "status": "pass" if (repo_root / path).exists() else "fail",
                "details": "The public issue chooser should keep the community entry path concrete.",
            }
        )

    for name, expected_path in REQUIRED_CONTACT_LINKS.items():
        actual_path = contact_links.get(name)
        checks.append(
            {
                "label": f"issue chooser link: {name}",
                "status": "pass" if actual_path == expected_path else "fail",
                "details": f"Expected `{expected_path}`; found `{actual_path or 'missing'}`.",
            }
        )

    failures = [check for check in checks if check["status"] != "pass"]
    return {
        "schema_version": "0.1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS" if not failures else "FAIL",
        "repo_root": str(repo_root.resolve()),
        "route_map": ROUTE_DOCS,
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failures),
            "failed_checks": len(failures),
        },
    }


def report_to_markdown(report: dict[str, Any], repo_root: Path) -> str:
    lines = [
        "# Community Entry Audit",
        "",
        f"Status: `{report['status']}`",
        f"Generated: `{report['generated_utc']}`",
        f"Repository root: `{repo_relative(Path(report['repo_root']), repo_root)}`",
        "",
        "This audit checks whether a first-time reader can find the main public entry paths without maintainer-only context.",
        "",
        "## Route Map",
        "",
        "| Need | Start Here | Why |",
        "| --- | --- | --- |",
    ]
    for route in report["route_map"]:
        lines.append(f"| {route['need']} | `{route['start']}` | {route['why']} |")
    lines.extend(
        [
            "",
            "## Check Summary",
            "",
            f"- Passed: `{report['summary']['passed_checks']}`",
            f"- Failed: `{report['summary']['failed_checks']}`",
            f"- Total: `{report['summary']['total_checks']}`",
            "",
            "## Detailed Checks",
            "",
            "| Check | Status | Details |",
            "| --- | --- | --- |",
        ]
    )
    for check in report["checks"]:
        lines.append(f"| {check['label']} | {check['status']} | {check['details']} |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- A passing audit means the public newcomer path is easier to discover and validate.",
            "- It does not create independent public feedback, benchmark adoption, or real GPU evidence by itself.",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit the public newcomer/community entry path for the repository."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to audit. Defaults to the current repository.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/community-entry-audit",
        help="Directory where markdown and JSON reports should be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root)
    if not repo_root.is_absolute():
        repo_root = (ROOT / repo_root).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(repo_root)
    report_json = output_dir / "community_entry_audit.json"
    report_md = output_dir / "community_entry_audit.md"
    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(report_to_markdown(report, repo_root), encoding="utf-8")
    print(f"wrote community entry audit to {repo_relative(report_md, ROOT)}")
    print(f"wrote community entry audit metadata to {repo_relative(report_json, ROOT)}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
