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


def test_protocol_guard_fails_before_any_network_io(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []

    def forbidden_urlopen(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))
        raise AssertionError("network I/O should not be reached")

    monkeypatch.setattr("urllib.request.urlopen", forbidden_urlopen)
    with pytest.raises(ValueError, match="protocol_only"):
        run_benchmark(_args("configs/workloads/l40s-vllm-reference-v1.yaml"))
    assert calls == []


def test_vllm_placeholder_model_is_rejected_in_real_mode() -> None:
    matrix = load_benchmark_matrix("configs/workloads/vllm-l40s-smoke.yaml")
    models = load_models("configs/models.yaml")
    with pytest.raises(ValueError, match="placeholder"):
        ensure_real_mode_allowed(matrix, models)


def test_vllm_synthetic_model_is_rejected_in_real_mode() -> None:
    matrix = load_benchmark_matrix("configs/benchmark_matrix.yaml")
    models = load_models("configs/models.yaml")
    with pytest.raises(ValueError, match="synthetic"):
        ensure_real_mode_allowed(matrix, models)


def test_fake_server_synthetic_model_remains_allowed() -> None:
    matrix = load_benchmark_matrix("configs/fake_server_matrix.yaml")
    models = load_models("configs/models.yaml")
    ensure_real_mode_allowed(matrix, models)


@pytest.mark.parametrize(
        ("model", "message"),
    [
        ({"source": "public", "model_revision": "rev-1"}, "model_id"),
        ({"source": "public", "model_id": "org/model"}, "revision"),
        (
            {
                "source": "public",
                "model_id": "org/model",
                "model_revision": "replace-with-fixed-model-revision",
            },
            "placeholder",
        ),
    ],
)
def test_vllm_real_mode_requires_fixed_model_provenance(
    model: dict[str, str], message: str
) -> None:
    matrix = {"cases": [{"framework": "vllm", "model": "real-model"}]}
    models = {"real-model": model}

    with pytest.raises(ValueError, match=message):
        ensure_real_mode_allowed(matrix, models)


def test_reference_contract_rejects_boolean_concurrency(tmp_path: Path) -> None:
    document = yaml.safe_load(Path("configs/workloads/l40s-vllm-reference-v1.yaml").read_text())
    document["cases"][0]["concurrency"] = True
    invalid_path = tmp_path / "invalid-contract.yaml"
    invalid_path.write_text(yaml.safe_dump(document))

    with pytest.raises(ValueError, match="concurrency"):
        validate_contract(invalid_path)


@pytest.mark.parametrize("field", ["model_id", "model_revision"])
def test_reference_contract_requires_model_provenance(field: str, tmp_path: Path) -> None:
    document = yaml.safe_load(Path("configs/workloads/l40s-vllm-reference-v1.yaml").read_text())
    document["contract"].pop(field)
    invalid_path = tmp_path / f"missing-{field}.yaml"
    invalid_path.write_text(yaml.safe_dump(document))

    with pytest.raises(ValueError, match=field):
        validate_contract(invalid_path)


def test_reference_contract_rejects_universal_claim_boundary(tmp_path: Path) -> None:
    document = yaml.safe_load(Path("configs/workloads/l40s-vllm-reference-v1.yaml").read_text())
    document["contract"]["public_boundary"]["no_universal_performance_claim"] = False
    invalid_path = tmp_path / "unsafe-boundary.yaml"
    invalid_path.write_text(yaml.safe_dump(document))

    with pytest.raises(ValueError, match="no_universal_performance_claim"):
        validate_contract(invalid_path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("dtype", None),
        ("max_model_len", True),
        ("tokenizer", ""),
        ("serving_flags", "--bad-shape"),
        ("prompt_seed", True),
        ("timeout_seconds", 0),
    ],
)
def test_reference_contract_rejects_invalid_execution_metadata(
    field: str, value: object, tmp_path: Path
) -> None:
    document = yaml.safe_load(Path("configs/workloads/l40s-vllm-reference-v1.yaml").read_text())
    document["contract"][field] = value
    invalid_path = tmp_path / f"invalid-{field}.yaml"
    invalid_path.write_text(yaml.safe_dump(document))

    with pytest.raises(ValueError, match=field):
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
