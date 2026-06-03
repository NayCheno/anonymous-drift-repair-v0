#!/usr/bin/env python
from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path


SCHEMA_VERSION = "driftbench_v0.1"
PERTURBATION_BY_DRIFT = {
    "G1_goal_drift": "goal_shift",
    "G2_constraint_drift": "constraint_update",
    "E1_evidence_drift": "unsupported_or_contradicted_evidence",
    "E2_retrieval_drift": "stale_retrieval",
    "T1_tool_state_drift": "tool_observation_conflict",
    "M1_memory_drift": "memory_supersession",
    "U1_abstention_drift": "unanswerable_or_underspecified",
}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def primary_perturbation(gold: dict) -> str:
    drift_types = gold.get("drift_types", [])
    if not drift_types:
        return "clean_control"
    return PERTURBATION_BY_DRIFT.get(drift_types[0], "mixed_state_drift")


def variant_record(template: dict, index: int, source_index: int, seed: int) -> dict:
    record = copy.deepcopy(template)
    source_id = template["id"]
    record["id"] = f"driftbench_v0_{index:04d}__{source_id}"
    record.setdefault("metadata", {})
    record["metadata"].update(
        {
            "benchmark": "DriftBench",
            "schema_version": SCHEMA_VERSION,
            "construction": "toy_equivalent_template_expansion",
            "source_example_id": source_id,
            "source_template_index": source_index,
            "variant_index": index,
            "seed": seed,
            "split": "draft",
            "perturbation": primary_perturbation(record.get("gold", {})),
            "manual_check_status": "unchecked",
        }
    )
    record.setdefault("gold", {})
    record["gold"].setdefault("schema_version", SCHEMA_VERSION)
    record["gold"].setdefault("annotation_status", "draft")
    return record


def build_dataset(templates: list[dict], target_size: int, seed: int) -> list[dict]:
    if target_size < len(templates):
        raise ValueError("target_size must be at least the number of input templates")
    rng = random.Random(seed)
    shuffled = list(templates)
    rng.shuffle(shuffled)
    records = []
    for index in range(target_size):
        source_index = index % len(shuffled)
        records.append(variant_record(shuffled[source_index], index, source_index, seed))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic DriftBench v0 JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--target-size", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)

    templates = load_jsonl(inp)
    records = build_dataset(templates, target_size=args.target_size, seed=args.seed)
    write_jsonl(out, records)

    print(f"Wrote {len(records)} DriftBench v0 examples: {out}")
    print(f"schema_version={SCHEMA_VERSION} seed={args.seed}")


if __name__ == "__main__":
    main()
