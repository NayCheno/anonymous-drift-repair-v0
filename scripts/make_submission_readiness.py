#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def file_exists(path: str) -> bool:
    return (ROOT / path).exists()


def audit_findings(path: str) -> int | None:
    if not file_exists(path):
        return None
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("Findings:"):
            return int(line.split(":", 1)[1].strip())
    return None


def gate(name: str, status: str, evidence: str, note: str = "") -> dict[str, str]:
    return {"name": name, "status": status, "evidence": evidence, "note": note}


def build_report() -> dict[str, Any]:
    dataset = load_json("results/dataset_license_review_v0.json")
    dialogtool_review = load_json("results/dialogtool_source_review_v0.json")
    aaai_main = load_json("results/aaai_template_readiness_v0.json")
    aaai_candidate = load_json("results/aaai_template_candidate_readiness_v0.json")
    llm_review = load_json("results/llm_review_validation_v0.json")
    package = load_json("results/anonymous_release_package_v0.json")
    remote = load_json("results/anonymous_remote_readiness_v0.json") if file_exists("results/anonymous_remote_readiness_v0.json") else {}
    tracked_findings = audit_findings("results/anonymous_release_audit_v0.md")
    tree_findings = audit_findings("results/anonymous_release_tree_audit_v0.md")

    gates = [
        gate(
            "deterministic_v0_reproduction",
            "pass" if file_exists("results/metrics_v0.json") and file_exists("paper/tables/generated/main_table_v0.tex") else "fail",
            "python scripts/reproduce_v0.py",
            "Expected deterministic v0 outputs are present.",
        ),
        gate(
            "dataset_license_gate",
            "pass" if dataset.get("valid") and dataset.get("n_enabled") == 2 else "fail",
            "results/dataset_license_review_v0.json",
            f"Pending external license reviews: {dataset.get('n_pending')}.",
        ),
        gate(
            "dialogtool_source_review",
            "pass"
            if dialogtool_review.get("valid_for_release")
            and not dialogtool_review.get("authoritative_repository_confirmed")
            and dialogtool_review.get("recommended_config", {}).get("license_status") == "pending"
            else "fail",
            "docs/dialogtool_source_review.md; results/dialogtool_source_review_v0.json",
            "Negative-evidence source review recorded; DialogTool remains disabled and pending.",
        ),
        gate(
            "llm_reviewed_validation",
            "pass" if llm_review.get("valid") else "fail",
            "results/llm_review_validation_v0.json",
            "A=240 and B=48 Mimo-reviewed labels validate locally without an API call.",
        ),
        gate(
            "aaai_main_template",
            "blocker" if not aaai_main.get("template_applied") else "pass",
            "results/aaai_template_readiness_v0.json",
            "paper/main.tex uses the current public AAAI 2026 proxy; final AAAI-27 kit must still be rechecked when available."
            if aaai_main.get("template_applied")
            else "Current paper/main.tex is not yet on the selected AAAI template.",
        ),
        gate(
            "aaai_single_source_candidate",
            "pass" if aaai_candidate.get("template_applied") else "fail",
            "results/aaai_template_candidate_readiness_v0.json",
            "Generated proxy candidate is ready against the current public AAAI 2026 proxy.",
        ),
        gate(
            "anonymous_release_audit",
            "pass" if tracked_findings == 0 and tree_findings == 0 else "fail",
            "results/anonymous_release_audit_v0.md; results/anonymous_release_tree_audit_v0.md",
            f"Tracked findings={tracked_findings}; release-tree findings={tree_findings}.",
        ),
        gate(
            "anonymous_release_package",
            "pass" if package.get("package_exists") and package.get("package_sha256") else "fail",
            "results/anonymous_release_package_v0.json",
            f"Zip SHA256: {package.get('package_sha256')}",
        ),
        gate(
            "remote_anonymous_repository",
            "pass" if remote.get("remote_created") else "blocker",
            "docs/anonymous_remote_repository.md; results/anonymous_remote_readiness_v0.json",
            "Anonymous remote repository is configured."
            if remote.get("remote_created")
            else "Requires external remote repository creation and upload.",
        ),
    ]
    blockers = [item for item in gates if item["status"] == "blocker"]
    failures = [item for item in gates if item["status"] == "fail"]
    return {
        "deterministic_v0_ready": not failures,
        "final_submission_ready": not failures and not blockers,
        "n_gates": len(gates),
        "n_failures": len(failures),
        "n_blockers": len(blockers),
        "gates": gates,
        "remaining_blockers": blockers,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Submission Readiness v0",
        "",
        f"Deterministic v0 ready: `{str(report['deterministic_v0_ready']).lower()}`",
        f"Final submission ready: `{str(report['final_submission_ready']).lower()}`",
        f"Failures: `{report['n_failures']}`",
        f"Blockers: `{report['n_blockers']}`",
        "",
        "## Gates",
        "",
        "| Gate | Status | Evidence | Note |",
        "|---|---|---|---|",
    ]
    for item in report["gates"]:
        lines.append(
            f"| `{item['name']}` | `{item['status']}` | `{item['evidence']}` | {item['note']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report intentionally separates deterministic v0 artifact readiness from final submission readiness. A blocker does not invalidate the deterministic scaffold; it marks work that still requires an external choice, account, or final target template.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate deterministic v0 and submission-readiness gates.")
    parser.add_argument("--output-json", default="results/submission_readiness_v0.json")
    parser.add_argument("--output-md", default="results/submission_readiness_v0.md")
    args = parser.parse_args()

    report = build_report()
    out_json = ROOT / args.output_json
    out_md = ROOT / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, out_md)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
