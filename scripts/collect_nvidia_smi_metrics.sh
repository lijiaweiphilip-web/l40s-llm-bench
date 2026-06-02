#!/usr/bin/env bash
set -euo pipefail

output="${1:-results/gpu/gpu-metrics.csv}"
samples="${GPU_METRICS_SAMPLES:-60}"
interval_seconds="${GPU_METRICS_INTERVAL_SECONDS:-1}"

query_fields=(
  "timestamp"
  "name"
  "uuid"
  "driver_version"
  "cuda_version"
  "power.draw"
  "power.limit"
  "temperature.gpu"
  "utilization.gpu"
  "utilization.memory"
  "memory.used"
  "memory.total"
  "clocks.sm"
  "clocks.mem"
  "pcie.link.gen.current"
  "pcie.link.width.current"
)

header="timestamp,gpu_name,gpu_uuid,driver_version,cuda_version,power.draw,power.limit,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,clocks.sm,clocks.mem,pcie.link.gen.current,pcie.link.width.current"
query=$(IFS=,; echo "${query_fields[*]}")

mkdir -p "$(dirname "$output")"
printf '%s\n' "$header" > "$output"

for _ in $(seq 1 "$samples"); do
  nvidia-smi --query-gpu="$query" --format=csv,noheader,nounits >> "$output"
  sleep "$interval_seconds"
done

printf 'wrote %s sample batch(es) to %s\n' "$samples" "$output"
