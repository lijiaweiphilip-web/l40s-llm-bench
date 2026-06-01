# AGENTS.md

Instructions for coding agents and maintainers working in this repository.

## Project Purpose

`l40s-llm-bench` is an early-stage scaffold for reproducible LLM inference
benchmark experiments on NVIDIA L40S and similar single-GPU setups. The current
value of the project is the evidence chain around future benchmark results:
exact commands, configs, raw JSONL, summaries, run manifests, environment
notes, and explicit limitations.

This repository does not currently claim real GPU benchmark results, production
fitness, broad adoption, or a public leaderboard.

## Default Working Rules

- Keep changes small, focused, and reviewable.
- Read nearby docs and tests before changing behavior.
- Do not revert, overwrite, or clean up work you did not make.
- Do not merge branches or push release tags unless explicitly asked.
- Do not fabricate benchmark results, adoption signals, issue history, user
  demand, citations, hardware access, or maintainer decisions.
- Prefer CPU-only validation unless a task explicitly requires real hardware.
- Keep generated result artifacts out of commits unless a maintainer explicitly
  approves a small, labeled fixture.

## Safe Local Commands

These commands are safe for routine local checks because they do not require
remote APIs, GPUs, credentials, or model downloads:

```powershell
python -m pip install -r requirements-dev.txt
python scripts\bench_openai_compatible.py --dry-run
python scripts\summarize_results.py --input results\raw\dry_run.jsonl --output-dir results\tables
python scripts\check_jsonl_compat.py --input results\raw\dry_run.jsonl
python scripts\run_sanity_checks.py --repeats 1
python scripts\build_run_manifest.py --run-id fake-server-smoke-run --config configs\fake_server_matrix.yaml --raw results\raw\fake_server_streaming.jsonl --summary results\tables\summary.csv
```

For docs-only changes, prefer lightweight checks such as reading the rendered
Markdown diff and confirming links or command names. Do not run long benchmark
or GPU checks just to validate prose.

## Test Commands

Use the smallest check that covers the change:

```powershell
python -m pytest -q
```

For benchmark client, schema, summary, manifest, or compatibility changes, add
the relevant dry-run or fake-server command from the safe command list.

For release readiness, use the CPU-only verification path from
`docs/release-checklist.md`.

## Release Commands

Only run release commands when the maintainer has explicitly requested a
release. Do not publish tags or GitHub releases as part of ordinary cleanup.

Expected release verification before publishing:

```powershell
python --version
python -m pytest -q
python scripts\bench_openai_compatible.py --config configs\generated_workload_matrix.yaml --dry-run --stream --output $env:TEMP\l40s-workload-profiles-dry-run.jsonl
python scripts\summarize_results.py --input $env:TEMP\l40s-workload-profiles-dry-run.jsonl --output-dir $env:TEMP\l40s-tables
python scripts\run_sanity_checks.py --repeats 1 --output $env:TEMP\l40s-sanity-checks.jsonl --report $env:TEMP\l40s-sanity-checks.md
```

Publish only after CI is green, release notes are final, and the diff has been
checked for private paths, credentials, unpublished benchmark claims, and
generated artifacts.

## No-Go Zones

Do not touch or inspect these areas unless the user explicitly asks:

- Sibling repositories or private projects under
  `C:\Users\56491\OneDrive\文档\学术`.
- Zotero libraries, PDFs, BibTeX exports, or paper drafts outside this repo.
- NTU GPU scripts, cluster paths, queue state, credentials, and private
  datasets outside this repo.
- Local virtual environments, caches, `.git`, `.codex`, `.pytest_cache`, and
  generated `results/` outputs except when a task is specifically about those
  outputs.
- Private endpoints, bearer tokens, API keys, hostnames, usernames, job IDs, or
  confidential infrastructure details.

If a benchmark submission includes sensitive material, ask for a redacted
version or keep the material local and summarize only the non-secret evidence.

## Synthetic, Fake-Server, and Real-Server Labeling

Always label run type clearly:

- `dry-run`: synthetic records that test the pipeline only.
- `fake-server`: controlled local OpenAI-compatible server data that validates
  measurement mechanics such as TTFT and TPOT.
- `real-server`: measurements from an actual model-serving stack.

Do not describe dry-run or fake-server output as model performance, GPU
performance, user adoption, or benchmark leadership. Real-server numbers still
need commands, configs, raw JSONL, summaries, manifest, hardware/runtime notes,
and limitations before they are treated as benchmark evidence.

## Branch Naming

Use short, descriptive branches:

- `docs/<topic>`
- `chore/<topic>`
- `fix/<topic>`
- `feat/<topic>`
- `release/<version>`

Use hyphenated lowercase slugs, for example
`chore/agents-maintainer-playbook`. Do not work directly on `main` for
multi-file or reviewable changes.

## Pull Request Style

Follow `.github/PULL_REQUEST_TEMPLATE.md`:

- State the focused change and why it helps this benchmark scaffold.
- Mark the correct scope, especially docs, governance, benchmark config, code,
  or result artifacts.
- List verification commands, or state why a docs-only change did not need
  heavy checks.
- Say explicitly whether the PR contains benchmark claims.
- Include limitations: what reviewers should not infer from the change.
- Confirm no secrets, private paths, unsupported results, or fabricated
  adoption claims were included.

## Maintainer References

- `README.md`: project scope, reproducibility contract, current status.
- `CONTRIBUTING.md`: contributor expectations and result submission basics.
- `docs/ten_minute_smoke_run.md`: first safe validation path.
- `docs/release-checklist.md`: release verification path.
- `docs/maintenance/maintainer-playbook.md`: maintainer triage and release
  operations.

<!-- codex-token-skill-bootstrap:start -->
## Token Cost Awareness

Use local project memory before rereading long chat history.

Trigger `token-cost-router` early when a task smells token-expensive:
screenshots/images, long logs, large files, browser traces, repeated polling,
Zotero/citations, subagents, external model review, GitHub Cloud
Agent/Copilot offload, repo-wide audits/refactors, CI failures, or cost
questions.

### Screenshot / Image Trigger

Treat screenshot handling as high-sensitivity: if the task includes a
screenshot, image upload, pasted base64, `.png`, `.jpg`, browser visual state,
UI capture, VPN/login screen, chart/table screenshot, Xiaohongshu page,
Playwright screenshot, `view_image`, or `input_image`, trigger
`screenshot-ocr-gate` immediately.

Default path: prefer DOM/text extraction for web pages; otherwise save the
image locally, run OCR/cache via `screenshot-ocr-gate`, read `ocr.md` or
`ocr.json`, and inspect the raw image only when layout, visual design, or
low-confidence OCR makes it necessary. Never paste raw base64 into Codex
context.

Before `view_image` on a large screenshot, rendered PDF/page image,
`render_check` page, contact sheet, video frame, or repeated visual target,
create a visual packet with
`screenshot-ocr-gate/scripts/prepare_visual_packet.py` and inspect
`visual_packet.md`, `preview.jpg`, or one relevant tile instead of the full
source image.

Before long-chat compaction, soft relay, or project handoff, make sure old
screenshots are represented by OCR/cache artifacts and local file links rather
than raw `input_image` or `data:image` history.

- Use `paper-session-relay` and `.paper/session-relay/current.md` when the chat
  gets long, laggy, crosses a day boundary, or changes stage.
- Use `screenshot-ocr-gate` before sending screenshots, pasted base64, image
  attachments, or visual captures into context.
- Use `tool-output-budget-guard` for tests, compilers, shell output, long file
  reads, and noisy logs.
- Use `gpu-kaggle-status-digest` for repeated GPU, Kaggle, SLURM, or queue
  polling.
- Use `zotero-citation-snapshot` before rescanning BibTeX, Zotero, DOI, and
  citation-heavy context.
- Use `warroom-subagent-budget` before sending context to subagents, Gemini,
  Claude, or DeepSeek.
- Use `github-cloud-agent-router` for GitHub-backed repo-wide code audits, CI
  failures, mechanical refactors, docs cleanup, or bounded PR-sized tasks that
  can be delegated as a GitHub issue.
- Use `automation-token-sentinel` for recurring scans so no-change runs stay
  local.
- Use `codex-cost-observer` when checking what burned tokens or what to
  optimize next.
- Use `token-cost-router` as the first routing layer when several token-saving
  tools might apply.

<!-- codex-token-skill-bootstrap:end -->
