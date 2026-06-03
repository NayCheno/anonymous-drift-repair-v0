from __future__ import annotations

from .schemas import Example, RepairResult
from .state_graph import StateGraphBuilder, ActiveStateResolver
from .detectors import RuleBasedDriftDetector
from .repair import TypedRepairPolicy


class SageRPipeline:
    def __init__(self):
        self.builder = StateGraphBuilder()
        self.resolver = ActiveStateResolver()
        self.detector = RuleBasedDriftDetector()
        self.repair_policy = TypedRepairPolicy()

    def run_one(self, ex: Example) -> RepairResult:
        graph = self.builder.build(ex)
        graph = self.resolver.resolve(graph)
        diagnosis = self.detector.detect(ex, graph)
        return self.repair_policy.repair(ex, diagnosis)
