#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def tex_escape(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
    )


DISPLAY_NAMES = {
    "sage_r": "SAGE-R",
    "query_rewrite_rag": "QueryRewrite",
    "self_reflection": "SelfReflect",
    "vanilla_rag": "Vanilla",
    "full_sage_r": "Full",
    "wo_goal_constraint": "w/o Goal+Constr.",
    "wo_retrieval": "w/o Retrieval",
    "wo_evidence_abstention": "w/o Evid.+Abst.",
    "wo_tool_state": "w/o Tool",
    "wo_memory": "w/o Memory",
    "diagnose_only": "Diagnose-only",
    "annotator_a_vs_answer_key": "A vs key",
    "annotator_a_vs_annotator_b": "A vs B",
    "drift_type_exact_match": "Exact",
    "drift_type_micro_f1": "Micro-F1",
    "repair_rate": "Repair",
    "over_repair_rate": "Over-repair",
}


def display(value: str) -> str:
    return DISPLAY_NAMES.get(value, value)


def main_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        "System & Exact & F1 & Repair & Over-repair & Tokens \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{tex_escape(display(row['system']))} & {row['drift_type_exact_match']} & "
            f"{row['micro_f1']} & {row['repair_rate']} & {row['over_repair_rate']} & "
            f"{row['avg_extra_tokens']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Deterministic DriftBench v0 scaffold results. These numbers validate the pipeline and are not final benchmark claims.}",
            "\\label{tab:v0-main}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def ablation_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Variant & Exact & F1 & Repair & Tokens \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{tex_escape(display(row['variant']))} & {row['drift_type_exact_match']} & "
            f"{row['micro_f1']} & {row['repair_rate']} & {row['avg_extra_tokens']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Deterministic ablations on DriftBench v0. Module-removal variants isolate diagnosis coverage in the scaffold.}",
            "\\label{tab:v0-ablation}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def cost_table(rows: list[dict[str, str]]) -> str:
    total_rows = [row for row in rows if row["repair_action"] == "ALL"]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "System & Repaired & Tokens & Retrievals & Tools \\\\",
        "\\midrule",
    ]
    for row in total_rows:
        lines.append(
            f"{tex_escape(display(row['system']))} & {row['n_repaired']} & {row['avg_extra_tokens']} & "
            f"{row['avg_extra_retrievals']} & {row['avg_extra_tool_calls']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Cost logging summary for the deterministic v0 scaffold.}",
            "\\label{tab:v0-cost}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def human_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Comparison & Pairs & Drift & Severity & Repair \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{tex_escape(display(row['comparison']))} & {row['n_pairs']} & {row['drift_type_agreement']} & "
            f"{row['severity_agreement']} & {row['repair_action_agreement']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Human-validation workflow scaffold. The current v0 table uses an answer-key proxy and must be replaced by filled human annotations before final reporting.}",
            "\\label{tab:v0-human}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def llm_validation_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Comparison & Pairs & Drift & Severity & Repair \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{tex_escape(display(row['comparison']))} & {row['n_pairs']} & {row['drift_type_agreement']} & "
            f"{row['severity_agreement']} & {row['repair_action_agreement']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Mimo-reviewed validation on the deterministic v0 packet. The table reports agreement between the LLM-reviewed labels, the scaffold answer key, and the 48-item double-reviewed subset. These results are LLM-reviewed validation, not human-only annotation.}",
            "\\label{tab:v0-llm-validation}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def over_repair_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "System & Clean & Over-repaired & Rate \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{tex_escape(display(row['system']))} & {row['n_clean_gold']} & "
            f"{row['n_over_repaired']} & {row['over_repair_rate']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Clean-case over-repair analysis for the deterministic v0 scaffold. The rate is computed over examples whose gold action is answer-as-is.}",
            "\\label{tab:v0-over-repair}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def statistical_tests_table(rows: list[dict[str, str]]) -> str:
    selected = [
        row
        for row in rows
        if row["row_type"] == "paired_delta"
        and row["metric"] in {"drift_type_exact_match", "drift_type_micro_f1"}
    ]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        "Comparison & Metric & Delta & 95\\% CI & p \\\\",
        "\\midrule",
    ]
    for row in selected:
        comparison = row["comparison"].replace("sage_r_minus_", "SAGE-R $-$ ")
        ci = f"[{row['ci95_low']}, {row['ci95_high']}]"
        lines.append(
            f"{tex_escape(display(comparison))} & {tex_escape(display(row['metric']))} & "
            f"{row['estimate']} & {tex_escape(ci)} & {row['p_value']} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Paired bootstrap comparisons for the deterministic v0 scaffold. These tests validate the reporting pipeline and are not final statistical claims.}",
            "\\label{tab:v0-stats}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LaTeX table snippets from v0 result CSVs.")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--output-dir", default="paper/tables/generated")
    args = parser.parse_args()

    results = Path(args.results_dir)
    out = Path(args.output_dir)
    write(out / "main_table_v0.tex", main_table(read_csv(results / "main_table_v0.csv")))
    write(out / "ablation_v0.tex", ablation_table(read_csv(results / "ablation_v0.csv")))
    write(out / "cost_analysis_v0.tex", cost_table(read_csv(results / "cost_analysis_v0.csv")))
    write(out / "human_agreement_v0.tex", human_table(read_csv(results / "human_agreement_v0.csv")))
    llm_agreement = results / "llm_human_agreement_v0.csv"
    if llm_agreement.exists():
        write(out / "llm_human_agreement_v0.tex", llm_validation_table(read_csv(llm_agreement)))
    write(out / "over_repair_v0.tex", over_repair_table(read_csv(results / "over_repair_analysis_v0.csv")))
    write(out / "statistical_tests_v0.tex", statistical_tests_table(read_csv(results / "statistical_tests_v0.csv")))
    print(f"Wrote generated paper tables to {out}")


if __name__ == "__main__":
    main()
