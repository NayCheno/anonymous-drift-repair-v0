# Reviewer Response Bank

## Concern: This is just a pipeline

Response outline:

- The contribution is not a new monolithic agent.
- We formalize state drift as a trajectory-level reliability problem.
- We introduce state-level labels and metrics that final-answer benchmarks do not capture.
- Ablations show which state components matter.

## Concern: Benchmark is synthetic

Response outline:

- Controlled perturbations are used to isolate causal failure modes.
- We also include naturally occurring failures from multi-turn RAG/tool datasets.
- Human validation confirms that labels correspond to realistic failure categories.

## Concern: LLM judge bias

Response outline:

- We report human agreement on a balanced subset.
- We test judge sensitivity across models.
- Core metrics such as tool-state conflicts and constraint violations include rule-based checks where possible.

## Concern: Repair costs too much

Response outline:

- We report reliability-cost trade-offs.
- Conservative thresholds avoid unnecessary repair.
- Some high-severity drifts justify additional tool/retrieval cost.

## Concern: Relation to CRAG/REAP

Response outline:

- CRAG focuses on inaccurate retrieval.
- REAP focuses on multi-hop reasoning planning.
- DRIFT-Repair focuses on active-state consistency across goals, constraints, evidence, tools, memory, and abstention.
