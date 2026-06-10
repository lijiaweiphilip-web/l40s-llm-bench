from pathlib import Path

from scripts.build_smoke_feedback_comment import build_comment
from scripts.build_smoke_feedback_comment import main as comment_main
from scripts.build_smoke_feedback_comment import apply_override_verdict
from scripts.review_smoke_feedback import ReviewInputs, review_feedback


EXAMPLE_DIR = Path("examples/feedback/first-user-sample")


def example_report():
    return review_feedback(
        ReviewInputs(
            issue_body=EXAMPLE_DIR / "issue_body.md",
            environment=EXAMPLE_DIR / "env" / "environment.json",
            output=Path("unused.md"),
        )
    )


def test_build_comment_for_ready_feedback_includes_bucket_and_note() -> None:
    comment = build_comment(example_report())

    assert "Automated verdict: `ready for triage`" in comment
    assert "Suggested triage bucket: `Documentation friction`" in comment
    assert "usability feedback, not benchmark validation" in comment


def test_comment_cli_writes_outputs(tmp_path: Path) -> None:
    comment_output = tmp_path / "comment.md"
    summary_output = tmp_path / "summary.md"

    assert (
        comment_main(
            [
                "--feedback-dir",
                str(EXAMPLE_DIR),
                "--output",
                str(comment_output),
                "--review-summary-output",
                str(summary_output),
            ]
        )
        == 0
    )
    assert "ready for triage" in comment_output.read_text(encoding="utf-8")
    assert "Smoke Feedback Review Summary" in summary_output.read_text(encoding="utf-8")


def test_apply_override_verdict_adds_scope_issue() -> None:
    report = apply_override_verdict(example_report(), "out of scope for issue #12")

    assert report.verdict == "out of scope for issue #12"
    assert any("dry-run / local fake-server feedback scope" in issue for issue in report.issues)
