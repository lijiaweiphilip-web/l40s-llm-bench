# Regression Comparison

The comparison tool checks whether a candidate summary regresses against a
baseline summary.

It compares rows by benchmark identity:

- `case_id`
- `framework`
- `model`
- `prompt_tokens`
- `output_tokens`
- `batch_size`
- `concurrency`

Lower is better for latency and error metrics. Higher is better for successful
runs and output tokens per second.

Example:

```bash
python scripts/compare_summaries.py \
  --baseline results/baselines/summary.csv \
  --candidate results/tables/summary.csv \
  --output results/tables/regression_compare.md \
  --csv-output results/tables/regression_compare.csv \
  --max-regression-pct 5 \
  --fail-on-regression
```

This does not prove that one model or server is better than another. It checks
whether the same benchmark case changed beyond the configured threshold.
