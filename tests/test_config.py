from pathlib import Path

import pytest
import yaml

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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt_tokens", 1.5),
        ("output_tokens", float("nan")),
        ("batch_size", True),
        ("repeats", float("inf")),
        ("concurrency", 2.5),
    ],
)
def test_matrix_rejects_non_integral_or_nonfinite_counts(
    tmp_path: Path, field: str, value: object
) -> None:
    case = {
        "case_id": "invalid-count",
        "framework": "fake-server",
        "model": "dry-run-model",
        "prompt_tokens": 8,
        "output_tokens": 4,
        "batch_size": 1,
        "concurrency": 1,
        "repeats": 1,
    }
    case[field] = value
    path = tmp_path / "matrix.yaml"
    path.write_text(yaml.safe_dump({"cases": [case]}), encoding="utf-8")

    with pytest.raises(ValueError, match=field):
        load_benchmark_matrix(path)
