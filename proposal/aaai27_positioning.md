# AAAI-27 Positioning

## Track

建议主投：**Main Technical Track**。

如果 AAAI-27 最终设置 AI Alignment / AI for Trustworthy AI 相关 special track，可视 CFP 再决定是否转投。但当前最稳定位仍是 Main Technical Track，因为本 work 包含问题定义、benchmark、方法和实验评估。

## Why AAAI

AAAI 对以下贡献类型较友好：

- 系统化定义新问题；
- 跨 NLP、IR、agent、tool-use、reliability 的研究；
- 不仅报告 SOTA，还提供 diagnosis、analysis、reproducibility；
- 对更广泛 AI 社区有意义的评测框架和工具。

本题的定位：

> We introduce state drift as a trajectory-level reliability problem in multi-turn RAG agents, provide state-level diagnostic annotations, and show typed repair improves consistency and recovery.

## 不要这样写

- “We propose a new RAG pipeline.”
- “We use prompt engineering to improve accuracy.”
- “We add self-reflection to RAG.”

## 应该这样写

- “Final-answer accuracy is insufficient for multi-turn agents.”
- “Failures often originate in stale or contradicted state.”
- “State-level diagnosis enables targeted repair and avoids blind self-correction.”
- “Typed repair improves recovery while exposing cost and over-repair trade-offs.”

## Reviewer 可能质疑

| 质疑 | 应对 |
|---|---|
| 只是 pipeline | 强调 formalization、taxonomy、state-level labels、typed repair ablation |
| LLM judge 不可靠 | 人工核验 200-300 cases，报告 agreement |
| benchmark 人工构造 | 结合真实 benchmark + controlled perturbation + natural failure subset |
| repair 成本高 | 报告 token/tool overhead 和 reliability-cost curve |
| 与 CRAG/REAP 重叠 | CRAG 修 retrieval，REAP 修 multi-hop planning；本文修 multi-turn active state |
