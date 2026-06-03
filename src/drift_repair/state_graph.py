from __future__ import annotations

from .schemas import Example, StateGraph, StateNode, StateEdge


GOAL_MARKERS = ("focus", "find", "summarize", "recommend", "refund", "now", "instead")
CONSTRAINT_MARKERS = (
    "only",
    "under",
    "after",
    "before",
    "budget",
    "provided corpus",
    "use only",
    "current budget",
)
MEMORY_MARKERS = ("remember", "update:", "my budget is now", "preference is now")


class StateGraphBuilder:
    """Lightweight state graph builder.

    This is a deterministic scaffold. Replace extraction rules with schema-constrained
    LLM extraction or a hybrid symbolic/LLM extractor in real experiments.
    """

    def build(self, ex: Example) -> StateGraph:
        graph = StateGraph()

        for i, turn in enumerate(ex.turns):
            node_id = f"turn_{i}_{turn.role}"
            graph.nodes.append(
                StateNode(
                    id=node_id,
                    type=f"turn:{turn.role}",
                    text=turn.content,
                    source="conversation",
                    turn_index=i,
                    meta={"role": turn.role},
                )
            )

            if turn.role == "user":
                lowered = turn.content.lower()
                if any(k in lowered for k in GOAL_MARKERS):
                    graph.nodes.append(
                        StateNode(
                            id=f"goal_{i}",
                            type="goal",
                            text=turn.content,
                            source="conversation",
                            turn_index=i,
                            meta={"resolution_scope": "latest_goal"},
                        )
                    )
                    graph.edges.append(StateEdge(source=node_id, target=f"goal_{i}", relation="states"))
                if any(k in lowered for k in CONSTRAINT_MARKERS):
                    graph.nodes.append(
                        StateNode(
                            id=f"constraint_{i}",
                            type="constraint",
                            text=turn.content,
                            source="conversation",
                            turn_index=i,
                            meta={"resolution_scope": _constraint_scope(lowered)},
                        )
                    )
                    graph.edges.append(StateEdge(source=node_id, target=f"constraint_{i}", relation="states"))
                if any(k in lowered for k in MEMORY_MARKERS):
                    graph.nodes.append(
                        StateNode(
                            id=f"memory_{i}",
                            type="memory",
                            text=turn.content,
                            source="conversation",
                            turn_index=i,
                            meta={"resolution_scope": _memory_scope(lowered)},
                        )
                    )
                    graph.edges.append(StateEdge(source=node_id, target=f"memory_{i}", relation="states"))

        for i, ev in enumerate(ex.retrieved):
            graph.nodes.append(
                StateNode(
                    id=f"evidence_{ev.id}",
                    type="evidence",
                    text=ev.text,
                    source="retrieval",
                    meta={"evidence_id": ev.id, "rank": i},
                )
            )

        for i, out in enumerate(ex.tool_outputs):
            graph.nodes.append(
                StateNode(
                    id=f"tool_{i}",
                    type="tool_output",
                    text=f"{out.tool}: {out.content}",
                    source="tool",
                    meta={"tool": out.tool, "rank": i},
                )
            )

        graph.nodes.append(
            StateNode(
                id="candidate_response",
                type="response",
                text=ex.candidate_response,
                source="candidate",
            )
        )
        return graph


class ActiveStateResolver:
    """Marks superseded memory/constraints inactive using simple update rules."""

    def resolve(self, graph: StateGraph) -> StateGraph:
        self._supersede_latest_by_scope(graph, "goal", "latest_goal")
        for scope in {"budget", "date", "source", "general"}:
            self._supersede_latest_by_scope(graph, "constraint", scope)
        for scope in {"budget", "preference", "general"}:
            self._supersede_latest_by_scope(graph, "memory", scope)
        return graph

    def _supersede_latest_by_scope(self, graph: StateGraph, node_type: str, scope: str) -> None:
        nodes = [
            n
            for n in graph.nodes
            if n.type == node_type and n.meta.get("resolution_scope") == scope
        ]
        if len(nodes) < 2:
            return
        nodes.sort(key=lambda n: -1 if n.turn_index is None else n.turn_index)
        for stale in nodes[:-1]:
            stale.active = False
            stale.status = "superseded"
            stale.meta["superseded_by"] = nodes[-1].id
            graph.edges.append(
                StateEdge(
                    source=nodes[-1].id,
                    target=stale.id,
                    relation="supersedes",
                    weight=1.0,
                    meta={"resolution_rule": f"latest_{node_type}_{scope}"},
                )
            )


def _constraint_scope(text: str) -> str:
    if "$" in text or "budget" in text or "under" in text:
        return "budget"
    if "after" in text or "before" in text:
        return "date"
    if "provided corpus" in text or "use only" in text:
        return "source"
    return "general"


def _memory_scope(text: str) -> str:
    if "$" in text or "budget" in text:
        return "budget"
    if "preference" in text:
        return "preference"
    return "general"
