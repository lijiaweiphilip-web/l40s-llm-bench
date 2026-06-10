from pathlib import Path

from scripts.run_community_entry_proof import StepResult, build_report, report_to_markdown


def test_build_report_tracks_audit_and_starter_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "community-entry-proof"
    results = [
        StepResult(
            step_id="audit_community_entry",
            label="Audit README and issue-chooser newcomer routes",
            status="passed",
            command="python scripts/audit_community_entry.py --output-dir results/community-entry-proof/audit",
            log_path="results/community-entry-proof/logs/audit_community_entry.log",
            duration_seconds=0.83,
            artifacts=(
                "results/community-entry-proof/audit/community_entry_audit.md",
                "results/community-entry-proof/audit/community_entry_audit.json",
            ),
            output_excerpt=(),
        ),
        StepResult(
            step_id="init_submission_starter",
            label="Create starter directory for a future benchmark submission",
            status="passed",
            command="python scripts/init_result_submission.py --run-id community-entry-proof",
            log_path="results/community-entry-proof/logs/init_submission_starter.log",
            duration_seconds=0.74,
            artifacts=("results/community-entry-proof/submission-starter/README.md",),
            output_excerpt=(),
        ),
    ]

    report = build_report(output_dir, results)

    assert report["status"] == "PASS"
    assert "docs/contributor-self-check.md" in report["next_docs"]
    assert any(
        artifact["path"].endswith("community_entry_audit.md")
        for artifact in report["artifacts"]
    )
    assert any(
        artifact["path"].endswith("community_entry_proof.md")
        for artifact in report["artifacts"]
    )


def test_markdown_mentions_remaining_limits(tmp_path: Path) -> None:
    output_dir = tmp_path / "community-entry-proof"
    results = [
        StepResult(
            step_id="review_example_submission",
            label="Review example benchmark-result packet",
            status="failed",
            command="python scripts/review_result_submission.py --submission-dir examples/results/fake-server-synthetic",
            log_path="results/community-entry-proof/logs/review_example_submission.log",
            duration_seconds=1.05,
            artifacts=(),
            output_excerpt=("missing required artifact",),
        )
    ]

    report = build_report(output_dir, results)
    markdown = report_to_markdown(report)

    assert "independent public tester feedback" in markdown
    assert "missing required artifact" in markdown
