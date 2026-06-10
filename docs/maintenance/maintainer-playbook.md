# Maintainer Playbook

This playbook is for routine maintenance of `l40s-llm-bench`. It keeps the
project focused on reproducible evidence rather than unsupported benchmark or
adoption claims.

## Weekly Triage

1. Review new issues and pull requests.
2. Check whether each item is a bug, feature request, benchmark-result
   submission, documentation request, release task, or security-sensitive
   report.
3. Confirm that no issue or PR includes API keys, bearer tokens, private
   endpoint URLs, private hostnames, internal paths, usernames, job IDs, or
   confidential benchmark data.
4. Apply labels from `docs/maintenance/labels-and-milestones.md`.
5. Ask for missing reproduction evidence before interpreting benchmark numbers.
6. Keep `v0.2.0` work scoped to reproducibility, first real-server smoke-run
   preparation, GPU metrics guidance, backend decision notes, troubleshooting,
   and examples.
7. Close or redirect requests that ask for a public leaderboard, unsupported
   vendor claims, fabricated adoption, or broad production guarantees.

## Issue Labeling

Use labels to describe review needs, not prestige or priority claims:

- `bug`: broken command, incorrect output, schema failure, or unexpected
  behavior.
- `benchmark-result`: submitted result bundle or request for result review.
- `reproducibility`: evidence bundle, run manifest, schema, or repeatability
  work.
- `documentation` or `docs`: documentation-only or documentation-led work.
- `vllm`, `l40s`, `gpu-metrics`, or `backend`: technical area labels when the
  issue is genuinely about that area.
- `needs-decision`: maintainer choice required before implementation.
- `good first issue`: small task that can be completed without private
  hardware, secrets, or unpublished benchmark artifacts.
- `security`: secret handling, private endpoint exposure, or vulnerability
  report.
- `release`: release notes, checklist, tag, or GitHub release work.

Do not use labels to imply external adoption, validated performance, or
maintainer endorsement of a benchmark result.

## Smoke-Run Verification

Use the 10-minute smoke path for routine confidence checks before spending GPU
time:

```powershell
python -m pip install -r requirements-dev.txt
python scripts\bench_openai_compatible.py --dry-run
python scripts\summarize_results.py --input results\raw\dry_run.jsonl --output-dir results\tables
python scripts\run_sanity_checks.py --repeats 1
```

For a submission or release candidate, prefer temporary output paths so local
generated artifacts do not accidentally enter a PR:

```powershell
python scripts\bench_openai_compatible.py --config configs\generated_workload_matrix.yaml --dry-run --stream --output $env:TEMP\l40s-workload-profiles-dry-run.jsonl
python scripts\summarize_results.py --input $env:TEMP\l40s-workload-profiles-dry-run.jsonl --output-dir $env:TEMP\l40s-tables
python scripts\run_sanity_checks.py --repeats 1 --output $env:TEMP\l40s-sanity-checks.jsonl --report $env:TEMP\l40s-sanity-checks.md
```

Interpretation rules:

- Dry-run output is synthetic and validates pipeline shape only.
- Fake-server output validates timing mechanics against controlled delays.
- Neither dry-run nor fake-server output is model or GPU performance.
- A real-server smoke run is still a local measurement until the evidence
  bundle is complete and limitations are stated.

## Benchmark Submission Handling

For every benchmark-result issue or PR, require:

- repository commit;
- exact benchmark, summary, and manifest commands;
- benchmark config and model/server config notes;
- raw JSONL or an explanation for why it cannot be shared;
- summary CSV or Markdown;
- run manifest when possible;
- serving stack, version, model identifier if public, streaming mode, and
  notable flags;
- hardware/runtime notes including GPU model, count, driver/runtime, CPU,
  memory, and power/thermal/shared-host constraints;
- repeated-run policy and treatment of failed, skipped, timeout, or OOM cases;
- limitations that explain what the result does not prove.

Review flow:

1. Check for secrets and private infrastructure details first.
2. Confirm the run type: dry-run, fake-server, or real-server.
3. Verify commands and configs are internally consistent with raw JSONL and
   summaries.
4. Confirm the manifest hashes the artifacts being discussed.
5. Check whether errors, failed requests, timeouts, or OOMs are reported rather
   than silently omitted.
6. Ask clarifying questions before accepting any performance interpretation.
7. Treat incomplete submissions as local observations, not benchmark claims.

Reject or rewrite language that claims leaderboard rank, broad hardware
performance, model superiority, ecosystem adoption, or production readiness
without direct evidence in the submitted artifacts.

Useful maintainer shortcuts:

```powershell
python scripts\review_result_submission.py --submission-dir results\submissions\<run-id>
python scripts\build_result_review_comment.py --submission-dir results\submissions\<run-id>
```

The first command generates a structured review summary. The second turns the
same review state into a maintainer-style public comment draft that can be
edited before posting on the GitHub issue.
For concrete tone and structure examples, use `docs/result_review_examples.md`.

If the artifact set is technically reviewable but the public post still needs a
different maintainer conclusion, use:

```powershell
python scripts\build_result_review_comment.py --submission-dir results\submissions\<run-id> --override-verdict "needs claim rewrite"
```

## Release Checklist

Use `docs/release-checklist.md` as the source of truth for release-specific
commands and observed results. A release should not move forward until:

1. Scope is limited and described in `CHANGELOG.md` and release notes.
2. Local CPU-only checks pass or failures are documented with a maintainer
   decision.
3. GitHub Actions are green on the release PR or branch.
4. Release notes clearly state whether the release includes only harness
   validation or any real-server evidence.
5. No generated outputs, private paths, credentials, unpublished results, or
   local-only artifacts are accidentally included.
6. Any examples are labeled as dry-run, fake-server, or real-server.
7. The tag and GitHub release text avoid fabricated adoption and unsupported
   performance claims.

Suggested release command order:

```powershell
python --version
python -m pytest -q
python scripts\bench_openai_compatible.py --config configs\generated_workload_matrix.yaml --dry-run --stream --output $env:TEMP\l40s-workload-profiles-dry-run.jsonl
python scripts\summarize_results.py --input $env:TEMP\l40s-workload-profiles-dry-run.jsonl --output-dir $env:TEMP\l40s-tables
python scripts\run_sanity_checks.py --repeats 1 --output $env:TEMP\l40s-sanity-checks.jsonl --report $env:TEMP\l40s-sanity-checks.md
```

Only create or push a release tag when explicitly requested by the maintainer.

## Pull Request Review Style

For PRs, check the template before code details:

- Is the scope focused?
- Are commands, configs, and artifacts listed?
- Does the PR say whether it includes benchmark claims?
- Are limitations explicit?
- Are dry-run, fake-server, and real-server contexts labeled correctly?
- Are secrets, private paths, and unsupported claims absent?

Prefer small follow-up issues over expanding a PR beyond its original scope.

## Sensitive Material

Keep these out of public issues, PRs, release notes, and examples:

- API keys, bearer tokens, cookies, and credentials.
- Private endpoint URLs, hostnames, usernames, job IDs, and cluster paths.
- Proprietary model names or internal datasets that cannot be disclosed.
- Unpublished paper/project material from sibling academic repositories.
- Raw benchmark logs that include confidential prompts, responses, or
  infrastructure metadata.

When in doubt, ask for a redacted artifact and preserve the original only in a
private local review context.
