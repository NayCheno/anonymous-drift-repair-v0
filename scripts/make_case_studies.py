#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DRIFT_ORDER = [
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


def clip(value: Any, limit: int = 320) -> str:
    text = str(value).replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def select_cases(predictions: list[dict[str, Any]], max_cases: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for drift_type in DRIFT_ORDER:
        for row in predictions:
            diagnosis = row.get("diagnosis", {})
            pred_types = set(diagnosis.get("drift_types", []))
            gold_types = set(row.get("gold", {}).get("drift_types", []))
            if row["example_id"] in used_ids:
                continue
            if drift_type in pred_types and pred_types == gold_types:
                selected.append(row)
                used_ids.add(row["example_id"])
                break

    for row in predictions:
        if len(selected) >= max_cases:
            break
        if row["example_id"] in used_ids:
            continue
        if not row.get("gold", {}).get("drift_types", []) and not row.get("diagnosis", {}).get("drift_types", []):
            selected.append(row)
            used_ids.add(row["example_id"])
            break

    return selected[:max_cases]


def format_case(row: dict[str, Any], example: dict[str, Any] | None, idx: int) -> list[str]:
    diagnosis = row.get("diagnosis", {})
    trace = row.get("repair_trace", {})
    cost = row.get("cost", {})
    gold = row.get("gold", {})
    turns = example.get("turns", []) if example else []
    retrieved = example.get("retrieved", []) if example else []
    tool_outputs = example.get("tool_outputs", []) if example else []
    pred_types = diagnosis.get("drift_types", []) or ["NONE"]
    gold_types = gold.get("drift_types", []) or ["NONE"]

    lines = [
        f"## Case {idx}: {row['example_id']}",
        "",
        f"- Predicted drift: `{', '.join(pred_types)}`",
        f"- Gold drift: `{', '.join(gold_types)}`",
        f"- Suggested repair: `{diagnosis.get('suggested_repair', '')}`",
        f"- Trace action: `{trace.get('action', '')}`",
        f"- Severity: `{diagnosis.get('severity', '')}`",
        f"- Cost proxy: tokens `{cost.get('extra_tokens', 0)}`, retrievals `{cost.get('extra_retrievals', 0)}`, tools `{cost.get('extra_tool_calls', 0)}`",
        "",
        "### Context",
        "",
    ]
    if turns:
        for turn in turns[-3:]:
            lines.append(f"- `{turn.get('role', '')}`: {clip(turn.get('content', ''))}")
    else:
        lines.append("- No conversation turns found.")

    lines.extend(["", "### Evidence and Tools", ""])
    for item in retrieved[:2]:
        lines.append(f"- Evidence `{item.get('id', '')}`: {clip(item.get('text', ''))}")
    for item in tool_outputs[:2]:
        lines.append(f"- Tool `{item.get('tool', '')}`: {clip(item.get('content', ''))}")
    if not retrieved and not tool_outputs:
        lines.append("- No retrieved evidence or tool output.")

    lines.extend(
        [
            "",
            "### Response and Repair",
            "",
            f"- Candidate: {clip(row.get('original_response', ''))}",
            f"- Repaired: {clip(row.get('repaired_response', ''))}",
            f"- Rationale: {clip(trace.get('rationale', diagnosis.get('notes', '')))}",
            "",
        ]
    )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic v0 case studies from SAGE-R traces.")
    parser.add_argument("--dataset", default="data/driftbench_v0.jsonl")
    parser.add_argument("--predictions", default="results/sage_r_v0.jsonl")
    parser.add_argument("--output", default="results/case_studies_v0.md")
    parser.add_argument("--max-cases", type=int, default=8)
    args = parser.parse_args()

    dataset = {row["id"]: row for row in load_jsonl(Path(args.dataset))}
    predictions = load_jsonl(Path(args.predictions))
    selected = select_cases(predictions, args.max_cases)

    lines = [
        "# Deterministic v0 Case Studies",
        "",
        "These cases are selected from the deterministic DriftBench v0 scaffold to audit diagnosis and repair traces. They are pipeline-validation examples, not final benchmark claims.",
        "",
        f"Selected cases: {len(selected)}",
        "",
    ]
    for idx, row in enumerate(selected, start=1):
        lines.extend(format_case(row, dataset.get(row["example_id"]), idx))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
