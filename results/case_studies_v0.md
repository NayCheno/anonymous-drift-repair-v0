# Deterministic v0 Case Studies

These cases are selected from the deterministic DriftBench v0 scaffold to audit diagnosis and repair traces. They are pipeline-validation examples, not final benchmark claims.

Selected cases: 8

## Case 1: driftbench_v0_0001__toy_goal_shift_002

- Predicted drift: `G1_goal_drift, E2_retrieval_drift`
- Gold drift: `G1_goal_drift, E2_retrieval_drift`
- Suggested repair: `rollback_and_replan`
- Trace action: `rollback_and_replan`
- Severity: `2`
- Cost proxy: tokens `58`, retrievals `1`, tools `0`

### Context

- `user`: Summarize the benchmark datasets for multi-turn RAG.
- `assistant`: I will summarize datasets.
- `user`: Switch to implementation details for the repair policy instead.

### Evidence and Tools

- Evidence `g2p1`: Old topic: MTRAG is a multi-turn RAG benchmark.

### Response and Repair

- Candidate: Here is a literature survey of multi-turn RAG datasets.
- Repaired: I should revise the answer using the latest user goal and active constraints, then retrieve evidence aligned with the current repair-focused request before answering.
- Rationale: Goal or constraint drift should be repaired by returning to the latest active state before answering.

## Case 2: driftbench_v0_0013__toy_retrieval_003

- Predicted drift: `G2_constraint_drift, G1_goal_drift, E2_retrieval_drift`
- Gold drift: `G1_goal_drift, G2_constraint_drift, E2_retrieval_drift`
- Suggested repair: `rollback_and_replan`
- Trace action: `rollback_and_replan`
- Severity: `3`
- Cost proxy: tokens `58`, retrievals `1`, tools `0`

### Context

- `user`: Find recent repair methods after 2024.
- `assistant`: I will search repair methods.
- `user`: Now focus specifically on tool-state repair.

### Evidence and Tools

- Evidence `r3p1`: Old topic: a 2023 survey covers general retrieval augmented generation.

### Response and Repair

- Candidate: A 2023 general RAG survey is the main relevant source.
- Repaired: I should revise the answer using the latest user goal and active constraints, then retrieve evidence aligned with the current repair-focused request before answering.
- Rationale: Goal or constraint drift should be repaired by returning to the latest active state before answering.

## Case 3: driftbench_v0_0004__toy_evidence_002

- Predicted drift: `E1_evidence_drift, U1_abstention_drift`
- Gold drift: `E1_evidence_drift, U1_abstention_drift`
- Suggested repair: `re_retrieve_and_verify`
- Trace action: `re_retrieve_and_verify`
- Severity: `2`
- Cost proxy: tokens `50`, retrievals `1`, tools `0`

### Context

- `user`: Use the corpus to report the number of human annotators.

### Evidence and Tools

- Evidence `e2p1`: The corpus does not specify the number of human annotators.

### Response and Repair

- Candidate: The study used exactly 4 human annotators.
- Repaired: I should verify each factual claim against the provided corpus, re-retrieve if needed, and abstain when the evidence is absent.
- Rationale: Evidence drift requires claim-level support checks before the answer can stand.

## Case 4: driftbench_v0_0008__toy_goal_shift_003

- Predicted drift: `G1_goal_drift, E2_retrieval_drift`
- Gold drift: `G1_goal_drift, E2_retrieval_drift`
- Suggested repair: `rollback_and_replan`
- Trace action: `rollback_and_replan`
- Severity: `2`
- Cost proxy: tokens `58`, retrievals `1`, tools `0`

### Context

- `user`: Find examples of retrieval drift.
- `assistant`: I will inspect retrieval cases.
- `user`: Instead compare tool safety failures.

### Evidence and Tools

- Evidence `g3p1`: Old topic: stale retrieval query examples in RAG.

### Response and Repair

- Candidate: The best answer is a retrieval drift dataset example.
- Repaired: I should revise the answer using the latest user goal and active constraints, then retrieve evidence aligned with the current repair-focused request before answering.
- Rationale: Goal or constraint drift should be repaired by returning to the latest active state before answering.

## Case 5: driftbench_v0_0002__toy_tool_state_003

- Predicted drift: `T1_tool_state_drift`
- Gold drift: `T1_tool_state_drift`
- Suggested repair: `cross_validate_tool`
- Trace action: `cross_validate_tool`
- Severity: `1`
- Cost proxy: tokens `42`, retrievals `0`, tools `1`

### Context

- `user`: Close ticket T77 only if the policy check passes.

### Evidence and Tools

- Tool `policy_check`: Policy check denied because required approval is missing.

### Response and Repair

- Candidate: Done, ticket T77 is closed.
- Repaired: I cannot complete that action because the tool output indicates the request is not eligible. I will explain the policy state instead of claiming completion.
- Rationale: Tool-state drift requires checking the observation before claiming completion.

## Case 6: driftbench_v0_0006__toy_memory_002

- Predicted drift: `M1_memory_drift`
- Gold drift: `M1_memory_drift`
- Suggested repair: `update_memory_priority`
- Trace action: `update_memory_priority`
- Severity: `1`
- Cost proxy: tokens `28`, retrievals `0`, tools `0`

### Context

- `assistant`: Saved.
- `user`: Update: my seat preference is now aisle.
- `user`: Recommend a seat using my current preference.

### Evidence and Tools

- No retrieved evidence or tool output.

### Response and Repair

- Candidate: I recommend a window seat.
- Repaired: I will use the updated current budget of $800 and mark the previous $500 budget as superseded.
- Rationale: Memory drift is repaired by giving explicit updates priority over stale remembered facts.

## Case 7: driftbench_v0_0007__toy_abstention_003

- Predicted drift: `E1_evidence_drift, U1_abstention_drift`
- Gold drift: `U1_abstention_drift, E1_evidence_drift`
- Suggested repair: `re_retrieve_and_verify`
- Trace action: `re_retrieve_and_verify`
- Severity: `2`
- Cost proxy: tokens `50`, retrievals `1`, tools `0`

### Context

- `user`: Which dataset license applies to MTRAG-UN? Use only the provided corpus.

### Evidence and Tools

- Evidence `u3p1`: The provided corpus does not include the MTRAG-UN license.

### Response and Repair

- Candidate: MTRAG-UN is released under the MIT license.
- Repaired: I should verify each factual claim against the provided corpus, re-retrieve if needed, and abstain when the evidence is absent.
- Rationale: Evidence drift requires claim-level support checks before the answer can stand.

## Case 8: driftbench_v0_0000__toy_clean_002

- Predicted drift: `NONE`
- Gold drift: `NONE`
- Suggested repair: `answer_as_is`
- Trace action: `answer_as_is`
- Severity: `0`
- Cost proxy: tokens `0`, retrievals `0`, tools `0`

### Context

- `user`: Summarize the active constraint in the provided evidence.

### Evidence and Tools

- Evidence `cl2p1`: The active constraint is to use only evidence published after 2024.

### Response and Repair

- Candidate: The active constraint is to use only evidence published after 2024.
- Repaired: The active constraint is to use only evidence published after 2024.
- Rationale: No diagnosis module emitted a drift signal.
