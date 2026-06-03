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


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate consistency of the submission handoff packet.")
    parser.add_argument("--output", default="results/submission_handoff_validation_v0.json")
    args = parser.parse_args()

    handoff = load_json("results/submission_handoff_v0.json")
    readiness = load_json("results/submission_readiness_v0.json")
    package = load_json("results/anonymous_release_package_v0.json")
    bundle = load_json("results/anonymous_git_bundle_v0.json")
    remote = load_json("results/anonymous_remote_readiness_v0.json")
    goal = load_json("results/goal_completion_audit_v0.json")

    errors: list[str] = []
    artifacts = handoff.get("anonymous_artifacts", {})
    verification = handoff.get("verification", {})

    checks = {
        "deterministic_v0_ready": handoff.get("deterministic_v0_ready") == readiness.get("deterministic_v0_ready"),
        "final_submission_ready": handoff.get("final_submission_ready") == readiness.get("final_submission_ready"),
        "zip_sha256": artifacts.get("zip", {}).get("sha256") == package.get("package_sha256"),
        "zip_bytes": artifacts.get("zip", {}).get("bytes") == package.get("package_bytes"),
        "zip_n_files": artifacts.get("zip", {}).get("n_files") == package.get("n_files"),
        "bundle_sha256": artifacts.get("git_bundle", {}).get("sha256") == bundle.get("bundle_sha256"),
        "bundle_bytes": artifacts.get("git_bundle", {}).get("bytes") == bundle.get("bundle_bytes"),
        "bundle_commit": artifacts.get("git_bundle", {}).get("commit_sha") == bundle.get("commit_sha"),
        "upload_ready": verification.get("upload_ready") == remote.get("upload_ready"),
        "hosted_remote_published": verification.get("hosted_remote_published") == remote.get("remote_publish_published"),
        "goal_not_complete_while_remote_blocked": (not goal.get("goal_complete")) if not remote.get("remote_created") else True,
    }
    for name, passed in checks.items():
        if not passed:
            errors.append(f"handoff consistency check failed: {name}")

    report = {
        "valid": not errors,
        "errors": errors,
        "checks": checks,
        "n_checks": len(checks),
        "n_errors": len(errors),
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    if errors:
        raise SystemExit("Submission handoff validation failed")


if __name__ == "__main__":
    main()
