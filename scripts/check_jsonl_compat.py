from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.compat import check_jsonl_inputs, report_to_markdown
from l40s_bench.io import ensure_parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/raw")
    parser.add_argument("--output", default="results/tables/jsonl_compat.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = check_jsonl_inputs(args.input)
    output = ensure_parent(args.output)
    output.write_text(report_to_markdown(report), encoding="utf-8")
    print(f"checked {report['records']} JSONL records")
    print(f"wrote compatibility report to {output}")
    if report["invalid_records"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
