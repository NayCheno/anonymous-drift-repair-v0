#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.metrics import compute_metrics


METRICS = ["drift_type_exact_match", "drift_type_micro_f1", "repair_rate", "over_repair_rate"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def group_baselines(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record.get("baseline", "unknown")].append(record)
    return dict(grouped)


def by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["example_id"]: record for record in records}


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def metric_value(records: list[dict[str, Any]], metric: str) -> float:
    return float(compute_metrics(records).get(metric, 0.0))


def bootstrap_ci(
    records: list[dict[str, Any]],
    metric: str,
    rng: random.Random,
    n_bootstrap: int,
) -> tuple[float, float, float]:
    n = len(records)
    estimate = metric_value(records, metric)
    samples = []
    for _ in range(n_bootstrap):
        sample = [records[rng.randrange(n)] for _ in range(n)]
        samples.append(metric_value(sample, metric))
    return estimate, percentile(samples, 0.025), percentile(samples, 0.975)


def paired_bootstrap(
    sage_records: list[dict[str, Any]],
    baseline_records: list[dict[str, Any]],
    metric: str,
    rng: random.Random,
    n_bootstrap: int,
) -> tuple[float, float, float, float]:
    sage_by_id = by_id(sage_records)
    baseline_by_id = by_id(baseline_records)
    ids = sorted(set(sage_by_id) & set(baseline_by_id))
    if not ids:
        return 0.0, 0.0, 0.0, 1.0

    sage_aligned = [sage_by_id[example_id] for example_id in ids]
    baseline_aligned = [baseline_by_id[example_id] for example_id in ids]
    estimate = metric_value(sage_aligned, metric) - metric_value(baseline_aligned, metric)

    diffs = []
    n = len(ids)
    for _ in range(n_bootstrap):
        sampled_positions = [rng.randrange(n) for _ in range(n)]
        sage_sample = [sage_aligned[position] for position in sampled_positions]
        baseline_sample = [baseline_aligned[position] for position in sampled_positions]
        diffs.append(metric_value(sage_sample, metric) - metric_value(baseline_sample, metric))

    p_lower = sum(diff <= 0 for diff in diffs) / len(diffs)
    p_upper = sum(diff >= 0 for diff in diffs) / len(diffs)
    p_value = min(1.0, 2 * min(p_lower, p_upper))
    return estimate, percentile(diffs, 0.025), percentile(diffs, 0.975), p_value


def format_row(
    row_type: str,
    system: str,
    comparison: str,
    metric: str,
    estimate: float,
    ci_low: float,
    ci_high: float,
    p_value: float | None,
    n_bootstrap: int,
    seed: int,
) -> dict[str, str]:
    return {
        "row_type": row_type,
        "system": system,
        "comparison": comparison,
        "metric": metric,
        "estimate": f"{estimate:.4f}",
        "ci95_low": f"{ci_low:.4f}",
        "ci95_high": f"{ci_high:.4f}",
        "p_value": "" if p_value is None else f"{p_value:.4f}",
        "n_bootstrap": str(n_bootstrap),
        "seed": str(seed),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic bootstrap CIs and paired comparisons for DriftBench v0."
    )
    parser.add_argument("--sage-r", required=True)
    parser.add_argument("--baselines", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--n-bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    sage_records = load_jsonl(Path(args.sage_r))
    baseline_groups = group_baselines(load_jsonl(Path(args.baselines)))
    systems = {"sage_r": sage_records, **baseline_groups}

    rows = []
    for system, records in sorted(systems.items()):
        for metric in METRICS:
            estimate, ci_low, ci_high = bootstrap_ci(records, metric, rng, args.n_bootstrap)
            rows.append(
                format_row("ci", system, "", metric, estimate, ci_low, ci_high, None, args.n_bootstrap, args.seed)
            )

    for baseline, baseline_records in sorted(baseline_groups.items()):
        for metric in METRICS:
            estimate, ci_low, ci_high, p_value = paired_bootstrap(
                sage_records,
                baseline_records,
                metric,
                rng,
                args.n_bootstrap,
            )
            rows.append(
                format_row(
                    "paired_delta",
                    "sage_r",
                    f"sage_r_minus_{baseline}",
                    metric,
                    estimate,
                    ci_low,
                    ci_high,
                    p_value,
                    args.n_bootstrap,
                    args.seed,
                )
            )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
