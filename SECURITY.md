# Security Policy

## Supported Versions

`l40s-llm-bench` is currently an early-stage benchmark scaffold. Security fixes
are handled on the default branch unless the project later publishes maintained
release branches.

## Reporting a Vulnerability

Please report security-sensitive issues privately instead of opening a public
issue. If GitHub private vulnerability reporting is enabled for this repository,
use that channel. Otherwise, contact the maintainers by a private channel listed
on the repository owner profile.

Include:

- affected commit or version;
- a short description of the issue;
- reproduction steps or a minimal proof of concept;
- whether secrets, private endpoints, logs, or credentials may be exposed;
- any suggested mitigation.

## Scope

Relevant security issues may include:

- accidental logging of API keys, bearer tokens, request headers, or endpoint
  URLs;
- unsafe handling of benchmark result artifacts;
- command injection or path traversal in scripts;
- dependencies that create exploitable behavior in normal project workflows;
- guidance that would cause users to publish private model, server, or hardware
  details unintentionally.

Benchmark result disputes, unsupported performance claims, and ordinary bugs
should use the issue templates unless they expose sensitive data.

## Secrets and Benchmark Artifacts

Do not post API keys, private OpenAI-compatible endpoint URLs, internal model
names, SSH details, cloud account identifiers, or non-public hardware inventory
in issues or pull requests. Redact raw logs before sharing them publicly.
