#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def grouped_records(sage_r_path: Path, baselines_path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped = {"sage_r": load_jsonl(sage_r_path)}
    for record in load_jsonl(baselines_path):
        grouped.setdefault(record.get("baseline", "unknown"), []).append(record)
    return grouped


def action(record: dict[str, Any]) -> str:
    return record.get("repair_trace", {}).get(
        "action",
        record.get("diagnosis", {}).get("suggested_repair", "unknown"),
    )


def summarize(system: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    clean = [r for r in records if not r.get("gold", {}).get("drift_types", [])]
    over_repaired = [r for r in clean if r.get("repaired")]
    action_counts = Counter(action(r) for r in over_repaired)
    clean_actions = Counter(action(r) for r in clean)
    return {
        "system": system,
        "n_examples": len(records),
        "n_clean_gold": len(clean),
        "n_over_repaired": len(over_repaired),
        "over_repair_rate": f"{(len(over_repaired) / len(clean) if clean else 0.0):.4f}",
        "clean_action_distribution": json.dumps(dict(sorted(clean_actions.items())), sort_keys=True),
        "over_repair_action_distribution": json.dumps(dict(sorted(action_counts.items())), sort_keys=True),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build over-repair analysis table.")
    parser.add_argument("--sage-r", required=True)
    parser.add_argument("--baselines", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = [
        summarize(system, records)
        for system, records in sorted(grouped_records(Path(args.sage_r), Path(args.baselines)).items())
    ]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
