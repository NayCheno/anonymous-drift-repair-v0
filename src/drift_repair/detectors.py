from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

from .schemas import Diagnosis, Example, StateGraph


class DriftDetector:
    def detect(self, ex: Example, graph: StateGraph) -> Diagnosis:
        raise NotImplementedError


@dataclass
class DetectionContext:
    example: Example
    graph: StateGraph
    response: str
    joined_turns: str
    evidence: str
    tools: str

    @classmethod
    def from_example(cls, ex: Example, graph: StateGraph) -> "DetectionContext":
        return cls(
            example=ex,
            graph=graph,
            response=ex.candidate_response.lower(),
            joined_turns="\n".join(t.content.lower() for t in ex.turns),
            evidence="\n".join(e.text.lower() for e in ex.retrieved),
            tools="\n".join(t.content.lower() for t in ex.tool_outputs),
        )


@dataclass
class DetectionSignal:
    drift_types: List[str]
    note: str
    conflicting_nodes: List[str] = field(default_factory=list)

    def to_dict(self, module: str) -> dict:
        return {
            "module": module,
            "drift_types": self.drift_types,
            "note": self.note,
            "conflicting_nodes": self.conflicting_nodes,
        }


class RuleModule:
    name = "base"

    def detect(self, ctx: DetectionContext) -> List[DetectionSignal]:
        raise NotImplementedError


class GoalConstraintModule(RuleModule):
    name = "goal_constraint"

    def detect(self, ctx: DetectionContext) -> List[DetectionSignal]:
        signals: List[DetectionSignal] = []

        if "after 2024" in ctx.joined_turns and "2023" in ctx.response:
            signals.append(
                DetectionSignal(
                    ["G2_constraint_drift"],
                    "Response cites content before the active date constraint.",
                    ["candidate_response"],
                )
            )
        if "before 2025" in ctx.joined_turns and "2026" in ctx.response:
            signals.append(
                DetectionSignal(
                    ["G2_constraint_drift"],
                    "Response cites content after the active date constraint.",
                    ["candidate_response"],
                )
            )
        if "use only the provided corpus" in ctx.joined_turns and "external blog" in ctx.response:
            signals.append(
                DetectionSignal(
                    ["G2_constraint_drift"],
                    "Response uses an external source despite a corpus-only constraint.",
                    ["candidate_response"],
                )
            )

        goal_mismatch = any(
            condition
            for condition in [
                "focus specifically on repair" in ctx.joined_turns and "general rag" in ctx.response,
                "switch to implementation details" in ctx.joined_turns
                and "literature survey" in ctx.response,
                "instead compare tool safety" in ctx.joined_turns
                and "retrieval drift dataset" in ctx.response,
                "now focus specifically on tool-state repair" in ctx.joined_turns
                and "general rag survey" in ctx.response,
                "switch to evidence faithfulness" in ctx.joined_turns
                and "abstention calibration" in ctx.response,
            ]
        )
        if goal_mismatch:
            signals.append(
                DetectionSignal(
                    ["G1_goal_drift"],
                    "Response follows a stale goal rather than the latest user objective.",
                    ["candidate_response"],
                )
            )
        return signals


class RetrievalDriftModule(RuleModule):
    name = "retrieval"

    def detect(self, ctx: DetectionContext) -> List[DetectionSignal]:
        stale_context = (
            ("focus specifically on repair" in ctx.joined_turns and "2023 survey" in ctx.evidence)
            or ("now focus specifically on tool-state repair" in ctx.joined_turns and "old topic" in ctx.evidence)
            or ("switch to implementation details" in ctx.joined_turns and "old topic" in ctx.evidence)
            or ("instead compare tool safety" in ctx.joined_turns and "old topic" in ctx.evidence)
            or ("switch to evidence faithfulness" in ctx.joined_turns and "old topic" in ctx.evidence)
        )
        if not stale_context:
            return []
        evidence_nodes = [n.id for n in ctx.graph.nodes if n.type == "evidence" and n.active]
        return [
            DetectionSignal(
                ["E2_retrieval_drift"],
                "Retrieved context contains stale evidence for the active turn.",
                evidence_nodes,
            )
        ]


class EvidenceAbstentionModule(RuleModule):
    name = "evidence_abstention"

    def detect(self, ctx: DetectionContext) -> List[DetectionSignal]:
        signals: List[DetectionSignal] = []
        has_number_claim = bool(re.search(r"\b\d+(\.\d+)?%", ctx.response))
        if has_number_claim and "no acceptance statistics" in ctx.evidence:
            signals.append(
                DetectionSignal(
                    ["E1_evidence_drift", "U1_abstention_drift"],
                    "Response provides unsupported exact statistic despite corpus absence.",
                    ["candidate_response"],
                )
            )

        unsupported_patterns: List[Tuple[str, str]] = [
            ("does not mention a driftbench leaderboard", "leaderboard"),
            ("does not specify the number of human annotators", "exactly 4"),
            ("contains no private api key", "redacted_test_key"),
            ("does not include the mtrag-un license", "mit license"),
        ]
        abstention_required = {
            "does not specify the number of human annotators",
            "contains no private api key",
            "does not include the mtrag-un license",
        }
        for missing_marker, asserted_marker in unsupported_patterns:
            if missing_marker in ctx.evidence and asserted_marker in ctx.response:
                drift_types = ["E1_evidence_drift"]
                if missing_marker in abstention_required:
                    drift_types.append("U1_abstention_drift")
                signals.append(
                    DetectionSignal(
                        drift_types,
                        "Response asserts a fact that the provided corpus marks as absent.",
                        ["candidate_response"],
                    )
                )
                break
        return signals


class ToolStateModule(RuleModule):
    name = "tool_state"

    def detect(self, ctx: DetectionContext) -> List[DetectionSignal]:
        negative_tool = any(
            x in ctx.tools
            for x in ["not eligible", "expired", "failed", "denied", "declined", "no seats are available"]
        )
        success_claim = any(
            x in ctx.response
            for x in ["processed", "completed", "done", "succeeded", "confirmed", "closed"]
        )
        if not (negative_tool and success_claim):
            return []
        drift_types = []
        if "state whether the tool succeeded" in ctx.joined_turns:
            drift_types.append("E1_evidence_drift")
        drift_types.append("T1_tool_state_drift")
        return [
            DetectionSignal(
                drift_types,
                "Response claims success despite negative tool observation.",
                ["candidate_response"],
            )
        ]


class MemoryDriftModule(RuleModule):
    name = "memory"

    def detect(self, ctx: DetectionContext) -> List[DetectionSignal]:
        signals: List[DetectionSignal] = []
        if "budget is now $800" in ctx.joined_turns and "under $500" in ctx.response:
            signals.append(
                DetectionSignal(
                    ["M1_memory_drift", "G2_constraint_drift"],
                    "Response uses obsolete budget after explicit update.",
                    ["candidate_response"],
                )
            )
        if "seat preference is now aisle" in ctx.joined_turns and "window seat" in ctx.response:
            signals.append(
                DetectionSignal(
                    ["M1_memory_drift"],
                    "Response uses obsolete seat preference after explicit update.",
                    ["candidate_response"],
                )
            )
        if "delivery address is now new address" in ctx.joined_turns and "old address" in ctx.response:
            signals.append(
                DetectionSignal(
                    ["M1_memory_drift"],
                    "Response uses obsolete delivery address after explicit update.",
                    ["candidate_response"],
                )
            )
        return signals


class RuleBasedDriftDetector(DriftDetector):
    """Deterministic detector for smoke tests and baseline wiring.

    The modules are intentionally simple and transparent. Real experiments should
    replace or augment them with NLI models, schema-constrained LLM judges,
    tool/database validators, and human-calibrated thresholds.
    """

    def __init__(self, modules: List[RuleModule] | None = None):
        self.modules = modules or [
            GoalConstraintModule(),
            RetrievalDriftModule(),
            EvidenceAbstentionModule(),
            ToolStateModule(),
            MemoryDriftModule(),
        ]

    def detect(self, ex: Example, graph: StateGraph) -> Diagnosis:
        ctx = DetectionContext.from_example(ex, graph)
        drift_types: List[str] = []
        notes: List[str] = []
        conflicting_nodes: List[str] = []
        module_hits: List[str] = []
        signal_records: List[dict] = []

        for module in self.modules:
            signals = module.detect(ctx)
            if not signals:
                continue
            module_hits.append(module.name)
            for signal in signals:
                drift_types.extend(signal.drift_types)
                notes.append(signal.note)
                conflicting_nodes.extend(signal.conflicting_nodes)
                signal_records.append(signal.to_dict(module.name))

        drift_types = list(dict.fromkeys(drift_types))
        severity = 0 if not drift_types else max(1, min(3, len(drift_types)))
        suggested = self._suggest_repair(drift_types)
        confidence = 0.95 if drift_types else 0.75
        primary_type = drift_types[0] if drift_types else ""
        return Diagnosis(
            example_id=ex.id,
            drift_types=drift_types,
            severity=severity,
            conflicting_nodes=list(dict.fromkeys(conflicting_nodes)),
            suggested_repair=suggested,
            confidence=confidence,
            primary_type=primary_type,
            severity_reason="count_based_week3_rule" if drift_types else "no_drift_detected",
            module_hits=module_hits,
            signals=signal_records,
            notes="; ".join(notes),
        )

    def _suggest_repair(self, drift_types: List[str]) -> str:
        if not drift_types:
            return "answer_as_is"
        priority = [
            ("T1_tool_state_drift", "cross_validate_tool"),
            ("G2_constraint_drift", "rollback_and_replan"),
            ("G1_goal_drift", "rollback_and_replan"),
            ("E2_retrieval_drift", "rewrite_query_and_retrieve"),
            ("E1_evidence_drift", "re_retrieve_and_verify"),
            ("M1_memory_drift", "update_memory_priority"),
            ("U1_abstention_drift", "calibrate_answer_clarify_abstain"),
        ]
        for drift_type, action in priority:
            if drift_type in drift_types:
                return action
        return "revise_response"
