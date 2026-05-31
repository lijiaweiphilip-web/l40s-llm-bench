from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.compare import (
    compare_summaries,
    comparison_to_markdown,
    has_regression,
    read_summary_csv,
)
from l40s_bench.io import ensure_parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", default="results/tables/regression_compare.md")
    parser.add_argument("--csv-output", default="results/tables/regression_compare.csv")
    parser.add_argument("--max-regression-pct", type=float, default=5.0)
    parser.add_argument("--fail-on-regression", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = compare_summaries(
        read_summary_csv(args.baseline),
        read_summary_csv(args.candidate),
        max_regression_pct=args.max_regression_pct,
    )
    md_path = ensure_parent(args.output)
    csv_path = ensure_parent(args.csv_output)
    md_path.write_text(comparison_to_markdown(rows), encoding="utf-8")
    headers = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} comparison rows to {md_path}")
    if args.fail_on_regression and has_regression(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
