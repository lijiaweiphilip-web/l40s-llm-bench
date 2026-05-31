from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from typing import Any


def iter_sse_data(lines: Iterable[bytes]) -> Iterator[dict[str, Any]]:
    """Yield JSON payloads from OpenAI-style server-sent event lines."""
    for raw_line in lines:
        line = raw_line.decode("utf-8").strip()
        if not line or not line.startswith("data:"):
            continue
        payload = line.removeprefix("data:").strip()
        if payload == "[DONE]":
            break
        yield json.loads(payload)


def extract_delta_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    delta = choices[0].get("delta") or {}
    return str(delta.get("content") or "")
