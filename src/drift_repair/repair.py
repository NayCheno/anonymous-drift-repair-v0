from __future__ import annotations

from .schemas import Example, Diagnosis, RepairResult


def _base_trace(ex: Example, diagnosis: Diagnosis, action: str) -> dict:
    return {
        "policy": "typed_rule_scaffold",
        "action": action,
        "diagnosis_types": diagnosis.drift_types,
        "primary_type": diagnosis.primary_type,
        "module_hits": diagnosis.module_hits,
        "checked_state": {
            "n_turns": len(ex.turns),
            "n_retrieved": len(ex.retrieved),
            "n_tool_outputs": len(ex.tool_outputs),
            "conflicting_nodes": diagnosis.conflicting_nodes,
        },
        "steps": [],
        "stop_condition": "",
        "rationale": "",
    }


class TypedRepairPolicy:
    """Typed repair policy.

    This scaffold returns transparent repaired responses. Real experiments should
    call a generator with repair-specific instructions and verified context.
    """

    def repair(self, ex: Example, diagnosis: Diagnosis) -> RepairResult:
        if not diagnosis.drift_types:
            trace = _base_trace(ex, diagnosis, "answer_as_is")
            trace.update(
                {
                    "steps": ["preserve_response"],
                    "stop_condition": "no_drift_detected",
                    "rationale": "No diagnosis module emitted a drift signal.",
                }
            )
            return RepairResult(
                example_id=ex.id,
                original_response=ex.candidate_response,
                repaired_response=ex.candidate_response,
                diagnosis=diagnosis,
                repaired=False,
                cost={"extra_tokens": 0, "extra_retrievals": 0, "extra_tool_calls": 0},
                repair_trace=trace,
            )

        action = diagnosis.suggested_repair
        trace = _base_trace(ex, diagnosis, action)
        if action == "cross_validate_tool":
            repaired = "I cannot complete that action because the tool output indicates the request is not eligible. I will explain the policy state instead of claiming completion."
            cost = {"extra_tokens": 42, "extra_retrievals": 0, "extra_tool_calls": 1}
            trace.update(
                {
                    "steps": ["inspect_tool_observation", "block_success_claim", "revise_action_status"],
                    "stop_condition": "tool_observation_overrides_candidate_response",
                    "rationale": "Tool-state drift requires checking the observation before claiming completion.",
                }
            )
        elif action == "rollback_and_replan":
            repaired = "I should revise the answer using the latest user goal and active constraints, then retrieve evidence aligned with the current repair-focused request before answering."
            cost = {"extra_tokens": 58, "extra_retrievals": 1, "extra_tool_calls": 0}
            trace.update(
                {
                    "steps": ["rollback_to_latest_active_state", "replan_under_active_constraints", "regenerate_answer"],
                    "stop_condition": "latest_goal_and_constraints_selected",
                    "rationale": "Goal or constraint drift should be repaired by returning to the latest active state before answering.",
                }
            )
        elif action == "rewrite_query_and_retrieve":
            repaired = "I should rewrite the retrieval query for the active user goal, retrieve fresh evidence, and answer only from the aligned context."
            cost = {"extra_tokens": 52, "extra_retrievals": 1, "extra_tool_calls": 0}
            trace.update(
                {
                    "steps": ["derive_active_goal", "rewrite_query", "reretrieve_context", "verify_response_claims"],
                    "stop_condition": "retrieval_context_aligned_with_active_goal",
                    "rationale": "Retrieval drift requires replacing stale context before regenerating the answer.",
                }
            )
        elif action == "re_retrieve_and_verify":
            repaired = "I should verify each factual claim against the provided corpus, re-retrieve if needed, and abstain when the evidence is absent."
            cost = {"extra_tokens": 50, "extra_retrievals": 1, "extra_tool_calls": 0}
            trace.update(
                {
                    "steps": ["extract_verifiable_claims", "check_claim_support", "reretrieve_if_missing", "remove_or_abstain_unsupported_claims"],
                    "stop_condition": "all_remaining_claims_supported_or_answer_abstains",
                    "rationale": "Evidence drift requires claim-level support checks before the answer can stand.",
                }
            )
        elif action == "update_memory_priority":
            repaired = "I will use the updated current budget of $800 and mark the previous $500 budget as superseded."
            cost = {"extra_tokens": 28, "extra_retrievals": 0, "extra_tool_calls": 0}
            trace.update(
                {
                    "steps": ["identify_same_scope_memory", "mark_old_memory_superseded", "answer_with_current_memory"],
                    "stop_condition": "latest_memory_value_selected",
                    "rationale": "Memory drift is repaired by giving explicit updates priority over stale remembered facts.",
                }
            )
        elif action == "calibrate_answer_clarify_abstain":
            repaired = "The provided corpus does not contain enough evidence to answer this exactly. I should abstain or ask for additional evidence."
            cost = {"extra_tokens": 34, "extra_retrievals": 0, "extra_tool_calls": 0}
            trace.update(
                {
                    "steps": ["check_required_slots", "check_evidence_availability", "choose_abstain_or_clarify"],
                    "stop_condition": "insufficient_evidence_or_missing_slot_detected",
                    "rationale": "Abstention drift is repaired by avoiding unsupported confident answers.",
                }
            )
        else:
            repaired = "The response should be revised after checking active state, evidence, and tools."
            cost = {"extra_tokens": 24, "extra_retrievals": 0, "extra_tool_calls": 0}
            trace.update(
                {
                    "steps": ["inspect_active_state", "inspect_evidence_and_tools", "revise_response"],
                    "stop_condition": "generic_revision_applied",
                    "rationale": "Fallback repair applies when no specialized action is selected.",
                }
            )

        return RepairResult(
            example_id=ex.id,
            original_response=ex.candidate_response,
            repaired_response=repaired,
            diagnosis=diagnosis,
            repaired=True,
            cost=cost,
            repair_trace=trace,
        )
