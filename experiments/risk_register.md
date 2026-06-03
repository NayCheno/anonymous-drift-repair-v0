# Risk Register

| Risk | Severity | Probability | Mitigation |
|---|---:|---:|---|
| Work looks like engineering pipeline | High | Medium | Formalize state drift; include taxonomy, metrics, ablation, analysis |
| LLM judge unreliable | High | High | Human validation; agreement report; sensitivity to judge model |
| Benchmark too synthetic | Medium | Medium | Mix natural failures from existing benchmarks with controlled perturbations |
| Repair increases cost too much | Medium | High | Report reliability-cost frontier; add thresholds |
| Over-repair hurts correct cases | High | Medium | Measure over-repair; introduce conservative repair policy |
| Tool benchmarks hard to integrate | Medium | Medium | Start with one domain; make tool adapter modular |
| Time too short | High | Medium | Focus on MTRAG/MTRAG-UN + one tool dataset; LongMemEval optional |
| Baselines too weak | High | Medium | Include self-reflection, CRAG-style, planner-style baselines |
