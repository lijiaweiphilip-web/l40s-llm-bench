#!/usr/bin/env bash
set -euo pipefail

config="${VLLM_SMOKE_CONFIG:-configs/workloads/vllm-l40s-smoke.yaml}"
models_config="${VLLM_MODELS_CONFIG:-configs/models.yaml}"
run_id="${VLLM_SMOKE_RUN_ID:-vllm-l40s-smoke-dry-validation}"
raw_output="${VLLM_SMOKE_RAW_OUTPUT:-results/raw/${run_id}.jsonl}"
summary_dir="${VLLM_SMOKE_SUMMARY_DIR:-results/tables}"
dry_run="${VLLM_SMOKE_DRY_RUN:-1}"
python_bin="${PYTHON:-}"

if [[ -z "$python_bin" ]]; then
  if command -v python >/dev/null 2>&1; then
    python_bin="python"
  elif command -v python3 >/dev/null 2>&1; then
    python_bin="python3"
  elif command -v py >/dev/null 2>&1; then
    python_bin="py"
  else
    printf 'ERROR: set PYTHON to a Python executable before running this script\n' >&2
    exit 2
  fi
fi

dry_run_args=()
if [[ "$dry_run" != "0" ]]; then
  dry_run_args=(--dry-run)
fi

"$python_bin" scripts/bench_openai_compatible.py \
  --config "$config" \
  --models-config "$models_config" \
  --run-id "$run_id" \
  --output "$raw_output" \
  --stream \
  "${dry_run_args[@]}"

"$python_bin" scripts/validate_result.py "$raw_output"
"$python_bin" scripts/summarize_results.py --input "$raw_output" --output-dir "$summary_dir"

printf 'vLLM/L40S smoke profile wrote %s and summaries under %s\n' \
  "$raw_output" \
  "$summary_dir"
