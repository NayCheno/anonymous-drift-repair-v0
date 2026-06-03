# 一页 Proposal：DRIFT-Repair

## 题目

**DRIFT-Repair: Diagnosing and Repairing State Drift in Multi-Turn Retrieval-Augmented LLM Agents**

中文：**多轮检索增强 LLM Agent 的状态漂移诊断与自修复**

## 核心洞察

多轮 RAG/Agent 的失败不是单点 hallucination，而是轨迹级错误：agent 的内部工作状态逐步偏离当前用户目标、活跃约束、检索证据、工具观测和记忆更新。我们称之为 **state drift**。

## 研究问题

1. 如何形式化定义多轮 RAG Agent 的 state drift？
2. 如何构造带状态级标注的诊断 benchmark？
3. 类型化 repair 是否比通用 self-reflection 更可靠？

## 主要贡献

- **Taxonomy**：定义 goal drift、constraint drift、evidence drift、retrieval drift、tool-state drift、memory drift、abstention drift。
- **Benchmark**：构造 DriftBench，加入可控扰动和状态级标签。
- **Method**：提出 SAGE-R：state graph construction、active-state resolution、drift detection、typed repair。
- **Evaluation**：使用 task success、state consistency、faithfulness、recovery rate、over-repair rate、cost 进行综合评估。

## 实验数据

- 主数据：MTRAG / MTRAG-UN。
- 工具数据：tau-bench 或 DialogTool。
- 选做：LongMemEval。

## Baselines

- Vanilla multi-turn RAG。
- Query rewriting RAG。
- Self-reflection。
- CRAG-style corrective RAG。
- ReAct/tool agent。
- Planner-RAG / REAP-style baseline。

## 预期结果

- Drift detection F1：75%-85%。
- Constraint/evidence/tool violations 降低 15%-40%。
- Initially failed cases 的 recovery rate：25%-45%。
- Over-repair rate 控制在 10%-15% 以下。

## AAAI 卖点

该 work 的优势不是追单一 benchmark SOTA，而是提出一个高频、重要、可复现的新问题：**trajectory-level reliability for multi-turn RAG agents**。
