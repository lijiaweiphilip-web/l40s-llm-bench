# Codex for Open Source Application Readiness Scorecard

Date: 2026-06-04

This scorecard is a maintainer-facing snapshot for `l40s-llm-bench`. It is
intentionally conservative and does not claim independent external adoption or
real GPU benchmark results.

| Area | Score | Evidence | Next improvement |
| --- | ---: | --- | --- |
| Project clarity | 4/5 | README, smoke-run docs, troubleshooting, result policy, evidence bundle docs, GPU metrics guide, and vLLM smoke-profile docs explain the scope and non-claims clearly. | Add one real public artifact bundle after hardware access exists. |
| Maintainer role | 5/5 | Public releases, issue-linked PRs, maintainer playbook, release notes, and evidence docs show active scoped stewardship. | Continue handling issue-linked follow-ups and keep limitations explicit. |
| Release cadence | 5/5 | `v0.1.0`, `v0.1.1`, and `v0.1.2` are published. `v0.1.2` is the current public release. | Publish the next release only after a real new signal lands. |
| CI and quality | 5/5 | Main CI succeeded on commit `2c8843b`, and the repo now includes a dedicated reviewer smoke proof workflow plus passing tests for schema, evidence bundles, GPU metrics parsing, and vLLM profile dry validation. | Keep public workflows CPU-only unless a safe public GPU runner exists. |
| Issue triage | 5/5 | Issues #2, #3, #4, #5, #6, and #7 were closed through merged PRs. Open issues are now focused on the remaining real-world gaps: #12 and #17. | Convert the next real feedback or hardware artifact into one follow-up PR. |
| Reproducibility | 5/5 | Evidence bundle checklist/rubric, synthetic bundle, validator, run manifests, GPU metrics guide, vLLM profile, and reviewer smoke proof pack create a strong public reproducibility trail. | Add one real artifact bundle when hardware exists. |
| Adoption and community | 2/5 | Issue #12 is a truthful public tester ask, but no independently confirmed external tester interaction is available to claim yet. | Obtain one real public tester interaction or a real hardware artifact. |
| Security and governance | 4/5 | License, contribution guide, code of conduct, security policy, support file, issue templates, PR template, AGENTS, and maintainer playbook are present. | Keep redaction guidance strong for any future real artifact. |
| Current risks | 4/5 | The repo is honest about synthetic validation, missing external feedback, and missing real GPU evidence. | Do not use an "80% readiness" framing until G9 or G10 is complete. |
| Next two-week plan | 4/5 | Remaining work is well bounded: independent feedback, or one real L40S/vLLM smoke artifact. | Convert whichever real-world signal arrives first into a public artifact PR. |

## Overall Verdict

Current readiness: **strong early-stage maintainer package with public
reproducibility proof, but not yet honest 80% readiness**.

The Codex-executable hardening work is now materially complete for the current
plan:

- PR #14 closed issue #2 with reproducibility evidence bundle validation.
- PR #15 closed issue #4 with GPU metrics preparation and parser coverage.
- PR #16 closed issue #3 with the vLLM/L40S smoke profile.
- PR #18 finalized the `v0.1.2` evidence packet and release framing.
- PR #19 tightened the public feedback path and triage policy.
- PR #20 documented the next backend sequence and closed issue #5.
- The reviewer smoke proof pack now gives one reviewer-oriented artifact path
  for CI-backed CPU-only verification.

This is enough to support an early-stage maintainer framing. It is still not
enough to claim the stronger "~80%" readiness framing without either
independent public feedback or one real hardware artifact bundle.

## Recommended Evidence Links

- Repository: https://github.com/lijiaweiphilip-web/l40s-llm-bench
- Latest release: https://github.com/lijiaweiphilip-web/l40s-llm-bench/releases/tag/v0.1.2
- Reproducibility bundle PR: https://github.com/lijiaweiphilip-web/l40s-llm-bench/pull/14
- GPU metrics PR: https://github.com/lijiaweiphilip-web/l40s-llm-bench/pull/15
- vLLM/L40S profile PR: https://github.com/lijiaweiphilip-web/l40s-llm-bench/pull/16
- Evidence and release prep PR: https://github.com/lijiaweiphilip-web/l40s-llm-bench/pull/18
- Feedback-path hardening PR: https://github.com/lijiaweiphilip-web/l40s-llm-bench/pull/19
- Backend sequencing PR: https://github.com/lijiaweiphilip-web/l40s-llm-bench/pull/20
- Reviewer smoke proof doc: `docs/maintenance/reviewer-smoke-proof.md`
- Early tester issue: https://github.com/lijiaweiphilip-web/l40s-llm-bench/issues/12
- Hardware-needed issue: https://github.com/lijiaweiphilip-web/l40s-llm-bench/issues/17

## 80-Readiness Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| G1 reproducibility evidence bundle | Complete | PR #14, issue #2 closed |
| G2 GPU metrics guide | Complete | PR #15, issue #4 closed |
| G3 vLLM/L40S smoke profile | Complete | PR #16, issue #3 closed |
| G4 `v0.1.2` release | Complete | Published release on 2026-06-02 |
| G5 evidence packet and scorecard | Complete | PR #18 and current maintenance docs |
| G6 GitHub profile signal | Complete | Public profile foregrounds `l40s-llm-bench` |
| G7 hardware/tester ask | Complete | Issues #12 and #17 |
| G8 conservative claims | Complete | Docs and releases avoid adoption or GPU overclaims |
| G9 external feedback | Missing | No independently confirmed public tester interaction yet |
| G10 real L40S artifact | Missing | Issue #17 is still an ask, not an artifact |
| G11 reviewer smoke proof pack | Complete | `scripts/run_reviewer_smoke_pack.py` and reviewer workflow |

## Application Recommendation

Apply if the framing is "strong early-stage maintainer package with public
reproducibility proof." Wait if the goal is specifically to maximize the
"~80%" framing. The remaining gap is no longer internal scaffolding. It is one
real outside signal: independent public feedback or one real L40S/vLLM smoke
artifact bundle.
