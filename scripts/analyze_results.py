#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def sorted_counts(counter: Counter) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a simple error analysis markdown file.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    drift_counter = Counter()
    repair_counter = Counter()
    trace_action_counter = Counter()
    stop_counter = Counter()
    module_counter = Counter()
    severity_counter = Counter()
    exact_matches = 0
    over_repairs = 0
    gold_clean = 0
    n = 0
    with open(args.predictions, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            n += 1
            obj = json.loads(line)
            diagnosis = obj.get("diagnosis", {})
            pred_types = set(diagnosis.get("drift_types", []))
            gold_types = set(obj.get("gold", {}).get("drift_types", []))
            if pred_types == gold_types:
                exact_matches += 1
            if not gold_types:
                gold_clean += 1
            if not gold_types and obj.get("repaired"):
                over_repairs += 1
            for drift_type in pred_types:
                drift_counter[drift_type] += 1
            repair_counter[diagnosis.get("suggested_repair", "unknown")] += 1
            severity_counter[str(diagnosis.get("severity", "unknown"))] += 1
            for module in diagnosis.get("module_hits", []):
                module_counter[module] += 1
            trace = obj.get("repair_trace", {})
            trace_action_counter[trace.get("action", "missing")] += 1
            stop_counter[trace.get("stop_condition", "missing")] += 1

    exact_rate = exact_matches / n if n else 0.0
    over_repair_rate = over_repairs / gold_clean if gold_clean else 0.0
    lines = [
        "# Error Analysis",
        "",
        f"Total examples: {n}",
        f"Drift-type exact match: {exact_rate:.4f}",
        f"Over-repair rate: {over_repair_rate:.4f}",
        "",
        "## Drift counts",
        "",
    ]
    for k, v in sorted_counts(drift_counter):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Suggested repairs", ""])
    for k, v in sorted_counts(repair_counter):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Repair trace actions", ""])
    for k, v in sorted_counts(trace_action_counter):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Repair stop conditions", ""])
    for k, v in sorted_counts(stop_counter):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Diagnosis modules", ""])
    for k, v in sorted_counts(module_counter):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Severity", ""])
    for k, v in sorted(severity_counter.items()):
        lines.append(f"- {k}: {v}")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
