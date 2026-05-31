from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from l40s_bench.io import ensure_parent
from l40s_bench.manifest import (
    artifact_record,
    build_manifest,
    manifest_to_markdown,
    write_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="local-dry-run")
    parser.add_argument("--config", default="configs/generated_workload_matrix.yaml")
    parser.add_argument("--raw", default="results/raw/workload_profiles_dry_run.jsonl")
    parser.add_argument("--summary", default="results/tables/summary.csv")
    parser.add_argument("--summary-md", default="results/tables/summary.md")
    parser.add_argument("--workload-report", default="results/tables/workload_profile_report.md")
    parser.add_argument("--environment", default="results/env/environment.json")
    parser.add_argument("--output", default="results/manifests/run_manifest.json")
    parser.add_argument("--markdown", default="results/manifests/run_manifest.md")
    parser.add_argument("--allow-missing-required", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = [
        artifact_record("benchmark_config", args.config, required=True),
        artifact_record("raw_jsonl", args.raw, required=True),
        artifact_record("summary_csv", args.summary, required=True),
        artifact_record("summary_markdown", args.summary_md, required=False),
        artifact_record("workload_profile_report", args.workload_report, required=False),
        artifact_record("environment_report", args.environment, required=False),
    ]
    manifest = build_manifest(args.run_id, artifacts)
    output = ensure_parent(args.output)
    markdown = ensure_parent(args.markdown)
    write_manifest(output, manifest)
    markdown.write_text(manifest_to_markdown(manifest), encoding="utf-8")
    print(f"wrote run manifest to {output}")
    print(f"wrote run manifest report to {markdown}")
    if manifest["missing_required_artifacts"] and not args.allow_missing_required:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
