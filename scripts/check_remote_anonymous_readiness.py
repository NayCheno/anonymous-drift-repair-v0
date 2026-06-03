#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def audit_findings(path: Path) -> int | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Findings:"):
            return int(line.split(":", 1)[1].strip())
    return None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    remotes = run_git(["remote", "-v"]).splitlines()
    package = load_json(ROOT / "results/anonymous_release_package_v0.json")
    bundle = load_json(ROOT / "results/anonymous_git_bundle_v0.json")
    bundle_verify = load_json(ROOT / "results/anonymous_git_bundle_verify_v0.json")
    import_verify = load_json(ROOT / "results/anonymous_remote_import_verify_v0.json")
    publish_verify = load_json(ROOT / "results/anonymous_remote_publish_v0.json")
    tracked_findings = audit_findings(ROOT / "results/anonymous_release_audit_v0.md")
    tree_findings = audit_findings(ROOT / "results/anonymous_release_tree_audit_v0.md")
    local_gh_available = shutil.which("gh") is not None or shutil.which("gh.exe") is not None

    package_ready = bool(package.get("package_exists") and package.get("package_sha256"))
    bundle_ready = bool(bundle.get("bundle_exists") and bundle.get("bundle_sha256"))
    bundle_verified = bool(bundle_verify.get("valid"))
    remote_import_verified = bool(import_verify.get("valid"))
    audits_ready = tracked_findings == 0 and tree_findings == 0
    anonymous_remote_configured = any(
        "anonymous" in remote.lower() or "drift-repair" in remote.lower()
        for remote in remotes
    )
    upload_ready = package_ready and bundle_ready and bundle_verified and remote_import_verified and audits_ready
    bundle_commit = bundle.get("commit_sha")
    publish_commit = publish_verify.get("commit_sha")
    remote_publish_commit_matches = bool(
        publish_verify.get("remote_commit_matches")
        and publish_verify.get("remote_commit_sha") == bundle_commit
        and publish_commit == bundle_commit
    )
    publish_verified = bool(publish_verify.get("published") and remote_publish_commit_matches)
    remote_created = anonymous_remote_configured or publish_verified
    gh_required_for_remote_creation = not remote_created
    gh_available = local_gh_available or not gh_required_for_remote_creation

    blockers = []
    if not package_ready:
        blockers.append("anonymous release package checksum is missing")
    if not bundle_ready:
        blockers.append("anonymous git bundle checksum is missing")
    if not bundle_verified:
        blockers.append("anonymous git bundle clone verification is missing or failed")
    if not remote_import_verified:
        blockers.append("anonymous bundle remote-import simulation is missing or failed")
    if not audits_ready:
        blockers.append("anonymous release audit has findings or missing outputs")
    if not remote_created:
        blockers.append("no anonymous hosted remote has been configured or successfully published")
    if gh_required_for_remote_creation and not gh_available:
        blockers.append("GitHub CLI is not available in this environment")

    return {
        "valid": upload_ready,
        "remote_created": remote_created,
        "upload_ready": upload_ready,
        "anonymous_remote_configured": anonymous_remote_configured,
        "gh_available": gh_available,
        "gh_required_for_remote_creation": gh_required_for_remote_creation,
        "gh_requirement_satisfied": gh_available,
        "remotes": remotes,
        "package": package.get("package"),
        "package_sha256": package.get("package_sha256"),
        "bundle": bundle.get("bundle"),
        "bundle_sha256": bundle.get("bundle_sha256"),
        "bundle_commit_sha": bundle_commit,
        "bundle_verify_valid": bundle_verify.get("valid"),
        "bundle_verify_commit_matches": bundle_verify.get("commit_matches"),
        "remote_import_verify_valid": import_verify.get("valid"),
        "remote_import_commit_matches": import_verify.get("remote_commit_matches"),
        "remote_publish_valid": publish_verify.get("valid"),
        "remote_publish_published": publish_verify.get("published"),
        "remote_publish_commit_matches": remote_publish_commit_matches,
        "tracked_audit_findings": tracked_findings,
        "release_tree_audit_findings": tree_findings,
        "blockers": blockers,
        "next_action": "Record the anonymous URL in the submission system and rerun submission readiness."
        if remote_created
        else "Create an anonymous remote repository, upload release/anonymous-drift-repair-v0.zip, import release/anonymous-drift-repair-v0.bundle, or push the release tree, and record the remote URL without author-identifying metadata.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check readiness for publishing the anonymous remote repository.")
    parser.add_argument("--output", default="results/anonymous_remote_readiness_v0.json")
    args = parser.parse_args()

    report = build_report()
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
