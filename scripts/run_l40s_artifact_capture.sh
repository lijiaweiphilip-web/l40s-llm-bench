#!/usr/bin/env bash
set -euo pipefail

config="${L40S_ARTIFACT_CONFIG:-configs/workloads/vllm-l40s-smoke.yaml}"
models_config="${L40S_MODELS_CONFIG:-configs/models.yaml}"
run_id="${L40S_ARTIFACT_RUN_ID:-l40s-vllm-smoke-YYYYMMDD}"
raw_output="${L40S_ARTIFACT_RAW_OUTPUT:-results/raw/${run_id}.jsonl}"
summary_dir="${L40S_ARTIFACT_SUMMARY_DIR:-results/tables/${run_id}}"
summary_csv="${L40S_ARTIFACT_SUMMARY_CSV:-${summary_dir}/summary.csv}"
environment_output="${L40S_ENV_OUTPUT:-results/env/${run_id}.json}"
bundle_dir="${L40S_BUNDLE_DIR:-results/evidence-bundles/${run_id}}"
gpu_metrics_csv="${L40S_GPU_METRICS_CSV:-results/gpu/${run_id}/gpu-metrics.csv}"
gpu_metrics_summary="${L40S_GPU_METRICS_SUMMARY:-results/gpu/${run_id}/gpu-metrics-summary.json}"
collect_gpu_metrics="${L40S_COLLECT_GPU_METRICS:-1}"
dry_run="${L40S_ARTIFACT_DRY_RUN:-0}"
python_bin="${PYTHON:-}"
model_label="${L40S_ARTIFACT_MODEL:-}"
gpu_model="${L40S_GPU_MODEL:-}"
gpu_count="${L40S_GPU_COUNT:-1}"
workload_profile="${L40S_WORKLOAD_PROFILE:-vllm-l40s-smoke}"
backend="${L40S_BACKEND:-vllm}"
endpoint_type="${L40S_ENDPOINT_TYPE:-openai-compatible}"

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

if [[ -z "$model_label" ]]; then
  printf 'ERROR: set L40S_ARTIFACT_MODEL to the public model identifier or label\n' >&2
  exit 2
fi

if [[ "$dry_run" == "0" && -z "$gpu_model" ]]; then
  printf 'ERROR: set L40S_GPU_MODEL for a non-synthetic artifact capture\n' >&2
  exit 2
fi

mkdir -p "$(dirname "$raw_output")" "$(dirname "$environment_output")" "$summary_dir" "$(dirname "$bundle_dir")"
if [[ "$collect_gpu_metrics" != "0" ]]; then
  mkdir -p "$(dirname "$gpu_metrics_csv")"
fi

metrics_pid=""

cleanup() {
  if [[ -n "$metrics_pid" ]] && kill -0 "$metrics_pid" 2>/dev/null; then
    kill "$metrics_pid" 2>/dev/null || true
    wait "$metrics_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT

if [[ "$collect_gpu_metrics" != "0" ]]; then
  bash scripts/collect_nvidia_smi_metrics.sh "$gpu_metrics_csv" &
  metrics_pid=$!
fi

VLLM_SMOKE_CONFIG="$config" \
VLLM_MODELS_CONFIG="$models_config" \
VLLM_SMOKE_RUN_ID="$run_id" \
VLLM_SMOKE_RAW_OUTPUT="$raw_output" \
VLLM_SMOKE_SUMMARY_DIR="$summary_dir" \
VLLM_SMOKE_DRY_RUN="$dry_run" \
PYTHON="$python_bin" \
bash scripts/run_vllm_smoke_profile.sh

cleanup
metrics_pid=""

"$python_bin" scripts/collect_env.py --output "$environment_output"

gpu_metric_args=()
if [[ "$collect_gpu_metrics" != "0" && -f "$gpu_metrics_csv" ]]; then
  "$python_bin" scripts/summarize_gpu_metrics.py "$gpu_metrics_csv" --output "$gpu_metrics_summary"
  gpu_metric_args=(
    --gpu-metrics-csv "$gpu_metrics_csv"
    --gpu-metrics-summary "$gpu_metrics_summary"
  )
fi

bundle_args=(
  scripts/build_evidence_bundle.py
  --run-id "$run_id"
  --raw "$raw_output"
  --config "$config"
  --environment "$environment_output"
  --output-dir "$bundle_dir"
  --benchmark-command "VLLM_SMOKE_DRY_RUN=$dry_run VLLM_SMOKE_RUN_ID=$run_id bash scripts/run_vllm_smoke_profile.sh"
  --backend "$backend"
  --endpoint-type "$endpoint_type"
  --model "$model_label"
  --workload-profile "$workload_profile"
)

if [[ -f "$summary_csv" ]]; then
  bundle_args+=(--summary-csv "$summary_csv")
fi

if [[ "$dry_run" != "0" ]]; then
  bundle_args+=(
    --synthetic
    --limitation "Synthetic smoke artifact for workflow validation only."
    --limitation "Not a real GPU benchmark, model benchmark, or hardware comparison."
  )
else
  bundle_args+=(
    --gpu-model "$gpu_model"
    --gpu-count "$gpu_count"
    --limitation "First public smoke artifact intended to validate the collection workflow."
    --limitation "Not a leaderboard result or broad performance claim."
  )
fi

bundle_args+=("${gpu_metric_args[@]}")

"$python_bin" "${bundle_args[@]}"
"$python_bin" scripts/validate_evidence_bundle.py "$bundle_dir"

printf 'artifact capture complete\n'
printf 'raw output: %s\n' "$raw_output"
printf 'bundle dir: %s\n' "$bundle_dir"
