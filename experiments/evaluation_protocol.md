# Evaluation Protocol

## Step 1: Build or load DriftBench

```bash
python scripts/make_driftbench.py --input data/toy_examples.jsonl --output data/driftbench_v0.jsonl --target-size 300 --seed 42
python scripts/validate_driftbench.py --input data/driftbench_v0.jsonl --review-output data/driftbench_v0_manual_check_50.jsonl
```

For the real paper, replace toy examples with MTRAG/MTRAG-UN and tau-bench/DialogTool adapters.

## Step 2: Run baselines

```bash
python scripts/run_baselines.py --dataset data/driftbench_v0.jsonl --output results/baselines.jsonl
```

## Step 3: Run SAGE-R

```bash
python scripts/run_agent.py --dataset data/driftbench_v0.jsonl --output results/sage_r.jsonl
```

## Step 4: Evaluate

```bash
python scripts/evaluate.py --predictions results/sage_r.jsonl --output results/metrics.json
python scripts/make_main_table.py --sage-r results/sage_r.jsonl --baselines results/baselines.jsonl --output results/main_table.csv
python scripts/make_drift_type_breakdown.py --sage-r results/sage_r.jsonl --baselines results/baselines.jsonl --output results/drift_type_breakdown.csv
python scripts/make_cost_analysis.py --sage-r results/sage_r.jsonl --baselines results/baselines.jsonl --output results/cost_analysis.csv
python scripts/run_ablations.py --dataset data/driftbench_v0.jsonl --predictions-output results/ablations.jsonl --table-output results/ablation.csv
python scripts/make_human_agreement.py --answer-key data/human_validation/human_validation_answer_key_v0.jsonl --annotator-a data/human_validation/human_validation_annotator_a_v0.jsonl --annotator-b data/human_validation/human_validation_annotator_b_v0.jsonl --output results/human_agreement.csv --status-output results/human_agreement_status.json
python scripts/make_over_repair_analysis.py --sage-r results/sage_r.jsonl --baselines results/baselines.jsonl --output results/over_repair_analysis.csv
python scripts/make_case_studies.py --dataset data/driftbench_v0.jsonl --predictions results/sage_r.jsonl --output results/case_studies.md
```

## Step 5: Analyze failures

```bash
python scripts/analyze_results.py --predictions results/sage_r.jsonl --output results/error_analysis.md
```

## Required result files for paper

```text
results/main_table.csv
results/drift_type_breakdown.csv
results/ablation.csv
results/cost_analysis.csv
results/human_agreement.csv
results/human_agreement_status.json
results/case_studies.md
```

This scaffold does not include real data downloads or model calls. Those must be added once dataset licenses and model providers are selected.
