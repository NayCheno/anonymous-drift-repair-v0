#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.dataset_adapters import load_jsonl, save_jsonl
from drift_repair.detectors import (
    EvidenceAbstentionModule,
    GoalConstraintModule,
    MemoryDriftModule,
    RetrievalDriftModule,
    RuleBasedDriftDetector,
    ToolStateModule,
)
from drift_repair.metrics import compute_metrics
from drift_repair.pipeline import SageRPipeline
from drift_repair.repair import TypedRepairPolicy
from drift_repair.schemas import Diagnosis, Example, RepairResult


ALL_MODULES = [
    GoalConstraintModule(),
    RetrievalDriftModule(),
    EvidenceAbstentionModule(),
    ToolStateModule(),
    MemoryDriftModule(),
]


VARIANTS = {
    "full_sage_r": [m.name for m in ALL_MODULES],
    "wo_goal_constraint": ["retrieval", "evidence_abstention", "tool_state", "memory"],
    "wo_retrieval": ["goal_constraint", "evidence_abstention", "tool_state", "memory"],
    "wo_evidence_abstention": ["goal_constraint", "retrieval", "tool_state", "memory"],
    "wo_tool_state": ["goal_constraint", "retrieval", "evidence_abstention", "memory"],
    "wo_memory": ["goal_constraint", "retrieval", "evidence_abstention", "tool_state"],
    "diagnose_only": [m.name for m in ALL_MODULES],
}


class DiagnoseOnlyRepairPolicy(TypedRepairPolicy):
    def repair(self, ex: Example, diagnosis: Diagnosis) -> RepairResult:
        return RepairResult(
            example_id=ex.id,
            original_response=ex.candidate_response,
            repaired_response=ex.candidate_response,
            diagnosis=diagnosis,
            repaired=False,
            cost={"extra_tokens": 0, "extra_retrievals": 0, "extra_tool_calls": 0},
            repair_trace={
                "policy": "diagnose_only",
                "action": "no_repair",
                "diagnosis_types": diagnosis.drift_types,
                "steps": ["diagnose_without_repair"],
                "stop_condition": "repair_disabled",
                "rationale": "Ablation disables repair actions while keeping diagnosis.",
            },
        )


def modules_for(names: list[str]):
    by_name = {module.name: module for module in ALL_MODULES}
    return [by_name[name] for name in names]


def run_variant(examples: list[Example], variant: str) -> list[dict[str, Any]]:
    pipe = SageRPipeline()
    pipe.detector = RuleBasedDriftDetector(modules=modules_for(VARIANTS[variant]))
    if variant == "diagnose_only":
        pipe.repair_policy = DiagnoseOnlyRepairPolicy()

    records = []
    for ex in examples:
        record = pipe.run_one(ex).to_dict()
        record["variant"] = variant
        record["gold"] = ex.gold
        records.append(record)
    return records


def table_row(variant: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = compute_metrics(records)
    return {
        "variant": variant,
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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic SAGE-R ablations.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--predictions-output", required=True)
    parser.add_argument("--table-output", required=True)
    args = parser.parse_args()

    examples = load_jsonl(args.dataset)
    all_records = []
    table_rows = []
    for variant in VARIANTS:
        records = run_variant(examples, variant)
        all_records.extend(records)
        table_rows.append(table_row(variant, records))

    save_jsonl(args.predictions_output, all_records)
    write_csv(Path(args.table_output), table_rows)
    print(f"Wrote ablation predictions: {args.predictions_output}")
    print(f"Wrote ablation table: {args.table_output}")


if __name__ == "__main__":
    main()
