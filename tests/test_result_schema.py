from l40s_bench.schema import validate_result
from scripts.bench_openai_compatible import dry_run_record


def test_dry_run_record_matches_schema() -> None:
    case = {
        "case_id": "case",
        "framework": "vllm",
        "model": "dry-run-model",
        "endpoint": "http://127.0.0.1:8000/v1/chat/completions",
        "prompt_tokens": 128,
        "output_tokens": 32,
        "batch_size": 1,
    }

    record = dry_run_record(case, repeat_index=0, run_id="test-run")

    validate_result(record)
    assert record["dry_run"] is True
    assert record["status"] == "ok"
