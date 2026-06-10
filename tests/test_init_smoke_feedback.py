from pathlib import Path

from scripts.init_smoke_feedback import main as init_feedback_main


def test_init_smoke_feedback_scaffolds_both_path(tmp_path: Path) -> None:
    output_dir = tmp_path / "feedback"

    assert (
        init_feedback_main(
            [
                "--feedback-id",
                "first-user-probe",
                "--smoke-path",
                "both",
                "--output-dir",
                str(output_dir),
                "--commit",
                "abc1234",
            ]
        )
        == 0
    )

    readme = (output_dir / "README.md").read_text(encoding="utf-8")
    issue_body = (output_dir / "issue_body.md").read_text(encoding="utf-8")
    commands = (output_dir / "commands.sh").read_text(encoding="utf-8")

    assert "Smoke Feedback Starter" in readme
    assert "Dry run and fake-server sanity suite" in readme
    assert "raw/dry_run.jsonl" in readme
    assert "raw/sanity_checks.jsonl" in readme
    assert "python scripts/collect_env.py" in commands
    assert "python scripts/run_sanity_checks.py" in commands
    assert "`abc1234`" in issue_body
    assert "I understand this report is usability feedback" in issue_body
