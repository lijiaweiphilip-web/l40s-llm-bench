from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent
from l40s_bench.profiles import load_workload_profiles
from l40s_bench.workload_report import read_summary_csv, workload_report_to_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="configs/workload_profiles.yaml")
    parser.add_argument("--summary", default="results/tables/summary.csv")
    parser.add_argument("--output", default="results/tables/workload_profile_report.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profiles = load_workload_profiles(args.profiles)
    summary_rows = read_summary_csv(args.summary)
    output = ensure_parent(args.output)
    output.write_text(workload_report_to_markdown(profiles, summary_rows), encoding="utf-8")
    print(f"wrote workload profile report to {output}")


if __name__ == "__main__":
    main()
