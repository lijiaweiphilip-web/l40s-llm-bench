from pathlib import Path

from scripts.run_feedback_triage_proof import build_report, report_to_markdown, StepResult


def test_build_report_tracks_feedback_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "feedback-triage-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="review_example_smoke_feedback",
            label="Review example smoke-feedback packet",
            status="passed",
            command="python scripts/review_smoke_feedback.py --feedback-dir examples/feedback/first-user-sample",
            log_path="results/feedback-triage-proof/logs/review_example_smoke_feedback.log",
            duration_seconds=0.41,
            artifacts=("results/feedback-triage-proof/review/example_smoke_feedback_review.md",),
            output_excerpt=("verdict: ready for triage",),
        )
    ]

    report = build_report(output_dir, results)

    assert report["status"] == "PASS"
    assert "docs/smoke_feedback_review.md" in report["next_docs"]
    assert any(
        artifact["path"].endswith("example_smoke_feedback_review.md")
        for artifact in report["artifacts"]
    )
    assert any(
        artifact["path"].endswith("feedback_triage_proof.md")
        for artifact in report["artifacts"]
    )


def test_report_markdown_includes_scope_note(tmp_path: Path) -> None:
    output_dir = tmp_path / "feedback-triage-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="draft_example_smoke_feedback_comment",
            label="Draft example maintainer comment for smoke feedback",
            status="failed",
            command="python scripts/build_smoke_feedback_comment.py --feedback-dir examples/feedback/first-user-sample",
            log_path="results/feedback-triage-proof/logs/draft_example_smoke_feedback_comment.log",
            duration_seconds=0.6,
            artifacts=(),
            output_excerpt=("example failure",),
        )
    ]

    report = build_report(output_dir, results)
    markdown = report_to_markdown(report)

    assert "What This Does Not Prove" in markdown
    assert "independent external feedback" in markdown
    assert "Failure Excerpts" in markdown
    assert "example failure" in markdown
