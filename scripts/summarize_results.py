from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent, read_jsonl
from l40s_bench.schema import validate_result
from l40s_bench.summary import rows_to_markdown, summarize_records


def collect_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(input_path.glob("*.jsonl"))
    raise FileNotFoundError(input_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/raw")
    parser.add_argument("--output-dir", default="results/tables")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = []
    for path in collect_inputs(Path(args.input)):
        for record in read_jsonl(path):
            validate_result(record)
            records.append(record)
    rows = summarize_records(records)

    output_dir = Path(args.output_dir)
    csv_path = ensure_parent(output_dir / "summary.csv")
    md_path = ensure_parent(output_dir / "summary.md")
    headers = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    md_path.write_text(rows_to_markdown(rows), encoding="utf-8")
    print(f"wrote {len(rows)} summary rows to {output_dir}")


if __name__ == "__main__":
    main()
