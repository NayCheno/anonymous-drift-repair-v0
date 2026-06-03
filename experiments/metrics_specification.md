# Metrics Specification

## 1. State Consistency Score

Let `E_conflict` be weighted conflicting state edges and `E_total` be total verifiable state edges.

```text
StateConsistency = 1 - sum(weight(e) for e in E_conflict) / sum(weight(e) for e in E_total)
```

Recommended weights:

| Edge type | Weight |
|---|---:|
| tool contradiction | 1.5 |
| active user constraint violation | 1.5 |
| unsupported factual claim | 1.0 |
| stale retrieval intent | 1.0 |
| obsolete memory use | 1.0 |
| abstention error | 1.2 |

## 2. Goal Consistency

```text
GoalConsistency = number_of_outputs_satisfying_active_goal / total_outputs
```

## 3. Constraint Consistency

```text
ConstraintConsistency = 1 - active_constraint_violations / active_constraints_checked
```

## 4. Evidence Faithfulness

```text
ClaimSupportRate = supported_claims / verifiable_claims
UnsupportedClaimRate = unsupported_claims / verifiable_claims
EvidenceConflictRate = contradicted_claims / verifiable_claims
```

## 5. Retrieval Drift

```text
RetrievalGoalAlignment = judge(query, active_goal)
ContextPrecision = relevant_retrieved_chunks / retrieved_chunks
StaleContextRate = stale_chunks / retrieved_chunks
```

## 6. Tool-State Consistency

```text
ToolStateConsistency = valid_actions_given_tool_state / total_tool_conditioned_actions
```

## 7. Abstention Calibration

Three-class decision:

```text
answer | ask_clarification | abstain
```

Report macro-F1 and confusion matrix.

## 8. Repair metrics

```text
RecoveryRate = cases_failed_before_repair_succeeded_after / cases_failed_before_repair
RepairPrecision = correct_repairs / all_repairs
OverRepairRate = cases_correct_before_repair_failed_after / cases_correct_before_repair
TimeToRecovery = extra_turns_or_calls_needed
RepairCost = extra_tokens + extra_retrievals + extra_tool_calls
```

## 9. Statistical reporting

- 95% bootstrap confidence intervals.
- Paired significance tests for main comparisons.
- At least three runs for stochastic agent settings.
