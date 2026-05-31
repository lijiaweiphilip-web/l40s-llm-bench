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
