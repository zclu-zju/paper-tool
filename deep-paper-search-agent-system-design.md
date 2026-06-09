# 深度论文搜索工具多 Agent 系统设计方案

## 1. 目标与核心问题

本系统面向“从不完整研究意图出发，逐步发现领域真实术语、关键论文、引用网络与隐藏相关方向”的深度论文搜索任务。它不是一次性关键词搜索工具，而是一个可循环、自我审查、自我扩展的研究发现系统。

典型问题：

- 用户初始关键词不完整，甚至不符合目标领域真实表达。
- 直接基于关键词搜索会漏掉使用不同术语、不同任务定义、不同实验场景但本质相关的论文。
- 领域常用词往往需要先读一批论文后才能发现。
- 高质量扩展需要同时利用关键词、语义检索、引用链、作者网络、会议期刊场域、代码仓库、数据集、术语共现和反向引用。
- 搜索系统必须能判断“当前覆盖是否足够”，并能被另一个审查 agent 质疑，触发继续搜索。

设计目标：

- 至少 30 个 Agent，可按职责独立调度，也可组成团队。
- 至少 20 个 Stage，支持顺序、并行、循环和质量门。
- 每一轮搜索都沉淀结构化知识：术语、论文、作者、数据集、方法、任务定义、引用边、排除原因、覆盖评分。
- 支持“鞭策式”互审：检查 agent 的检查结果也要被挑战，防止过早收敛。
- 支持可解释终止：不是“搜不到了”才停止，而是达到用户目标、覆盖评分、边际收益和反方审查阈值后停止。

## 2. 总体架构

```text
User Query
   |
   v
Intake & Scope Layer
   |
   v
Query Expansion Loop <--------------------------------------+
   |                                                       |
   v                                                       |
Parallel Discovery Layer                                   |
   |                                                       |
   v                                                       |
Corpus Cleaning & Evidence Graph Layer                     |
   |                                                       |
   v                                                       |
Coverage Audit & Adversarial Review Layer                  |
   |                                                       |
   +-- PASS --> Final Corpus Package / Search Report       |
   |                                                       |
   +-- REVISE --> New Terms / New Seeds / New Constraints -+
```

系统内部维护一个持续更新的 `Research State`：

```yaml
research_state:
  user_goal:
    raw_request: string
    normalized_topic: string
    target_domain: string
    target_task: string
    required_depth: exploratory | survey | systematic | near_exhaustive
    constraints: []
  search_space:
    accepted_terms: []
    candidate_terms: []
    rejected_terms: []
    boolean_queries: []
    semantic_queries: []
    seed_papers: []
    citation_frontier: []
    venue_frontier: []
    author_frontier: []
    dataset_frontier: []
  corpus:
    raw_records: []
    canonical_papers: []
    excluded_records: []
    clusters: []
  evidence_graph:
    paper_nodes: []
    term_nodes: []
    author_nodes: []
    venue_nodes: []
    dataset_nodes: []
    method_nodes: []
    edges: []
  quality:
    coverage_scores: {}
    bias_flags: []
    contradiction_flags: []
    iteration_history: []
    stop_decision: null
```

## 3. Agent 清单

### 3.1 编排与状态管理 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 1 | `orchestrator_agent` | 全局调度 stage、分配预算、处理循环与终止 | 执行计划、stage 状态 |
| 2 | `state_manager_agent` | 维护 `Research State`，合并各 agent 输出，记录版本 | 状态快照、diff |
| 3 | `budget_controller_agent` | 控制 API、数据库、时间、下载和 token 预算 | 预算分配、截断策略 |
| 4 | `provenance_logger_agent` | 记录每条论文、术语、评分的来源与推理链 | provenance log |
| 5 | `failure_recovery_agent` | 处理搜索失败、接口错误、空结果、格式异常 | 重试计划、降级路径 |

### 3.2 用户意图与参数定义 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 6 | `intent_parser_agent` | 解析用户自然语言需求，抽取领域、任务、对象、限制 | 规范化研究意图 |
| 7 | `parameter_definition_agent` | 检查关键概念定义是否清晰，如“频域补全”“CSI 反馈” | 参数定义表 |
| 8 | `ambiguity_detector_agent` | 找出歧义词、跨领域同名术语、潜在错误翻译 | 歧义清单 |
| 9 | `scope_boundary_agent` | 定义 in-scope、out-of-scope、near-scope | 范围边界 |
| 10 | `user_need_classifier_agent` | 判断用户需要探索型、综述型、系统型还是接近穷尽型搜索 | 深度等级 |

### 3.3 关键词与术语扩展 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 11 | `initial_keyword_agent` | 根据初始需求生成第一批关键词、同义词、缩写 | 初始关键词集 |
| 12 | `domain_vocabulary_agent` | 从种子论文摘要、标题、引言中抽取领域真实术语 | 领域词汇表 |
| 13 | `term_normalization_agent` | 统一同义词、缩写、大小写、英美拼写、中文翻译 | 术语规范表 |
| 14 | `boolean_query_builder_agent` | 生成数据库可执行的 Boolean 查询式 | 查询式集合 |
| 15 | `semantic_query_builder_agent` | 生成面向 embedding / 语义检索的自然语言查询 | 语义查询集合 |
| 16 | `negative_keyword_agent` | 发现容易带来噪声的排除词 | 排除词与规则 |
| 17 | `keyword_gap_agent` | 检查当前关键词是否覆盖任务、方法、数据集、场景、评价指标 | 关键词缺口报告 |
| 18 | `keyword_adversary_agent` | 专门质疑关键词覆盖，寻找漏词、错词、伪相关词 | 关键词反方意见 |

### 3.4 并行论文发现 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 19 | `scholar_search_agent` | 搜索 Google Scholar 或等价学术索引 | 候选论文 |
| 20 | `semantic_scholar_agent` | 使用 Semantic Scholar 检索、引用和相似论文 | 候选论文、引用边 |
| 21 | `crossref_agent` | 使用 Crossref 查 DOI、期刊、元数据 | DOI 元数据 |
| 22 | `openalex_agent` | 使用 OpenAlex 查 works、concepts、引用网络 | 候选论文、concepts |
| 23 | `arxiv_agent` | 搜索 arXiv 预印本 | 候选预印本 |
| 24 | `ieee_acm_agent` | 搜索 IEEE、ACM、通信与计算机相关库 | 候选论文 |
| 25 | `venue_scout_agent` | 从顶会顶刊和领域会议目录扩展论文 | venue frontier |
| 26 | `author_network_agent` | 根据核心作者扩展其相关论文 | 作者扩展结果 |
| 27 | `citation_snowball_agent` | 正向引用、反向引用、共同引用扩展 | 引用扩展结果 |
| 28 | `dataset_benchmark_agent` | 根据常见数据集、benchmark、仿真平台扩展论文 | 数据集相关论文 |
| 29 | `code_repository_agent` | 从 GitHub、Papers with Code 等代码线索发现论文 | 代码关联论文 |
| 30 | `patent_industry_agent` | 可选：查产业白皮书、专利、标准文档辅助发现术语 | 辅助线索 |

### 3.5 过滤、去重与质量 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 31 | `metadata_canonicalizer_agent` | 标准化标题、作者、年份、venue、DOI、arXiv ID | canonical record |
| 32 | `deduplication_agent` | 合并 arXiv/会议/期刊扩展版、重复索引结果 | 去重 corpus |
| 33 | `relevance_classifier_agent` | 判断论文是否真正符合用户主题 | relevance score |
| 34 | `near_miss_classifier_agent` | 识别“接近但不纳入”的论文，保留扩展价值 | near-miss pool |
| 35 | `quality_assessor_agent` | 评估论文质量、引用、venue、实验完整性 | quality score |
| 36 | `method_taxonomy_agent` | 将论文按方法族、任务定义、技术路线聚类 | 方法 taxonomy |
| 37 | `evidence_graph_agent` | 构建论文、术语、作者、引用、数据集之间的图 | evidence graph |

### 3.6 覆盖审查与反方鞭策 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 38 | `coverage_scoring_agent` | 对当前搜索覆盖度打分 | 覆盖评分 |
| 39 | `coverage_auditor_agent` | 审查覆盖评分是否可信，要求证据 | 审查意见 |
| 40 | `devils_advocate_agent` | 从反方角度质疑“已经足够全面”的结论 | 反方挑战 |
| 41 | `missing_cluster_agent` | 检查是否存在未探索的论文聚类或方法族 | 缺失聚类 |
| 42 | `citation_closure_agent` | 判断引用网络是否接近闭合，核心节点是否已覆盖 | 引用闭合报告 |
| 43 | `terminology_drift_agent` | 检查不同年份、不同社区术语是否发生迁移 | 术语漂移报告 |
| 44 | `iteration_decision_agent` | 根据评分、边际收益、反方意见决定是否继续循环 | PASS / REVISE |

### 3.7 输出与后处理 Agent

| # | Agent | 职责 | 主要输出 |
|---|---|---|---|
| 45 | `corpus_packager_agent` | 输出最终论文库、BibTeX、CSV、JSON | corpus package |
| 46 | `search_report_agent` | 输出搜索过程、查询式、纳入排除标准、覆盖证据 | search report |
| 47 | `gap_summary_agent` | 总结已发现的研究空白和未覆盖风险 | gap summary |
| 48 | `monitoring_agent` | 后续持续监控新论文、引用变化、撤稿 | monitoring plan |

本设计包含 48 个 Agent，其中 30 个以上为核心可执行 Agent。实际部署时可按预算裁剪，但不建议删除 `keyword_adversary_agent`、`coverage_auditor_agent`、`devils_advocate_agent` 和 `iteration_decision_agent`，它们是系统避免早停和漏检的关键。

## 4. Stage 设计

### Stage 1: Intake 初始化

- 输入：用户原始需求。
- Agent：`intent_parser_agent`、`state_manager_agent`。
- 输出：`raw_request`、初始 `research_state`。
- 并行：否。
- 失败处理：若无法识别研究对象，进入 Stage 2 的歧义澄清。

### Stage 2: 参数定义检查

- 输入：用户需求和初始状态。
- Agent：`parameter_definition_agent`、`ambiguity_detector_agent`。
- 输出：参数定义表、歧义清单。
- 并行：可并行。
- 质量门：核心概念必须至少包含“对象、方法、场景、评价目标”四类定义。

### Stage 3: 范围边界设定

- 输入：参数定义表。
- Agent：`scope_boundary_agent`、`user_need_classifier_agent`。
- 输出：in-scope、out-of-scope、near-scope、深度等级。
- 并行：可并行。
- 质量门：必须明确哪些相邻领域只作为扩展线索，不纳入最终 corpus。

### Stage 4: 初始关键词生成

- 输入：规范化研究意图、范围边界。
- Agent：`initial_keyword_agent`。
- 输出：初始关键词、缩写、同义词、Boolean 草案。
- 并行：否。

### Stage 5: 初始关键词反方审查

- 输入：初始关键词。
- Agent：`keyword_adversary_agent`、`negative_keyword_agent`。
- 输出：漏词风险、噪声词、排除词。
- 并行：可并行。
- 循环：若关键词明显偏离领域，返回 Stage 4。

### Stage 6: 查询式构建

- 输入：关键词、排除词、范围边界。
- Agent：`boolean_query_builder_agent`、`semantic_query_builder_agent`。
- 输出：Boolean 查询式、语义查询式、数据库适配版本。
- 并行：可并行。

### Stage 7: 第一轮并行数据库检索

- 输入：查询式。
- Agent：`scholar_search_agent`、`semantic_scholar_agent`、`crossref_agent`、`openalex_agent`、`arxiv_agent`、`ieee_acm_agent`。
- 输出：raw records。
- 并行：强制并行。
- 失败处理：单个数据源失败不阻断整体，但由 `failure_recovery_agent` 记录并重试。

### Stage 8: 元数据规范化

- 输入：raw records。
- Agent：`metadata_canonicalizer_agent`。
- 输出：canonical records。
- 并行：可按批次并行。

### Stage 9: 去重与版本合并

- 输入：canonical records。
- Agent：`deduplication_agent`。
- 输出：唯一论文记录、重复映射、版本关系。
- 并行：可按标题哈希和 DOI 分片并行。
- 质量门：arXiv、会议版、期刊扩展版不能被简单丢弃，必须保留关系。

### Stage 10: 初步相关性分类

- 输入：去重论文。
- Agent：`relevance_classifier_agent`、`near_miss_classifier_agent`。
- 输出：in-scope、near-scope、out-of-scope。
- 并行：强制批量并行。

### Stage 11: 种子论文选择

- 输入：相关论文、near-miss 论文。
- Agent：`quality_assessor_agent`、`method_taxonomy_agent`。
- 输出：高置信种子论文、方法族初稿。
- 并行：可并行。
- 质量门：种子论文不能只按引用数选择，必须覆盖不同方法族和年份。

### Stage 12: 领域术语抽取

- 输入：种子论文标题、摘要、关键词、引言片段。
- Agent：`domain_vocabulary_agent`、`term_normalization_agent`。
- 输出：真实领域术语表、术语别名、术语来源论文。
- 并行：按论文批次并行。

### Stage 13: 关键词缺口评分

- 输入：当前关键词、领域术语表、方法 taxonomy。
- Agent：`keyword_gap_agent`。
- 输出：关键词覆盖评分、缺口项。
- 并行：否。
- 评分维度：任务术语、方法术语、数据集术语、应用场景、评价指标、年代术语、社区术语。

### Stage 14: 关键词缺口反方鞭策

- 输入：关键词覆盖评分和证据。
- Agent：`keyword_adversary_agent`、`coverage_auditor_agent`。
- 输出：评分质疑、补充搜索建议。
- 并行：可并行。
- 循环：若反方指出高风险缺口，返回 Stage 6 生成新查询。

### Stage 15: 引用雪球扩展

- 输入：种子论文。
- Agent：`citation_snowball_agent`、`semantic_scholar_agent`、`openalex_agent`。
- 输出：正向引用、反向引用、共同引用、bibliographic coupling。
- 并行：强制并行。

### Stage 16: 作者网络扩展

- 输入：核心作者、实验室、机构。
- Agent：`author_network_agent`。
- 输出：作者相关论文、作者聚类。
- 并行：按作者并行。
- 限制：作者扩展必须由相关性分类器过滤，避免泛化到作者无关研究。

### Stage 17: Venue 与社区扩展

- 输入：核心论文 venue、领域会议期刊。
- Agent：`venue_scout_agent`。
- 输出：同 venue 同 track 论文、专题论文集。
- 并行：按 venue 并行。

### Stage 18: 数据集与 Benchmark 扩展

- 输入：种子论文中出现的数据集、仿真平台、实验设置。
- Agent：`dataset_benchmark_agent`。
- 输出：使用相同数据集或 benchmark 的论文。
- 并行：按数据集并行。

### Stage 19: 代码与实现线索扩展

- 输入：论文标题、方法名、作者、数据集。
- Agent：`code_repository_agent`。
- 输出：代码仓库关联论文、README 中提及论文、Papers with Code 条目。
- 并行：按方法名和论文标题并行。

### Stage 20: 辅助资料扩展

- 输入：核心术语和方法。
- Agent：`patent_industry_agent`。
- 输出：标准、白皮书、专利、产业术语。
- 并行：可并行。
- 说明：默认不纳入论文 corpus，只用于发现术语和应用场景。

### Stage 21: 第二轮候选合并

- 输入：引用、作者、venue、dataset、code、辅助资料扩展结果。
- Agent：`state_manager_agent`、`metadata_canonicalizer_agent`、`deduplication_agent`。
- 输出：更新后的 canonical corpus。
- 并行：规范化可并行，最终状态合并串行。

### Stage 22: 深度相关性与质量评估

- 输入：更新后的 corpus。
- Agent：`relevance_classifier_agent`、`quality_assessor_agent`、`method_taxonomy_agent`。
- 输出：相关性分数、质量分数、方法聚类。
- 并行：强制批量并行。

### Stage 23: Evidence Graph 构建

- 输入：论文、术语、作者、引用、venue、数据集、方法。
- Agent：`evidence_graph_agent`。
- 输出：异构证据图。
- 并行：节点抽取可并行，图合并串行。

### Stage 24: 缺失聚类检测

- 输入：evidence graph、方法 taxonomy、near-miss pool。
- Agent：`missing_cluster_agent`、`terminology_drift_agent`。
- 输出：未覆盖聚类、术语漂移风险。
- 并行：可并行。

### Stage 25: 引用闭合检查

- 输入：核心论文子图、引用边。
- Agent：`citation_closure_agent`。
- 输出：引用闭合度、未访问高权重节点。
- 并行：按 cluster 并行。
- 质量门：核心 cluster 的高频引用节点必须被访问或明确排除。

### Stage 26: 覆盖度综合评分

- 输入：关键词评分、聚类覆盖、引用闭合、数据源覆盖、时间覆盖。
- Agent：`coverage_scoring_agent`。
- 输出：综合覆盖评分。
- 并行：否。

### Stage 27: 覆盖评分审查

- 输入：综合覆盖评分和证据。
- Agent：`coverage_auditor_agent`。
- 输出：评分可信度、证据不足项。
- 并行：否。
- 质量门：评分必须引用具体证据，不允许只给主观判断。

### Stage 28: 反方总审

- 输入：当前 corpus、所有评分、排除记录、搜索历史。
- Agent：`devils_advocate_agent`。
- 输出：最强反方意见、可能漏掉的重要方向、是否建议继续搜索。
- 并行：可与 Stage 27 并行。

### Stage 29: 迭代决策

- 输入：覆盖评分、审查意见、反方意见、预算状态、边际收益。
- Agent：`iteration_decision_agent`、`budget_controller_agent`。
- 输出：`PASS`、`REVISE_QUERY`、`EXPAND_CITATION`、`EXPAND_VENUE`、`ASK_USER`、`STOP_WITH_RISK`。
- 并行：否。
- 循环：
  - `REVISE_QUERY` 回到 Stage 6。
  - `EXPAND_CITATION` 回到 Stage 15。
  - `EXPAND_VENUE` 回到 Stage 17。
  - `ASK_USER` 只在范围冲突或预算不足时触发。

### Stage 30: 最终论文包生成

- 输入：通过审查的 corpus。
- Agent：`corpus_packager_agent`。
- 输出：CSV、BibTeX、JSON、去重映射、排除清单。
- 并行：可并行输出多格式。

### Stage 31: 搜索过程报告

- 输入：完整 provenance、查询式、stage history、评分。
- Agent：`search_report_agent`。
- 输出：可复现搜索报告。
- 并行：可与 Stage 30 并行。

### Stage 32: 研究空白与风险总结

- 输入：evidence graph、缺失聚类、反方意见。
- Agent：`gap_summary_agent`。
- 输出：研究空白、残余漏检风险、后续建议。
- 并行：可与 Stage 30、31 并行。

### Stage 33: 后续监控配置

- 输入：最终关键词、核心作者、venue、数据集、引用前沿。
- Agent：`monitoring_agent`。
- 输出：监控查询、提醒策略、更新周期。
- 并行：可选。

## 5. 并行执行策略

### 5.1 数据源并行

Stage 7 中多个搜索 Agent 必须并行执行。每个 Agent 独立返回：

```yaml
search_result_batch:
  source: semantic_scholar | openalex | arxiv | crossref | ieee | acm | scholar
  query_id: string
  query_text: string
  records: []
  failures: []
  timestamp: string
```

这样可以避免单一数据源偏差，也能在某个 API 失败时保留其他结果。

### 5.2 扩展路径并行

Stage 15-20 可以并行运行：

- 引用扩展发现“学术传承链”。
- 作者扩展发现“同团队未被关键词命中的论文”。
- Venue 扩展发现“同社区使用不同术语的论文”。
- 数据集扩展发现“任务相同但方法名不同的论文”。
- 代码扩展发现“论文标题和正式索引缺失但代码生态中常见的工作”。
- 辅助资料扩展发现“产业或标准中的别名”。

### 5.3 批量分类并行

相关性、质量、方法聚类可以按论文分片并行。最终由 `state_manager_agent` 汇总，避免多个 agent 直接写全局状态导致冲突。

## 6. 循环与鞭策机制

### 6.1 主循环

```text
Stage 4-14: 关键词发现循环
Stage 15-25: 论文扩展循环
Stage 26-29: 覆盖审查循环
```

主循环伪代码：

```python
while budget.remaining() and iteration < max_iterations:
    build_or_update_queries()
    run_parallel_discovery()
    normalize_deduplicate_filter()
    extract_terms_and_expand_graph()
    score = coverage_scoring_agent.evaluate(state)
    audit = coverage_auditor_agent.audit(score, state)
    challenge = devils_advocate_agent.challenge(state, score, audit)
    decision = iteration_decision_agent.decide(score, audit, challenge, budget)

    if decision == "PASS":
        break
    if decision == "REVISE_QUERY":
        continue_from_stage(6)
    if decision == "EXPAND_CITATION":
        continue_from_stage(15)
    if decision == "EXPAND_VENUE":
        continue_from_stage(17)
    if decision == "STOP_WITH_RISK":
        record_residual_risk()
        break
```

### 6.2 Agent 互相鞭策关系

| 被检查 Agent | 鞭策 Agent | 检查重点 |
|---|---|---|
| `initial_keyword_agent` | `keyword_adversary_agent` | 是否漏掉领域真实术语 |
| `keyword_gap_agent` | `coverage_auditor_agent` | 覆盖评分是否有证据 |
| `coverage_scoring_agent` | `coverage_auditor_agent` | 分数是否虚高 |
| `coverage_auditor_agent` | `devils_advocate_agent` | 审查是否太宽松 |
| `relevance_classifier_agent` | `near_miss_classifier_agent` | 是否错排边界论文 |
| `deduplication_agent` | `metadata_canonicalizer_agent` | 是否错误合并不同论文 |
| `method_taxonomy_agent` | `missing_cluster_agent` | 是否漏掉方法族 |
| `citation_snowball_agent` | `citation_closure_agent` | 引用网络是否过早截断 |
| `iteration_decision_agent` | `devils_advocate_agent` | 是否过早停止 |

### 6.3 鞭策输出格式

```yaml
challenge_report:
  target_agent: string
  challenged_claim: string
  challenge_type:
    - missing_evidence
    - over_generalization
    - source_bias
    - terminology_gap
    - citation_gap
    - venue_gap
    - premature_stop
  severity: low | medium | high | critical
  required_action: revise | expand | justify | reject_claim
  evidence_needed: []
  suggested_next_stage: int
```

## 7. 覆盖评分体系

综合覆盖评分不应只看论文数量。建议使用 100 分制：

| 维度 | 权重 | 说明 |
|---|---:|---|
| 任务定义覆盖 | 15 | 是否覆盖用户目标任务的主要叫法和变体 |
| 方法族覆盖 | 15 | 是否覆盖主流、早期、最新、替代技术路线 |
| 术语覆盖 | 10 | 是否覆盖不同社区、不同年份的术语 |
| 引用闭合 | 15 | 核心论文引用网络是否接近闭合 |
| 数据源覆盖 | 10 | 是否跨多个索引和数据库 |
| Venue 覆盖 | 10 | 是否覆盖领域核心会议期刊 |
| 时间覆盖 | 8 | 是否覆盖早期奠基、发展期、最新工作 |
| 数据集与 benchmark 覆盖 | 7 | 是否覆盖常见实验环境 |
| 近邻论文解释 | 5 | 是否解释 near-miss 为什么排除或保留 |
| 反方审查通过度 | 5 | 反方意见是否已解决 |

建议阈值：

- `>= 90`: 接近系统性综述级别，可以停止。
- `80-89`: 适合深度调研，多数场景可以停止，但保留残余风险。
- `70-79`: 可用于初步调研，不建议声称全面。
- `< 70`: 必须继续迭代，除非预算耗尽。

## 8. 终止条件

系统只有在满足以下任一条件时终止：

1. 覆盖评分达到用户设定阈值，且 `coverage_auditor_agent` 和 `devils_advocate_agent` 都未提出 high 或 critical 问题。
2. 连续两轮新增高相关论文低于边际收益阈值，例如新增核心论文少于 3 篇，且引用闭合度稳定。
3. 用户预算耗尽，但必须输出 `STOP_WITH_RISK`，并明确残余风险。
4. 用户明确停止。

禁止以下终止理由：

- “关键词已经很多了”。
- “搜索结果数量已经很多了”。
- “没有新的想法了”。
- 单个 Agent 自称覆盖足够但没有反方审查。

## 9. 数据模型建议

### 9.1 Paper Record

```yaml
paper:
  canonical_id: string
  title: string
  authors: []
  year: int
  venue: string
  doi: string | null
  arxiv_id: string | null
  url: string
  abstract: string
  source_records: []
  relevance:
    score: float
    label: in_scope | near_scope | out_of_scope
    rationale: string
  quality:
    score: float
    venue_rank: string | null
    citation_count: int | null
    evidence_level: string
  taxonomy:
    task: []
    method_family: []
    dataset: []
    metrics: []
  graph:
    references: []
    cited_by: []
    related_terms: []
```

### 9.2 Term Record

```yaml
term:
  canonical_term: string
  aliases: []
  source_papers: []
  first_seen_iteration: int
  term_type: task | method | dataset | metric | domain | application | exclusion
  confidence: float
  status: accepted | candidate | rejected
```

### 9.3 Iteration Record

```yaml
iteration:
  id: int
  triggered_by: initial | keyword_gap | citation_gap | venue_gap | adversarial_challenge
  queries_run: []
  new_raw_records: int
  new_canonical_papers: int
  new_in_scope_papers: int
  new_terms: []
  coverage_score_before: float
  coverage_score_after: float
  challenges: []
  decision: PASS | REVISE_QUERY | EXPAND_CITATION | EXPAND_VENUE | STOP_WITH_RISK
```

## 10. 以“频域补全在 CSI 反馈中如何工作”为例的运行路径

用户输入可能只有：

```text
调研频域补全在 CSI 反馈是如何工作的
```

系统不会只生成 `frequency-domain completion`、`CSI feedback` 这些直译词，而会经历以下发现过程：

1. Stage 2 判断核心对象是无线通信中的 Channel State Information feedback，不是一般 computer vision completion。
2. Stage 4 生成初始关键词：`CSI feedback`、`channel state information feedback`、`frequency domain`、`completion`、`reconstruction`。
3. Stage 7 第一轮搜索得到部分相关论文。
4. Stage 12 从论文中抽取真实术语，可能发现 `CSI compression`、`CSI reconstruction`、`CsiNet`、`channel extrapolation`、`angular-delay domain`、`OFDM subcarriers`、`frequency extrapolation`、`partial CSI` 等。
5. Stage 14 反方指出：只搜 `completion` 可能漏掉叫 `extrapolation`、`reconstruction`、`prediction`、`compression feedback` 的论文。
6. Stage 15 引用扩展发现早期深度学习 CSI feedback 和传统压缩感知路线。
7. Stage 18 根据数据集或仿真设置扩展到 COST 2100、QuaDRiGa、3GPP channel model 等相关论文。
8. Stage 24 检查是否漏掉角度域、延迟域、时频联合、多天线、多子载波反馈等 cluster。
9. Stage 28 反方质疑：如果只覆盖深度学习路线，是否漏掉压缩感知、码本反馈、transform-domain sparse recovery。
10. Stage 29 决定继续扩展或停止。

这个例子体现系统关键能力：初始关键词只是起点，真正的搜索空间由论文自身反向塑造。

## 11. 技术实现建议

### 11.1 Orchestration

推荐使用 DAG + 状态机混合编排：

- DAG 负责明确可并行 stage。
- 状态机负责循环、质量门和终止。
- 每个 Agent 是可重试的任务单元。
- 所有 Agent 输出必须写入 append-only event log，再由 `state_manager_agent` 生成当前状态。

可选框架：

- LangGraph：适合循环式 agent graph。
- Temporal：适合强可靠后台任务。
- Prefect / Dagster：适合数据管线和可视化。
- 自研轻量 orchestrator：适合原型，但必须保留状态快照和重试。

### 11.2 检索后端

建议组合：

- Semantic Scholar API：引用、相似论文、元数据。
- OpenAlex：开放元数据、concept、引用网络。
- Crossref：DOI 和出版元数据。
- arXiv：预印本。
- DBLP：计算机领域会议论文。
- IEEE / ACM：如果有机构权限，用于通信、网络和计算机方向。
- 本地向量库：存储标题、摘要、引言、相关片段。

### 11.3 去重策略

去重不能只靠标题完全匹配。建议分层：

1. DOI / arXiv ID 精确匹配。
2. 规范化标题哈希。
3. 标题 embedding 相似度 + 作者重叠 + 年份接近。
4. 会议版和期刊扩展版保留 parent-child 关系。
5. 不确定合并进入人工或高阶 agent 审查队列。

### 11.4 相关性判断策略

相关性分类应输出理由，而不是只输出标签：

```yaml
relevance_decision:
  label: in_scope
  score: 0.87
  matched_scope:
    - CSI feedback
    - frequency-domain reconstruction
  excluded_risks:
    - not generic image completion
  rationale: "The paper studies feedback and reconstruction of downlink CSI over OFDM subcarriers."
```

### 11.5 质量与覆盖可解释性

每一个覆盖分数都必须能追溯到：

- 哪些论文支持。
- 哪些查询发现。
- 哪些引用路径发现。
- 哪些候选被排除。
- 哪些缺口仍未解决。

## 12. MVP 到完整系统的分阶段落地

### MVP 版本

必须包含：

- `intent_parser_agent`
- `parameter_definition_agent`
- `initial_keyword_agent`
- `semantic_scholar_agent`
- `openalex_agent`
- `metadata_canonicalizer_agent`
- `deduplication_agent`
- `relevance_classifier_agent`
- `domain_vocabulary_agent`
- `keyword_gap_agent`
- `coverage_scoring_agent`
- `coverage_auditor_agent`
- `devils_advocate_agent`
- `iteration_decision_agent`
- `search_report_agent`

MVP Stage 可压缩为：

1. 需求解析。
2. 初始关键词。
3. 第一轮检索。
4. 去重过滤。
5. 术语抽取。
6. 查询扩展。
7. 引用扩展。
8. 覆盖审查。
9. 迭代决策。
10. 输出报告。

### 完整版本

加入：

- 作者网络扩展。
- Venue 扩展。
- 数据集扩展。
- 代码仓库扩展。
- 术语漂移。
- 引用闭合。
- 监控。
- 多格式论文包。

## 13. 风险与防护

| 风险 | 表现 | 防护 |
|---|---|---|
| 关键词幻觉 | Agent 生成看似合理但领域不用的词 | 必须由真实论文术语回填验证 |
| 数据源偏差 | 只覆盖某个数据库 | 多数据源并行和数据源覆盖评分 |
| 引用马太效应 | 只发现高引用经典论文，漏掉新论文 | 时间覆盖评分和最新论文搜索 |
| 作者网络漂移 | 核心作者其他方向论文混入 | 相关性分类和 scope 过滤 |
| 过早停止 | 覆盖分数虚高 | 覆盖审查 + 反方总审 |
| 错误去重 | 不同论文被合并 | DOI、标题、作者、年份多证据合并 |
| 术语漂移 | 新旧术语不同导致漏检 | `terminology_drift_agent` |
| 近邻误排除 | 边界论文被丢弃 | `near_miss_classifier_agent` 保留扩展池 |

## 14. 推荐默认配置

```yaml
defaults:
  max_iterations: 6
  min_coverage_score: 85
  min_citation_closure_score: 0.75
  min_new_core_papers_per_iteration: 3
  require_adversarial_pass: true
  preserve_near_miss_pool: true
  data_sources:
    - semantic_scholar
    - openalex
    - crossref
    - arxiv
  expansion_modes:
    - keyword
    - citation
    - author
    - venue
    - dataset
    - code
  output_formats:
    - csv
    - bibtex
    - json
    - markdown_report
```

## 15. 最终输出物

虽然当前需求不要求实际输出论文结果，但完整系统最终应支持以下产物：

- `corpus.csv`：去重后的论文库。
- `corpus.bib`：BibTeX。
- `corpus.json`：完整结构化元数据。
- `excluded.csv`：排除论文与排除原因。
- `near_miss.csv`：接近主题但未纳入的论文。
- `search_report.md`：可复现搜索报告。
- `coverage_report.md`：覆盖评分和反方审查。
- `evidence_graph.json`：论文、术语、作者、引用图。
- `monitoring_config.yaml`：后续监控配置。

## 16. 核心设计原则

1. 初始关键词只用于启动，不用于限定最终搜索空间。
2. 论文自身生成下一轮术语、引用、作者、venue 和数据集扩展。
3. 每个“足够全面”的判断都必须被另一个 Agent 质疑。
4. 搜索过程必须可复现，所有查询式、排除理由、评分证据都要记录。
5. 近邻论文不能直接丢弃，它们是发现隐藏术语和相邻 cluster 的重要线索。
6. 去重必须保留版本关系，不能把 arXiv、会议版、期刊版粗暴压成一条不可解释记录。
7. 终止必须基于覆盖评分、边际收益、引用闭合和反方审查，而不是基于搜索轮数。

