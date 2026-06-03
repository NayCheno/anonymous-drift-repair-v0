from __future__ import annotations

from typing import Dict, Any


class LLMJudge:
    """Provider-neutral judge interface.

    This class intentionally does not call any external API. Add provider-specific
    clients in a separate non-anonymous configuration file.
    """

    def score(self, prompt: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


JUDGE_PROMPT_TEMPLATE = """
You are evaluating a multi-turn RAG/agent trajectory.
Return JSON with:
- drift_types: list of labels from G1,G2,E1,E2,T1,M1,U1
- severity: integer 0-3
- conflicting_nodes: list of node ids or spans
- suggested_repair: one action
- rationale: brief explanation

Conversation:
{conversation}

Retrieved evidence:
{evidence}

Tool outputs:
{tool_outputs}

Agent response:
{response}
"""
