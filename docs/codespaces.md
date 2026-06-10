# Codespaces Path

`l40s-llm-bench` can now be reviewed and maintained in GitHub Codespaces for
the CPU-only parts of the repository.

## Good Fit For Codespaces

- README and maintenance doc edits
- issue and PR follow-up work
- dry runs
- `pytest`
- reviewer smoke proof runs
- schema and evidence validation

## Not A Replacement For Real Hardware

GitHub Codespaces is useful for repository maintenance and CPU-only validation.
It is not a substitute for the remaining real-world gap:

- a genuine independent public tester interaction, or
- one real L40S/vLLM artifact bundle with raw events, summary, manifest,
  environment notes, and GPU metrics

Issue `#17` still requires real hardware access.

## Suggested First Commands

The dev container installs `requirements-dev.txt` after creation. After the
codespace is ready, these are the most useful first checks:

```bash
python -m pytest -q
python scripts/run_contributor_self_check.py
python scripts/run_reviewer_smoke_pack.py
```

## Why This Helps

This lowers reviewer and maintainer friction:

- less local memory pressure for documentation and validation work
- a more repeatable cloud environment for CPU-only checks
- a clearer handoff path for future contributors

For the bounded newcomer-oriented proof path, see
`docs/contributor-self-check.md`.
