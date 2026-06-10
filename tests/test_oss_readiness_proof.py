from pathlib import Path

from scripts.run_oss_readiness_proof import build_report, report_to_markdown, StepResult


def test_build_report_tracks_nested_proof_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "oss-readiness-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="community_entry_proof",
            label="Generate community entry proof pack",
            status="passed",
            command="python scripts/run_community_entry_proof.py",
            log_path="results/oss-readiness-proof/logs/community_entry_proof.log",
            duration_seconds=1.2,
            artifacts=("results/oss-readiness-proof/packs/community-entry-proof/community_entry_proof.md",),
            output_excerpt=("PASS",),
        )
    ]

    report = build_report(output_dir, results)

    assert report["status"] == "PASS"
    assert "docs/maintenance/current-maintainer-readiness.md" in report["next_docs"]
    assert "docs/maintenance/community-entry-proof.md" in report["next_docs"]
    assert any(
        artifact["path"].endswith("community_entry_proof.md")
        for artifact in report["artifacts"]
    )
    assert any(
        artifact["path"].endswith("oss_readiness_proof.md")
        for artifact in report["artifacts"]
    )


def test_report_markdown_includes_gate_note(tmp_path: Path) -> None:
    output_dir = tmp_path / "oss-readiness-proof"
    output_dir.mkdir()
    results = [
        StepResult(
            step_id="submission_review_proof",
            label="Generate submission review proof pack",
            status="failed",
            command="python scripts/run_submission_review_proof.py",
            log_path="results/oss-readiness-proof/logs/submission_review_proof.log",
            duration_seconds=0.8,
            artifacts=(),
            output_excerpt=("example failure",),
        )
    ]

    report = build_report(output_dir, results)
    markdown = report_to_markdown(report)

    assert "What This Does Not Prove" in markdown
    assert "G9 or G10" in markdown
    assert "Failure Excerpts" in markdown
    assert "example failure" in markdown
