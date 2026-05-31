from scripts.run_sanity_checks import run_scenarios


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
