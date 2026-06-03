#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "MANIFEST.txt",
    "RELEASE_MANIFEST.txt",
    "docs/reproducibility_checklist.md",
    "scripts/reproduce_v0.py",
    "scripts/smoke_test.py",
]


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def command_succeeds(cmd: list[str], cwd: Path) -> bool:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode == 0


def count_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def verify(bundle: Path, output_dir: Path, expected_commit: str | None) -> dict[str, Any]:
    if output_dir.exists():
        shutil.rmtree(output_dir, onexc=remove_readonly)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", str(bundle), str(output_dir)], cwd=ROOT)
    if not command_succeeds(["git", "rev-parse", "--verify", "HEAD"], cwd=output_dir):
        run(["git", "checkout", "-b", "main", "origin/main"], cwd=output_dir)

    commit = run(["git", "rev-parse", "HEAD"], cwd=output_dir)
    branches = run(["git", "branch", "--show-current"], cwd=output_dir)
    missing = [path for path in REQUIRED_FILES if not (output_dir / path).exists()]
    release_manifest = output_dir / "RELEASE_MANIFEST.txt"
    manifest_entries = []
    if release_manifest.exists():
        manifest_entries = [
            line.strip()
            for line in release_manifest.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    report = {
        "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
        "clone_dir": str(output_dir.relative_to(ROOT)).replace("\\", "/"),
        "cloned": output_dir.exists(),
        "branch": branches,
        "commit_sha": commit,
        "expected_commit_sha": expected_commit,
        "commit_matches": expected_commit is None or commit == expected_commit,
        "n_files": count_files(output_dir),
        "n_release_manifest_entries": len(manifest_entries),
        "missing_required_files": missing,
        "valid": not missing and (expected_commit is None or commit == expected_commit),
    }
    return report


def remove_readonly(func: Any, path: str, _exc_info: Any) -> None:
    os.chmod(path, 0o700)
    func(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone and verify the anonymous git bundle.")
    parser.add_argument("--bundle", default="release/anonymous-drift-repair-v0.bundle")
    parser.add_argument("--clone-dir", default="release/anonymous-drift-repair-v0-verify")
    parser.add_argument("--bundle-report", default="results/anonymous_git_bundle_v0.json")
    parser.add_argument("--output", default="results/anonymous_git_bundle_verify_v0.json")
    args = parser.parse_args()

    bundle = (ROOT / args.bundle).resolve()
    clone_dir = (ROOT / args.clone_dir).resolve()
    release_dir = (ROOT / "release").resolve()
    if not bundle.exists():
        raise SystemExit(f"Bundle does not exist: {bundle}")
    if release_dir not in clone_dir.parents:
        raise SystemExit(f"Refusing to clone outside release/: {clone_dir}")

    bundle_report_path = ROOT / args.bundle_report
    expected_commit = None
    if bundle_report_path.exists():
        expected_commit = json.loads(bundle_report_path.read_text(encoding="utf-8")).get("commit_sha")

    report = verify(bundle, clone_dir, expected_commit)
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    if not report["valid"]:
        raise SystemExit("Anonymous git bundle verification failed")


if __name__ == "__main__":
    main()
