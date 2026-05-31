from l40s_bench.config import load_benchmark_matrix, load_models


def test_default_configs_load() -> None:
    matrix = load_benchmark_matrix("configs/benchmark_matrix.yaml")
    models = load_models("configs/models.yaml")

    assert matrix["cases"]
    assert "dry-run-model" in models
    assert {case["model"] for case in matrix["cases"]} <= set(models)


def test_cases_have_positive_sizes() -> None:
    matrix = load_benchmark_matrix("configs/benchmark_matrix.yaml")

    for case in matrix["cases"]:
        assert case["prompt_tokens"] > 0
        assert case["output_tokens"] > 0
        assert case["batch_size"] > 0
        assert case["concurrency"] > 0
