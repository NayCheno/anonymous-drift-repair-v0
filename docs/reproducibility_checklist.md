# Reproducibility Checklist

## Data

- [x] Dataset names and versions listed for deterministic v0 scaffold.
- [ ] Dataset licenses checked.
- [x] Dataset license gate included for deterministic v0; external licenses remain pending.
- [x] External license review status recorded for available upstream sources; DialogTool remains pending.
- [x] Draft split frozen for DriftBench v0.
- [x] DriftBench construction scripts released.
- [x] Annotation guidelines released.
- [x] Human validation protocol documented.
- [x] Human annotation completion checker and adjudication queue scaffold included.
- [x] Human agreement reportability gate included; proxy agreement is marked non-reportable.
- [x] LLM reviewer workflow smoke validated with Mimo OpenAI-compatible config.
- [x] LLM-reviewed validation completed for DriftBench v0 packet.

## Models

- [x] Generator model names and versions listed for deterministic v0.
- [x] Verifier/judge model names and versions listed for deterministic v0.
- [x] Decoding parameters fixed for deterministic v0.
- [x] Random seeds fixed for deterministic v0 scaffold.
- [x] API model date/version placeholders recorded; no API model is enabled in deterministic v0.

## Retrieval

- [x] Corpus preprocessing documented for deterministic v0.
- [x] Retriever type documented for deterministic v0.
- [x] top-k and chunking fixed for deterministic v0.
- [x] Index construction reproducible for deterministic v0.

## Agent and repair

- [x] State graph schema documented.
- [x] Drift detectors described.
- [x] Repair actions described.
- [x] Thresholds and budgets listed for deterministic v0 scaffold.
- [x] Trace logs saved.

## Metrics

- [x] Task success metric defined.
- [x] State consistency metric defined.
- [x] Faithfulness metric defined.
- [x] Recovery and over-repair defined.
- [x] Cost metric defined.
- [x] Statistical test scaffold included for deterministic v0.

## Artifact release

- [ ] Anonymous repository.
- [x] Anonymous remote readiness checker included; remote creation remains external.
- [x] AAAI template migration readiness report generated for deterministic v0.
- [x] AAAI single-source migration candidate generated against current public proxy.
- [x] `paper/main.tex` migrated to the current public AAAI 2026 proxy format; final AAAI-27 kit must still be rechecked.
- [x] Local anonymous release package checksum generated for deterministic v0.
- [x] Local anonymous release manifest integrity validation generated for deterministic v0.
- [x] Local anonymous git bundle checksum generated for deterministic v0.
- [x] Local anonymous git bundle clone verification generated for deterministic v0.
- [x] Local anonymous bare-remote import verification generated for deterministic v0.
- [x] Hosted anonymous remote publish dry-run generated for deterministic v0.
- [x] Submission handoff packet generated for deterministic v0.
- [x] Submission handoff consistency validation generated for deterministic v0.
- [x] Goal completion audit generated for deterministic v0.
- [x] Installation instructions.
- [x] Smoke test.
- [x] Expected outputs.
- [x] Results reproduction script.

## Deterministic v0 reproduction

Run:

```bash
python scripts/reproduce_v0.py
```

Configuration check:

```bash
python scripts/validate_dataset_licenses.py
python scripts/validate_repro_config.py
python scripts/check_aaai_template_readiness.py
python scripts/check_aaai_template_readiness.py --input paper/main_aaai2026_candidate.tex --output results/aaai_template_candidate_readiness_v0.json
python scripts/validate_llm_review_outputs.py
python scripts/check_remote_anonymous_readiness.py
python scripts/make_submission_readiness.py
```

Expected key outputs:

- `data/driftbench_v0.jsonl`
- `results/aaai_template_readiness_v0.json`
- `results/aaai_template_candidate_readiness_v0.json`
- `results/anonymous_release_package_v0.json`
- `results/anonymous_release_manifest_validation_v0.json`
- `results/anonymous_git_bundle_v0.json`
- `results/anonymous_git_bundle_verify_v0.json`
- `results/anonymous_remote_import_verify_v0.json`
- `results/anonymous_remote_publish_v0.json`
- `results/anonymous_remote_readiness_v0.json`
- `results/dataset_license_review_v0.json`
- `results/sage_r_v0.jsonl`
- `results/baselines_v0.jsonl`
- `results/case_studies_v0.md`
- `results/main_table_v0.csv`
- `results/drift_type_breakdown_v0.csv`
- `results/cost_analysis_v0.csv`
- `results/ablation_v0.csv`
- `results/human_agreement_v0.csv`
- `results/human_agreement_status_v0.json`
- `results/human_annotation_status_v0.json`
- `results/llm_annotation_review_smoke_v0.json`
- `results/llm_annotation_review_a_v0.json`
- `results/llm_annotation_review_b_v0.json`
- `results/llm_annotation_status_v0.json`
- `results/llm_human_agreement_v0.csv`
- `results/llm_human_agreement_status_v0.json`
- `results/llm_review_validation_v0.json`
- `results/over_repair_analysis_v0.csv`
- `results/statistical_tests_v0.csv`
- `results/submission_readiness_v0.json`
- `results/submission_readiness_v0.md`
- `results/submission_handoff_v0.json`
- `results/submission_handoff_v0.md`
- `results/submission_handoff_validation_v0.json`
- `results/goal_completion_audit_v0.json`
- `results/goal_completion_audit_v0.md`
- `paper/tables/generated/main_table_v0.tex`
- `paper/tables/generated/llm_human_agreement_v0.tex`
