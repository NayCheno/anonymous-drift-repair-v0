#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def primary_label(record: dict[str, Any]) -> str:
    drift_types = record.get("gold", {}).get("drift_types", [])
    return drift_types[0] if drift_types else "NONE"


def balanced_sample(records: list[dict[str, Any]], target_size: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_label[primary_label(record)].append(record)
    for rows in by_label.values():
        rng.shuffle(rows)

    selected = []
    labels = sorted(by_label)
    cursor = {label: 0 for label in labels}
    while len(selected) < target_size:
        progressed = False
        for label in labels:
            if len(selected) >= target_size:
                break
            index = cursor[label]
            if index < len(by_label[label]):
                selected.append(by_label[label][index])
                cursor[label] += 1
                progressed = True
        if not progressed:
            break
    selected.sort(key=lambda r: r["id"])
    return selected


def annotation_item(record: dict[str, Any], annotator: str, review_round: str, double_annotated: bool) -> dict[str, Any]:
    return {
        "id": record["id"],
        "annotator": annotator,
        "review_round": review_round,
        "double_annotated": double_annotated,
        "source_example_id": record.get("metadata", {}).get("source_example_id", ""),
        "turns": record["turns"],
        "retrieved": record["retrieved"],
        "tool_outputs": record["tool_outputs"],
        "candidate_response": record["candidate_response"],
        "labels_to_fill": {
            "drift_types": [],
            "severity": None,
            "expected_repair": "",
            "task_success": None,
            "notes": "",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a human validation annotation packet.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-size", type=int, default=240)
    parser.add_argument("--double-annotate-rate", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    records = balanced_sample(load_jsonl(Path(args.input)), args.target_size, args.seed)
    double_n = int(round(len(records) * args.double_annotate_rate))
    double_ids = {row["id"] for row in records[:double_n]}

    packet = []
    annotator_a = []
    annotator_b = []
    answer_key = []
    for index, record in enumerate(records):
        packet.append(
            {
                "id": record["id"],
                "primary_label": primary_label(record),
                "source_example_id": record.get("metadata", {}).get("source_example_id", ""),
                "double_annotated": record["id"] in double_ids,
            }
        )
        double_annotated = record["id"] in double_ids
        item_a = annotation_item(record, "annotator_a", "v0_human_validation", double_annotated)
        annotator_a.append(item_a)
        if double_annotated:
            annotator_b.append(annotation_item(record, "annotator_b", "v0_human_validation", double_annotated))
        answer_key.append(
            {
                "id": record["id"],
                "gold_drift_types": record.get("gold", {}).get("drift_types", []),
                "gold_expected_action": record.get("gold", {}).get("expected_action", ""),
                "gold_task_success": record.get("gold", {}).get("task_success"),
                "primary_label": primary_label(record),
                "double_annotated": record["id"] in double_ids,
            }
        )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "human_validation_packet_v0.jsonl", packet)
    write_jsonl(out_dir / "human_validation_annotator_a_v0.jsonl", annotator_a)
    write_jsonl(out_dir / "human_validation_annotator_b_v0.jsonl", annotator_b)
    write_jsonl(out_dir / "human_validation_answer_key_v0.jsonl", answer_key)

    all_label_counts: dict[str, int] = defaultdict(int)
    for record in records:
        labels = record.get("gold", {}).get("drift_types", []) or ["NONE"]
        for label in labels:
            all_label_counts[label] += 1

    summary = {
        "input": args.input,
        "target_size": args.target_size,
        "n_selected": len(records),
        "double_annotate_rate": args.double_annotate_rate,
        "n_double_annotated": len(double_ids),
        "n_annotator_a": len(annotator_a),
        "n_annotator_b": len(annotator_b),
        "seed": args.seed,
        "primary_label_counts": dict(sorted((label, sum(1 for r in records if primary_label(r) == label)) for label in {primary_label(r) for r in records})),
        "all_gold_label_counts": dict(sorted(all_label_counts.items())),
        "files": [
            "human_validation_packet_v0.jsonl",
            "human_validation_annotator_a_v0.jsonl",
            "human_validation_annotator_b_v0.jsonl",
            "human_validation_answer_key_v0.jsonl",
        ],
    }
    (out_dir / "human_validation_summary_v0.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
