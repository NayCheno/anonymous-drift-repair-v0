from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class Evidence:
    id: str
    text: str


@dataclass
class ToolOutput:
    tool: str
    content: str


@dataclass
class Example:
    id: str
    turns: List[Turn]
    retrieved: List[Evidence] = field(default_factory=list)
    tool_outputs: List[ToolOutput] = field(default_factory=list)
    candidate_response: str = ""
    gold: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> "Example":
        return Example(
            id=obj["id"],
            turns=[Turn(**t) for t in obj.get("turns", [])],
            retrieved=[Evidence(**e) for e in obj.get("retrieved", [])],
            tool_outputs=[ToolOutput(**t) for t in obj.get("tool_outputs", [])],
            candidate_response=obj.get("candidate_response", ""),
            gold=obj.get("gold", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "turns": [turn.__dict__ for turn in self.turns],
            "retrieved": [evidence.__dict__ for evidence in self.retrieved],
            "tool_outputs": [tool_output.__dict__ for tool_output in self.tool_outputs],
            "candidate_response": self.candidate_response,
            "gold": self.gold,
        }


@dataclass
class StateNode:
    id: str
    type: str
    text: str
    active: bool = True
    source: str = ""
    turn_index: Optional[int] = None
    status: str = "active"
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0
    active: bool = True
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateGraph:
    nodes: List[StateNode] = field(default_factory=list)
    edges: List[StateEdge] = field(default_factory=list)


@dataclass
class Diagnosis:
    example_id: str
    drift_types: List[str]
    severity: int
    conflicting_nodes: List[str]
    suggested_repair: str
    confidence: float
    primary_type: str = ""
    severity_reason: str = ""
    module_hits: List[str] = field(default_factory=list)
    signals: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""


@dataclass
class RepairResult:
    example_id: str
    original_response: str
    repaired_response: str
    diagnosis: Diagnosis
    repaired: bool
    cost: Dict[str, int] = field(default_factory=dict)
    repair_trace: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "example_id": self.example_id,
            "original_response": self.original_response,
            "repaired_response": self.repaired_response,
            "diagnosis": self.diagnosis.__dict__,
            "repaired": self.repaired,
            "cost": self.cost,
            "repair_trace": self.repair_trace,
        }
