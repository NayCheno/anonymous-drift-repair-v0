# Ablation Plan

## Core ablations

| Variant | Removes | Hypothesis |
|---|---|---|
| Full SAGE-R | Nothing | Best consistency/recovery |
| w/o state graph | Explicit graph structure | Worse diagnosis localization |
| w/o active-state resolution | Supersession logic | Worse on constraint and memory updates |
| w/o evidence detector | Evidence consistency | More unsupported claims |
| w/o retrieval detector | Query-goal alignment | More stale retrieval |
| w/o tool detector | Tool-state check | More invalid actions |
| w/o abstention detector | answer/clarify/refuse calibration | More hallucinated answers and over-refusals |
| diagnose-only | Repair actions | Good detection but no recovery |
| repair-only | Typed diagnosis | More over-repair and unstable recovery |

## Sensitivity analysis

- Drift severity threshold.
- Number of retrieved passages.
- Number of repair attempts.
- Model size.
- Judge model.
- Tool-call budget.

## Cost analysis

For each variant report:

```text
extra_tokens
extra_retrievals
extra_tool_calls
extra_latency_proxy
success_gain_per_1k_tokens
```
