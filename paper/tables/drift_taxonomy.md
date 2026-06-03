# Drift Taxonomy

| Code | Type | Decision rule | Typical failure | Repair |
|---|---|---|---|---|
| G1 | Goal drift | Latest explicit task objective is active unless the user asks to combine goals. | Answers an earlier task after a goal shift. | Rollback and re-plan |
| G2 | Constraint drift | Later same-scope constraints supersede earlier ones; source and policy constraints stay active until lifted. | Violates latest budget, date, source, format, or policy constraint. | Rollback and re-plan |
| E1 | Evidence drift | Verifiable claims must be supported by retrieved evidence or tool observations. | Invents a statistic or states a contradicted fact. | Re-retrieve and verify |
| E2 | Retrieval drift | Retrieved context should match the active goal and constraints. | Retrieves for stale intent after a goal or constraint update. | Rewrite query |
| T1 | Tool-state drift | Tool/database observations override agent assumptions. | Claims success after failed, expired, denied, or not-eligible tool output. | Cross-validate tool and revise action |
| M1 | Memory drift | Explicit memory updates supersede previous same-scope preferences or facts. | Uses an old budget, address, preference, or profile fact. | Update memory priority |
| U1 | Abstention drift | Answer only when required slots and evidence are sufficient under active source constraints. | Fabricates an answer for an unanswerable request or over-refuses. | Calibrate decision |
