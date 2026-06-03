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


def remove_readonly(func: Any, path: str, _exc_info: Any) -> None:
    os.chmod(path, 0o700)
    func(path)


def clean(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, onexc=remove_readonly)


def load_expected_commit(path: Path) -> str | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("commit_sha")


def checkout_bundle(bundle: Path, clone_dir: Path) -> str:
    clean(clone_dir)
    clone_dir.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", str(bundle), str(clone_dir)], cwd=ROOT)
    try:
        run(["git", "rev-parse", "--verify", "HEAD"], cwd=clone_dir)
    except RuntimeError:
        run(["git", "checkout", "-b", "main", "origin/main"], cwd=clone_dir)
    return run(["git", "rev-parse", "HEAD"], cwd=clone_dir)


def publish(
    bundle: Path,
    clone_dir: Path,
    remote_url: str,
    expected_commit: str | None,
    push: bool,
    record_url: bool,
    force: bool,
) -> dict[str, Any]:
    commit = checkout_bundle(bundle, clone_dir)
    report = {
        "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
        "clone_dir": str(clone_dir.relative_to(ROOT)).replace("\\", "/"),
        "commit_sha": commit,
        "expected_commit_sha": expected_commit,
        "commit_matches_expected": expected_commit is None or commit == expected_commit,
        "remote_url": remote_url if record_url else "<redacted>",
        "dry_run": not push,
        "published": False,
        "force_push": force,
        "remote_commit_sha": None,
        "remote_commit_matches": False,
        "valid": False,
        "next_action": "Run again with --push after creating the anonymous hosted repository.",
    }
    if not push:
        report["valid"] = report["commit_matches_expected"]
        return report

    run(["git", "remote", "add", "anonymous-hosted", remote_url], cwd=clone_dir)
    push_cmd = ["git", "push", "anonymous-hosted", "main:main"]
    if force:
        push_cmd.insert(2, "--force")
    run(push_cmd, cwd=clone_dir)
    remote_refs = run(["git", "ls-remote", remote_url, "refs/heads/main"], cwd=ROOT).splitlines()
    remote_commit = remote_refs[0].split()[0] if remote_refs else None
    report.update(
        {
            "published": True,
            "remote_commit_sha": remote_commit,
            "remote_commit_matches": remote_commit == commit,
            "valid": report["commit_matches_expected"] and remote_commit == commit,
            "next_action": "Record the anonymous URL in the submission system and rerun submission readiness.",
        }
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the anonymous bundle to a provided hosted remote.")
    parser.add_argument("--bundle", default="release/anonymous-drift-repair-v0.bundle")
    parser.add_argument("--clone-dir", default="release/anonymous-drift-repair-v0-publish")
    parser.add_argument("--bundle-report", default="results/anonymous_git_bundle_v0.json")
    parser.add_argument("--remote-url", default="ANONYMOUS_REMOTE_URL_REQUIRED")
    parser.add_argument("--output", default="results/anonymous_remote_publish_v0.json")
    parser.add_argument("--push", action="store_true", help="Actually push main to --remote-url.")
    parser.add_argument("--force", action="store_true", help="Force-update the hosted main branch from the regenerated anonymous bundle.")
    parser.add_argument("--record-url", action="store_true", help="Record --remote-url in the JSON report.")
    args = parser.parse_args()

    release_dir = (ROOT / "release").resolve()
    bundle = (ROOT / args.bundle).resolve()
    clone_dir = (ROOT / args.clone_dir).resolve()
    if not bundle.exists():
        raise SystemExit(f"Bundle does not exist: {bundle}")
    if release_dir not in clone_dir.parents:
        raise SystemExit(f"Refusing to write outside release/: {clone_dir}")
    if args.push and args.remote_url == "ANONYMOUS_REMOTE_URL_REQUIRED":
        raise SystemExit("--remote-url is required with --push")

    report = publish(
        bundle=bundle,
        clone_dir=clone_dir,
        remote_url=args.remote_url,
        expected_commit=load_expected_commit(ROOT / args.bundle_report),
        push=args.push,
        record_url=args.record_url,
        force=args.force,
    )
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    if args.push and not report["valid"]:
        raise SystemExit("Anonymous remote publish verification failed")


if __name__ == "__main__":
    main()
