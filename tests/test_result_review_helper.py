import shutil
from pathlib import Path

from scripts.review_result_submission import main as review_main
from scripts.review_result_submission import report_to_markdown, review_submission
from scripts.review_result_submission import ReviewInputs


EXAMPLE_DIR = Path("examples/results/fake-server-synthetic")


def make_submission_dir(tmp_path: Path) -> Path:
    submission_dir = tmp_path / "submission"
    (submission_dir / "raw").mkdir(parents=True)
    (submission_dir / "tables").mkdir()
    (submission_dir / "manifests").mkdir()
    shutil.copy2(EXAMPLE_DIR / "raw.jsonl", submission_dir / "raw" / "raw.jsonl")
    shutil.copy2(EXAMPLE_DIR / "summary.csv", submission_dir / "tables" / "summary.csv")
    shutil.copy2(
        EXAMPLE_DIR / "run_manifest.json",
        submission_dir / "manifests" / "run_manifest.json",
    )
    return submission_dir


def test_review_submission_accepts_example_artifacts() -> None:
    report = review_submission(
        ReviewInputs(
            raw=EXAMPLE_DIR / "raw.jsonl",
            summary=EXAMPLE_DIR / "summary.csv",
            manifest=EXAMPLE_DIR / "run_manifest.json",
            output=Path("unused.md"),
        )
    )

    assert report.verdict == "ready for review"
    assert report.run_id == "synthetic-fake-server-example"
    assert report.raw_records == 2
    assert report.summary_rows == 2
    markdown = report_to_markdown(report)
    assert "Automated Checks Passed" in markdown
    assert "summary CSV matches" in markdown


def test_review_submission_rejects_summary_mismatch(tmp_path: Path) -> None:
    summary = tmp_path / "summary.csv"
    summary.write_text("case_id,runs\nwrong_case,99\n", encoding="utf-8")

    report = review_submission(
        ReviewInputs(
            raw=EXAMPLE_DIR / "raw.jsonl",
            summary=summary,
            manifest=EXAMPLE_DIR / "run_manifest.json",
            output=tmp_path / "review.md",
        )
    )

    assert report.verdict == "exploratory only, not ready for benchmark discussion"
    assert any("summary.csv does not match" in issue for issue in report.issues)


def test_review_cli_accepts_submission_dir(tmp_path: Path) -> None:
    submission_dir = make_submission_dir(tmp_path)
    output = submission_dir / "review.md"

    assert review_main(["--submission-dir", str(submission_dir), "--output", str(output)]) == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "Verdict: `ready for review`" in text
