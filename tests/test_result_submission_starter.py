from pathlib import Path

from scripts.init_result_submission import main as starter_main
from scripts.init_result_submission import scaffold_submission


def test_scaffold_submission_creates_expected_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "starter"

    written = scaffold_submission(
        output_dir=output_dir,
        run_id="test-run",
        config_path="configs/workloads/vllm-l40s-smoke.yaml",
        commit="abc1234",
    )

    expected = {
        output_dir / "README.md",
        output_dir / "issue_body.md",
        output_dir / "commands.sh",
        output_dir / "raw" / ".gitkeep",
        output_dir / "tables" / ".gitkeep",
        output_dir / "manifests" / ".gitkeep",
    }
    assert set(written) == expected
    assert all(path.exists() for path in expected)

    issue_body = (output_dir / "issue_body.md").read_text(encoding="utf-8")
    assert "`abc1234`" in issue_body
    assert "configs/workloads/vllm-l40s-smoke.yaml" in issue_body
    assert "test-run" in issue_body
    assert "raw/raw.jsonl" in issue_body
    assert "manifests/run_manifest.json" in issue_body


def test_starter_cli_respects_explicit_output_dir(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.chdir(repo_root)

    output_dir = repo_root / "custom-output"
    exit_code = starter_main(
        [
            "--run-id",
            "demo-run",
            "--config",
            "configs/fake_server_matrix.yaml",
            "--output-dir",
            str(output_dir),
            "--commit",
            "deadbee",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "README.md").exists()
    readme = (output_dir / "README.md").read_text(encoding="utf-8")
    assert "demo-run" in readme
    assert "configs/fake_server_matrix.yaml" in readme
