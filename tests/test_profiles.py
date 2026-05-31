from pathlib import Path

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
