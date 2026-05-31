from l40s_bench.errors import HTTP_ERROR
from l40s_bench.summary import summarize_records
from scripts.bench_openai_compatible import dry_run_record


def test_summary_groups_records() -> None:
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
    records = [
        dry_run_record(case, repeat_index=0, run_id="test-run"),
        dry_run_record(case, repeat_index=1, run_id="test-run"),
    ]

    rows = summarize_records(records)

    assert len(rows) == 1
    assert rows[0]["runs"] == 2
    assert rows[0]["ok_runs"] == 2
    assert rows[0]["median_latency_ms"] is not None


def test_summary_counts_error_kinds() -> None:
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
    ok_record = dry_run_record(case, repeat_index=0, run_id="test-run")
    error_record = dry_run_record(case, repeat_index=1, run_id="test-run")
    error_record.update(
        {
            "status": "error",
            "error": "HTTP 500: synthetic",
            "error_kind": HTTP_ERROR,
            "http_status": 500,
        }
    )

    rows = summarize_records([ok_record, error_record])

    assert rows[0]["runs"] == 2
    assert rows[0]["ok_runs"] == 1
    assert rows[0]["error_runs"] == 1
    assert rows[0]["http_error_runs"] == 1
    assert rows[0]["timeout_runs"] == 0
    assert rows[0]["other_error_runs"] == 0
