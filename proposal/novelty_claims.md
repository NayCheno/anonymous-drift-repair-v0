# Novelty Claims

## Claim 1: State drift is not equivalent to hallucination

Hallucination is often evaluated at the output level. State drift is trajectory-level: the model's active working state becomes stale, contradicted, or superseded across turns.

## Claim 2: Multi-turn reliability needs state-level labels

Final answer correctness cannot distinguish whether failure came from stale goals, violated constraints, unsupported evidence, tool conflict, or obsolete memory.

## Claim 3: Typed repair is more principled than generic self-reflection

Generic self-reflection asks the model to re-check itself without knowing which subsystem failed. Typed repair maps each drift type to a targeted repair action.

## Claim 4: Over-repair is a measurable failure mode

A repair system can harm originally correct outputs. Reporting over-repair rate is essential for reliability claims.

## Claim 5: Reliability should be evaluated with cost

Repair improves consistency but adds retrievals, tokens, and tool calls. The paper should report a reliability-cost frontier rather than accuracy alone.
