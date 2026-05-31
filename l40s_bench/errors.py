from __future__ import annotations

import socket
from typing import Any


HTTP_ERROR = "http_error"
TIMEOUT = "timeout"
CONNECTION_ERROR = "connection_error"
URL_ERROR = "url_error"

ERROR_KIND_TO_SUMMARY_COLUMN = {
    HTTP_ERROR: "http_error_runs",
    TIMEOUT: "timeout_runs",
    CONNECTION_ERROR: "connection_error_runs",
    URL_ERROR: "url_error_runs",
}
OTHER_ERROR_SUMMARY_COLUMN = "other_error_runs"
ERROR_SUMMARY_COLUMNS = tuple(ERROR_KIND_TO_SUMMARY_COLUMN.values()) + (
    OTHER_ERROR_SUMMARY_COLUMN,
)


def classify_url_error(reason: Any) -> str:
    text = str(reason).lower()
    if isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in text:
        return TIMEOUT
    if isinstance(reason, (ConnectionError, OSError)):
        return CONNECTION_ERROR
    return URL_ERROR
