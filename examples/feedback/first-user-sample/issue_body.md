## Repository commit

`a934f33`

## Smoke-test path

`Dry run and fake-server sanity suite`

## Commands run

```bash
python -m pip install -r requirements-dev.txt
python scripts/collect_env.py --output examples/feedback/first-user-sample/env/environment.json
python scripts/bench_openai_compatible.py --dry-run --run-id first-user-sample --output results/raw/first_user_sample_dry_run.jsonl
python scripts/summarize_results.py --input results/raw/first_user_sample_dry_run.jsonl --output-dir results/tables/first_user_sample
python scripts/run_sanity_checks.py --repeats 1 --output results/raw/first_user_sample_sanity.jsonl --report results/tables/first_user_sample/sanity_checks.md
```

## Environment

- OS: Ubuntu 24.04
- Python version: 3.12
- Shell or terminal: bash
- Install method: `python -m pip install -r requirements-dev.txt`
- Optional environment file: `examples/feedback/first-user-sample/env/environment.json`

## Expected artifacts

- `results/raw/first_user_sample_dry_run.jsonl`
- `results/tables/first_user_sample/summary.csv`
- `results/tables/first_user_sample/summary.md`
- `results/raw/first_user_sample_sanity.jsonl`
- `results/tables/first_user_sample/sanity_checks.md`
- `examples/feedback/first-user-sample/env/environment.json`

## What happened?

- Worked / failed / partially worked: worked, but the entry path felt a little split across README and the first-user guide
- First confusing step: I could not tell immediately whether a newcomer should start from the README quickstart or jump straight to `docs/first-user-smoke-test.md`
- First failure, if any: none

## Approximate time spent

About 11 minutes from install to the sanity-check markdown report.

## Short redacted output, if useful

```text
Dry run completed and wrote synthetic records.
The fake-server sanity suite also passed, but I had to double-check which document should be the main newcomer entry point.
```

## Suggested improvements

- Add a more opinionated first-user entry link near the top of the README.
- Mention the smoke-feedback starter next to the issue form link.

## Safety checks

- [x] I only used dry-run or local fake-server commands for this report.
- [x] I removed API keys, bearer tokens, private endpoint URLs, private hostnames, job IDs, and confidential data.
- [x] I understand this report is usability feedback, not a real GPU benchmark result.
