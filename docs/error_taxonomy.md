# Error and Timeout Taxonomy

The benchmark records a compact `error_kind` for failed requests so summary
tables can separate infrastructure failures from model-serving behavior.

Current kinds:

| `error_kind` | Meaning | Summary column |
|---|---|---|
| `http_error` | The endpoint returned a non-2xx HTTP response | `http_error_runs` |
| `timeout` | The client timed out before a complete response | `timeout_runs` |
| `connection_error` | The client could not connect or the socket failed | `connection_error_runs` |
| `url_error` | A URL-layer error did not fit the categories above | `url_error_runs` |
| unset/other | Legacy records or uncategorized failures | `other_error_runs` |

HTTP failures also record `http_status` when available.

This taxonomy is intentionally small. It does not diagnose the root cause of a
serving failure by itself; it makes raw logs easier to triage and makes summary
regression checks sensitive to failure-type changes.
