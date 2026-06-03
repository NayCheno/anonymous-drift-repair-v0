#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict[str, Any]:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def build_handoff() -> dict[str, Any]:
    readiness = load_json("results/submission_readiness_v0.json")
    package = load_json("results/anonymous_release_package_v0.json")
    bundle = load_json("results/anonymous_git_bundle_v0.json")
    bundle_verify = load_json("results/anonymous_git_bundle_verify_v0.json")
    import_verify = load_json("results/anonymous_remote_import_verify_v0.json")
    publish = load_json("results/anonymous_remote_publish_v0.json")
    remote = load_json("results/anonymous_remote_readiness_v0.json")

    return {
        "deterministic_v0_ready": readiness.get("deterministic_v0_ready"),
        "final_submission_ready": readiness.get("final_submission_ready"),
        "remaining_blockers": readiness.get("remaining_blockers", []),
        "anonymous_artifacts": {
            "zip": {
                "path": package.get("package"),
                "sha256": package.get("package_sha256"),
                "bytes": package.get("package_bytes"),
                "n_files": package.get("n_files"),
            },
            "git_bundle": {
                "path": bundle.get("bundle"),
                "sha256": bundle.get("bundle_sha256"),
                "bytes": bundle.get("bundle_bytes"),
                "commit_sha": bundle.get("commit_sha"),
            },
        },
        "verification": {
            "tracked_audit_findings": remote.get("tracked_audit_findings"),
            "release_tree_audit_findings": remote.get("release_tree_audit_findings"),
            "bundle_clone_valid": bundle_verify.get("valid"),
            "bundle_clone_commit_matches": bundle_verify.get("commit_matches"),
            "bare_remote_import_valid": import_verify.get("valid"),
            "bare_remote_commit_matches": import_verify.get("remote_commit_matches"),
            "publish_valid": publish.get("valid"),
            "publish_dry_run": publish.get("dry_run"),
            "hosted_remote_published": publish.get("published"),
            "hosted_remote_commit_matches": publish.get("remote_commit_matches"),
            "upload_ready": remote.get("upload_ready"),
        },
        "external_action_required": {
            "create_hosted_anonymous_repo": not remote.get("remote_created"),
            "record_remote_url": True,
            "commands": [
                "python scripts/publish_anonymous_remote.py --remote-url <anonymous-url> --push",
                "python scripts/check_remote_anonymous_readiness.py",
                "python scripts/make_submission_readiness.py",
                "python scripts/make_submission_handoff.py",
            ],
        },
        "reporting_boundaries": [
            "Deterministic v0 scaffold is reproducible; real benchmark results are not claimed.",
            "DialogTool remains disabled and pending license/source confirmation.",
            "paper/main.tex uses the current public AAAI 2026 proxy; final AAAI-27 kit must be rechecked.",
            "LLM-reviewed validation uses Mimo outputs and should not be described as human-only annotation.",
        ],
    }


def write_markdown(handoff: dict[str, Any], path: Path) -> None:
    artifacts = handoff["anonymous_artifacts"]
    verification = handoff["verification"]
    commands = handoff["external_action_required"]["commands"]
    blockers = handoff.get("remaining_blockers", [])
    lines = [
        "# Submission Handoff v0",
        "",
        f"Deterministic v0 ready: `{str(handoff.get('deterministic_v0_ready')).lower()}`",
        f"Final submission ready: `{str(handoff.get('final_submission_ready')).lower()}`",
        "",
        "## Anonymous Artifacts",
        "",
        f"- Zip: `{artifacts['zip']['path']}`",
        f"- Zip SHA256: `{artifacts['zip']['sha256']}`",
        f"- Git bundle: `{artifacts['git_bundle']['path']}`",
        f"- Git bundle SHA256: `{artifacts['git_bundle']['sha256']}`",
        f"- Git bundle commit: `{artifacts['git_bundle']['commit_sha']}`",
        "",
        "## Verification",
        "",
        f"- Tracked audit findings: `{verification.get('tracked_audit_findings')}`",
        f"- Release-tree audit findings: `{verification.get('release_tree_audit_findings')}`",
        f"- Bundle clone valid: `{str(verification.get('bundle_clone_valid')).lower()}`",
        f"- Bare-remote import valid: `{str(verification.get('bare_remote_import_valid')).lower()}`",
        f"- Hosted remote published: `{str(verification.get('hosted_remote_published')).lower()}`",
        f"- Hosted remote commit matches bundle: `{str(verification.get('hosted_remote_commit_matches')).lower()}`",
        f"- Publish dry-run: `{str(verification.get('publish_dry_run')).lower()}`",
        f"- Publish valid: `{str(verification.get('publish_valid')).lower()}`",
        f"- Upload ready: `{str(verification.get('upload_ready')).lower()}`",
        "",
        "## Remaining Action",
        "",
    ]
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker.get('name')}`: {blocker.get('note')}")
    else:
        lines.append("- None recorded.")
    if handoff["external_action_required"]["create_hosted_anonymous_repo"]:
        lines.extend(["", "Run after creating the anonymous hosted repository:", ""])
        lines.append("```bash")
        lines.extend(commands)
        lines.append("```")
    else:
        lines.extend(["", "The hosted anonymous repository is already published. Record the anonymous URL in the submission system."])
    lines.extend(["", "## Reporting Boundaries", ""])
    for item in handoff["reporting_boundaries"]:
        lines.append(f"- {item}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a deterministic v0 submission handoff packet.")
    parser.add_argument("--output-json", default="results/submission_handoff_v0.json")
    parser.add_argument("--output-md", default="results/submission_handoff_v0.md")
    args = parser.parse_args()

    handoff = build_handoff()
    out_json = ROOT / args.output_json
    out_md = ROOT / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(handoff, out_md)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
