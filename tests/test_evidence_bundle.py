import json
from pathlib import Path
import shutil

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
