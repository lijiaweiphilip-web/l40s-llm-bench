"""Validate the locked, result-free L40S/vLLM workload contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

EXPECTED_CONCURRENCIES = (1, 4, 8)
EXPECTED_PROFILES = {
    "short": (128, 64),
    "medium": (512, 128),
}


def _fail(message: str) -> None:
    raise ValueError(message)


def _as_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(f"{field} must be a non-negative integer")
    return value


def _as_positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        _fail(f"{field} must be a positive integer")
    return value


def validate_contract(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        _fail("contract must be a mapping")
    contract = document.get("contract")
    if not isinstance(contract, dict):
        _fail("missing contract mapping")
    if contract.get("name") != "l40s-vllm-reference-v1":
        _fail("unexpected contract name")
    if contract.get("version") != "1.0":
        _fail("unsupported contract version")
    if contract.get("status") != "protocol_only":
        _fail("contract status must remain protocol_only")
    for field in ("model_id", "model_revision"):
        value = contract.get(field)
        if not isinstance(value, str) or not value.strip():
            _fail(f"{field} must be a non-empty string, even for a protocol placeholder")
    for field in ("dtype", "tokenizer"):
        value = contract.get(field)
        if not isinstance(value, str) or not value.strip():
            _fail(f"{field} must be a non-empty string")
    _as_positive_int(contract.get("max_model_len"), "max_model_len")
    serving_flags = contract.get("serving_flags")
    if not isinstance(serving_flags, list) or any(
        not isinstance(flag, str) or not flag.strip() for flag in serving_flags
    ):
        _fail("serving_flags must be a list of non-empty strings")
    _as_int(contract.get("prompt_seed"), "prompt_seed")
    _as_positive_int(contract.get("timeout_seconds"), "timeout_seconds")
    if _as_int(contract.get("warmup_repeats"), "warmup_repeats") != 1:
        _fail("warmup_repeats must be 1")
    if _as_int(contract.get("measured_repeats"), "measured_repeats") != 3:
        _fail("measured_repeats must be 3")
    boundary = contract.get("public_boundary")
    if not isinstance(boundary, dict):
        _fail("missing public_boundary")
    for key in (
        "real_result_required",
        "dry_run_is_benchmark_claim",
        "fake_server_is_hardware_evidence",
        "no_universal_performance_claim",
    ):
        if not isinstance(boundary.get(key), bool):
            _fail(f"public_boundary.{key} must be boolean")
    if boundary["real_result_required"] is not True:
        _fail("real_result_required must stay true")
    if boundary["dry_run_is_benchmark_claim"] is not False:
        _fail("dry_run_is_benchmark_claim must stay false")
    if boundary["fake_server_is_hardware_evidence"] is not False:
        _fail("fake_server_is_hardware_evidence must stay false")
    if boundary["no_universal_performance_claim"] is not True:
        _fail("no_universal_performance_claim must stay true")

    defaults = document.get("defaults")
    cases = document.get("cases")
    if not isinstance(defaults, dict) or not isinstance(cases, list):
        _fail("defaults and cases are required")
    if defaults.get("repeats") != contract["measured_repeats"]:
        _fail("case repeats must equal measured_repeats")
    if defaults.get("framework") != "vllm":
        _fail("framework must be vllm")

    expected_ids = {
        f"l40s_reference_{profile}_c{concurrency}"
        for profile in EXPECTED_PROFILES
        for concurrency in EXPECTED_CONCURRENCIES
    }
    actual_ids = {case.get("case_id") for case in cases if isinstance(case, dict)}
    if len(cases) != len(expected_ids) or actual_ids != expected_ids:
        _fail("cases must contain exactly short/medium x concurrency 1/4/8")
    for case in cases:
        if not isinstance(case, dict):
            _fail("each case must be a mapping")
        case_id = case["case_id"]
        profile = "short" if "_short_" in case_id else "medium"
        prompt_tokens, output_tokens = EXPECTED_PROFILES[profile]
        if case.get("prompt_tokens") != prompt_tokens or case.get("output_tokens") != output_tokens:
            _fail(f"{case_id} has unexpected prompt/output targets")
        concurrency = case.get("concurrency")
        if (
            isinstance(concurrency, bool)
            or not isinstance(concurrency, int)
            or concurrency not in EXPECTED_CONCURRENCIES
        ):
            _fail(f"{case_id} has unexpected concurrency")
        effective_repeats = case.get("repeats", defaults.get("repeats"))
        if effective_repeats != contract["measured_repeats"]:
            _fail(f"{case_id} has unexpected repeats")
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the result-free L40S reference protocol.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        validate_contract(args.path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 1
    print("valid: protocol_only; no benchmark result asserted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
