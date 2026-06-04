from pathlib import Path

from scripts.run_reviewer_smoke_pack import build_report, report_to_markdown, StepResult


def test_build_report_marks_failure_and_indexes_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "reviewer-smoke-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="pytest",
            label="Run pytest suite",
            status="passed",
            command="python -m pytest -q",
            log_path="results/reviewer-smoke-proof/logs/pytest.log",
            duration_seconds=3.21,
            artifacts=(),
            output_excerpt=("36 passed",),
        ),
        StepResult(
            step_id="dry_run",
            label="Generate CPU-only dry-run records",
            status="failed",
            command="python scripts/bench_openai_compatible.py --dry-run",
            log_path="results/reviewer-smoke-proof/logs/dry_run.log",
            duration_seconds=1.0,
            artifacts=("results/reviewer-smoke-proof/raw/reviewer_dry_run.jsonl",),
            output_excerpt=("example failure",),
        ),
    ]

    report = build_report(output_dir, results)

    assert report["status"] == "FAIL"
    assert any(
        artifact["path"].endswith("reviewer_dry_run.jsonl")
        for artifact in report["artifacts"]
    )
    assert any(
        artifact["path"].endswith("reviewer_smoke_proof.md")
        for artifact in report["artifacts"]
    )


def test_report_markdown_includes_scope_and_failure_excerpt(tmp_path: Path) -> None:
    output_dir = tmp_path / "reviewer-smoke-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="pytest",
            label="Run pytest suite",
            status="failed",
            command="python -m pytest -q",
            log_path="results/reviewer-smoke-proof/logs/pytest.log",
            duration_seconds=2.5,
            artifacts=(),
            output_excerpt=("E assert 1 == 2",),
        )
    ]

    report = build_report(output_dir, results)
    markdown = report_to_markdown(report)

    assert "What This Does Not Prove" in markdown
    assert "independent external feedback" in markdown
    assert "Failure Excerpts" in markdown
    assert "E assert 1 == 2" in markdown
