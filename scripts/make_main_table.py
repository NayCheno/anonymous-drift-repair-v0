#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from drift_repair.metrics import compute_metrics


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def flatten_metrics(system: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = compute_metrics(records)
    return {
        "system": system,
        "n_examples": int(metrics.get("n_examples", 0)),
        "drift_type_exact_match": f"{metrics.get('drift_type_exact_match', 0.0):.4f}",
        "micro_precision": f"{metrics.get('drift_type_micro_precision', 0.0):.4f}",
        "micro_recall": f"{metrics.get('drift_type_micro_recall', 0.0):.4f}",
        "micro_f1": f"{metrics.get('drift_type_micro_f1', 0.0):.4f}",
        "repair_rate": f"{metrics.get('repair_rate', 0.0):.4f}",
        "over_repair_rate": f"{metrics.get('over_repair_rate', 0.0):.4f}",
        "avg_extra_tokens": f"{metrics.get('avg_extra_tokens', 0.0):.2f}",
        "avg_extra_retrievals": f"{metrics.get('avg_extra_retrievals', 0.0):.4f}",
        "avg_extra_tool_calls": f"{metrics.get('avg_extra_tool_calls', 0.0):.4f}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a main result table from prediction JSONL files.")
    parser.add_argument("--sage-r", required=True, help="SAGE-R prediction JSONL.")
    parser.add_argument("--baselines", required=True, help="Baseline prediction JSONL with a baseline field.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = [flatten_metrics("sage_r", load_jsonl(Path(args.sage_r)))]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in load_jsonl(Path(args.baselines)):
        grouped[record.get("baseline", "unknown")].append(record)
    for baseline in sorted(grouped):
        rows.append(flatten_metrics(baseline, grouped[baseline]))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
