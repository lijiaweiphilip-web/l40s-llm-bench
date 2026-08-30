from argparse import Namespace
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from l40s_bench.config import load_benchmark_matrix, load_models
from scripts.bench_openai_compatible import ensure_real_mode_allowed, run_benchmark
from scripts.validate_l40s_contract import validate_contract


def _args(config: str) -> Namespace:
    return Namespace(
        config=config,
        models_config="configs/models.yaml",
        run_id="test-real-mode-guard",
        limit_cases=1,
        dry_run=False,
        stream=False,
    )


def test_protocol_only_reference_config_is_rejected_in_real_mode() -> None:
    with pytest.raises(ValueError, match="protocol_only"):
        run_benchmark(_args("configs/workloads/l40s-vllm-reference-v1.yaml"))


def test_vllm_placeholder_model_is_rejected_in_real_mode() -> None:
    matrix = load_benchmark_matrix("configs/workloads/vllm-l40s-smoke.yaml")
    models = load_models("configs/models.yaml")
    with pytest.raises(ValueError, match="placeholder"):
        ensure_real_mode_allowed(matrix, models)


def test_fake_server_synthetic_model_remains_allowed() -> None:
    matrix = load_benchmark_matrix("configs/fake_server_matrix.yaml")
    models = load_models("configs/models.yaml")
    ensure_real_mode_allowed(matrix, models)


def test_reference_contract_rejects_boolean_concurrency(tmp_path: Path) -> None:
    document = yaml.safe_load(Path("configs/workloads/l40s-vllm-reference-v1.yaml").read_text())
    document["cases"][0]["concurrency"] = True
    invalid_path = tmp_path / "invalid-contract.yaml"
    invalid_path.write_text(yaml.safe_dump(document))

    with pytest.raises(ValueError, match="concurrency"):
        validate_contract(invalid_path)


def test_real_mode_guard_cli_is_concise_and_nonzero() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/bench_openai_compatible.py",
            "--config",
            "configs/workloads/l40s-vllm-reference-v1.yaml",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "protocol_only" in result.stderr
    assert "Traceback" not in result.stderr
