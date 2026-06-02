# Artifact Review Rubric

Use this rubric when reviewing a benchmark artifact before treating it as public
evidence.

| Area | Pass | Needs follow-up | Reject as evidence |
| --- | --- | --- | --- |
| Scope | Bundle states whether it is synthetic, smoke, or real GPU evidence. | Scope is present but vague. | Summary is presented without scope or limitations. |
| Raw data | Raw JSONL exists and validates. | Raw data exists but has minor schema or metadata gaps. | Raw data is missing or cannot be parsed. |
| Config | Config or command is reproducible from the repo. | Config is present but some flags are ambiguous. | Command/config is missing. |
| Environment | Runtime and hardware notes are present. | Notes are incomplete but recoverable. | Hardware/runtime context is absent for a real result. |
| GPU telemetry | Real GPU runs include telemetry or a stated reason it is missing. | Telemetry exists but lacks sampling details. | GPU performance is claimed without telemetry. |
| Counts | Manifest, summary, and raw records agree on request counts. | Counts need clarification. | Counts conflict and cannot be reconciled. |
| Limitations | Limitations prevent overclaiming. | Limitations are too generic. | Artifact implies broader performance conclusions than it supports. |
| Safety | No secrets, private paths, or sensitive identifiers. | Needs light redaction. | Contains secrets or private infrastructure details. |

## Reviewer Notes

For synthetic fake-server bundles, the expected decision is usually "Pass as
tooling evidence" and "Reject as GPU performance evidence." That is intentional:
synthetic artifacts keep the harness honest before real GPU time is spent.
