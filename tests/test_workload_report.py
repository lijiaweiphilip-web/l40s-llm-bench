from l40s_bench.profiles import load_workload_profiles
from l40s_bench.workload_report import error_breakdown, workload_report_to_markdown


def summary_row(case_id: str, **updates):
    row = {
        "case_id": case_id,
        "framework": "vllm",
        "model": "dry-run-model",
        "runs": "2",
        "ok_runs": "2",
        "error_runs": "0",
        "median_latency_ms": "100.0",
        "p95_latency_ms": "110.0",
        "median_ttft_ms": "20.0",
        "median_tpot_ms": "5.0",
        "avg_output_tokens_per_second": "100.0",
        "http_error_runs": "0",
        "timeout_runs": "0",
        "connection_error_runs": "0",
        "url_error_runs": "0",
        "other_error_runs": "0",
    }
    row.update(updates)
    return row


def test_workload_report_includes_profile_shapes_and_results() -> None:
    profiles = load_workload_profiles("configs/workload_profiles.yaml")
    markdown = workload_report_to_markdown(
        profiles,
        [summary_row("chat_short")],
    )

    assert "Profiles with summary rows: 1/5" in markdown
    assert "| chat_short | Short assistant-style interaction." in markdown
    assert "| chat_short | vllm | dry-run-model | 2 | 2 | 0 | 100.0" in markdown
    assert "| none |" in markdown
    assert "`summarization_medium`" in markdown
    assert "does not prove" in markdown


def test_error_breakdown_omits_zero_counts() -> None:
    assert error_breakdown(summary_row("chat_short")) == "none"
    assert (
        error_breakdown(summary_row("chat_short", http_error_runs="2"))
        == "http_error=2"
    )
