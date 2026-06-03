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
ALLOWED_REPAIRS = {
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


def labels(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("labels_to_fill", {})


def is_complete(row: dict[str, Any]) -> bool:
    row_labels = labels(row)
    drift_types = row_labels.get("drift_types", [])
    expected_repair = row_labels.get("expected_repair", "")
    severity = row_labels.get("severity")
    task_success = row_labels.get("task_success")
    if not isinstance(drift_types, list):
        return False
    if set(drift_types) - ALLOWED_DRIFT_TYPES:
        return False
    if severity not in {0, 1, 2, 3}:
        return False
    if expected_repair not in ALLOWED_REPAIRS:
        return False
    return isinstance(task_success, bool)


def invalid_reasons(row: dict[str, Any]) -> list[str]:
    row_labels = labels(row)
    reasons = []
    drift_types = row_labels.get("drift_types", [])
    if not isinstance(drift_types, list):
        reasons.append("drift_types_not_list")
    elif set(drift_types) - ALLOWED_DRIFT_TYPES:
        reasons.append("invalid_drift_type")
    if row_labels.get("severity") not in {0, 1, 2, 3}:
        reasons.append("missing_or_invalid_severity")
    if row_labels.get("expected_repair", "") not in ALLOWED_REPAIRS:
        reasons.append("missing_or_invalid_expected_repair")
    if not isinstance(row_labels.get("task_success"), bool):
        reasons.append("missing_or_invalid_task_success")
    return reasons


def disagreement_rows(rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]]) -> list[dict[str, Any]]:
    b_by_id = {row["id"]: row for row in rows_b}
    disagreements = []
    for row_a in rows_a:
        row_b = b_by_id.get(row_a["id"])
        if not row_b:
            continue
        if not row_a.get("double_annotated") and not row_b.get("double_annotated"):
            continue
        labels_a = labels(row_a)
        labels_b = labels(row_b)
        fields = []
        if set(labels_a.get("drift_types", [])) != set(labels_b.get("drift_types", [])):
            fields.append("drift_types")
        for field in ("severity", "expected_repair", "task_success"):
            if labels_a.get(field) != labels_b.get(field):
                fields.append(field)
        if fields:
            disagreements.append(
                {
                    "id": row_a["id"],
                    "source_example_id": row_a.get("source_example_id", ""),
                    "disagreement_fields": fields,
                    "annotator_a_labels": labels_a,
                    "annotator_b_labels": labels_b,
                    "adjudication": {
                        "final_drift_types": [],
                        "final_severity": None,
                        "final_expected_repair": "",
                        "final_task_success": None,
                        "notes": "",
                    },
                }
            )
    return disagreements


def completion_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    incomplete = [
        {"id": row["id"], "reasons": invalid_reasons(row)}
        for row in rows
        if not is_complete(row)
    ]
    return {
        "n_items": len(rows),
        "n_complete": len(rows) - len(incomplete),
        "n_incomplete": len(incomplete),
        "complete": not incomplete,
        "incomplete_examples": incomplete[:20],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check filled human annotation status and build adjudication queue.")
    parser.add_argument("--annotator-a", required=True)
    parser.add_argument("--annotator-b", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--adjudication-output", required=True)
    args = parser.parse_args()

    rows_a = load_jsonl(Path(args.annotator_a))
    rows_b = load_jsonl(Path(args.annotator_b))
    disagreements = disagreement_rows(rows_a, rows_b)
    report = {
        "annotator_a": completion_summary(rows_a),
        "annotator_b": completion_summary(rows_b),
        "n_double_annotated": sum(
            1 for row in rows_b if row["id"] in {row_a["id"] for row_a in rows_a} and row.get("double_annotated")
        ),
        "n_disagreements": len(disagreements),
        "human_annotation_completed": completion_summary(rows_a)["complete"]
        and completion_summary(rows_b)["complete"],
        "note": "Completion is evaluated on the provided annotation files. For v0, these may be filled by human annotators or an explicitly documented LLM reviewer.",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_jsonl(Path(args.adjudication_output), disagreements)
    print(f"Wrote {out}")
    print(f"Wrote {args.adjudication_output}")


if __name__ == "__main__":
    main()
