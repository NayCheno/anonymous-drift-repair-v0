# Experimental Plan

## 1. Main question

Does state-graph diagnosis with typed repair improve multi-turn RAG/Agent reliability compared with vanilla RAG, self-reflection, corrective RAG, and planner-style baselines?

## 2. Datasets

### Required

| Dataset | Role | Drift types |
|---|---|---|
| MTRAG / MTRAG-UN | Multi-turn RAG | G1, G2, E1, E2, U1 |
| tau-bench or DialogTool | Tool-use agent | G2, T1, U1 |

### Optional

| Dataset | Role | Drift types |
|---|---|---|
| LongMemEval | Long-term memory | M1, U1, temporal consistency |

## 3. DriftBench construction

Week 1 freezes the deterministic scaffold around seven drift types:
`G1_goal_drift`, `G2_constraint_drift`, `E1_evidence_drift`,
`E2_retrieval_drift`, `T1_tool_state_drift`, `M1_memory_drift`, and
`U1_abstention_drift`. The active-state resolver uses latest-same-scope
rules for goals, constraints, and memory; tool observations override agent
assumptions; and source-restricted evidence gates abstention decisions.

### Inputs

- Original multi-turn conversation.
- Corpus / retrieved passages.
- Tool outputs or database state.
- User goal and final answer labels.

### Transformations

| Perturbation | Operation | Expected behavior |
|---|---|---|
| Goal shift | Insert turn that changes task objective | Re-plan using latest goal |
| Constraint update | Add or supersede constraints | Use active constraint only |
| Evidence conflict | Add contradicted passage | Verify claims, cite supported evidence |
| Stale retrieval | Force old-query retrieval | Rewrite query, re-retrieve |
| Tool conflict | Tool output contradicts action | Stop or revise action |
| Memory update | Replace user preference/fact | Mark old memory inactive |
| Unanswerable/underspecified | Remove evidence or omit key slot | Abstain or ask clarification |

## 4. Systems compared

| ID | System | Description |
|---|---|---|
| B0 | Vanilla RAG | Conversation history + retrieval + generation |
| B1 | Standalone query rewriting RAG | Rewrite current turn before retrieval |
| B2 | Self-reflection RAG | Generate then ask model to check/revise |
| B3 | CRAG-style corrective RAG | Evaluate retrieved context and re-retrieve if weak |
| B4 | ReAct/tool agent | Think-act-observe loop with tools |
| B5 | Planner-RAG / REAP-style | Maintain subgoals/facts for planning |
| Ours | SAGE-R | State graph + active-state resolution + drift detection + typed repair |

## 5. Model matrix

Minimum:

| Role | Models |
|---|---|
| Generator | 1 strong API model + 2 open-source models |
| Verifier/Judge | strong model or NLI/LLM hybrid |
| Retriever | BM25 + dense retrieval |

Recommended open-source candidates:

- Qwen family.
- Llama family.
- Mistral family.

The code scaffold keeps model calls abstract to avoid coupling the project to one provider.

## 6. Main metrics

- Task Success Rate.
- State Consistency Score.
- Goal Consistency.
- Constraint Consistency.
- Evidence Faithfulness.
- Tool-State Consistency.
- Abstention Calibration.
- Recovery Rate.
- Repair Precision.
- Over-Repair Rate.
- Extra token / retrieval / tool-call cost.

## 7. Human validation

Manual annotation target:

```text
200-300 examples
balanced across drift types
2 annotators if possible
adjudication for disagreements
report Cohen's kappa or percent agreement
```

## 8. Tables to produce

1. Main performance table across datasets.
2. Drift-type breakdown.
3. Ablation table.
4. Recovery-vs-cost table.
5. Over-repair analysis.
6. Human agreement table.
7. Case study table.

## 9. Figures to produce

1. State graph architecture.
2. DriftBench construction pipeline.
3. Reliability-cost frontier.
4. Drift distribution by model.
