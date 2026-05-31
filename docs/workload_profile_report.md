# Workload Profile Report

The workload profile report turns a summary CSV into a scenario-oriented
Markdown report. It pairs each workload shape with the available benchmark
summary rows so readers can see which request patterns were covered.

Example:

```bash
python scripts/report_workload_profiles.py \
  --profiles configs/workload_profiles.yaml \
  --summary results/tables/summary.csv \
  --output results/tables/workload_profile_report.md
```

The report includes:

- profile descriptions and token shapes
- per-profile latency, TTFT, TPOT, throughput, and error counts
- missing workload profiles
- unmatched summary rows
- a scope note that the report is local evidence, not a universal benchmark

Use it after `scripts/summarize_results.py` when preparing results for review.
