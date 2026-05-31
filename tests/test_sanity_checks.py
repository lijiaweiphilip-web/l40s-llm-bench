from scripts.run_sanity_checks import run_scenarios


def test_sanity_check_suite_passes() -> None:
    records, failures = run_scenarios(repeats=1)

    assert not failures
    assert len(records) == 4
    assert {record["case_id"] for record in records} == {
        "baseline_stream",
        "high_ttft_stream",
        "slow_tpot_stream",
        "server_error",
    }
