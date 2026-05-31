from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from l40s_bench.config import load_yaml


REQUIRED_PROFILE_FIELDS = {
    "name",
    "prompt_tokens",
    "output_tokens",
    "batch_size",
    "concurrency",
}


def load_workload_profiles(path: str | Path) -> dict[str, Any]:
    data = load_yaml(path)
    defaults = data.get("defaults") or {}
    profiles = data.get("profiles")
    if not isinstance(defaults, dict):
        raise ValueError("workload profile defaults must be a mapping")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("workload profile config must contain a non-empty profiles list")

    normalized: list[dict[str, Any]] = []
    names: set[str] = set()
    for raw_profile in profiles:
        if not isinstance(raw_profile, dict):
            raise ValueError("each workload profile must be a mapping")
        missing = REQUIRED_PROFILE_FIELDS - set(raw_profile)
        if missing:
            raise ValueError(f"profile missing required fields: {sorted(missing)}")
        profile = dict(raw_profile)
        if profile["name"] in names:
            raise ValueError(f"duplicate workload profile: {profile['name']}")
        names.add(str(profile["name"]))
        for key in ("prompt_tokens", "output_tokens", "batch_size", "concurrency"):
            profile[key] = int(profile[key])
            if profile[key] <= 0:
                raise ValueError(f"{key} must be positive in {profile['name']}")
        normalized.append(profile)
    return {"defaults": defaults, "profiles": normalized}


def profiles_to_matrix(
    profiles_config: dict[str, Any],
    framework: str | None = None,
    model: str | None = None,
    endpoint: str | None = None,
) -> dict[str, Any]:
    defaults = dict(profiles_config["defaults"])
    if framework is not None:
        defaults["framework"] = framework
    if model is not None:
        defaults["model"] = model
    if endpoint is not None:
        defaults["endpoint"] = endpoint

    cases: list[dict[str, Any]] = []
    for profile in profiles_config["profiles"]:
        case = {
            "case_id": profile["name"],
            "framework": defaults["framework"],
            "model": defaults["model"],
            "endpoint": defaults["endpoint"],
            "timeout_seconds": int(defaults.get("timeout_seconds", 60)),
            "repeats": int(defaults.get("repeats", 1)),
            "prompt_tokens": profile["prompt_tokens"],
            "output_tokens": profile["output_tokens"],
            "batch_size": profile["batch_size"],
            "concurrency": profile["concurrency"],
            "description": profile.get("description", ""),
        }
        cases.append(case)
    return {"defaults": {}, "cases": cases}


def write_matrix(path: str | Path, matrix: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8")
