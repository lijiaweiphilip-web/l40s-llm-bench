from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent


def run_command(command: list[str]) -> str | None:
    if shutil.which(command[0]) is None:
        return None
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        return exc.output.strip()


def collect_environment() -> dict[str, object]:
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version,
        "git_commit": run_command(["git", "rev-parse", "HEAD"]),
        "nvidia_smi": run_command(["nvidia-smi"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/env/environment.json")
    args = parser.parse_args()
    output = ensure_parent(Path(args.output))
    output.write_text(json.dumps(collect_environment(), indent=2), encoding="utf-8")
    print(f"wrote environment report to {output}")


if __name__ == "__main__":
    main()
