# Evidence Bundle Quickstart

This page is the shortest path from a real run artifact set to a reviewable
bundle for issue `#17`.

If you want the shortest end-to-end shell path instead of manual step-by-step
commands, use `scripts/run_l40s_artifact_capture.sh`.

## End-To-End Runbook

```bash
L40S_ARTIFACT_RUN_ID=l40s-vllm-smoke-YYYYMMDD \
L40S_ARTIFACT_MODEL=<public-model-id> \
L40S_GPU_MODEL=L40S \
L40S_GPU_COUNT=1 \
bash scripts/run_l40s_artifact_capture.sh
```

That one command does four things:

1. runs the bounded vLLM smoke profile
2. collects environment metadata
3. summarizes optional GPU metrics if they were captured
4. builds and validates an evidence bundle under `results/evidence-bundles/`

## Minimal Inputs

Have these ready first:

- raw JSONL from the benchmark client
- benchmark config file
- environment JSON or a machine where `scripts/collect_env.py` can run
- optional GPU metrics CSV and GPU metrics summary JSON

## Bundle Build

Example command:

```bash
python scripts/build_evidence_bundle.py \
  --run-id l40s-vllm-smoke-YYYYMMDD \
  --raw results/raw/l40s-vllm-smoke-YYYYMMDD.jsonl \
  --config configs/workloads/vllm-l40s-smoke.yaml \
  --collect-environment \
  --output-dir examples/evidence-bundles/l40s-vllm-smoke-YYYYMMDD \
  --benchmark-command "VLLM_SMOKE_DRY_RUN=0 VLLM_SMOKE_RUN_ID=l40s-vllm-smoke-YYYYMMDD bash scripts/run_vllm_smoke_profile.sh" \
  --backend vllm \
  --model <public-model-id> \
  --workload-profile vllm-l40s-smoke \
  --gpu-model L40S \
  --gpu-count 1 \
  --gpu-metrics-csv results/gpu/gpu-metrics.csv \
  --gpu-metrics-summary results/gpu/gpu-metrics-summary.json \
  --limitation "First public smoke artifact intended to validate the collection workflow." \
  --limitation "Not a leaderboard result or broad performance claim."
```

## Validation

After the bundle is written:

```bash
python scripts/validate_evidence_bundle.py \
  examples/evidence-bundles/l40s-vllm-smoke-YYYYMMDD
```

## Next Links

- Real artifact requirements:
  `docs/maintenance/real-l40s-artifact-needed.md`
- vLLM smoke path:
  `docs/vllm-l40s-smoke-run.md`
- End-to-end capture script:
  `scripts/run_l40s_artifact_capture.sh`
- GPU metrics guide:
  `docs/gpu-metrics.md`
- Evidence bundle rules:
  `docs/reproducibility-evidence-bundle.md`
