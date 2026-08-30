from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml

REQUIRED_CASE_FIELDS = {
    "case_id",
    "framework",
    "model",
    "prompt_tokens",
    "output_tokens",
    "batch_size",
}


def _positive_integer(value: Any, field: str, case_id: Any) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer in {case_id}")
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be a positive integer in {case_id}") from exc
    if not math.isfinite(numeric) or not numeric.is_integer() or numeric <= 0:
        raise ValueError(f"{field} must be a positive integer in {case_id}")
    return int(numeric)


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a YAML mapping")
    return data


def load_benchmark_matrix(path: str | Path) -> dict[str, Any]:
    matrix = load_yaml(path)
    cases = matrix.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("benchmark matrix must contain a non-empty 'cases' list")

    defaults = matrix.get("defaults") or {}
    if not isinstance(defaults, dict):
        raise TypeError("'defaults' must be a mapping when provided")

    normalized_cases: list[dict[str, Any]] = []
    seen_case_ids: set[str] = set()
    for raw_case in cases:
        if not isinstance(raw_case, dict):
            raise TypeError("each benchmark case must be a mapping")
        case = {**defaults, **raw_case}
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            raise ValueError(f"case is missing required fields: {sorted(missing)}")
        if case["case_id"] in seen_case_ids:
            raise ValueError(f"duplicate case_id: {case['case_id']}")
        seen_case_ids.add(str(case["case_id"]))
        for key in ("prompt_tokens", "output_tokens", "batch_size"):
            case[key] = _positive_integer(case[key], key, case["case_id"])
        case["repeats"] = _positive_integer(
            case.get("repeats", 1), "repeats", case["case_id"]
        )
        case["concurrency"] = _positive_integer(
            case.get("concurrency", case["batch_size"]),
            "concurrency",
            case["case_id"],
        )
        normalized_cases.append(case)

    matrix["cases"] = normalized_cases
    matrix["defaults"] = defaults
    return matrix


def load_models(path: str | Path) -> dict[str, dict[str, Any]]:
    data = load_yaml(path)
    models = data.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("models config must contain a non-empty 'models' list")

    by_name: dict[str, dict[str, Any]] = {}
    for model in models:
        if not isinstance(model, dict) or "name" not in model:
            raise ValueError("each model must be a mapping with a 'name'")
        name = str(model["name"])
        if name in by_name:
            raise ValueError(f"duplicate model name: {name}")
        by_name[name] = model
    return by_name
