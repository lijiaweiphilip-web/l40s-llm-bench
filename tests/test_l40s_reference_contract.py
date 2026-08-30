from __future__ import annotations

from pathlib import Path

from scripts.validate_l40s_contract import validate_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "configs" / "workloads" / "l40s-vllm-reference-v1.yaml"


def test_l40s_reference_contract_is_locked_and_result_free() -> None:
    document = validate_contract(CONTRACT)
    assert document["contract"]["status"] == "protocol_only"
    assert document["contract"]["public_boundary"]["real_result_required"] is True


def test_l40s_reference_contract_has_six_fixed_cells() -> None:
    document = validate_contract(CONTRACT)
    cases = document["cases"]
    assert len(cases) == 6
    assert {case["concurrency"] for case in cases} == {1, 4, 8}
    assert {(case["prompt_tokens"], case["output_tokens"]) for case in cases} == {
        (128, 64),
        (512, 128),
    }
