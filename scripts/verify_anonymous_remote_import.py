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


def verify(bundle: Path, clone_dir: Path, bare_remote: Path, expected_commit: str | None) -> dict[str, Any]:
    clean(clone_dir)
    clean(bare_remote)
    clone_dir.parent.mkdir(parents=True, exist_ok=True)
    bare_remote.parent.mkdir(parents=True, exist_ok=True)

    run(["git", "clone", str(bundle), str(clone_dir)], cwd=ROOT)
    try:
        run(["git", "rev-parse", "--verify", "HEAD"], cwd=clone_dir)
    except RuntimeError:
        run(["git", "checkout", "-b", "main", "origin/main"], cwd=clone_dir)
    commit = run(["git", "rev-parse", "HEAD"], cwd=clone_dir)

    run(["git", "init", "--bare", str(bare_remote)], cwd=ROOT)
    run(["git", "remote", "add", "anonymous-local", str(bare_remote)], cwd=clone_dir)
    run(["git", "push", "anonymous-local", "main:main"], cwd=clone_dir)
    remote_commit = run(["git", "--git-dir", str(bare_remote), "rev-parse", "refs/heads/main"], cwd=ROOT)
    remote_refs = run(["git", "--git-dir", str(bare_remote), "show-ref"], cwd=ROOT).splitlines()

    return {
        "bundle": str(bundle.relative_to(ROOT)).replace("\\", "/"),
        "clone_dir": str(clone_dir.relative_to(ROOT)).replace("\\", "/"),
        "bare_remote": str(bare_remote.relative_to(ROOT)).replace("\\", "/"),
        "commit_sha": commit,
        "expected_commit_sha": expected_commit,
        "remote_commit_sha": remote_commit,
        "commit_matches_expected": expected_commit is None or commit == expected_commit,
        "remote_commit_matches": remote_commit == commit,
        "remote_refs": remote_refs,
        "valid": (expected_commit is None or commit == expected_commit) and remote_commit == commit,
        "note": "This is a local bare-repository import simulation. It does not create the final anonymous hosted repository.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify that the anonymous bundle can be imported into a bare remote.")
    parser.add_argument("--bundle", default="release/anonymous-drift-repair-v0.bundle")
    parser.add_argument("--clone-dir", default="release/anonymous-drift-repair-v0-import")
    parser.add_argument("--bare-remote", default="release/anonymous-drift-repair-v0-remote.git")
    parser.add_argument("--bundle-report", default="results/anonymous_git_bundle_v0.json")
    parser.add_argument("--output", default="results/anonymous_remote_import_verify_v0.json")
    args = parser.parse_args()

    release_dir = (ROOT / "release").resolve()
    bundle = (ROOT / args.bundle).resolve()
    clone_dir = (ROOT / args.clone_dir).resolve()
    bare_remote = (ROOT / args.bare_remote).resolve()
    if not bundle.exists():
        raise SystemExit(f"Bundle does not exist: {bundle}")
    for path in (clone_dir, bare_remote):
        if release_dir not in path.parents:
            raise SystemExit(f"Refusing to write outside release/: {path}")

    report = verify(bundle, clone_dir, bare_remote, load_expected_commit(ROOT / args.bundle_report))
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    if not report["valid"]:
        raise SystemExit("Anonymous remote import verification failed")


if __name__ == "__main__":
    main()
