from pathlib import Path

from scripts.review_smoke_feedback import main as review_main
from scripts.review_smoke_feedback import report_to_markdown, review_feedback, ReviewInputs


EXAMPLE_DIR = Path("examples/feedback/first-user-sample")


def test_review_smoke_feedback_accepts_example_feedback() -> None:
    report = review_feedback(
        ReviewInputs(
            issue_body=EXAMPLE_DIR / "issue_body.md",
            environment=EXAMPLE_DIR / "env" / "environment.json",
            output=Path("unused.md"),
        )
    )

    assert report.verdict == "ready for triage"
    assert report.triage_bucket == "Documentation friction"
    markdown = report_to_markdown(report)
    assert "Smoke Feedback Review Summary" in markdown
    assert "Suggested triage bucket" in markdown


def test_review_smoke_feedback_flags_placeholders(tmp_path: Path) -> None:
    issue_body = tmp_path / "issue_body.md"
    issue_body.write_text(
        "## Repository commit\n\n`abc1234`\n\n## Smoke-test path\n\n`Dry run only`\n\n## Commands run\n\n```bash\npython scripts/bench_openai_compatible.py --dry-run\n```\n\n## Environment\n\n- OS: <fill-me>\n\n## Expected artifacts\n\n- `raw/dry_run.jsonl`\n\n## What happened?\n\n- Worked / failed / partially worked: <fill-me>\n\n## Approximate time spent\n\n<fill-me>\n\n## Suggested improvements\n\n- <fill-me>\n\n## Safety checks\n\n- [x] I only used dry-run or local fake-server commands for this report.\n- [x] I removed API keys, bearer tokens, private endpoint URLs, private hostnames, job IDs, and confidential data.\n- [x] I understand this report is usability feedback, not a real GPU benchmark result.\n",
        encoding="utf-8",
    )

    report = review_feedback(
        ReviewInputs(issue_body=issue_body, environment=None, output=tmp_path / "out.md")
    )

    assert report.verdict == "needs missing detail"
    assert any("`<fill-me>` placeholders" in issue for issue in report.issues)


def test_review_smoke_feedback_cli_accepts_feedback_dir(tmp_path: Path) -> None:
    feedback_dir = tmp_path / "feedback"
    (feedback_dir / "env").mkdir(parents=True)
    issue_body = feedback_dir / "issue_body.md"
    issue_body.write_text(
        (EXAMPLE_DIR / "issue_body.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (feedback_dir / "env" / "environment.json").write_text(
        (EXAMPLE_DIR / "env" / "environment.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    output = feedback_dir / "smoke_feedback_review.md"

    assert review_main(["--feedback-dir", str(feedback_dir), "--output", str(output)]) == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "Verdict: `ready for triage`" in text
