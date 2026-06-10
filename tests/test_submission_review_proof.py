from pathlib import Path

from scripts.run_submission_review_proof import build_report, report_to_markdown, StepResult


def test_build_report_tracks_submission_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "submission-review-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="review_example_submission",
            label="Review example submission pack",
            status="passed",
            command="python scripts/review_result_submission.py --raw examples/results/fake-server-synthetic/raw.jsonl",
            log_path="results/submission-review-proof/logs/review_example_submission.log",
            duration_seconds=0.42,
            artifacts=("results/submission-review-proof/review/example_result_review.md",),
            output_excerpt=("verdict: ready for review",),
        )
    ]

    report = build_report(output_dir, results)

    assert report["status"] == "PASS"
    assert "docs/result_review_quickstart.md" in report["next_docs"]
    assert any(
        artifact["path"].endswith("example_result_review.md")
        for artifact in report["artifacts"]
    )
    assert any(
        artifact["path"].endswith("submission_review_proof.md")
        for artifact in report["artifacts"]
    )


def test_report_markdown_includes_scope_note(tmp_path: Path) -> None:
    output_dir = tmp_path / "submission-review-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="draft_example_comment",
            label="Draft example maintainer comment",
            status="failed",
            command="python scripts/build_result_review_comment.py --raw examples/results/fake-server-synthetic/raw.jsonl",
            log_path="results/submission-review-proof/logs/draft_example_comment.log",
            duration_seconds=0.61,
            artifacts=(),
            output_excerpt=("example failure",),
        )
    ]

    report = build_report(output_dir, results)
    markdown = report_to_markdown(report)

    assert "What This Does Not Prove" in markdown
    assert "real hardware artifact" in markdown
    assert "Failure Excerpts" in markdown
    assert "example failure" in markdown
