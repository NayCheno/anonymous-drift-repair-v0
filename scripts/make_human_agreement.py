#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
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


def label_set(row: dict[str, Any], field: str) -> set[str]:
    values = row.get(field, [])
    if values is None:
        return set()
    return set(values)


def expected_from_answer_key(row: dict[str, Any]) -> dict[str, Any]:
    drift_types = row.get("gold_drift_types", [])
    return {
        "id": row["id"],
        "drift_types": drift_types,
        "task_success": row.get("gold_task_success"),
        "expected_repair": row.get("gold_expected_action", ""),
        "severity": 0 if not drift_types else min(3, max(1, len(drift_types))),
    }


def annotation_from_filled(row: dict[str, Any]) -> dict[str, Any]:
    labels = row.get("labels_to_fill", {})
    return {
        "id": row["id"],
        "drift_types": labels.get("drift_types", []),
        "task_success": labels.get("task_success"),
        "expected_repair": labels.get("expected_repair", ""),
        "severity": labels.get("severity"),
    }


def annotation_complete(row: dict[str, Any]) -> bool:
    drift_types = row.get("drift_types", [])
    if not isinstance(drift_types, list):
        return False
    if set(drift_types) - ALLOWED_DRIFT_TYPES:
        return False
    if row.get("severity") not in {0, 1, 2, 3}:
        return False
    if row.get("expected_repair", "") not in ALLOWED_REPAIRS:
        return False
    return isinstance(row.get("task_success"), bool)


def completion_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n_complete = sum(1 for row in rows if annotation_complete(row))
    return {
        "n_items": len(rows),
        "n_complete": n_complete,
        "n_incomplete": len(rows) - n_complete,
        "complete": n_complete == len(rows),
    }


def percent_agreement(rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]], field: str) -> float:
    b_by_id = {row["id"]: row for row in rows_b}
    compared = 0
    matched = 0
    for row_a in rows_a:
        row_b = b_by_id.get(row_a["id"])
        if not row_b:
            continue
        compared += 1
        if field == "drift_types":
            matched += label_set(row_a, field) == label_set(row_b, field)
        else:
            matched += row_a.get(field) == row_b.get(field)
    return matched / compared if compared else 0.0


def pair_count(rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]]) -> int:
    ids_b = {row["id"] for row in rows_b}
    return sum(1 for row in rows_a if row["id"] in ids_b)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute human/judge agreement scaffold metrics.")
    parser.add_argument("--answer-key", required=True)
    parser.add_argument("--annotator-a")
    parser.add_argument("--annotator-b")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--proxy-from-answer-key",
        action="store_true",
        help="Use answer key as deterministic proxy annotations for workflow validation.",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow agreement calculation from incomplete filled annotations. Intended only for debugging.",
    )
    parser.add_argument("--status-output", help="Optional JSON status report for whether agreement is reportable.")
    args = parser.parse_args()

    answer_rows = [expected_from_answer_key(row) for row in load_jsonl(Path(args.answer_key))]
    completion: dict[str, Any]
    if args.proxy_from_answer_key:
        annotator_a = list(answer_rows)
        annotator_b = [row for row in answer_rows if row["id"] in {r["id"] for r in answer_rows[:48]}]
        mode = "answer_key_proxy"
        completion = {
            "annotator_a": {
                "n_items": len(annotator_a),
                "n_complete": len(annotator_a),
                "n_incomplete": 0,
                "complete": True,
            },
            "annotator_b": {
                "n_items": len(annotator_b),
                "n_complete": len(annotator_b),
                "n_incomplete": 0,
                "complete": True,
            },
        }
    else:
        if not args.annotator_a or not args.annotator_b:
            raise SystemExit("--annotator-a and --annotator-b are required without --proxy-from-answer-key")
        annotator_a = [annotation_from_filled(row) for row in load_jsonl(Path(args.annotator_a))]
        annotator_b = [annotation_from_filled(row) for row in load_jsonl(Path(args.annotator_b))]
        mode = "filled_annotations"
        completion = {
            "annotator_a": completion_summary(annotator_a),
            "annotator_b": completion_summary(annotator_b),
        }
        if (
            not args.allow_incomplete
            and (not completion["annotator_a"]["complete"] or not completion["annotator_b"]["complete"])
        ):
            status = {
                "mode": mode,
                "agreement_reportable": False,
                "reason": "filled annotation files are incomplete",
                "completion": completion,
            }
            if args.status_output:
                out_status = Path(args.status_output)
                out_status.parent.mkdir(parents=True, exist_ok=True)
                out_status.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                print(f"Wrote {out_status}")
            raise SystemExit("Filled annotation files are incomplete; rerun with --allow-incomplete only for debugging.")

    rows = [
        {
            "comparison": "annotator_a_vs_answer_key",
            "mode": mode,
            "n_pairs": pair_count(annotator_a, answer_rows),
            "drift_type_agreement": f"{percent_agreement(annotator_a, answer_rows, 'drift_types'):.4f}",
            "severity_agreement": f"{percent_agreement(annotator_a, answer_rows, 'severity'):.4f}",
            "task_success_agreement": f"{percent_agreement(annotator_a, answer_rows, 'task_success'):.4f}",
            "repair_action_agreement": f"{percent_agreement(annotator_a, answer_rows, 'expected_repair'):.4f}",
        },
        {
            "comparison": "annotator_a_vs_annotator_b",
            "mode": mode,
            "n_pairs": pair_count(annotator_a, annotator_b),
            "drift_type_agreement": f"{percent_agreement(annotator_a, annotator_b, 'drift_types'):.4f}",
            "severity_agreement": f"{percent_agreement(annotator_a, annotator_b, 'severity'):.4f}",
            "task_success_agreement": f"{percent_agreement(annotator_a, annotator_b, 'task_success'):.4f}",
            "repair_action_agreement": f"{percent_agreement(annotator_a, annotator_b, 'expected_repair'):.4f}",
        },
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}")
    status = {
        "mode": mode,
        "agreement_reportable": mode == "filled_annotations"
        and completion["annotator_a"]["complete"]
        and completion["annotator_b"]["complete"],
        "reason": "answer-key proxy is a workflow check, not a reportable human agreement"
        if mode == "answer_key_proxy"
        else "filled annotation files are complete",
        "n_answer_key_items": len(answer_rows),
        "n_pairs_a_vs_key": pair_count(annotator_a, answer_rows),
        "n_pairs_a_vs_b": pair_count(annotator_a, annotator_b),
        "completion": completion,
    }
    if args.status_output:
        out_status = Path(args.status_output)
        out_status.parent.mkdir(parents=True, exist_ok=True)
        out_status.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {out_status}")


if __name__ == "__main__":
    main()
