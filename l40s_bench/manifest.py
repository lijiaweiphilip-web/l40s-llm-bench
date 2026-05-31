from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_SCOPE_NOTE = (
    "This manifest records local benchmark artifacts. It does not prove general "
    "model, server, framework, or GPU performance."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact_record(label: str, path: str | Path, required: bool) -> dict[str, Any]:
    target = Path(path)
    record: dict[str, Any] = {
        "label": label,
        "path": str(target),
        "required": required,
        "exists": target.exists(),
    }
    if target.exists() and target.is_file():
        record.update(
            {
                "bytes": target.stat().st_size,
                "sha256": sha256_file(target),
            }
        )
    return record


def build_manifest(
    run_id: str,
    artifacts: list[dict[str, Any]],
    scope_note: str = DEFAULT_SCOPE_NOTE,
) -> dict[str, Any]:
    missing_required = [
        item["label"]
        for item in artifacts
        if item.get("required") and not item.get("exists")
    ]
    return {
        "schema_version": "0.1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "run_id": run_id,
        "status": "complete" if not missing_required else "missing-required-artifacts",
        "missing_required_artifacts": missing_required,
        "scope_note": scope_note,
        "artifacts": artifacts,
    }


def manifest_to_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Run Manifest",
        "",
        f"Run ID: `{manifest['run_id']}`",
        f"Status: `{manifest['status']}`",
        "",
        "## Artifacts",
        "",
        "| Label | Required | Exists | Bytes | SHA256 | Path |",
        "|---|---|---|---|---|---|",
    ]
    for item in manifest["artifacts"]:
        sha = str(item.get("sha256", ""))
        sha_short = sha[:12] if sha else ""
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["label"]),
                    str(item["required"]),
                    str(item["exists"]),
                    str(item.get("bytes", "")),
                    sha_short,
                    str(item["path"]),
                ]
            )
            + " |"
        )
    if manifest["missing_required_artifacts"]:
        lines.extend(["", "## Missing Required Artifacts", ""])
        lines.extend(f"- `{label}`" for label in manifest["missing_required_artifacts"])
    lines.extend(["", "## Scope Note", "", manifest["scope_note"], ""])
    return "\n".join(lines)


def write_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
