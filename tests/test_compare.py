from l40s_bench.compare import compare_summaries, has_regression


def base_row(**updates):
    row = {
        "case_id": "chat_short",
        "framework": "vllm",
        "model": "dry-run-model",
        "prompt_tokens": "128",
        "output_tokens": "128",
        "batch_size": "1",
        "concurrency": "1",
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


def test_compare_flags_latency_regression() -> None:
    rows = compare_summaries(
        [base_row()],
        [base_row(median_latency_ms="108.0")],
        max_regression_pct=5.0,
    )

    latency = next(row for row in rows if row["metric"] == "median_latency_ms")

    assert latency["status"] == "regression"
    assert has_regression(rows)


def test_compare_accepts_throughput_improvement() -> None:
    rows = compare_summaries(
        [base_row()],
        [base_row(avg_output_tokens_per_second="120.0")],
        max_regression_pct=5.0,
    )

    throughput = next(
        row for row in rows if row["metric"] == "avg_output_tokens_per_second"
    )

    assert throughput["status"] == "ok"
    assert not has_regression(rows)


def test_compare_flags_error_count_from_zero() -> None:
    rows = compare_summaries(
        [base_row(error_runs="0")],
        [base_row(error_runs="1")],
        max_regression_pct=5.0,
    )

    errors = next(row for row in rows if row["metric"] == "error_runs")

    assert errors["status"] == "regression"
    assert has_regression(rows)


def test_compare_flags_error_kind_regression() -> None:
    rows = compare_summaries(
        [base_row(http_error_runs="0")],
        [base_row(http_error_runs="1")],
        max_regression_pct=5.0,
    )

    errors = next(row for row in rows if row["metric"] == "http_error_runs")

    assert errors["status"] == "regression"
    assert has_regression(rows)
