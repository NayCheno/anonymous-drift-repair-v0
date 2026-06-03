# Human Annotation Guidelines

## Objective

Annotate whether an agent response/action exhibits state drift and which repair action is appropriate.

## Unit of annotation

One example contains:

- conversation history;
- current user turn;
- retrieved passages;
- tool outputs, if any;
- agent action/response;
- candidate active goals and constraints.

## Labels

### Drift type

Choose all that apply:

- `G1_goal_drift`
- `G2_constraint_drift`
- `E1_evidence_drift`
- `E2_retrieval_drift`
- `T1_tool_state_drift`
- `M1_memory_drift`
- `U1_abstention_drift`
- `NONE`

### Severity

| Label | Meaning |
|---|---|
| 0 | No issue |
| 1 | Minor issue, response mostly usable |
| 2 | Major issue, response/action unreliable |
| 3 | Critical issue, harmful or invalid action |

### Expected repair

Choose one primary action:

- `answer_as_is`
- `revise_response`
- `re_retrieve`
- `call_tool`
- `cross_validate_tool`
- `ask_clarification`
- `abstain`
- `rollback_and_replan`

## Decision rules

1. User's latest explicit instruction overrides older instructions unless the latest instruction is ambiguous.
2. Tool/database outputs override agent assumptions.
3. Retrieved evidence does not automatically override user-provided facts; mark conflict if both cannot be true.
4. If the answer is absent from the evidence and the system is required to be grounded, mark `U1_abstention_drift` if the agent answers confidently.
5. If a response is correct but uses stale or unsupported evidence, mark evidence drift separately from task success.

## Quality control

- Double-annotate at least 20% of cases.
- Compute agreement on drift type and severity.
- Adjudicate disagreements before final test labels.

## Week 2 v0 review workflow

For the toy-equivalent v0 scaffold, generate a 50-case schema and label consistency review file:

```bash
python scripts/validate_driftbench.py --input data/driftbench_v0.jsonl --review-output data/driftbench_v0_manual_check_50.jsonl
```

The generated review file is a scaffold consistency check, not a substitute for the 200-300 human validation cases required for the final paper.

## Week 6 v0 human validation packet

Create the blinded annotation packet and answer key:

```bash
python scripts/make_human_validation_packet.py --input data/driftbench_v0.jsonl --output-dir data/human_validation --target-size 240 --double-annotate-rate 0.2 --seed 42
```

Generated files:

- `human_validation_annotator_a_v0.jsonl`: 240 blinded annotation items.
- `human_validation_annotator_b_v0.jsonl`: 48 blinded annotation items for the double-annotation subset.
- `human_validation_answer_key_v0.jsonl`: held-out scaffold labels for audit and agreement calculation.
- `human_validation_summary_v0.json`: packet size, seed, and label coverage.

These files prepare the 200-300 case validation workflow. They do not claim that human annotation has been completed.

After annotators fill their labels, compute agreement:

```bash
python scripts/make_human_agreement.py --answer-key data/human_validation/human_validation_answer_key_v0.jsonl --annotator-a data/human_validation/human_validation_annotator_a_v0.jsonl --annotator-b data/human_validation/human_validation_annotator_b_v0.jsonl --output results/human_agreement.csv
```

This command fails by default if either annotator file is incomplete. Use `--status-output results/human_agreement_status.json` to write a machine-readable reportability gate. `--allow-incomplete` is only for debugging partially filled files and must not be used for paper reporting.

For scaffold validation only, the answer key can be used as a deterministic proxy:

```bash
python scripts/make_human_agreement.py --answer-key data/human_validation/human_validation_answer_key_v0.jsonl --proxy-from-answer-key --output results/human_agreement_v0.csv --status-output results/human_agreement_status_v0.json
```

The proxy table verifies the workflow and file format only; `results/human_agreement_status_v0.json` marks it as `agreement_reportable: false`. It must be replaced by filled human annotations before reporting judge-human agreement.

Check whether annotation files are complete and generate an adjudication queue:

```bash
python scripts/check_human_annotation_status.py --annotator-a data/human_validation/human_validation_annotator_a_v0.jsonl --annotator-b data/human_validation/human_validation_annotator_b_v0.jsonl --output results/human_annotation_status_v0.json --adjudication-output data/human_validation/human_adjudication_queue_v0.jsonl
```

For the current v0 scaffold this report is expected to show incomplete labels. The adjudication queue becomes meaningful after both annotators fill the double-annotated subset.

## LLM reviewer option

If human review capacity is unavailable, use the local Mimo OpenAI-compatible configuration in `.env` to fill blinded annotation files with an LLM reviewer. The script reads `openai_base_url`, `openai_api_key`, and optionally `openai_model` from `.env`; it never writes the API key to outputs.

Smoke one item:

```bash
python scripts/run_llm_annotation_review.py --model mimo-v2.5 --input data/human_validation/human_validation_annotator_a_v0.jsonl --output data/human_validation/llm_review/human_validation_annotator_a_llm_smoke_v0.jsonl --status-output results/llm_annotation_review_smoke_v0.json --max-items 1
```

Full LLM review:

```bash
python scripts/run_llm_annotation_review.py --model mimo-v2.5 --concurrency 4 --input data/human_validation/human_validation_annotator_a_v0.jsonl --output data/human_validation/llm_review/human_validation_annotator_a_llm_v0.jsonl --status-output results/llm_annotation_review_a_v0.json
python scripts/run_llm_annotation_review.py --model mimo-v2.5 --concurrency 4 --input data/human_validation/human_validation_annotator_b_v0.jsonl --output data/human_validation/llm_review/human_validation_annotator_b_llm_v0.jsonl --status-output results/llm_annotation_review_b_v0.json
```

After the full run, compute agreement against the answer key and the double-annotated subset:

```bash
python scripts/make_human_agreement.py --answer-key data/human_validation/human_validation_answer_key_v0.jsonl --annotator-a data/human_validation/llm_review/human_validation_annotator_a_llm_v0.jsonl --annotator-b data/human_validation/llm_review/human_validation_annotator_b_llm_v0.jsonl --output results/llm_human_agreement_v0.csv --status-output results/llm_human_agreement_status_v0.json
```

Report this as LLM-reviewed validation unless a real human annotation pass is later completed.

Current v0 LLM-reviewed outputs:

- `data/human_validation/llm_review/human_validation_annotator_a_llm_v0.jsonl`: 240 completed Mimo-reviewed labels.
- `data/human_validation/llm_review/human_validation_annotator_b_llm_v0.jsonl`: 48 completed Mimo-reviewed labels for the double-annotation subset.
- `results/llm_annotation_review_a_v0.json` and `results/llm_annotation_review_b_v0.json`: completion status for the two LLM passes.
- `results/llm_human_agreement_v0.csv` and `results/llm_human_agreement_status_v0.json`: answer-key and A/B agreement metrics.
- `data/human_validation/llm_review/llm_adjudication_queue_v0.jsonl`: disagreement queue for the double-annotated subset.

Validate the committed LLM-reviewed outputs without calling the API:

```bash
python scripts/validate_llm_review_outputs.py
```
