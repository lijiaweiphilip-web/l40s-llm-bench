import csv
import json
from pathlib import Path

from scripts.summarize_gpu_metrics import main as gpu_metrics_main
from scripts.summarize_gpu_metrics import summarize_gpu_metrics


SAMPLE_CSV = Path("examples/gpu-metrics/nvidia-smi-sample.csv")


def test_gpu_metrics_sample_summarizes() -> None:
    summary = summarize_gpu_metrics(SAMPLE_CSV)

    assert summary["sample_count"] == 3
    assert summary["gpu_count"] == 1
    gpu = summary["gpus"][0]
    assert gpu["gpu_uuid"] == "GPU-synthetic-l40s-0001"
    assert gpu["power_draw_w"]["max"] == 130.0
    assert gpu["utilization_gpu_percent"]["avg"] == 58.333
    assert gpu["memory_used_mib"]["max"] == 12150.0


def test_gpu_metrics_cli_writes_output(tmp_path: Path) -> None:
    output = tmp_path / "gpu-metrics-summary.json"

    assert gpu_metrics_main([str(SAMPLE_CSV), "--output", str(output)]) == 0

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["sample_count"] == 3
    assert loaded["gpus"][0]["timestamp_end"] == "2026-06-01T00:00:02Z"


def test_gpu_metrics_rejects_missing_required_columns(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "gpu_name"])
        writer.writeheader()
        writer.writerow({"timestamp": "2026-06-01T00:00:00Z", "gpu_name": "fixture"})

    assert gpu_metrics_main([str(path)]) == 2
