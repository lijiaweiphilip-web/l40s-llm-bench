# Community Feedback

This project is early-stage. Feedback is most useful when it improves
reproducibility, makes benchmark claims harder to overstate, or catches missing
metadata before GPU time is spent.

## Useful Feedback

- A smoke-run result that includes commands, raw JSONL, summaries, and a run
  manifest.
- A report that a documented command failed on a clean environment.
- A missing field needed to reproduce a run.
- A confusing metric name or schema field.
- A workload shape that should be represented before real L40S runs.
- A limitation that should be made more visible.

## Result Reports

When sharing a result, include:

- repository commit or release reference
- exact benchmark command
- benchmark config and model config
- raw JSONL path or artifact
- summary CSV or Markdown
- run manifest
- hardware, driver, CUDA, framework, model, and serving-flag notes
- repeated-run policy and any failed, timeout, skipped, or OOM cases

Please label dry-run and fake-server outputs as harness checks. They are not
GPU benchmark results.

## Questions To Ask Before Trusting A Number

- Was the run real, dry-run, or fake-server validation?
- Which model revision and serving framework version were used?
- What hardware, driver, CUDA, and serving flags were used?
- Are raw JSONL records available?
- Are failed requests included in the summary?
- Is there a run manifest tying the artifacts together?
- Does the result explain what it does not prove?

## Current Boundaries

The repository does not yet publish real GPU benchmark claims, adoption claims,
or framework rankings. Feedback that assumes those claims already exist should
be reframed as a request for the metadata or experiment needed to support them.

For first-user dry-run and fake-server reports, maintainers use
`docs/feedback-triage-policy.md` to separate documentation friction, setup
failures, harness failures, artifact gaps, real-run requests, and out-of-scope
claims.
