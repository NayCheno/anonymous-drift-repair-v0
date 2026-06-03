#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.dataset_adapters import load_jsonl, save_jsonl


BASELINES = ("vanilla_rag", "query_rewrite_rag", "self_reflection")


def empty_diagnosis(example_id: str, baseline: str) -> dict[str, Any]:
    return {
        "example_id": example_id,
        "drift_types": [],
        "severity": 0,
        "conflicting_nodes": [],
        "suggested_repair": "answer_as_is",
        "confidence": 0.5,
        "primary_type": "",
        "severity_reason": f"{baseline}_does_not_model_state_drift",
        "module_hits": [],
        "signals": [],
        "notes": "Baseline does not emit typed drift diagnosis.",
    }


def gold_subset_diagnosis(example_id: str, baseline: str, gold_types: list[str], supported: set[str]) -> dict[str, Any]:
    predicted = [drift_type for drift_type in gold_types if drift_type in supported]
    severity = 0 if not predicted else max(1, min(3, len(predicted)))
    suggested = "answer_as_is" if not predicted else _baseline_repair_action(predicted)
    return {
        "example_id": example_id,
        "drift_types": predicted,
        "severity": severity,
        "conflicting_nodes": ["candidate_response"] if predicted else [],
        "suggested_repair": suggested,
        "confidence": 0.65 if predicted else 0.55,
        "primary_type": predicted[0] if predicted else "",
        "severity_reason": f"{baseline}_limited_rule_proxy",
        "module_hits": [baseline] if predicted else [],
        "signals": [
            {
                "module": baseline,
                "drift_types": predicted,
                "note": "Deterministic baseline proxy detected a supported subset of gold drift labels.",
                "conflicting_nodes": ["candidate_response"],
            }
        ]
        if predicted
        else [],
        "notes": "Baseline proxy models only a subset of state drift types.",
    }


def _baseline_repair_action(drift_types: list[str]) -> str:
    if "T1_tool_state_drift" in drift_types:
        return "cross_validate_tool"
    if "E2_retrieval_drift" in drift_types:
        return "rewrite_query_and_retrieve"
    if "E1_evidence_drift" in drift_types:
        return "re_retrieve_and_verify"
    if "U1_abstention_drift" in drift_types:
        return "calibrate_answer_clarify_abstain"
    if "G1_goal_drift" in drift_types or "G2_constraint_drift" in drift_types:
        return "rollback_and_replan"
    return "revise_response"


def baseline_record(ex, baseline: str) -> dict[str, Any]:
    gold_types = list(ex.gold.get("drift_types", []))
    if baseline == "vanilla_rag":
        diagnosis = empty_diagnosis(ex.id, baseline)
        repaired = False
        repaired_response = ex.candidate_response
        cost = {"extra_tokens": 0, "extra_retrievals": 0, "extra_tool_calls": 0}
    elif baseline == "query_rewrite_rag":
        diagnosis = gold_subset_diagnosis(
            ex.id,
            baseline,
            gold_types,
            {"E2_retrieval_drift", "G1_goal_drift"},
        )
        repaired = bool(diagnosis["drift_types"])
        repaired_response = (
            "Query rewrite baseline would rewrite the current turn before retrieval."
            if repaired
            else ex.candidate_response
        )
        cost = {"extra_tokens": 18 if repaired else 0, "extra_retrievals": 1 if repaired else 0, "extra_tool_calls": 0}
    elif baseline == "self_reflection":
        diagnosis = gold_subset_diagnosis(
            ex.id,
            baseline,
            gold_types,
            {"G1_goal_drift", "G2_constraint_drift", "E1_evidence_drift", "U1_abstention_drift"},
        )
        repaired = bool(diagnosis["drift_types"])
        repaired_response = (
            "Self-reflection baseline would ask the model to critique and revise the response."
            if repaired
            else ex.candidate_response
        )
        cost = {"extra_tokens": 64 if repaired else 0, "extra_retrievals": 0, "extra_tool_calls": 0}
    else:
        raise ValueError(f"Unknown baseline: {baseline}")

    return {
        "example_id": ex.id,
        "baseline": baseline,
        "original_response": ex.candidate_response,
        "repaired_response": repaired_response,
        "diagnosis": diagnosis,
        "repaired": repaired,
        "cost": cost,
        "repair_trace": {
            "policy": baseline,
            "action": diagnosis["suggested_repair"],
            "diagnosis_types": diagnosis["drift_types"],
            "steps": ["baseline_proxy"],
            "stop_condition": "baseline_proxy_completed",
            "rationale": "Deterministic proxy used for Week 5 scaffold comparisons.",
        },
        "gold": ex.gold,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic baseline proxies.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--baselines",
        nargs="+",
        choices=BASELINES,
        default=list(BASELINES),
        help="Baselines to run.",
    )
    args = parser.parse_args()

    examples = load_jsonl(args.dataset)
    records = []
    for baseline in args.baselines:
        for ex in examples:
            records.append(baseline_record(ex, baseline))
    save_jsonl(args.output, records)
    print(f"Wrote {len(records)} baseline records: {args.output}")


if __name__ == "__main__":
    main()
