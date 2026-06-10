from pathlib import Path

from scripts.build_result_review_comment import build_comment
from scripts.build_result_review_comment import main as comment_main
from scripts.review_result_submission import ReviewInputs, review_submission


EXAMPLE_DIR = Path("examples/results/fake-server-synthetic")


def make_ready_report():
    return review_submission(
        ReviewInputs(
            raw=EXAMPLE_DIR / "raw.jsonl",
            summary=EXAMPLE_DIR / "summary.csv",
            manifest=EXAMPLE_DIR / "run_manifest.json",
            output=Path("unused.md"),
        )
    )


def test_build_comment_for_ready_review_includes_positive_and_manual_checks() -> None:
    report = make_ready_report()

    comment = build_comment(report)

    assert "Automated verdict: `ready for review`" in comment
    assert "What already looks good:" in comment
    assert "Manual maintainer checks still needed:" in comment
    assert "not that the repository is endorsing a broad benchmark claim yet" in comment


def test_comment_cli_writes_comment_and_summary(tmp_path: Path) -> None:
    comment_output = tmp_path / "comment.md"
    summary_output = tmp_path / "summary.md"

    exit_code = comment_main(
        [
            "--raw",
            str(EXAMPLE_DIR / "raw.jsonl"),
            "--summary",
            str(EXAMPLE_DIR / "summary.csv"),
            "--manifest",
            str(EXAMPLE_DIR / "run_manifest.json"),
            "--output",
            str(comment_output),
            "--review-summary-output",
            str(summary_output),
        ]
    )

    assert exit_code == 0
    assert comment_output.exists()
    assert summary_output.exists()
    assert "ready for review" in comment_output.read_text(encoding="utf-8")
    assert "Result Review Summary" in summary_output.read_text(encoding="utf-8")
