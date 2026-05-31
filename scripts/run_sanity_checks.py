from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from bench_openai_compatible import real_request_record
from fake_openai_server import make_handler

from l40s_bench.io import ensure_parent, write_jsonl
from l40s_bench.schema import validate_result
from l40s_bench.summary import rows_to_markdown, summarize_records


@dataclass(frozen=True)
class SanityScenario:
    name: str
    ttft_ms: float
    tpot_ms: float
    tokens: int
    expected_status: str = "ok"
    status_code: int = 200
    ttft_tolerance_ms: float = 80.0
    tpot_tolerance_ms: float = 20.0


SCENARIOS = [
    SanityScenario(name="baseline_stream", ttft_ms=80, tpot_ms=20, tokens=8),
    SanityScenario(name="high_ttft_stream", ttft_ms=350, tpot_ms=20, tokens=8),
    SanityScenario(name="slow_tpot_stream", ttft_ms=80, tpot_ms=90, tokens=8),
    SanityScenario(
        name="server_error",
        ttft_ms=0,
        tpot_ms=0,
        tokens=1,
        expected_status="error",
        status_code=500,
    ),
]


def start_server(scenario: SanityScenario) -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(
            ttft_ms=scenario.ttft_ms,
            tpot_ms=scenario.tpot_ms,
            tokens=scenario.tokens,
            status_code=scenario.status_code,
        ),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}/v1/chat/completions"


def check_record(record: dict[str, Any], scenario: SanityScenario) -> list[str]:
    failures: list[str] = []
    if record["status"] != scenario.expected_status:
        failures.append(
            f"{scenario.name}: expected status {scenario.expected_status}, "
            f"got {record['status']}"
        )
    if scenario.expected_status != "ok":
        return failures
    if record["output_token_events"] != scenario.tokens:
        failures.append(
            f"{scenario.name}: expected {scenario.tokens} token events, "
            f"got {record['output_token_events']}"
        )
    ttft = record["ttft_ms"]
    if ttft is None or abs(float(ttft) - scenario.ttft_ms) > scenario.ttft_tolerance_ms:
        failures.append(
            f"{scenario.name}: expected TTFT near {scenario.ttft_ms} ms, got {ttft}"
        )
    tpot = record["tpot_ms"]
    if tpot is None or abs(float(tpot) - scenario.tpot_ms) > scenario.tpot_tolerance_ms:
        failures.append(
            f"{scenario.name}: expected TPOT near {scenario.tpot_ms} ms, got {tpot}"
        )
    return failures


def run_scenarios(repeats: int) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for scenario in SCENARIOS:
        server, endpoint = start_server(scenario)
        try:
            for repeat_index in range(repeats):
                case = {
                    "case_id": scenario.name,
                    "framework": "fake-openai",
                    "model": "fake-openai-model",
                    "endpoint": endpoint,
                    "prompt_tokens": 64,
                    "output_tokens": scenario.tokens,
                    "batch_size": 1,
                    "timeout_seconds": 10,
                }
                record = real_request_record(
                    case,
                    repeat_index=repeat_index,
                    run_id="sanity-checks",
                    stream=True,
                )
                validate_result(record)
                record["expected_ttft_ms"] = scenario.ttft_ms
                record["expected_tpot_ms"] = scenario.tpot_ms
                records.append(record)
                failures.extend(check_record(record, scenario))
        finally:
            server.shutdown()
            server.server_close()
    return records, failures


def write_report(path: Path, rows: list[dict[str, Any]], failures: list[str]) -> None:
    status = "PASS" if not failures else "FAIL"
    body = [f"# Benchmark Sanity Checks", "", f"Status: {status}", ""]
    body.append("These checks use a local fake OpenAI-compatible streaming server.")
    body.append("They validate the measurement harness, not model performance.")
    body.extend(["", "## Summary", "", rows_to_markdown(rows)])
    if failures:
        body.extend(["", "## Failures", ""])
        body.extend(f"- {failure}" for failure in failures)
    ensure_parent(path).write_text("\n".join(body), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--output", default="results/raw/sanity_checks.jsonl")
    parser.add_argument("--report", default="results/tables/sanity_checks.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records, failures = run_scenarios(repeats=args.repeats)
    write_jsonl(args.output, records)
    rows = summarize_records(records)
    write_report(Path(args.report), rows, failures)
    print(f"wrote {len(records)} records to {args.output}")
    print(f"wrote sanity report to {args.report}")
    if failures:
        for failure in failures:
            print(failure)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
