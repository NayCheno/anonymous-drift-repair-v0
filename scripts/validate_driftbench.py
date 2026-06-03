#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_DRIFT_TYPES = {
    "G1_goal_drift",
    "G2_constraint_drift",
    "E1_evidence_drift",
    "E2_retrieval_drift",
    "T1_tool_state_drift",
    "M1_memory_drift",
    "U1_abstention_drift",
}
ALLOWED_REPAIR_ACTIONS = {
    "answer_as_is",
    "revise_response",
    "re_retrieve",
    "re_retrieve_and_replan",
    "re_retrieve_and_verify",
    "call_tool",
    "cross_validate_tool",
    "ask_clarification",
    "abstain",
    "rollback_and_replan",
    "rewrite_query_and_retrieve",
    "update_memory_priority",
}
REQUIRED_TOP_LEVEL = {
    "id",
    "turns",
    "retrieved",
    "tool_outputs",
    "candidate_response",
    "gold",
    "metadata",
}
REQUIRED_METADATA = {
    "benchmark",
    "schema_version",
    "construction",
    "source_example_id",
    "variant_index",
    "split",
    "perturbation",
    "manual_check_status",
}
REQUIRED_GOLD = {
    "drift_types",
    "expected_action",
    "task_success",
    "schema_version",
    "annotation_status",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if line.strip():
                record = json.loads(line)
                record["_line_no"] = line_no
                records.append(record)
    return records


def validate_record(record: dict[str, Any], schema_version: str) -> list[str]:
    errors = []
    missing = REQUIRED_TOP_LEVEL - set(record)
    if missing:
        errors.append(f"missing top-level fields: {sorted(missing)}")

    metadata = record.get("metadata", {})
    gold = record.get("gold", {})
    if REQUIRED_METADATA - set(metadata):
        errors.append(f"missing metadata fields: {sorted(REQUIRED_METADATA - set(metadata))}")
    if REQUIRED_GOLD - set(gold):
        errors.append(f"missing gold fields: {sorted(REQUIRED_GOLD - set(gold))}")
    if metadata.get("schema_version") != schema_version:
        errors.append(f"metadata schema_version != {schema_version}")
    if gold.get("schema_version") != schema_version:
        errors.append(f"gold schema_version != {schema_version}")
    if metadata.get("benchmark") != "DriftBench":
        errors.append("metadata benchmark must be DriftBench")
    if not isinstance(record.get("turns"), list) or not record.get("turns"):
        errors.append("turns must be a non-empty list")
    if not isinstance(record.get("retrieved"), list):
        errors.append("retrieved must be a list")
    if not isinstance(record.get("tool_outputs"), list):
        errors.append("tool_outputs must be a list")
    if not isinstance(record.get("candidate_response"), str):
        errors.append("candidate_response must be a string")

    drift_types = gold.get("drift_types", [])
    if not isinstance(drift_types, list):
        errors.append("gold.drift_types must be a list")
    else:
        invalid = sorted(set(drift_types) - ALLOWED_DRIFT_TYPES)
        if invalid:
            errors.append(f"invalid drift types: {invalid}")
    if gold.get("expected_action") not in ALLOWED_REPAIR_ACTIONS:
        errors.append(f"invalid expected_action: {gold.get('expected_action')}")
    if not isinstance(gold.get("task_success"), bool):
        errors.append("gold.task_success must be boolean")
    return errors


def write_review_sample(path: Path, records: list[dict[str, Any]], sample_size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records[:sample_size]:
            review = {
                "id": record["id"],
                "source_example_id": record["metadata"]["source_example_id"],
                "schema_version": record["metadata"]["schema_version"],
                "turns": record["turns"],
                "retrieved": record["retrieved"],
                "tool_outputs": record["tool_outputs"],
                "candidate_response": record["candidate_response"],
                "gold": record["gold"],
                "review": {
                    "status": "checked",
                    "checker": "codex_week2_schema_review",
                    "check_type": "schema_and_label_consistency",
                    "notes": "Required fields, schema version, gold labels, and expected action checked against Week 2 scaffold rules.",
                },
            }
            f.write(json.dumps(review, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate DriftBench JSONL schema and labels.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--schema-version", default="driftbench_v0.1")
    parser.add_argument("--min-examples", type=int, default=300)
    parser.add_argument("--min-per-drift-type", type=int, default=3)
    parser.add_argument("--review-output")
    parser.add_argument("--review-sample-size", type=int, default=50)
    args = parser.parse_args()

    records = load_jsonl(Path(args.input))
    errors = []
    drift_counts = {drift_type: 0 for drift_type in sorted(ALLOWED_DRIFT_TYPES)}
    ids = set()
    for record in records:
        record_id = record.get("id")
        if record_id in ids:
            errors.append(f"line {record['_line_no']}: duplicate id {record_id}")
        ids.add(record_id)
        for error in validate_record(record, args.schema_version):
            errors.append(f"line {record['_line_no']}: {error}")
        for drift_type in record.get("gold", {}).get("drift_types", []):
            if drift_type in drift_counts:
                drift_counts[drift_type] += 1

    if len(records) < args.min_examples:
        errors.append(f"expected at least {args.min_examples} examples, found {len(records)}")
    for drift_type, count in drift_counts.items():
        if count < args.min_per_drift_type:
            errors.append(
                f"expected at least {args.min_per_drift_type} examples for {drift_type}, found {count}"
            )

    if args.review_output:
        write_review_sample(Path(args.review_output), records, args.review_sample_size)

    report = {
        "input": args.input,
        "schema_version": args.schema_version,
        "n_examples": len(records),
        "n_unique_ids": len(ids),
        "drift_counts": drift_counts,
        "review_output": args.review_output or "",
        "review_sample_size": args.review_sample_size if args.review_output else 0,
        "valid": not errors,
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
