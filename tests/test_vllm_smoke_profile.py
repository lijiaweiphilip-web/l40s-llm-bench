from argparse import Namespace

from l40s_bench.config import load_benchmark_matrix, load_models
from scripts.bench_openai_compatible import run_benchmark


PROFILE_CONFIG = "configs/workloads/vllm-l40s-smoke.yaml"
MODELS_CONFIG = "configs/models.yaml"


def test_vllm_l40s_smoke_profile_config_loads() -> None:
    matrix = load_benchmark_matrix(PROFILE_CONFIG)
    models = load_models(MODELS_CONFIG)

    assert {case["case_id"] for case in matrix["cases"]} == {
        "vllm_l40s_smoke_short_stream",
        "vllm_l40s_smoke_concurrent_stream",
    }
    assert {case["model"] for case in matrix["cases"]} <= set(models)


def test_vllm_l40s_smoke_profile_dry_validates() -> None:
    args = Namespace(
        config=PROFILE_CONFIG,
        models_config=MODELS_CONFIG,
        run_id="test-vllm-l40s-smoke",
        limit_cases=None,
        dry_run=True,
        stream=True,
    )

    records = run_benchmark(args)

    assert len(records) == 3
    assert {record["dry_run"] for record in records} == {True}
    assert {record["framework"] for record in records} == {"vllm"}
    assert {record["model"] for record in records} == {"vllm-l40s-smoke-model"}
    assert all(record["ttft_ms"] is not None for record in records)
