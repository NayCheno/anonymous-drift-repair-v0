#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.dataset_adapters import load_jsonl, save_jsonl
from drift_repair.pipeline import SageRPipeline
from drift_repair.metrics import compute_metrics


def main() -> None:
    data_path = ROOT / "data" / "toy_examples.jsonl"
    out_path = ROOT / "results" / "smoke_predictions.jsonl"
    metrics_path = ROOT / "results" / "smoke_metrics.json"

    examples = load_jsonl(data_path)
    pipe = SageRPipeline()
    records = []
    for ex in examples:
        result = pipe.run_one(ex).to_dict()
        result["gold"] = ex.gold
        records.append(result)

    save_jsonl(out_path, records)
    metrics = compute_metrics(records)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Wrote predictions: {out_path}")
    print(f"Wrote metrics: {metrics_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
