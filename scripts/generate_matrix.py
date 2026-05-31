from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.profiles import load_workload_profiles, profiles_to_matrix, write_matrix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="configs/workload_profiles.yaml")
    parser.add_argument("--output", default="configs/generated_workload_matrix.yaml")
    parser.add_argument("--framework")
    parser.add_argument("--model")
    parser.add_argument("--endpoint")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profiles = load_workload_profiles(args.profiles)
    matrix = profiles_to_matrix(
        profiles,
        framework=args.framework,
        model=args.model,
        endpoint=args.endpoint,
    )
    write_matrix(args.output, matrix)
    print(f"wrote {len(matrix['cases'])} cases to {args.output}")


if __name__ == "__main__":
    main()
