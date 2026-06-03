from __future__ import annotations

from typing import Dict, Iterable, Any


def compute_metrics(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(records)
    n = len(rows)
    if n == 0:
        return {}

    detected = [r for r in rows if r["diagnosis"]["drift_types"]]
    repaired = [r for r in rows if r.get("repaired")]

    # Toy proxy: if gold drift types are present in record, compute exact drift-type recall.
    exact = 0
    gold_count = 0
    over_repair = 0
    tp = 0
    fp = 0
    fn = 0
    gold_type_counts: Dict[str, int] = {}
    pred_type_counts: Dict[str, int] = {}
    for r in rows:
        gold = r.get("gold", {})
        gold_types = set(gold.get("drift_types", []))
        pred_types = set(r["diagnosis"].get("drift_types", []))
        if gold_types == pred_types:
            exact += 1
        if gold_types:
            gold_count += 1
        if not gold_types and r.get("repaired"):
            over_repair += 1
        tp += len(gold_types & pred_types)
        fp += len(pred_types - gold_types)
        fn += len(gold_types - pred_types)
        for drift_type in gold_types:
            gold_type_counts[drift_type] = gold_type_counts.get(drift_type, 0) + 1
        for drift_type in pred_types:
            pred_type_counts[drift_type] = pred_type_counts.get(drift_type, 0) + 1

    total_extra_tokens = sum(r.get("cost", {}).get("extra_tokens", 0) for r in rows)
    total_extra_retrievals = sum(r.get("cost", {}).get("extra_retrievals", 0) for r in rows)
    total_extra_tools = sum(r.get("cost", {}).get("extra_tool_calls", 0) for r in rows)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    return {
        "n_examples": float(n),
        "n_gold_drift_examples": float(gold_count),
        "drift_detection_rate": len(detected) / n,
        "repair_rate": len(repaired) / n,
        "drift_type_exact_match": exact / n,
        "drift_type_micro_precision": precision,
        "drift_type_micro_recall": recall,
        "drift_type_micro_f1": f1,
        "over_repair_rate": over_repair / max(1, n - gold_count),
        "avg_extra_tokens": total_extra_tokens / n,
        "avg_extra_retrievals": total_extra_retrievals / n,
        "avg_extra_tool_calls": total_extra_tools / n,
        "gold_type_counts": dict(sorted(gold_type_counts.items())),
        "pred_type_counts": dict(sorted(pred_type_counts.items())),
    }
