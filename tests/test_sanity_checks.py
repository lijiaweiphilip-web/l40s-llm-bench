from l40s_bench.errors import HTTP_ERROR
from scripts.run_sanity_checks import SanityScenario, check_record, run_scenarios


def test_sanity_check_suite_passes() -> None:
    records, failures = run_scenarios(repeats=1)

    assert not failures
    assert len(records) == 8
    assert {record["case_id"] for record in records} == {
        "baseline_stream",
        "concurrent_stream",
        "high_ttft_stream",
        "slow_tpot_stream",
        "server_error",
    }
    concurrent_records = [
        record for record in records if record["case_id"] == "concurrent_stream"
    ]
    assert {record["request_index"] for record in concurrent_records} == {0, 1, 2, 3}
    server_error = next(record for record in records if record["case_id"] == "server_error")
    assert server_error["error_kind"] == HTTP_ERROR


def test_timing_check_tolerates_scheduler_delay_but_rejects_bad_measurements() -> None:
    scenario = SanityScenario(name="timing", ttft_ms=80, tpot_ms=20, tokens=4)
    delayed = {
        "status": "ok",
        "output_token_events": 4,
        "ttft_ms": 500.0,
        "tpot_ms": 100.0,
    }
    assert check_record(delayed, scenario) == []

    invalid_records = (
        {**delayed, "ttft_ms": 10.0},
        {**delayed, "tpot_ms": -1.0},
        {**delayed, "ttft_ms": 5000.0},
    )
    for invalid in invalid_records:
        failures = check_record(invalid, scenario)
        assert failures
        assert any("timing" in failure for failure in failures)
