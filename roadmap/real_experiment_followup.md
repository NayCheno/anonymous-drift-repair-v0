# Real-Experiment Follow-up Roadmap

This roadmap starts after deterministic v0 closure. It is not evidence that real benchmark experiments are complete, and it must not be cited as a v0 readiness blocker.

## Stage A: Data and Licensing

- [ ] Acquire local copies of MTRAG/MTRAG-UN and tau-bench under licenses compatible with local evaluation.
- [ ] Keep DialogTool disabled until an authoritative repository and license are confirmed.
- [ ] Optionally acquire LongMemEval for memory-drift analysis after required datasets are stable.
- [ ] Convert each approved dataset through `scripts/convert_external_dataset.py` or a dataset-specific adapter.
- [ ] Record every source URL, version, split, license, redistribution status, and disabled/enabled decision in `configs/datasets.yaml` and `docs/dataset_license_status.md`.

Acceptance criteria:

- Enabled datasets have `license_status: checked` or another explicitly allowed status.
- Disabled or pending datasets cannot be loaded by the reproduction path.
- Converted examples remain marked `needs_annotation` until labels are reviewed.

## Stage B: Real Models and Retrieval

- [ ] Add provider-backed generator and verifier/Judge implementations behind the existing scaffold interfaces.
- [ ] Configure one strong API model and at least two open-source model candidates for generator runs.
- [ ] Configure BM25 plus one dense retriever; freeze corpus preprocessing, query rewriting, top-k, and reranking settings.
- [ ] Log model name, model version, decoding parameters, prompt version, retriever version, token counts, retrieval counts, tool calls, and wall-clock cost for every run.

Acceptance criteria:

- Real-model runs can be reproduced from config files without editing code.
- Missing API keys or model weights fail with a clear configuration error.
- Deterministic v0 smoke tests still pass without network or API access.

## Stage C: Benchmark Labels and Validation

- [ ] Sample 200-300 examples balanced across drift types and datasets for true human validation.
- [ ] Use two annotators on the overlap subset and adjudicate disagreements before reporting agreement.
- [ ] Keep Mimo-reviewed validation clearly labeled as LLM-reviewed unless replaced by human labels.
- [ ] Freeze final label schema, annotation guidelines, adjudication protocol, and reportability gate before running final tables.

Acceptance criteria:

- Agreement reports distinguish human-human, LLM-human, and answer-key proxy agreement.
- Paper tables never describe LLM-reviewed labels as human-only annotation.
- Final examples used for reporting have complete drift type, severity, expected repair, and task success labels.

## Stage D: Baselines, SAGE-R, and Tables

- [ ] Run the required baseline matrix on each enabled dataset: vanilla RAG, query rewriting RAG, self-reflection, CRAG-style correction, and at least one planner/tool-agent baseline where applicable.
- [ ] Run SAGE-R with the same generator/retriever budget controls used for comparable baselines.
- [ ] Produce main performance, drift-type breakdown, ablation, recovery-vs-cost, over-repair, human agreement, and case-study tables from real runs.
- [ ] Run statistical tests only on real experiment outputs and record the test assumptions.

Acceptance criteria:

- At least two approved datasets and three baselines are complete before any real-result claim is made.
- Reported improvements include cost and over-repair tradeoffs.
- Real-result files are named separately from deterministic v0 scaffold outputs.

## Stage E: Paper and Submission Refresh

- [ ] Replace deterministic scaffold result language with real-result language only after Stages A-D pass.
- [ ] Rebuild the paper PDF and supplementary material from the final real-result tables.
- [ ] Recheck the AAAI-27 official author kit when it is available and migrate away from the AAAI 2026 proxy if required.
- [ ] Rebuild and audit a fresh anonymous release package after all real-experiment artifacts are frozen.

Acceptance criteria:

- The paper, supplement, README, data card, and anonymous release agree on exactly which results are deterministic v0 versus real experiments.
- The final anonymous release has zero configured metadata findings.
- The submission checklist has no remaining external blockers before upload.
