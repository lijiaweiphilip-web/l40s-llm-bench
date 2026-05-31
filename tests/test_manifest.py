import json

from l40s_bench.manifest import (
    artifact_record,
    build_manifest,
    manifest_to_markdown,
    write_manifest,
)


def test_manifest_records_artifact_hash(tmp_path) -> None:
    artifact = tmp_path / "summary.csv"
    artifact.write_text("case_id,runs\nchat_short,2\n", encoding="utf-8")

    record = artifact_record("summary_csv", artifact, required=True)
    manifest = build_manifest("test-run", [record])

    assert manifest["status"] == "complete"
    assert record["exists"] is True
    assert record["bytes"] > 0
    assert len(record["sha256"]) == 64
    assert "does not prove general" in manifest["scope_note"]


def test_manifest_reports_missing_required_artifacts(tmp_path) -> None:
    record = artifact_record("raw_jsonl", tmp_path / "missing.jsonl", required=True)
    manifest = build_manifest("test-run", [record])
    markdown = manifest_to_markdown(manifest)

    assert manifest["status"] == "missing-required-artifacts"
    assert manifest["missing_required_artifacts"] == ["raw_jsonl"]
    assert "`raw_jsonl`" in markdown


def test_write_manifest(tmp_path) -> None:
    output = tmp_path / "manifest.json"
    manifest = build_manifest("test-run", [])

    write_manifest(output, manifest)

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["run_id"] == "test-run"
