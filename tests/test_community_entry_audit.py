from pathlib import Path

from scripts.audit_community_entry import build_report, report_to_markdown


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "maintenance").mkdir(parents=True)
    (repo / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)

    for path in (
        "docs/ten_minute_smoke_run.md",
        "docs/contributor-self-check.md",
        "docs/smoke_feedback_starter.md",
        "docs/result_submission_starter.md",
        "docs/result_submission_example.md",
        "docs/community-feedback.md",
        "docs/maintenance/current-maintainer-readiness.md",
        ".github/ISSUE_TEMPLATE/smoke_run_feedback.yml",
        ".github/ISSUE_TEMPLATE/benchmark_result.yml",
    ):
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {target.name}\n", encoding="utf-8")

    (repo / "README.md").write_text(
        "\n".join(
            [
                "docs/contributor-self-check.md",
                "docs/smoke_feedback_starter.md",
                "docs/result_submission_starter.md",
                "docs/community-feedback.md",
                "docs/maintenance/current-maintainer-readiness.md",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".github" / "ISSUE_TEMPLATE" / "config.yml").write_text(
        "\n".join(
            [
                "blank_issues_enabled: false",
                "contact_links:",
                "  - name: Start with the 10-minute smoke run",
                "    url: https://github.com/example/repo/blob/main/docs/ten_minute_smoke_run.md",
                "  - name: Result submission example",
                "    url: https://github.com/example/repo/blob/main/docs/result_submission_example.md",
                "  - name: Community feedback expectations",
                "    url: https://github.com/example/repo/blob/main/docs/community-feedback.md",
                "  - name: Current maintainer readiness",
                "    url: https://github.com/example/repo/blob/main/docs/maintenance/current-maintainer-readiness.md",
            ]
        ),
        encoding="utf-8",
    )
    return repo


def test_build_report_passes_for_complete_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    report = build_report(repo)

    assert report["status"] == "PASS"
    assert report["summary"]["failed_checks"] == 0
    assert any(route["start"] == "docs/contributor-self-check.md" for route in report["route_map"])


def test_markdown_mentions_public_limits(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    readme = repo / "README.md"
    readme.write_text("docs/contributor-self-check.md\n", encoding="utf-8")

    report = build_report(repo)
    markdown = report_to_markdown(report, repo)

    assert report["status"] == "FAIL"
    assert "does not create independent public feedback" in markdown
