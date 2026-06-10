# Result Review Examples

This page shows a few concrete benchmark-result review threads in the tone this
repository is trying to support.

The goal is not to give maintainers canned praise. The goal is to show how to
stay:

- specific about artifacts
- careful about claims
- useful to contributors
- honest about what the repository is and is not endorsing

## Example 1: `ready for review`

Use when the artifact chain is internally consistent and the public wording is
already reasonably disciplined.

> Thanks for sharing this result. I ran the repository-side review helper, and
> the submitted artifact set looks internally consistent enough for maintainer
> review.
>
> Automated verdict: `ready for review`
>
> What already looks good:
>
> - raw JSONL validates against the public result schema
> - manifest run ID matches the raw JSONL run ID
> - manifest hashes match the attached raw JSONL and summary CSV
> - summary CSV matches a fresh summary generated from the raw JSONL
>
> Manual maintainer checks still needed:
>
> - confirm the public issue text does not overstate the result
> - confirm the hardware/runtime notes are specific enough for another
>   contributor to attempt reproduction
>
> Current maintainer note:
>
> - this means the artifact chain is reviewable, not that the repository is
>   endorsing a broad benchmark claim yet
> - any interpretation should stay tied to the submitted hardware, software
>   stack, and stated limitations

Why this works:

- It acknowledges the contributor without inflating the result.
- It separates automated consistency from maintainer judgment.
- It keeps the project away from accidental leaderboard language.

## Example 2: `needs missing artifact`

Use when the issue is promising but still incomplete.

> Thanks for sharing this run. I checked the submission against the repository
> review flow, and it is not ready to be treated as reproducibility evidence
> yet.
>
> Automated verdict: `needs missing artifact`
>
> What should be fixed or clarified next:
>
> - the issue includes a summary table, but the raw JSONL is still missing
> - the exact manifest command is not listed yet
> - the hardware/runtime section needs the GPU model, driver/runtime, and
>   whether the host was shared
>
> Please update the issue with those items first. Once the raw JSONL, summary,
> and manifest are all present, maintainers can re-run the review helper on the
> same artifact set.
>
> Current maintainer note:
>
> - until the missing pieces are filled in, this should be treated as a local
>   observation or draft submission rather than a benchmark claim

Why this works:

- It tells the contributor exactly what to add next.
- It avoids debating the number before the evidence chain exists.
- It keeps the door open for a clean follow-up.

## Example 3: `needs claim rewrite`

Use when the artifacts are useful but the public wording is too broad.

> Thanks for sharing this result. I ran the repository-side review helper, and
> the artifact chain itself looks useful, but the current public framing needs
> to be narrowed before maintainers treat this as a benchmark discussion.
>
> Automated verdict: `needs claim rewrite`
>
> What already looks good:
>
> - raw JSONL, summary CSV, and manifest are all present
> - the summary matches a fresh summary generated from the raw JSONL
> - the run manifest points at the same artifact set being discussed
>
> What should be fixed or clarified next:
>
> - please remove wording that implies broad hardware superiority
> - please keep the conclusion tied to this exact setup rather than presenting
>   it as a general ranking
> - if this was a single local smoke run, say that explicitly in the
>   limitations section
>
> Current maintainer note:
>
> - the concern here is wording discipline rather than whether the repository
>   can parse the artifact chain
> - please keep the claim tied to the exact setup and avoid implying leaderboard
>   rank, adoption evidence, or broader framework conclusions than the attached
>   evidence supports

Why this works:

- It distinguishes claim discipline from artifact quality.
- It gives the contributor a credible path to revise without hostility.
- It protects the repository from overstated public claims.

## Practical Use

The intended maintainer flow is:

1. Run `scripts/review_result_submission.py` for the artifact checks.
2. Run `scripts/build_result_review_comment.py` for a public reply draft.
3. Use `docs/result_review_response_templates.md` when the public verdict should
   be overridden to `needs redaction` or `needs claim rewrite`.
4. Use the examples on this page to sanity-check tone before posting.
