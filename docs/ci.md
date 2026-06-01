# CI

The GitHub Actions workflow in `.github/workflows/ci.yml` is CPU-only and does
not require API keys, GPUs, model servers, or external model downloads.

It runs on pushes to `main`, pull requests, and manual dispatch:

1. Install Python 3.10 dependencies from `requirements-dev.txt`.
2. Run the test suite with `python -m pytest -q`.
3. Run a synthetic benchmark dry run:
   `python scripts/bench_openai_compatible.py --dry-run --run-id ci-dry-run --output results/raw/ci_dry_run.jsonl`.
4. Summarize the dry-run output with `scripts/summarize_results.py`.
5. Validate JSONL compatibility with `scripts/check_jsonl_compat.py`.
6. Run local fake-server sanity checks with `scripts/run_sanity_checks.py --repeats 1`.
7. Upload generated raw JSONL and table/report artifacts.

The workflow intentionally does not run real benchmark requests against vLLM,
OpenAI-compatible model servers, or remote APIs. Those checks require separate
runtime provisioning and should stay out of default CI until a bounded,
credential-free smoke target exists.
