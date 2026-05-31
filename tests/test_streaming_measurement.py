from __future__ import annotations

from http.server import ThreadingHTTPServer
from threading import Thread

from l40s_bench.errors import HTTP_ERROR
from scripts.bench_openai_compatible import real_request_record
from scripts.fake_openai_server import make_handler


def test_fake_server_streaming_metrics_are_measured() -> None:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(ttft_ms=20, tpot_ms=10, tokens=4),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        case = {
            "case_id": "fake",
            "framework": "fake-openai",
            "model": "fake-openai-model",
            "endpoint": f"http://{host}:{port}/v1/chat/completions",
            "prompt_tokens": 8,
            "output_tokens": 4,
            "batch_size": 1,
            "concurrency": 1,
            "timeout_seconds": 5,
        }

        record = real_request_record(case, repeat_index=0, run_id="test-run", stream=True)

        assert record["status"] == "ok"
        assert record["output_token_events"] == 4
        assert record["ttft_ms"] is not None
        assert record["tpot_ms"] is not None
        assert 5 <= record["ttft_ms"] <= 100
        assert 3 <= record["tpot_ms"] <= 80
    finally:
        server.shutdown()
        server.server_close()


def test_fake_server_http_errors_are_classified() -> None:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(ttft_ms=0, tpot_ms=0, tokens=1, status_code=503),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        case = {
            "case_id": "fake",
            "framework": "fake-openai",
            "model": "fake-openai-model",
            "endpoint": f"http://{host}:{port}/v1/chat/completions",
            "prompt_tokens": 8,
            "output_tokens": 1,
            "batch_size": 1,
            "concurrency": 1,
            "timeout_seconds": 5,
        }

        record = real_request_record(case, repeat_index=0, run_id="test-run", stream=True)

        assert record["status"] == "error"
        assert record["error_kind"] == HTTP_ERROR
        assert record["http_status"] == 503
    finally:
        server.shutdown()
        server.server_close()
