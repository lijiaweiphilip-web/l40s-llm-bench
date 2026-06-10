import json
from pathlib import Path

from scripts.build_evidence_bundle import main as build_bundle_main
from scripts.validate_evidence_bundle import validate_bundle


EXAMPLE_RAW = Path("examples/evidence-bundles/fake-server-smoke/raw-events.jsonl")
EXAMPLE_ENV = Path("examples/evidence-bundles/fake-server-smoke/environment.json")
EXAMPLE_CONFIG = Path("configs/fake_server_matrix.yaml")


def test_build_evidence_bundle_creates_valid_synthetic_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"

    exit_code = build_bundle_main(
        [
            "--run-id",
            "synthetic-fake-server-smoke",
            "--raw",
            str(EXAMPLE_RAW),
            "--config",
            str(EXAMPLE_CONFIG),
            "--environment",
            str(EXAMPLE_ENV),
            "--output-dir",
            str(output_dir),
            "--benchmark-command",
            "python scripts/run_sanity_checks.py --repeats 1",
            "--backend",
            "fake-openai-compatible",
            "--model",
            "fake-server-model",
            "--workload-profile",
            "fake-server-smoke",
            "--synthetic",
        ]
    )

    assert exit_code == 0
    report = validate_bundle(output_dir)
    assert report.ok
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["hardware"]["synthetic"] is True
    assert manifest["request_count"] == 2
    assert (output_dir / "limitations.md").exists()


def test_build_evidence_bundle_rejects_real_bundle_without_gpu_model(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"

    exit_code = build_bundle_main(
        [
            "--run-id",
            "realish-run",
            "--raw",
            str(EXAMPLE_RAW),
            "--config",
            str(EXAMPLE_CONFIG),
            "--environment",
            str(EXAMPLE_ENV),
            "--output-dir",
            str(output_dir),
            "--benchmark-command",
            "python scripts/run_vllm_smoke_profile.sh",
            "--backend",
            "vllm",
            "--model",
            "some-model",
            "--workload-profile",
            "vllm-l40s-smoke",
        ]
    )

    assert exit_code == 2
