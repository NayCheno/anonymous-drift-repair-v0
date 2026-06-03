# Baseline Matrix

| Baseline | Required? | Why included | Expected weakness |
|---|---:|---|---|
| Vanilla multi-turn RAG | Yes | Basic reference point | Fails on stale goals and constraints |
| Query rewriting RAG | Yes | Strong retrieval-oriented baseline | May rewrite to wrong active state |
| Self-reflection | Yes | Common repair baseline | Generic, not typed, can over-repair |
| RAGAS-style filtering | Yes | Faithfulness/retrieval quality baseline | Mostly per-turn; weak for tool/memory drift |
| CRAG-style correction | Yes | Corrective retrieval baseline | Focuses retrieval, not goals/tools/memory |
| ReAct agent | Yes for tool setting | Standard tool-agent baseline | Can propagate wrong observations |
| Planner-RAG / REAP-style | Recommended | Strong planning baseline | Good for subgoals, less direct for state drift |
| Oracle drift detector | Analysis only | Upper bound for repair | Not deployable |

## Implementation rule

Keep every baseline under the same generator model and retrieval backend where possible. This reduces confounding.

## Reporting rule

Do not report only task success. Every baseline should be evaluated on:

- state consistency;
- drift-type-specific violations;
- recovery;
- over-repair;
- cost.
