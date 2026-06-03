#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ENABLED_LICENSE_STATUS = {"internal_scaffold", "checked"}
ALLOWED_ENABLED_REDISTRIBUTION = {"allowed", "not_redistributed"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate dataset license gates for enabled datasets.")
    parser.add_argument("--config", default="configs/datasets.yaml")
    parser.add_argument("--output", default="results/dataset_license_review_v0.json")
    args = parser.parse_args()

    config_path = ROOT / args.config
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    errors = []
    warnings = []
    report_rows = []
    datasets: dict[str, dict[str, Any]] = config.get("datasets", {})
    for name, dataset in datasets.items():
        license_status = dataset.get("license_status")
        redistribution = dataset.get("redistribution")
        row = {
            "name": name,
            "enabled": bool(dataset.get("enabled")),
            "path": dataset.get("path"),
            "source_url": dataset.get("source_url"),
            "license_status": license_status,
            "license_spdx": dataset.get("license_spdx"),
            "license_reviewed_on": dataset.get("license_reviewed_on"),
            "redistribution": redistribution,
        }
        report_rows.append(row)
        if not license_status:
            errors.append(f"{name}: missing license_status")
        if not redistribution:
            errors.append(f"{name}: missing redistribution")
        if license_status == "checked":
            if not dataset.get("source_url"):
                errors.append(f"{name}: checked dataset is missing source_url")
            if not dataset.get("license_spdx"):
                errors.append(f"{name}: checked dataset is missing license_spdx")
            if not dataset.get("license_reviewed_on"):
                errors.append(f"{name}: checked dataset is missing license_reviewed_on")
        if not dataset.get("enabled") and license_status == "pending":
            warnings.append(f"{name}: disabled dataset remains pending license review")
        if dataset.get("enabled"):
            if license_status not in ALLOWED_ENABLED_LICENSE_STATUS:
                errors.append(f"{name}: enabled dataset has unapproved license_status={license_status}")
            if redistribution not in ALLOWED_ENABLED_REDISTRIBUTION:
                errors.append(f"{name}: enabled dataset has unapproved redistribution={redistribution}")
            path = dataset.get("path")
            if path and not (ROOT / path).exists():
                errors.append(f"{name}: enabled dataset path does not exist: {path}")

    report = {
        "config": args.config,
        "valid": not errors,
        "n_datasets": len(report_rows),
        "n_enabled": sum(1 for row in report_rows if row["enabled"]),
        "n_checked": sum(1 for row in report_rows if row["license_status"] == "checked"),
        "n_pending": sum(1 for row in report_rows if row["license_status"] == "pending"),
        "errors": errors,
        "warnings": warnings,
        "datasets": report_rows,
    }
    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Dataset license gate valid: {args.config}")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
