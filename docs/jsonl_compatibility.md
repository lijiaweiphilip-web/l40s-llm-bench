# JSONL Compatibility Check

Raw benchmark records are the source of truth. The compatibility checker helps
catch schema drift before summaries or regression comparisons rely on those
records.

Example:

```bash
python scripts/check_jsonl_compat.py --input results/raw --output results/tables/jsonl_compat.md
```

The report includes:

- total, valid, and invalid record counts
- schema version counts
- missing required fields
- missing optional fields that were backfilled by validation
- invalid record messages

Missing optional fields are expected for older logs. Missing required fields or
invalid values should be fixed before claiming results from that run.
