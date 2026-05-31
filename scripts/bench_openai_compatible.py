from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.config import load_benchmark_matrix, load_models
from l40s_bench.io import write_jsonl
from l40s_bench.schema import validate_result


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def synthetic_prompt(prompt_tokens: int) -> str:
    words = ["benchmark"] * max(1, prompt_tokens)
    return " ".join(words)


def dry_run_record(case: dict[str, Any], repeat_index: int, run_id: str) -> dict[str, Any]:
    latency_ms = 40.0 + case["prompt_tokens"] * 0.02 + case["output_tokens"] * 0.4
    output_tps = case["output_tokens"] / max(latency_ms / 1000.0, 0.001)
    return {
        "schema_version": "0.1",
        "timestamp_utc": utc_now(),
        "run_id": run_id,
        "case_id": case["case_id"],
        "framework": case["framework"],
        "model": case["model"],
        "endpoint": case.get("endpoint"),
        "prompt_tokens": case["prompt_tokens"],
        "output_tokens": case["output_tokens"],
        "batch_size": case["batch_size"],
        "repeat_index": repeat_index,
        "dry_run": True,
        "status": "ok",
        "latency_ms": round(latency_ms, 3),
        "ttft_ms": None,
        "output_tokens_per_second": round(output_tps, 3),
        "error": None,
    }


def real_request_record(case: dict[str, Any], repeat_index: int, run_id: str) -> dict[str, Any]:
    endpoint = case["endpoint"]
    payload = {
        "model": case["model"],
        "messages": [{"role": "user", "content": synthetic_prompt(case["prompt_tokens"])}],
        "max_tokens": case["output_tokens"],
        "temperature": 0,
        "stream": False,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    status = "ok"
    error = None
    try:
        with urllib.request.urlopen(request, timeout=int(case["timeout_seconds"])) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        status = "error"
        error = f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        status = "error"
        error = str(exc.reason)
    except TimeoutError:
        status = "error"
        error = "request timed out"
    latency_ms = (time.perf_counter() - started) * 1000.0
    output_tps = (
        case["output_tokens"] / (latency_ms / 1000.0) if status == "ok" and latency_ms else None
    )
    return {
        "schema_version": "0.1",
        "timestamp_utc": utc_now(),
        "run_id": run_id,
        "case_id": case["case_id"],
        "framework": case["framework"],
        "model": case["model"],
        "endpoint": endpoint,
        "prompt_tokens": case["prompt_tokens"],
        "output_tokens": case["output_tokens"],
        "batch_size": case["batch_size"],
        "repeat_index": repeat_index,
        "dry_run": False,
        "status": status,
        "latency_ms": round(latency_ms, 3),
        "ttft_ms": None,
        "output_tokens_per_second": round(output_tps, 3) if output_tps else None,
        "error": error,
    }


def run_benchmark(args: argparse.Namespace) -> list[dict[str, Any]]:
    matrix = load_benchmark_matrix(args.config)
    models = load_models(args.models_config)
    run_id = args.run_id or str(uuid.uuid4())
    records: list[dict[str, Any]] = []
    cases = matrix["cases"][: args.limit_cases] if args.limit_cases else matrix["cases"]
    for case in cases:
        if case["model"] not in models:
            raise ValueError(f"unknown model in benchmark case: {case['model']}")
        for repeat_index in range(case["repeats"]):
            record = (
                dry_run_record(case, repeat_index, run_id)
                if args.dry_run
                else real_request_record(case, repeat_index, run_id)
            )
            validate_result(record)
            records.append(record)
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/benchmark_matrix.yaml")
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--output", default="results/raw/dry_run.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--limit-cases", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = run_benchmark(args)
    write_jsonl(Path(args.output), records)
    print(f"wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
