import json
from pathlib import Path

from l40s_bench.schema import validate_result
from scripts.bench_openai_compatible import dry_run_record
from scripts.validate_result import main as validate_result_main
from scripts.validate_result import validate_paths


EXAMPLE_RESULT = Path("examples/results/fake-server-synthetic/raw.jsonl")


def test_dry_run_record_matches_schema() -> None:
    case = {
        "case_id": "case",
        "framework": "vllm",
        "model": "dry-run-model",
        "endpoint": "http://127.0.0.1:8000/v1/chat/completions",
        "prompt_tokens": 128,
        "output_tokens": 32,
        "batch_size": 1,
        "concurrency": 1,
    }

    record = dry_run_record(case, repeat_index=0, run_id="test-run")

    validate_result(record)
    assert record["dry_run"] is True
    assert record["synthetic"] is True
    assert record["benchmark_claim"] is False
    assert record["status"] == "ok"
    assert record["concurrency"] == 1
    assert record["request_index"] == 0


def test_legacy_record_gets_optional_streaming_fields() -> None:
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

    validate_result(record)

    assert record["ttft_ms"] is None
    assert record["tpot_ms"] is None
    assert record["output_token_events"] is None
    assert record["concurrency"] == 1
    assert record["request_index"] == 0
    assert record["error_kind"] is None
    assert record["http_status"] is None


def test_synthetic_fake_server_example_validates() -> None:
    report = validate_paths([EXAMPLE_RESULT], require_synthetic_fake_server=True)

    assert report.ok
    assert report.records == 2


def test_validator_rejects_unmarked_synthetic_example(tmp_path: Path) -> None:
    case = {
        "case_id": "case",
        "framework": "fake-openai-compatible",
        "model": "fake-server-model",
        "endpoint": "http://127.0.0.1:18000/v1/chat/completions",
        "prompt_tokens": 128,
        "output_tokens": 32,
        "batch_size": 1,
        "concurrency": 1,
    }
    record = dry_run_record(case, repeat_index=0, run_id="test-run")
    path = tmp_path / "unmarked.jsonl"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    report = validate_paths([path], require_synthetic_fake_server=True)

    assert not report.ok
    assert any("synthetic" in issue.message for issue in report.issues)


def test_validator_cli_accepts_packaged_example() -> None:
    assert (
        validate_result_main(
            [str(EXAMPLE_RESULT), "--require-synthetic-fake-server"]
        )
        == 0
    )
