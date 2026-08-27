# Quality gates

The public CI gate is intentionally scoped to the maintained Python package and
the fake-server sanity regression test:

```text
python -m pytest -q
python -m compileall -q l40s_bench scripts tests
python -m ruff check l40s_bench scripts/run_sanity_checks.py tests/test_sanity_checks.py
```

The repository also contains older helper scripts and proof workflows that are
kept for compatibility with earlier local checks. Their historical Ruff
findings are informational and are not represented as a claim that every
legacy script is lint-clean. The scoped gate checks package installation,
measurement mechanics, and the CPU/fake-server validation path; it does not
claim real GPU performance.
