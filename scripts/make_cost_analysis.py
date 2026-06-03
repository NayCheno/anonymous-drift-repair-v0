#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def grouped_records(sage_r_path: Path, baselines_path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped = {"sage_r": load_jsonl(sage_r_path)}
    for record in load_jsonl(baselines_path):
        grouped.setdefault(record.get("baseline", "unknown"), []).append(record)
    return grouped


def cost_key(record: dict[str, Any]) -> str:
    trace = record.get("repair_trace", {})
    if trace.get("action"):
        return trace["action"]
    return record.get("diagnosis", {}).get("suggested_repair", "unknown")


def summarize(system: str, records: list[dict[str, Any]], action: str) -> dict[str, Any]:
    rows = records if action == "ALL" else [r for r in records if cost_key(r) == action]
    n = len(rows)
    total_tokens = sum(r.get("cost", {}).get("extra_tokens", 0) for r in rows)
    total_retrievals = sum(r.get("cost", {}).get("extra_retrievals", 0) for r in rows)
    total_tool_calls = sum(r.get("cost", {}).get("extra_tool_calls", 0) for r in rows)
    repaired = sum(1 for r in rows if r.get("repaired"))
    return {
        "system": system,
        "repair_action": action,
        "n_examples": n,
        "n_repaired": repaired,
        "repair_rate": f"{(repaired / n if n else 0.0):.4f}",
        "total_extra_tokens": total_tokens,
        "avg_extra_tokens": f"{(total_tokens / n if n else 0.0):.2f}",
        "total_extra_retrievals": total_retrievals,
        "avg_extra_retrievals": f"{(total_retrievals / n if n else 0.0):.4f}",
        "total_extra_tool_calls": total_tool_calls,
        "avg_extra_tool_calls": f"{(total_tool_calls / n if n else 0.0):.4f}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build repair cost analysis table.")
    parser.add_argument("--sage-r", required=True)
    parser.add_argument("--baselines", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out_rows = []
    for system, records in sorted(grouped_records(Path(args.sage_r), Path(args.baselines)).items()):
        actions = sorted({cost_key(record) for record in records})
        out_rows.append(summarize(system, records, "ALL"))
        for action in actions:
            out_rows.append(summarize(system, records, action))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
