#!/usr/bin/env python
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


COMMANDS = [
    [
        "scripts/validate_dataset_licenses.py",
    ],
    [
        "scripts/validate_repro_config.py",
    ],
    [
        "scripts/check_aaai_template_readiness.py",
    ],
    [
        "scripts/make_aaai_source_candidate.py",
    ],
    [
        "scripts/check_aaai_template_readiness.py",
        "--input",
        "paper/main_aaai2026_candidate.tex",
        "--output",
        "results/aaai_template_candidate_readiness_v0.json",
    ],
    [
        "scripts/make_driftbench.py",
        "--input",
        "data/toy_examples.jsonl",
        "--output",
        "data/driftbench_v0.jsonl",
        "--target-size",
        "300",
        "--seed",
        "42",
    ],
    [
        "scripts/validate_driftbench.py",
        "--input",
        "data/driftbench_v0.jsonl",
        "--review-output",
        "data/driftbench_v0_manual_check_50.jsonl",
    ],
    [
        "scripts/run_agent.py",
        "--dataset",
        "data/driftbench_v0.jsonl",
        "--output",
        "results/sage_r_v0.jsonl",
    ],
    [
        "scripts/run_baselines.py",
        "--dataset",
        "data/driftbench_v0.jsonl",
        "--output",
        "results/baselines_v0.jsonl",
    ],
    [
        "scripts/evaluate.py",
        "--predictions",
        "results/sage_r_v0.jsonl",
        "--output",
        "results/metrics_v0.json",
    ],
    [
        "scripts/evaluate.py",
        "--predictions",
        "results/baselines_v0.jsonl",
        "--output",
        "results/baseline_metrics_v0.json",
    ],
    [
        "scripts/analyze_results.py",
        "--predictions",
        "results/sage_r_v0.jsonl",
        "--output",
        "results/error_analysis_v0.md",
    ],
    [
        "scripts/make_case_studies.py",
        "--dataset",
        "data/driftbench_v0.jsonl",
        "--predictions",
        "results/sage_r_v0.jsonl",
        "--output",
        "results/case_studies_v0.md",
    ],
    [
        "scripts/make_main_table.py",
        "--sage-r",
        "results/sage_r_v0.jsonl",
        "--baselines",
        "results/baselines_v0.jsonl",
        "--output",
        "results/main_table_v0.csv",
    ],
    [
        "scripts/make_drift_type_breakdown.py",
        "--sage-r",
        "results/sage_r_v0.jsonl",
        "--baselines",
        "results/baselines_v0.jsonl",
        "--output",
        "results/drift_type_breakdown_v0.csv",
    ],
    [
        "scripts/make_cost_analysis.py",
        "--sage-r",
        "results/sage_r_v0.jsonl",
        "--baselines",
        "results/baselines_v0.jsonl",
        "--output",
        "results/cost_analysis_v0.csv",
    ],
    [
        "scripts/run_ablations.py",
        "--dataset",
        "data/driftbench_v0.jsonl",
        "--predictions-output",
        "results/ablations_v0.jsonl",
        "--table-output",
        "results/ablation_v0.csv",
    ],
    [
        "scripts/make_human_validation_packet.py",
        "--input",
        "data/driftbench_v0.jsonl",
        "--output-dir",
        "data/human_validation",
        "--target-size",
        "240",
        "--double-annotate-rate",
        "0.2",
        "--seed",
        "42",
    ],
    [
        "scripts/make_human_agreement.py",
        "--answer-key",
        "data/human_validation/human_validation_answer_key_v0.jsonl",
        "--proxy-from-answer-key",
        "--output",
        "results/human_agreement_v0.csv",
        "--status-output",
        "results/human_agreement_status_v0.json",
    ],
    [
        "scripts/check_human_annotation_status.py",
        "--annotator-a",
        "data/human_validation/human_validation_annotator_a_v0.jsonl",
        "--annotator-b",
        "data/human_validation/human_validation_annotator_b_v0.jsonl",
        "--output",
        "results/human_annotation_status_v0.json",
        "--adjudication-output",
        "data/human_validation/human_adjudication_queue_v0.jsonl",
    ],
    [
        "scripts/validate_llm_review_outputs.py",
    ],
    [
        "scripts/make_over_repair_analysis.py",
        "--sage-r",
        "results/sage_r_v0.jsonl",
        "--baselines",
        "results/baselines_v0.jsonl",
        "--output",
        "results/over_repair_analysis_v0.csv",
    ],
    [
        "scripts/make_statistical_tests.py",
        "--sage-r",
        "results/sage_r_v0.jsonl",
        "--baselines",
        "results/baselines_v0.jsonl",
        "--output",
        "results/statistical_tests_v0.csv",
        "--n-bootstrap",
        "1000",
        "--seed",
        "42",
    ],
    [
        "scripts/make_paper_tables.py",
        "--results-dir",
        "results",
        "--output-dir",
        "paper/tables/generated",
    ],
    [
        "scripts/make_submission_readiness.py",
    ],
    [
        "scripts/build_anonymous_release.py",
        "--clean",
    ],
    [
        "scripts/audit_anonymous_release.py",
        "--output",
        "results/anonymous_release_audit_v0.md",
    ],
    [
        "scripts/audit_anonymous_release.py",
        "--root",
        "release/anonymous-drift-repair-v0",
        "--output",
        "results/anonymous_release_tree_audit_v0.md",
    ],
    [
        "scripts/package_anonymous_release.py",
    ],
    [
        "scripts/validate_anonymous_release_manifest.py",
    ],
    [
        "scripts/package_anonymous_git_bundle.py",
    ],
    [
        "scripts/verify_anonymous_git_bundle.py",
    ],
    [
        "scripts/verify_anonymous_remote_import.py",
    ],
    [
        "scripts/publish_anonymous_remote.py",
        "--remote-url",
        "ANONYMOUS_REMOTE_URL_REQUIRED",
        "--output",
        "results/anonymous_remote_publish_dry_run_v0.json",
    ],
    [
        "scripts/check_remote_anonymous_readiness.py",
    ],
    [
        "scripts/make_submission_readiness.py",
    ],
    [
        "scripts/make_submission_handoff.py",
    ],
    [
        "scripts/make_goal_completion_audit.py",
    ],
    [
        "scripts/validate_submission_handoff.py",
    ],
]


EXPECTED_OUTPUTS = [
    "data/driftbench_v0.jsonl",
    "data/driftbench_v0_manual_check_50.jsonl",
    "data/human_validation/human_validation_summary_v0.json",
    "data/human_validation/human_adjudication_queue_v0.jsonl",
    "results/dataset_license_review_v0.json",
    "results/aaai_template_readiness_v0.json",
    "results/aaai_template_candidate_readiness_v0.json",
    "paper/main_aaai2026_candidate.tex",
    "results/sage_r_v0.jsonl",
    "results/baselines_v0.jsonl",
    "results/metrics_v0.json",
    "results/baseline_metrics_v0.json",
    "results/case_studies_v0.md",
    "results/main_table_v0.csv",
    "results/drift_type_breakdown_v0.csv",
    "results/cost_analysis_v0.csv",
    "results/ablation_v0.csv",
    "results/human_agreement_v0.csv",
    "results/human_agreement_status_v0.json",
    "results/human_annotation_status_v0.json",
    "results/llm_review_validation_v0.json",
    "results/over_repair_analysis_v0.csv",
    "results/statistical_tests_v0.csv",
    "paper/tables/generated/main_table_v0.tex",
    "paper/tables/generated/llm_human_agreement_v0.tex",
    "paper/tables/generated/statistical_tests_v0.tex",
    "results/anonymous_release_audit_v0.md",
    "results/anonymous_release_tree_audit_v0.md",
    "results/anonymous_release_package_v0.json",
    "results/anonymous_release_manifest_validation_v0.json",
    "results/anonymous_git_bundle_v0.json",
    "results/anonymous_git_bundle_verify_v0.json",
    "results/anonymous_remote_import_verify_v0.json",
    "results/anonymous_remote_publish_v0.json",
    "results/anonymous_remote_readiness_v0.json",
    "results/submission_readiness_v0.json",
    "results/submission_readiness_v0.md",
    "results/submission_handoff_v0.json",
    "results/submission_handoff_v0.md",
    "results/goal_completion_audit_v0.json",
    "results/goal_completion_audit_v0.md",
    "results/submission_handoff_validation_v0.json",
]


def run_command(args: list[str], dry_run: bool) -> None:
    command = [sys.executable, *args]
    print("+ " + " ".join(command))
    if dry_run:
        return
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce deterministic DriftBench v0 artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them.")
    args = parser.parse_args()

    for command in COMMANDS:
        run_command(command, args.dry_run)

    if not args.dry_run:
        missing = [path for path in EXPECTED_OUTPUTS if not (ROOT / path).exists()]
        if missing:
            raise SystemExit(f"Missing expected outputs: {missing}")
        print("All expected DriftBench v0 outputs are present.")


if __name__ == "__main__":
    main()
