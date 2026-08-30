from pathlib import Path

import pytest
import yaml

from l40s_bench.config import load_benchmark_matrix
from l40s_bench.profiles import load_workload_profiles, profiles_to_matrix, write_matrix


def test_workload_profiles_generate_valid_matrix(tmp_path: Path) -> None:
    profiles = load_workload_profiles("configs/workload_profiles.yaml")
    matrix = profiles_to_matrix(profiles)
    output = tmp_path / "matrix.yaml"

    write_matrix(output, matrix)
    loaded = load_benchmark_matrix(output)

    assert len(loaded["cases"]) == 5
    assert {case["case_id"] for case in loaded["cases"]} == {
        "chat_short",
        "summarization_medium",
        "code_generation",
        "long_context_qa",
        "burst_chat_concurrency",
    }
    burst = next(
        case for case in loaded["cases"] if case["case_id"] == "burst_chat_concurrency"
    )
    assert burst["concurrency"] == 4


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt_tokens", 1.5),
        ("output_tokens", True),
        ("batch_size", float("nan")),
        ("concurrency", 2.5),
    ],
)
def test_workload_profiles_reject_unsafe_count_coercion(
    tmp_path: Path, field: str, value: object
) -> None:
    profile = {
        "name": "invalid-profile",
        "prompt_tokens": 8,
        "output_tokens": 4,
        "batch_size": 1,
        "concurrency": 1,
    }
    profile[field] = value
    path = tmp_path / "profiles.yaml"
    path.write_text(yaml.safe_dump({"profiles": [profile]}), encoding="utf-8")

    with pytest.raises(ValueError, match=field):
        load_workload_profiles(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [("repeats", 1.5), ("timeout_seconds", True), ("timeout_seconds", float("inf"))],
)
def test_profiles_to_matrix_rejects_unsafe_default_coercion(
    tmp_path: Path, field: str, value: object
) -> None:
    path = tmp_path / "profiles.yaml"
    document = {
        "defaults": {
            "framework": "vllm",
            "model": "dry-run-model",
            "endpoint": "http://127.0.0.1:8000/v1/chat/completions",
            field: value,
        },
        "profiles": [
            {
                "name": "valid-profile",
                "prompt_tokens": 8,
                "output_tokens": 4,
                "batch_size": 1,
                "concurrency": 1,
            }
        ],
    }
    path.write_text(yaml.safe_dump(document), encoding="utf-8")

    profiles = load_workload_profiles(path)
    with pytest.raises(ValueError, match=field):
        profiles_to_matrix(profiles)
