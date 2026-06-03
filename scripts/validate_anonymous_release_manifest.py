#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_anonymous_release import DEFAULT_EXCLUDES, manifest_entries


ROOT = Path(__file__).resolve().parents[1]


def release_files(root: Path) -> list[str]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rows.append(path.relative_to(root).as_posix())
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate anonymous release tree manifest integrity.")
    parser.add_argument("--manifest", default="MANIFEST.txt")
    parser.add_argument("--release-root", default="release/anonymous-drift-repair-v0")
    parser.add_argument("--package-report", default="results/anonymous_release_package_v0.json")
    parser.add_argument("--output", default="results/anonymous_release_manifest_validation_v0.json")
    args = parser.parse_args()

    release_root = ROOT / args.release_root
    release_manifest = release_root / "RELEASE_MANIFEST.txt"
    expected_entries = manifest_entries(ROOT / args.manifest)
    release_entries = [
        line.strip()
        for line in release_manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if release_manifest.exists() else []
    expected_files = sorted([*expected_entries, "RELEASE_MANIFEST.txt"])
    actual_files = release_files(release_root) if release_root.exists() else []
    package_report = {}
    report_path = ROOT / args.package_report
    if report_path.exists():
        package_report = json.loads(report_path.read_text(encoding="utf-8"))

    errors = []
    if release_entries != expected_entries:
        errors.append("RELEASE_MANIFEST.txt does not match filtered MANIFEST.txt entries")
    missing = sorted(set(expected_files) - set(actual_files))
    extra = sorted(set(actual_files) - set(expected_files))
    if missing:
        errors.append(f"missing release files: {missing}")
    if extra:
        errors.append(f"unexpected release files: {extra}")
    if package_report.get("n_files") is not None and package_report.get("n_files") != len(actual_files):
        errors.append("package report n_files does not match release tree file count")
    leaked_excluded = sorted(set(actual_files).intersection(DEFAULT_EXCLUDES))
    if leaked_excluded:
        errors.append(f"excluded files leaked into release tree: {leaked_excluded}")

    report = {
        "valid": not errors,
        "errors": errors,
        "n_expected_manifest_entries": len(expected_entries),
        "n_expected_release_files": len(expected_files),
        "n_actual_release_files": len(actual_files),
        "package_report_n_files": package_report.get("n_files"),
        "missing": missing,
        "extra": extra,
        "excluded_files_checked": sorted(DEFAULT_EXCLUDES),
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    if errors:
        raise SystemExit("Anonymous release manifest validation failed")


if __name__ == "__main__":
    main()
