# Error Analysis

Total examples: 300
Drift-type exact match: 1.0000
Over-repair rate: 0.0000

## Drift counts

- E1_evidence_drift: 85
- E2_retrieval_drift: 71
- G1_goal_drift: 71
- G2_constraint_drift: 70
- T1_tool_state_drift: 58
- U1_abstention_drift: 57
- M1_memory_drift: 42

## Suggested repairs

- rollback_and_replan: 113
- cross_validate_tool: 58
- re_retrieve_and_verify: 57
- answer_as_is: 44
- update_memory_priority: 28

## Repair trace actions

- rollback_and_replan: 113
- cross_validate_tool: 58
- re_retrieve_and_verify: 57
- answer_as_is: 44
- update_memory_priority: 28

## Repair stop conditions

- latest_goal_and_constraints_selected: 113
- tool_observation_overrides_candidate_response: 58
- all_remaining_claims_supported_or_answer_abstains: 57
- no_drift_detected: 44
- latest_memory_value_selected: 28

## Diagnosis modules

- goal_constraint: 99
- evidence_abstention: 71
- retrieval: 71
- tool_state: 58
- memory: 42

## Severity

- 0: 44
- 1: 86
- 2: 142
- 3: 28
