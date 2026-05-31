from l40s_bench.compat import check_records


def legacy_record(**updates):
    record = {
        "schema_version": "0.1",
        "timestamp_utc": "2026-05-31T00:00:00+00:00",
        "run_id": "legacy",
        "case_id": "case",
        "framework": "vllm",
        "model": "dry-run-model",
        "prompt_tokens": 128,
        "output_tokens": 32,
        "batch_size": 1,
        "repeat_index": 0,
        "dry_run": True,
        "status": "ok",
        "latency_ms": 10.0,
        "output_tokens_per_second": 100.0,
    }
    record.update(updates)
    return record


def test_compat_accepts_missing_optional_fields() -> None:
    report = check_records([legacy_record()])

    assert report["valid_records"] == 1
    assert report["invalid_records"] == 0
    assert report["missing_optional_fields"]["ttft_ms"] == 1
    assert report["missing_optional_fields"]["error_kind"] == 1


def test_compat_reports_invalid_records() -> None:
    report = check_records([legacy_record(status="not-a-status")])

    assert report["valid_records"] == 0
    assert report["invalid_records"] == 1
    assert "invalid status" in report["invalid_messages"][0]["error"]
