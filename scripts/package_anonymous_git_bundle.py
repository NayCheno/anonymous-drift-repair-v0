#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def copy_release_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst, onexc=remove_readonly)
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
    shutil.copytree(src, dst, ignore=ignore)


def remove_readonly(func: Any, path: str, _exc_info: Any) -> None:
    os.chmod(path, 0o700)
    func(path)


def count_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def build_bundle(release_root: Path, worktree: Path, bundle_path: Path) -> dict[str, Any]:
    copy_release_tree(release_root, worktree)
    env = {
        **__import__("os").environ,
        "GIT_AUTHOR_NAME": "Anonymous Authors",
        "GIT_AUTHOR_EMAIL": "anonymous@example.com",
        "GIT_COMMITTER_NAME": "Anonymous Authors",
        "GIT_COMMITTER_EMAIL": "anonymous@example.com",
    }
    run(["git", "init"], cwd=worktree, env=env)
    run(["git", "add", "-A"], cwd=worktree, env=env)
    run(["git", "commit", "-m", "Anonymous deterministic v0 release"], cwd=worktree, env=env)
    run(["git", "branch", "-M", "main"], cwd=worktree, env=env)
    commit_sha = run(["git", "rev-parse", "HEAD"], cwd=worktree, env=env)
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    if bundle_path.exists():
        bundle_path.unlink()
    run(["git", "bundle", "create", str(bundle_path), "main"], cwd=worktree, env=env)
    return {"commit_sha": commit_sha, "n_source_files": count_files(worktree)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an importable anonymous git bundle from the release tree.")
    parser.add_argument("--root", default="release/anonymous-drift-repair-v0")
    parser.add_argument("--worktree", default="release/anonymous-drift-repair-v0-git")
    parser.add_argument("--output", default="release/anonymous-drift-repair-v0.bundle")
    parser.add_argument("--manifest-output", default="results/anonymous_git_bundle_v0.json")
    args = parser.parse_args()

    release_root = (ROOT / args.root).resolve()
    worktree = (ROOT / args.worktree).resolve()
    bundle_path = (ROOT / args.output).resolve()
    release_dir = (ROOT / "release").resolve()
    if not release_root.exists():
        raise SystemExit(f"Release root does not exist: {release_root}")
    if release_dir not in worktree.parents:
        raise SystemExit(f"Refusing to write worktree outside release/: {worktree}")
    if release_dir not in bundle_path.parents:
        raise SystemExit(f"Refusing to write bundle outside release/: {bundle_path}")

    bundle_info = build_bundle(release_root, worktree, bundle_path)
    report = {
        "bundle": args.output,
        "bundle_bytes": bundle_path.stat().st_size,
        "bundle_exists": bundle_path.exists(),
        "bundle_sha256": sha256_file(bundle_path),
        "release_root": args.root,
        "worktree": args.worktree,
        "note": "The bundle is generated under release/ and ignored by git; this JSON is the tracked checksum record for offline remote import.",
        **bundle_info,
    }
    out = ROOT / args.manifest_output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {bundle_path}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
