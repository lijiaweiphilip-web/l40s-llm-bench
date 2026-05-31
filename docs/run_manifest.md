# Run Manifest

The run manifest is a small evidence bundle for one benchmark run. It records
where the important artifacts are and hashes them so a later reader can confirm
which files supported a summary or report.

Example:

```bash
python scripts/build_run_manifest.py \
  --run-id workload-profiles-dry-run \
  --config configs/generated_workload_matrix.yaml \
  --raw results/raw/workload_profiles_dry_run.jsonl \
  --summary results/tables/summary.csv \
  --workload-report results/tables/workload_profile_report.md
```

The manifest includes:

- benchmark config path
- raw JSONL path
- summary CSV and Markdown paths
- workload profile report path
- optional environment report path
- file sizes and SHA256 hashes
- missing required artifacts
- a scope note about what the run does not prove

Use the manifest before publishing or comparing benchmark results.
