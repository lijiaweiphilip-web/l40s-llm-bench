import json
from pathlib import Path
import shutil

from scripts.bench_openai_compatible import dry_run_record
from scripts.validate_evidence_bundle import main as evidence_bundle_main
from scripts.validate_evidence_bundle import validate_bundle
from scripts.validate_evidence_bundle import validate_paths


EXAMPLE_BUNDLE = Path("examples/evidence-bundles/fake-server-smoke")


def copy_example_bundle(tmp_path: Path) -> Path:
    target = tmp_path / "fake-server-smoke"
    shutil.copytree(EXAMPLE_BUNDLE, target)
    return target


def test_packaged_fake_server_evidence_bundle_validates() -> None:
    report = validate_bundle(EXAMPLE_BUNDLE)

    assert report.ok


def test_evidence_bundle_parent_directory_discovers_bundle() -> None:
    report = validate_paths(["examples/evidence-bundles"])

    assert report.ok
    assert EXAMPLE_BUNDLE in report.bundles


def test_evidence_bundle_parent_directory_ignores_placeholder_dirs() -> None:
    report = validate_paths(["examples/evidence-bundles"])

    assert all("placeholder" not in str(bundle) for bundle in report.bundles)


def test_evidence_bundle_cli_accepts_packaged_example() -> None:
    assert evidence_bundle_main([str(EXAMPLE_BUNDLE)]) == 0


def test_evidence_bundle_rejects_missing_required_file(tmp_path: Path) -> None:
    bundle = copy_example_bundle(tmp_path)
    (bundle / "environment.json").unlink()

    report = validate_bundle(bundle)

    assert not report.ok
    assert any("missing required file environment.json" in issue.message for issue in report.issues)


def test_evidence_bundle_rejects_count_mismatch(tmp_path: Path) -> None:
    bundle = copy_example_bundle(tmp_path)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["request_count"] = 999
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = validate_bundle(bundle)

    assert not report.ok
    assert any("manifest.request_count" in issue.message for issue in report.issues)


def test_synthetic_bundle_rejects_unmarked_raw_record(tmp_path: Path) -> None:
    bundle = copy_example_bundle(tmp_path)
    raw_path = bundle / "raw-events.jsonl"
    records = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    records[0].pop("synthetic")
    raw_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    report = validate_bundle(bundle)

    assert not report.ok
    assert any("expected synthetic=True" in issue.message for issue in report.issues)


def test_synthetic_dry_run_bundle_validates_without_fake_server_marker(tmp_path: Path) -> None:
    bundle = tmp_path / "synthetic-dry-run"
    bundle.mkdir()
    case = {
        "case_id": "case",
        "framework": "vllm",
        "model": "vllm-l40s-smoke-model",
        "endpoint": "http://127.0.0.1:8000/v1/chat/completions",
        "prompt_tokens": 128,
        "output_tokens": 32,
        "batch_size": 1,
        "concurrency": 1,
    }
    record = dry_run_record(case, repeat_index=0, run_id="synthetic-dry-run")
    (bundle / "raw-events.jsonl").write_text(
        json.dumps(record) + "\n",
        encoding="utf-8",
    )
    (bundle / "README.md").write_text("synthetic dry run bundle\n", encoding="utf-8")
    (bundle / "config.json").write_text(
        json.dumps({"profile": "vllm-l40s-smoke"}),
        encoding="utf-8",
    )
    (bundle / "summary.json").write_text(
        json.dumps(
            {
                "benchmark_claim": False,
                "failure_count": 0,
                "request_count": 1,
                "run_id": "synthetic-dry-run",
                "schema_version": "0.1",
                "success_count": 1,
                "synthetic": True,
                "ttft_ms_summary": {"median": 26.28, "unit": "ms"},
                "tpot_ms_summary": {"median": 8.0, "unit": "ms"},
            }
        ),
        encoding="utf-8",
    )
    (bundle / "environment.json").write_text(
        json.dumps(
            {
                "gpu": {"available": False, "gpu_count": 0, "gpu_model": None, "synthetic": True},
                "notes": ["synthetic dry run"],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "synthetic-dry-run",
                "created_at": "2026-06-10T00:00:00Z",
                "project_version": "test",
                "git_commit": "abc1234",
                "benchmark_command": "python scripts/bench_openai_compatible.py --dry-run",
                "backend": "vllm",
                "endpoint_type": "openai-compatible",
                "model": "vllm-l40s-smoke-model",
                "workload_profile": "vllm-l40s-smoke",
                "request_count": 1,
                "success_count": 1,
                "failure_count": 0,
                "streaming": True,
                "ttft_ms_summary": {"median": 26.28, "unit": "ms"},
                "tpot_ms_summary": {"median": 8.0, "unit": "ms"},
                "raw_event_file": "raw-events.jsonl",
                "summary_file": "summary.json",
                "manifest_file": "manifest.json",
                "environment_file": "environment.json",
                "config_file": "config.json",
                "hardware": {"synthetic": True, "gpu_model": None, "gpu_count": 0},
                "limitations": ["synthetic dry-run bundle only"],
            }
        ),
        encoding="utf-8",
    )

    report = validate_bundle(bundle)

    assert report.ok
