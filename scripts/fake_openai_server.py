from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def make_handler(
    ttft_ms: float,
    tpot_ms: float,
    tokens: int,
    status_code: int = 200,
) -> type[BaseHTTPRequestHandler]:
    class FakeOpenAIHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            if status_code != 200:
                self._send_error_json()
                return
            requested_tokens = int(payload.get("max_tokens") or tokens)
            emit_tokens = max(1, min(requested_tokens, tokens))
            if payload.get("stream"):
                self._send_stream(emit_tokens)
            else:
                self._send_json(emit_tokens)

        def log_message(self, fmt: str, *args: object) -> None:
            return

        def _send_error_json(self) -> None:
            body = json.dumps(
                {
                    "error": {
                        "message": "synthetic fake server error",
                        "type": "synthetic_error",
                    }
                }
            ).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()

        def _send_json(self, emit_tokens: int) -> None:
            time.sleep(ttft_ms / 1000.0)
            content = " ".join(["x"] * emit_tokens)
            body = json.dumps(
                {
                    "id": "fake-response",
                    "object": "chat.completion",
                    "choices": [{"message": {"role": "assistant", "content": content}}],
                    "usage": {"completion_tokens": emit_tokens},
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()

        def _send_stream(self, emit_tokens: int) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            time.sleep(ttft_ms / 1000.0)
            for index in range(emit_tokens):
                if index > 0:
                    time.sleep(tpot_ms / 1000.0)
                payload = {
                    "id": "fake-stream",
                    "object": "chat.completion.chunk",
                    "choices": [{"delta": {"content": "x"}}],
                }
                self.wfile.write(f"data: {json.dumps(payload)}\n\n".encode("utf-8"))
                self.wfile.flush()
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

    return FakeOpenAIHandler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18000)
    parser.add_argument("--ttft-ms", type=float, default=120.0)
    parser.add_argument("--tpot-ms", type=float, default=25.0)
    parser.add_argument("--tokens", type=int, default=16)
    parser.add_argument("--status-code", type=int, default=200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer(
        (args.host, args.port),
        make_handler(
            ttft_ms=args.ttft_ms,
            tpot_ms=args.tpot_ms,
            tokens=args.tokens,
            status_code=args.status_code,
        ),
    )
    print(
        f"serving fake OpenAI endpoint on http://{args.host}:{args.port} "
        f"(ttft_ms={args.ttft_ms}, tpot_ms={args.tpot_ms}, tokens={args.tokens})"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
