# Fake-Server Smoke Evidence Bundle

This bundle is a tiny synthetic artifact for validating the evidence bundle
format. It uses fake-server style records and exists only to test the path from
raw JSONL to summary, manifest, environment notes, and validator checks.

It is not a model benchmark, GPU benchmark, hardware comparison, vLLM result, or
L40S performance claim.

Validate it with:

```bash
python scripts/validate_evidence_bundle.py examples/evidence-bundles/fake-server-smoke
```

The bundle includes one successful streaming record and one synthetic HTTP-error
record so reviewers can see both success and failure accounting in the evidence
package.
