#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
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
SECRET_PATTERNS = [
    re.compile(r"tp-[A-Za-z0-9]{16,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def labels_complete(row: dict[str, Any]) -> bool:
    labels = row.get("labels_to_fill", {})
    drift_types = labels.get("drift_types", [])
    if not isinstance(drift_types, list):
        return False
    if set(drift_types) - ALLOWED_DRIFT_TYPES:
        return False
    if labels.get("severity") not in {0, 1, 2, 3}:
        return False
    if labels.get("expected_repair") not in ALLOWED_REPAIRS:
        return False
    if not isinstance(labels.get("task_success"), bool):
        return False
    if labels.get("reviewer") != "llm_mimo_openai_compatible":
        return False
    return bool(labels.get("review_model"))


def assert_no_secret(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path}: contains API-key-shaped secret")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate committed LLM-reviewed annotation outputs without calling an API.")
    parser.add_argument("--annotator-a", default="data/human_validation/llm_review/human_validation_annotator_a_llm_v0.jsonl")
    parser.add_argument("--annotator-b", default="data/human_validation/llm_review/human_validation_annotator_b_llm_v0.jsonl")
    parser.add_argument("--status-a", default="results/llm_annotation_review_a_v0.json")
    parser.add_argument("--status-b", default="results/llm_annotation_review_b_v0.json")
    parser.add_argument("--annotation-status", default="results/llm_annotation_status_v0.json")
    parser.add_argument("--agreement", default="results/llm_human_agreement_v0.csv")
    parser.add_argument("--agreement-status", default="results/llm_human_agreement_status_v0.json")
    parser.add_argument("--adjudication", default="data/human_validation/llm_review/llm_adjudication_queue_v0.jsonl")
    parser.add_argument("--output", default="results/llm_review_validation_v0.json")
    args = parser.parse_args()

    paths = {name: ROOT / value for name, value in vars(args).items() if name != "output"}
    errors: list[str] = []
    for name, path in paths.items():
        if not path.exists():
            errors.append(f"{name}: missing {path}")

    if not errors:
        rows_a = load_jsonl(paths["annotator_a"])
        rows_b = load_jsonl(paths["annotator_b"])
        if len(rows_a) != 240:
            errors.append(f"annotator_a: expected 240 rows, found {len(rows_a)}")
        if len(rows_b) != 48:
            errors.append(f"annotator_b: expected 48 rows, found {len(rows_b)}")
        incomplete_a = [row["id"] for row in rows_a if not labels_complete(row)]
        incomplete_b = [row["id"] for row in rows_b if not labels_complete(row)]
        if incomplete_a:
            errors.append(f"annotator_a: incomplete/invalid labels for {len(incomplete_a)} rows")
        if incomplete_b:
            errors.append(f"annotator_b: incomplete/invalid labels for {len(incomplete_b)} rows")

        status_a = load_json(paths["status_a"])
        status_b = load_json(paths["status_b"])
        if not status_a.get("complete") or status_a.get("n_completed") != 240:
            errors.append("status_a: expected complete true and n_completed 240")
        if not status_b.get("complete") or status_b.get("n_completed") != 48:
            errors.append("status_b: expected complete true and n_completed 48")

        annotation_status = load_json(paths["annotation_status"])
        if not annotation_status.get("human_annotation_completed"):
            errors.append("annotation_status: expected completed true for provided LLM reviewer files")
        if annotation_status.get("n_disagreements") != len(load_jsonl(paths["adjudication"])):
            errors.append("annotation_status: disagreement count does not match adjudication queue")

        agreement_status = load_json(paths["agreement_status"])
        if not agreement_status.get("agreement_reportable"):
            errors.append("agreement_status: expected agreement_reportable true")
        agreement_rows = load_csv(paths["agreement"])
        if len(agreement_rows) != 2:
            errors.append(f"agreement: expected 2 rows, found {len(agreement_rows)}")
        expected_pairs = {"annotator_a_vs_answer_key": "240", "annotator_a_vs_annotator_b": "48"}
        for row in agreement_rows:
            expected = expected_pairs.get(row.get("comparison", ""))
            if expected and row.get("n_pairs") != expected:
                errors.append(f"agreement: {row['comparison']} expected n_pairs {expected}")

        for path in paths.values():
            assert_no_secret(path, errors)

    report = {
        "valid": not errors,
        "errors": errors,
        "checks": {
            "annotator_a_rows": 240,
            "annotator_b_rows": 48,
            "expected_agreement_rows": 2,
            "requires_no_api_call": True,
        },
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
