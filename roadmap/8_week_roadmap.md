# 8-Week Roadmap

## Week 1: Problem and schema freeze

Deliverables:

- Final state drift taxonomy.
- State graph schema.
- 20 hand-written examples.
- Paper skeleton with intro and problem formulation.

Exit criteria:

- Every drift type has at least 3 examples.
- Active-state resolution rules are written.

Status:

- Completed in the Week 1 scaffold: taxonomy/schema freeze, active-state resolution rules, and 21 hand-written smoke examples.

## Week 2: DriftBench v0

Deliverables:

- Dataset adapters for MTRAG/MTRAG-UN or toy equivalents.
- Perturbation scripts.
- 300-500 draft examples.
- Annotation guideline v1.

Exit criteria:

- JSONL schema frozen.
- 50 examples manually checked.

Status:

- Completed for toy-equivalent v0: `driftbench_v0.1` JSONL schema, 300 draft examples, 50-case scaffold review file, and runnable baseline/SAGE-R/evaluation entrypoints.

## Week 3: Diagnosis modules

Deliverables:

- Goal/constraint detector.
- Evidence detector.
- Retrieval drift detector.
- Tool-state detector.
- Abstention detector.

Exit criteria:

- Diagnosis output includes type, severity, conflicting nodes, suggested repair.

Status:

- Completed for deterministic scaffold: diagnosis modules implemented for goal/constraint, evidence/abstention, retrieval, tool-state, and memory drift. Diagnosis output includes drift types, severity, conflicting nodes, suggested repair, module hits, and structured signals.

## Week 4: Repair policy

Deliverables:

- Rollback + replan.
- Query rewrite + re-retrieve.
- Tool cross-validation.
- Clarify/abstain decision.
- Initial SAGE-R results on toy and dev data.

Exit criteria:

- Repair trace can be inspected for every example.

Status:

- Completed for deterministic v0 scaffold: typed repair traces exist for answer-as-is, rollback/replan, re-retrieve/verify, tool cross-validation, and memory priority updates. Every DriftBench v0 prediction includes inspectable repair trace fields.

## Week 5: Main experiments

Deliverables:

- Baseline implementations.
- Main result table.
- Drift-type breakdown.
- Cost logging.

Exit criteria:

- At least 2 datasets and 3 baselines complete.

Status:

- Completed for deterministic v0 scaffold: implemented three baseline proxies (`vanilla_rag`, `query_rewrite_rag`, `self_reflection`) on DriftBench v0, with cost logging, `results/main_table_v0.csv`, `results/drift_type_breakdown_v0.csv`, and `results/cost_analysis_v0.csv`. Local JSON/JSONL seed adapters exist for MTRAG, MTRAG-UN, tau-bench, DialogTool, and LongMemEval. A dataset license gate prevents pending external datasets from being enabled. Upstream license status is recorded for MTRAG/MTRAG-UN, tau-bench, and LongMemEval; DialogTool, external dataset downloads, and final real-data labels remain post-v0 work.

## Week 6: Ablations and human validation

Deliverables:

- Ablation table.
- Human validation of 200-300 cases.
- Judge-human agreement.
- Over-repair analysis.

Exit criteria:

- All core paper tables are populated.

Status:

- Completed for deterministic v0 scaffold: generated `results/ablation_v0.csv` and `results/ablations_v0.jsonl` for module-removal and diagnose-only ablations. Prepared a 240-case blinded validation packet with a 48-case double-annotation subset, a human-agreement calculation workflow and proxy table, a non-reportable agreement status gate, and a completion checker with adjudication queue. Mimo `mimo-v2.5` LLM-reviewed validation is complete for 240 A items and 48 B items, with agreement/status outputs, an adjudication queue, and a no-API verifier. `results/over_repair_analysis_v0.csv` and `results/statistical_tests_v0.csv` are generated.

## Week 7: Paper full draft

Deliverables:

- Complete 7-8 page draft.
- Figures and case studies.
- Related work refined.
- Limitations and ethics section.

Exit criteria:

- Draft can be sent to collaborators.

Status:

- Completed for deterministic v0 scaffold: deterministic v0 scaffold results have been integrated into the paper draft with generated LaTeX tables for main results, ablations, cost, human-validation workflow, and Mimo-reviewed validation. The SAGE-R algorithm box is included, and deterministic case-study traces are generated for qualitative audit. Full real-data paper draft remains post-v0 work.

## Week 8: Submission package

Deliverables:

- Final PDF.
- Supplementary material.
- Anonymous code repo.
- Reproducibility checklist.
- Final proofreading.

Exit criteria:

- Paper, supplement, code, and data card are internally consistent.

Status:

- Completed for deterministic v0 scaffold: deterministic v0 artifacts can be regenerated with `python scripts/reproduce_v0.py`; README, MANIFEST, and reproducibility checklist document the v0 scaffold outputs. Model, decoding, and keyword retriever settings are frozen for deterministic v0 and checked by `python scripts/validate_repro_config.py`. `paper/main.tex` is migrated to the current public AAAI 2026 proxy format, with `paper/main_aaai2026_candidate.tex` retained for auditability; final AAAI-27 kit compliance must still be rechecked once the target kit is available. A local anonymous release tree can be built with `python scripts/build_anonymous_release.py --clean`; tracked files and release tree pass audit with zero configured findings; `python scripts/package_anonymous_release.py` writes a local zip checksum report. A v0 supplementary PDF is generated. The hosted anonymous remote repository is published and verified by bundle commit match, and `results/submission_readiness_v0.md` reports zero aggregate blockers.
