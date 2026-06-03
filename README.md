# DRIFT-Repair AAAI-27 Research Package

**项目主题**：多轮 Retrieval-Augmented LLM Agent 的可靠性诊断与自修复  
**拟投会议**：AAAI-27 Main Technical Track  
**当前英文题目**：*DRIFT-Repair: Diagnosing and Repairing State Drift in Multi-Turn Retrieval-Augmented LLM Agents*

本仓库是一个可直接启动的 research scaffold，包含：

- `paper/`：英文论文草稿、BibTeX、图示、taxonomy 与指标表。
- `proposal/`：中文一页 proposal、AAAI 定位、novelty claims。
- `experiments/`：实验计划、baseline matrix、ablation plan、metrics、人工标注指南、风险表。
- `src/drift_repair/`：可运行的实验框架代码骨架。
- `scripts/`：构造 DriftBench、运行 baseline、评估和 smoke test 的入口脚本。
- `configs/`：数据集、模型、drift 类型和实验配置。
- `roadmap/`：8 周 roadmap、milestone checklist、投稿日历。
- `docs/`：复现清单、匿名发布计划、reviewer response bank。

## 0. 快速开始

```bash
cd DRIFT_Repair
python scripts/smoke_test.py
```

该 smoke test 使用 `data/toy_examples.jsonl` 和纯规则 dummy pipeline，不需要 API key，也不访问网络。

复现当前 deterministic DriftBench v0 scaffold 的全部数据、预测、结果表、人类验证包和论文表格：

```bash
python scripts/reproduce_v0.py
```

该命令不访问网络，不调用真实 LLM API，会重生成 `data/driftbench_v0.jsonl`、`results/*_v0.*`、`paper/tables/generated/*.tex`，并刷新本地匿名 release zip/bundle、bundle 验证、handoff、goal audit 和 handoff consistency validation。

检查 deterministic v0 的数据许可 gate、模型、解码和检索配置：

```bash
python scripts/validate_dataset_licenses.py
python scripts/validate_repro_config.py
python scripts/check_aaai_template_readiness.py
python scripts/make_aaai_source_candidate.py
python scripts/check_aaai_template_readiness.py --input paper/main_aaai2026_candidate.tex --output results/aaai_template_candidate_readiness_v0.json
python scripts/validate_llm_review_outputs.py
python scripts/make_submission_readiness.py
```

使用本地 `.env` 中的 Mimo OpenAI-compatible 配置做 LLM 标注 smoke：

```bash
python scripts/run_llm_annotation_review.py --model mimo-v2.5 --input data/human_validation/human_validation_annotator_a_v0.jsonl --output data/human_validation/llm_review/human_validation_annotator_a_llm_smoke_v0.jsonl --status-output results/llm_annotation_review_smoke_v0.json --max-items 1
```

构建本地匿名发布树并审计：

```bash
python scripts/build_anonymous_release.py --clean
python scripts/audit_anonymous_release.py --root release/anonymous-drift-repair-v0 --output results/anonymous_release_tree_audit_v0.md
python scripts/package_anonymous_release.py
python scripts/validate_anonymous_release_manifest.py
python scripts/package_anonymous_git_bundle.py
python scripts/verify_anonymous_git_bundle.py
python scripts/verify_anonymous_remote_import.py
python scripts/publish_anonymous_remote.py --remote-url ANONYMOUS_REMOTE_URL_REQUIRED
python scripts/check_remote_anonymous_readiness.py
python scripts/make_submission_handoff.py
python scripts/validate_submission_handoff.py
python scripts/make_goal_completion_audit.py
```

生成补充材料 PDF：

```bash
cd paper
pdflatex -interaction=nonstopmode supplement.tex
```

转换本地已下载的外部数据 seed：

```bash
python scripts/convert_external_dataset.py --adapter mtrag --input external/mt-rag-benchmark --output data/external_mtrag_seed.jsonl
python scripts/smoke_dataset_adapters.py
```

外部 adapter 只做本地 JSON/JSONL 规范化，不下载或再分发数据；输出记录仍标记为 `needs_annotation`。

## 1. 项目定位

本文不主张“再提出一个 RAG pipeline”。核心观点是：

> 多轮 RAG/Agent 的失败常常不是孤立 hallucination，而是 **state drift**：agent 的工作状态逐步偏离当前用户目标、活跃约束、检索证据、工具观测和长期记忆更新。

论文目标是形成四个贡献：

1. **Problem**：形式化定义 state drift。
2. **Benchmark**：构造带状态级标注的 DriftBench。
3. **Method**：提出 state graph diagnosis + typed repair。
4. **Evaluation**：跨多轮 RAG、tool-use 和 memory 设置验证 recovery、consistency、cost。

## 2. 推荐最小可发表版本

```text
Datasets: MTRAG / MTRAG-UN + tau-bench or DialogTool
DriftBench: 500-800 conversations, 3,000-6,000 turns, 5 drift types
Models: 2 open-source LLMs + 1 strong API model + 1 verifier/judge
Baselines: vanilla RAG, query rewriting RAG, self-reflection, CRAG-style, planner/RAG baseline
Metrics: task success, state consistency, faithfulness, recovery rate, over-repair rate, cost
```

## 3. 当前目录中的核心文件

| 文件 | 用途 |
|---|---|
| `paper/main.tex` | 英文论文草稿，已迁移到当前公共 AAAI 2026 proxy 单源格式 |
| `paper/refs.bib` | related work BibTeX |
| `paper/main.pdf` | 从当前草稿编译出的预览 PDF |
| `experiments/experimental_plan.md` | 完整实验设计 |
| `experiments/metrics_specification.md` | 指标定义与公式 |
| `experiments/human_annotation_guidelines.md` | 人工标注指南 |
| `roadmap/8_week_roadmap.md` | 从立项到提交的 8 周路线图 |
| `src/drift_repair/` | 框架代码骨架 |
| `scripts/smoke_test.py` | 本地最小运行验证 |

## 4. 当前完成状态与后续真实实验工作

deterministic v0 scaffold 已完成并通过聚合 readiness gate。匿名发布包、git bundle、本地 bare-remote 导入验证和托管匿名 remote 发布均已记录，当前没有 v0 聚合 blocker。

后续真实实验版不属于 deterministic v0 完成标准，需要单独推进：

- 下载/接入真实数据集 loader：MTRAG、MTRAG-UN、tau-bench；DialogTool 只有在 authoritative source 和 license 确认后才能启用。
- 替换 dummy LLM/Judge 为真实模型调用，并记录模型、解码、检索和成本配置。
- 对 DriftBench 至少人工核验 200-300 条，或明确标注非人工替代协议。
- 使用真实运行结果重建 main、ablation、cost、over-repair 和 statistical test tables。
- 在 AAAI-27 官方 author kit 发布后复核并替换当前 AAAI 2026 proxy 模板。

具体后续执行清单见 `roadmap/real_experiment_followup.md`。

## 5. 当前 deterministic v0 scaffold 状态

当前代码是 deterministic v0 scaffold，不包含真实 LLM API、真实检索器或真实 benchmark 结果。已完成的基础版本包括：

- 7 类 state drift taxonomy：`G1/G2/E1/E2/T1/M1/U1`。
- 轻量 state graph schema 和 active-state resolution 规则。
- 21 条 hand-written JSONL smoke examples，每类 drift 至少 3 条。
- 300 条 toy-equivalent DriftBench v0 draft examples。
- 3 个 deterministic baseline proxies、SAGE-R v0 predictions、main table、drift breakdown、cost analysis、ablation table、over-repair analysis、statistical test scaffold。
- 240 条 blinded human-validation packet、answer-key proxy agreement workflow，以及 non-reportable status gate。
- Mimo OpenAI-compatible LLM reviewer workflow 和 1 条 smoke annotation。
- Mimo `mimo-v2.5` LLM-reviewed validation：Annotator A 240 条、Annotator B 48 条、agreement/status/adjudication queue。
- `scripts/validate_llm_review_outputs.py` 可在不调用 API 的情况下校验已提交的 LLM-reviewed validation 产物。
- deterministic v0 case-study trace audit。
- `scripts/smoke_test.py` 和 `scripts/reproduce_v0.py` 作为本地验收入口。
- `scripts/convert_external_dataset.py` 和 `src/drift_repair/dataset_adapters.py` 提供外部数据 seed adapter scaffold。
- `configs/datasets.yaml` 和 `docs/dataset_license_status.md` 记录 deterministic v0 数据许可 gate；可公开核到的外部源已记录 license，DialogTool 仍为 pending，所有外部数据仍 disabled/local-only。
- `configs/models.yaml` 和 `docs/model_retrieval_config_v0.md` 固定 deterministic v0 的本地规则模型和 keyword retriever 配置。
- `paper/supplement.tex` 和 `paper/supplement.pdf` 作为 deterministic v0 scaffold 的补充材料。
- `paper/main.tex` 和 `paper/main_aaai2026_candidate.tex` 当前均满足 AAAI 2026 proxy 单源检查；这不代表最终 AAAI-27 模板已发布或已复核。
- `results/submission_readiness_v0.md` 汇总 deterministic v0 readiness；当前 final submission readiness 为 `true`，failures/blockers 均为 `0`。
- `results/submission_handoff_v0.md` 汇总匿名包 checksum、验证状态和剩余动作；当前 hosted anonymous remote 已发布，剩余动作仅是在投稿系统记录匿名 URL。
- `results/submission_handoff_validation_v0.json` 校验 handoff 与 readiness、zip、bundle 和 goal audit 的一致性。
- `results/goal_completion_audit_v0.md` 汇总当前目标完成证据和剩余外部 blocker。
- `scripts/build_anonymous_release.py`、`scripts/audit_anonymous_release.py`、`scripts/package_anonymous_release.py`、`scripts/validate_anonymous_release_manifest.py`、`scripts/package_anonymous_git_bundle.py`、`scripts/verify_anonymous_git_bundle.py`、`scripts/verify_anonymous_remote_import.py`、`scripts/publish_anonymous_remote.py` 和 `scripts/check_remote_anonymous_readiness.py` 用于本地匿名发布树构建、审计、zip/bundle checksum 打包、release manifest 校验、bundle 克隆验证、本地 bare remote 导入验证、托管 remote 发布和远程发布 readiness 检查。

## 6. 当前版本边界

当前版本只声明 deterministic scaffold 可复现，不声明真实实验结果。外部数据 adapter 已提供本地 seed 转换入口，LLM-reviewed validation 已用 Mimo `mimo-v2.5` 完成；远程匿名仓库已发布并通过 commit match 验证。

后续真实实验版仍需完成：外部数据完整许可核验与导入、正式 DriftBench 人工标注、真实 LLM/Judge 实验调用、真实实验统计显著性检验，以及 AAAI-27 最终模板复核。纯人工标注可在后续替换当前 LLM-reviewed 版本。

## 7. 设计原则

- 不训练大模型，优先做 inference-time diagnosis/repair。
- 不只报告 final accuracy，要报告 drift-level diagnosis 和 repair outcome。
- 不只依赖 LLM judge，要有人类核验子集和 judge-human agreement。
- 必须报告 over-repair rate 和额外 token/tool cost。
