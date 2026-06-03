#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DRIFT_TYPES = [
    "G1_goal_drift",
    "G2_constraint_drift",
    "E1_evidence_drift",
    "E2_retrieval_drift",
    "T1_tool_state_drift",
    "M1_memory_drift",
    "U1_abstention_drift",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def grouped_records(sage_r_path: Path, baselines_path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped = {"sage_r": load_jsonl(sage_r_path)}
    for record in load_jsonl(baselines_path):
        grouped.setdefault(record.get("baseline", "unknown"), []).append(record)
    return grouped


def score_type(records: list[dict[str, Any]], drift_type: str) -> dict[str, int | float]:
    tp = fp = fn = support = 0
    for record in records:
        gold = set(record.get("gold", {}).get("drift_types", []))
        pred = set(record.get("diagnosis", {}).get("drift_types", []))
        if drift_type in gold:
            support += 1
        if drift_type in gold and drift_type in pred:
            tp += 1
        elif drift_type not in gold and drift_type in pred:
            fp += 1
        elif drift_type in gold and drift_type not in pred:
            fn += 1
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "support": support,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build drift-type breakdown table.")
    parser.add_argument("--sage-r", required=True)
    parser.add_argument("--baselines", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = []
    for system, records in sorted(grouped_records(Path(args.sage_r), Path(args.baselines)).items()):
        for drift_type in DRIFT_TYPES:
            scores = score_type(records, drift_type)
            rows.append(
                {
                    "system": system,
                    "drift_type": drift_type,
                    "support": scores["support"],
                    "tp": scores["tp"],
                    "fp": scores["fp"],
                    "fn": scores["fn"],
                    "precision": f"{scores['precision']:.4f}",
                    "recall": f"{scores['recall']:.4f}",
                    "f1": f"{scores['f1']:.4f}",
                }
            )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
