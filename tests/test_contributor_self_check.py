from pathlib import Path

from scripts.run_contributor_self_check import build_report, report_to_markdown, StepResult


def test_build_report_tracks_artifacts_and_pass_state(tmp_path: Path) -> None:
    output_dir = tmp_path / "contributor-self-check"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="dry_run",
            label="Generate CPU-only dry-run records",
            status="passed",
            command="python scripts/bench_openai_compatible.py --dry-run",
            log_path="results/contributor-self-check/logs/dry_run.log",
            duration_seconds=1.23,
            artifacts=("results/contributor-self-check/raw/contributor_dry_run.jsonl",),
            output_excerpt=("wrote 3 records",),
        )
    ]

    report = build_report(output_dir, results)

    assert report["status"] == "PASS"
    assert "docs/result_submission_starter.md" in report["next_docs"]
    assert any(
        artifact["path"].endswith("contributor_dry_run.jsonl")
        for artifact in report["artifacts"]
    )
    assert any(
        artifact["path"].endswith("contributor_self_check.md")
        for artifact in report["artifacts"]
    )


def test_report_markdown_includes_next_docs_and_failure_excerpt(tmp_path: Path) -> None:
    output_dir = tmp_path / "contributor-self-check"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="review_example_submission",
            label="Review example submission pack",
            status="failed",
            command="python scripts/review_result_submission.py --submission-dir examples/results/fake-server-synthetic",
            log_path="results/contributor-self-check/logs/review_example_submission.log",
            duration_seconds=2.0,
            artifacts=(),
            output_excerpt=("missing required artifact",),
        )
    ]

    report = build_report(output_dir, results)
    markdown = report_to_markdown(report)

    assert "Next Docs To Open" in markdown
    assert "docs/first-user-smoke-test.md" in markdown
    assert "Failure Excerpts" in markdown
    assert "missing required artifact" in markdown
