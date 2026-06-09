# 深度论文搜索工具多 Agent 系统设计方案

## 1. 设计目标

这个系统要解决的不是“帮用户生成一批关键词再查论文”，而是“从不完整、不准确、甚至不符合领域真实表达的初始需求出发，自动发现领域术语、核心论文、引用网络、作者网络、会议社区、数据集、代码生态和未覆盖分支，并通过多轮互审逼近全面覆盖”。

核心目标：

- 初始关键词只作为启动线索，不作为最终边界。
- 搜索范围由论文内容、引用关系、作者关系、venue 社区、数据集、代码仓库和术语漂移共同反向塑造。
- 每个 Agent 必须有不可替代职责，不能为了数量拆分同一件事。
- 每个 Stage 必须产生后续 Stage 会消费的结构化结果。
- 每个 Flow 必须有明确触发条件、收益目标、失败模式和回流路径。
- 系统必须支持并行搜索、循环扩展、互相鞭策、可解释停止。

## 2. Agent 入选标准

为了避免凑数，一个 Agent 只有同时满足以下条件才允许进入系统：

1. 有独立失败模式：如果没有它，系统会以某种具体方式漏检、误检、误停或不可复现。
2. 有独立输入：它消费的数据不是另一个 Agent 的完全同构输入。
3. 有独立输出：它产生的 artifact 会被后续 Stage、评分器或审查器消费。
4. 有可审查边界：它的输出能被另一个 Agent 质疑、验证或修正。
5. 不只是“换个名字”：如果两个 Agent 的输入、动作、输出和失败模式都高度重合，必须合并。

下面的 Agent 清单按这个标准设计。每个 Agent 都绑定一个实际搜索问题，不把普通函数包装成 Agent。

## 3. 总体架构

```text
User Query
  |
  v
Intent, Scope, Assumption Layer
  |
  v
Seed Query Layer
  |
  +------------------+-------------------+-------------------+
  |                  |                   |                   |
  v                  v                   v                   v
Database Search   Citation Search    Author Search      Venue Search
  |                  |                   |                   |
  +------------------+-------------------+-------------------+
  |
  +------------------+-------------------+-------------------+
  |                  |                   |                   |
  v                  v                   v                   v
Dataset Search    Code Search        Term Mining       Full Text Mining
  |                  |                   |                   |
  +------------------+-------------------+-------------------+
  |
  v
Canonical Corpus + Evidence Graph
  |
  v
Coverage Audit + Adversarial Challenge
  |
  +-- PASS -------------------------------------> Final Corpus Package
  |
  +-- REVISE_QUERY ----------------------------> Seed Query Layer
  |
  +-- EXPAND_CITATION / AUTHOR / VENUE / DATA -> Parallel Expansion Layer
  |
  +-- ASK_USER --------------------------------> Clarify only unresolved scope conflict
```

系统内部维护一个 append-only event log，再由状态归约器生成当前 `Research State`。这样可以保证可复现、可回滚、可审查。

```yaml
research_state:
  run:
    id: string
    iteration: int
    depth_contract: exploratory | deep_survey | systematic_like | near_exhaustive
    budgets:
      api_calls: int
      wall_time_minutes: int
      pdf_downloads: int
      llm_tokens: int
  intent:
    raw_request: string
    normalized_topic: string
    domain: string
    task: string
    objects: []
    methods: []
    constraints: []
    assumptions: []
  scope:
    in_scope: []
    near_scope: []
    out_of_scope: []
    unresolved_ambiguities: []
  search_space:
    accepted_terms: []
    candidate_terms: []
    rejected_terms: []
    boolean_queries: []
    semantic_queries: []
    negative_queries: []
    seed_papers: []
    frontiers:
      citation: []
      author: []
      venue: []
      dataset: []
      code: []
      standards: []
  corpus:
    raw_records: []
    canonical_papers: []
    versions: []
    duplicates: []
    excluded_records: []
    near_miss_records: []
  evidence_graph:
    paper_nodes: []
    term_nodes: []
    author_nodes: []
    venue_nodes: []
    dataset_nodes: []
    code_nodes: []
    claim_nodes: []
    edges: []
  quality:
    coverage_scores: {}
    audit_reports: []
    adversarial_challenges: []
    residual_risks: []
    stop_decision: null
```

## 4. Agent 清单

本设计包含 79 个 Agent。它们不是全部每次都必须启用；orchestrator 会根据领域、预算和用户深度要求启用子集。但系统级设计保留这些 Agent，是因为它们分别覆盖不同漏检路径。

### 4.1 编排、状态与复现

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 1 | `run_orchestrator_agent` | 执行全局 DAG、启动并行任务、推进循环 | run plan、stage status | 多个搜索分支互相覆盖或遗漏 |
| 2 | `state_reducer_agent` | 从 append-only events 归约出唯一 `Research State` | state snapshot、state diff | 并行 Agent 直接写状态导致冲突 |
| 3 | `provenance_trace_agent` | 记录论文、术语、评分、排除理由的来源链 | provenance graph | 搜索过程不可复现 |
| 4 | `frontier_budget_allocator_agent` | 在关键词、引用、作者、venue、数据集等 frontier 间分配预算 | frontier budget plan | 预算被单一路径耗尽 |
| 5 | `failure_triage_agent` | 区分 API 失败、查询语法失败、空结果、权限失败 | recovery action | 把工具失败误判为主题无论文 |

### 4.2 意图、定义与边界

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 6 | `intent_decomposition_agent` | 把用户描述拆成领域、任务、对象、方法、场景、评价目标 | intent frame | 初始需求被当成单个关键词 |
| 7 | `domain_disambiguation_agent` | 识别跨领域同名术语，如 completion 在通信和视觉中的差异 | domain decision | 搜到大量错误学科论文 |
| 8 | `concept_definition_agent` | 给核心概念建立操作性定义和必要证据 | concept definition table | 后续相关性判断没有标准 |
| 9 | `scope_boundary_agent` | 定义 in-scope、near-scope、out-of-scope | scope contract | 扩展搜索无限漂移 |
| 10 | `depth_contract_agent` | 把用户需求转成搜索深度、覆盖阈值、停止阈值 | depth contract | 轻量调研和近穷尽调研混用同一流程 |
| 11 | `assumption_registry_agent` | 记录系统做出的隐含假设并等待后续证据验证 | assumption ledger | 错误假设静默影响全流程 |

### 4.3 术语、关键词与查询

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 12 | `seed_keyword_agent` | 从意图框架生成第一批启动词 | seed term set | 没有初始检索入口 |
| 13 | `translation_alias_agent` | 处理中英翻译、缩写、别名、全称和常见误译 | alias map | 中文需求直译导致漏检 |
| 14 | `controlled_vocabulary_agent` | 对照领域 taxonomy、ACM CCS、IEEE terms、MeSH 等受控词表 | controlled term candidates | 忽略数据库真实索引词 |
| 15 | `paper_term_extractor_agent` | 从真实论文标题、摘要、关键词、引言抽取术语 | observed term set | Agent 自造关键词而非领域真实词 |
| 16 | `term_canonicalization_agent` | 合并同义词、缩写、大小写、复数、英美拼写 | canonical term table | 同一概念被当成多个方向 |
| 17 | `term_cooccurrence_graph_agent` | 建立术语共现图，找隐藏连接词和桥接词 | term graph | 漏掉连接两个社区的中间术语 |
| 18 | `terminology_drift_agent` | 分析不同年份、社区、venue 的叫法变化 | drift report | 只搜新词或旧词导致年代偏差 |
| 19 | `negative_query_agent` | 生成排除词和噪声模式 | negative query rules | 搜索结果被相邻领域淹没 |
| 20 | `query_mutation_agent` | 基于别名、术语图、失败查询生成变体 | mutated query set | 第一批查询失败后无法系统扩展 |
| 21 | `boolean_query_compiler_agent` | 为不同数据库生成合法 Boolean 查询 | source-specific Boolean queries | 查询语法不适配数据库 |
| 22 | `semantic_query_compiler_agent` | 生成适合 embedding / semantic search 的自然语言检索语句 | semantic query set | 只靠 Boolean 无法命中换词论文 |
| 23 | `query_probe_agent` | 用小样本命中结果评估查询噪声率和漏检迹象 | query probe report | 大规模搜索前就把预算浪费在坏查询 |
| 24 | `keyword_gap_auditor_agent` | 审查关键词是否覆盖任务、方法、数据集、指标、应用场景 | keyword gap report | 关键词覆盖虚高 |

### 4.4 数据源检索

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 25 | `semantic_scholar_search_agent` | 查语义相关论文、引用、相似论文 | Semantic Scholar batch | 缺少引用和相似论文入口 |
| 26 | `openalex_search_agent` | 查开放 works、concept、机构、引用网络 | OpenAlex batch | 只依赖商业或单一学术索引 |
| 27 | `crossref_metadata_agent` | 查 DOI、出版元数据、期刊版本 | Crossref batch | DOI 和出版版本不完整 |
| 28 | `arxiv_search_agent` | 查预印本和最新未正式出版论文 | arXiv batch | 漏掉最新工作 |
| 29 | `dblp_search_agent` | 查计算机领域会议、作者、venue 记录 | DBLP batch | 计算机会议论文元数据缺失 |
| 30 | `ieee_xplore_search_agent` | 查通信、信号处理、硬件相关论文 | IEEE batch | 无线通信主题漏掉 IEEE 主阵地 |
| 31 | `acm_dl_search_agent` | 查计算机系统、网络、数据库和 HCI 等 ACM 论文 | ACM batch | ACM 社区论文漏检 |
| 32 | `domain_specific_database_agent` | 根据领域启用 PubMed、ACL Anthology、INSPIRE、SSRN 等专库 | domain DB batch | 用通用库覆盖不了特定学科 |
| 33 | `scholarly_web_fallback_agent` | 在 API 覆盖不足时搜索学术网页、实验室页面、课程页面 | scholarly web batch | API 索引缺失导致空白 |

### 4.5 全文与内容获取

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 34 | `full_text_locator_agent` | 定位 PDF、HTML、开放获取版本、作者主页版本 | full text links | 只能看标题摘要，无法挖术语 |
| 35 | `pdf_parse_agent` | 从 PDF 提取标题、摘要、章节、参考文献、表格 caption | parsed paper text | 全文信息不可用 |
| 36 | `reference_section_parser_agent` | 从全文参考文献解析未被 API 暴露的引用 | parsed references | 引用 API 不完整时漏掉关键旧文 |
| 37 | `figure_table_signal_agent` | 从图表 caption、表格列名提取方法、数据集、指标 | figure/table signals | 重要实验术语不在摘要里 |

### 4.6 扩展 Frontier

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 38 | `backward_citation_agent` | 沿种子论文参考文献找奠基论文 | backward citation frontier | 漏掉早期基础工作 |
| 39 | `forward_citation_agent` | 找引用种子论文的后续工作 | forward citation frontier | 漏掉后续改进和最新分支 |
| 40 | `co_citation_agent` | 找与种子论文共同被引用的论文 | co-citation frontier | 漏掉同一知识簇的非直接引用论文 |
| 41 | `bibliographic_coupling_agent` | 找引用相同文献的论文 | coupling frontier | 漏掉同源但不互引的平行工作 |
| 42 | `author_profile_agent` | 解析核心作者身份，抓取其主题相关论文 | author frontier | 漏掉同作者换术语工作 |
| 43 | `lab_institution_agent` | 从实验室、课题组、机构页面找项目和论文 | lab frontier | 漏掉尚未被数据库充分索引的系列工作 |
| 44 | `venue_track_agent` | 按核心会议、期刊、track、session 目录扩展 | venue frontier | 漏掉同社区但关键词不同论文 |
| 45 | `workshop_special_issue_agent` | 查 workshop、special issue、challenge 论文 | workshop frontier | 漏掉新兴方向的早期聚集地 |
| 46 | `dataset_benchmark_agent` | 根据数据集、仿真平台、benchmark 扩展论文 | dataset frontier | 漏掉同任务不同术语论文 |
| 47 | `code_repository_agent` | 从 GitHub、Papers with Code、README、release 找论文线索 | code frontier | 漏掉代码生态常见但索引弱的论文 |
| 48 | `leaderboard_challenge_agent` | 查 leaderboard、challenge、competition 关联论文 | leaderboard frontier | 漏掉 benchmark 社区论文 |
| 49 | `standard_patent_agent` | 查标准、专利、白皮书中的别名和应用术语 | standards frontier | 工程领域术语与论文术语断裂 |

### 4.7 规范化、去重与身份解析

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 50 | `metadata_canonicalization_agent` | 标准化标题、作者、年份、venue、DOI、arXiv ID | canonical record candidates | 元数据格式混乱无法合并 |
| 51 | `author_identity_resolution_agent` | 合并同名作者、区分重名作者、关联 ORCID/DBLP/OpenAlex ID | author identity map | 作者扩展误入同名作者 |
| 52 | `venue_identity_resolution_agent` | 合并 venue 缩写、全称、子刊、workshop 名称 | venue identity map | venue 扩展漏掉同一会议不同写法 |
| 53 | `version_linking_agent` | 关联 arXiv、会议版、期刊扩展版、技术报告 | version graph | 重复统计或丢失扩展版 |
| 54 | `deduplication_agent` | 按 DOI、标题、作者、年份、embedding 合并重复记录 | deduplicated corpus | 同一论文多次进入 corpus |
| 55 | `metadata_conflict_resolver_agent` | 解决年份、venue、作者顺序、标题变体冲突 | conflict resolution log | 错误元数据污染引用图 |
| 56 | `retraction_errata_agent` | 检查撤稿、勘误、问题论文、版本警告 | validity flags | 把失效论文作为核心证据 |

### 4.8 筛选、分类与证据建模

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 57 | `relevance_screening_agent` | 按 scope contract 判断 in-scope / near-scope / out-of-scope | relevance decisions | 噪声论文进入核心集合 |
| 58 | `near_miss_mining_agent` | 从 near-scope 论文提取可用于扩展的术语、引用、数据集 | near-miss signals | 边界论文被丢弃导致漏掉桥接词 |
| 59 | `exclusion_reason_agent` | 为排除论文生成结构化、可审查理由 | exclusion ledger | 排除不可复核 |
| 60 | `task_taxonomy_agent` | 将论文按任务定义和问题设置分层 | task taxonomy | 不同任务被混成一个集合 |
| 61 | `method_taxonomy_agent` | 将论文按技术路线、模型族、理论假设分层 | method taxonomy | 主流方法族覆盖不清 |
| 62 | `dataset_metric_extraction_agent` | 抽取数据集、仿真平台、评价指标 | dataset/metric table | 实验语境缺失 |
| 63 | `experimental_setting_agent` | 抽取系统设置，如信道模型、频段、天线、子载波、训练条件 | setting table | 论文表面相关但实验条件不匹配 |
| 64 | `evidence_graph_agent` | 构建论文、术语、作者、venue、数据集、代码、引用、claim 的异构图 | evidence graph | 无法判断覆盖和缺口 |

### 4.9 覆盖审查与反方机制

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 65 | `cluster_coverage_agent` | 计算任务簇、方法簇、数据集簇、venue 簇覆盖率 | cluster coverage matrix | 只看总论文数掩盖局部缺口 |
| 66 | `citation_closure_agent` | 判断核心引用网络是否接近闭合 | citation closure report | 引用扩展过早停止 |
| 67 | `source_diversity_agent` | 检查数据源、venue、年份、机构、作者群体多样性 | diversity report | 单一数据库或单一团队偏差 |
| 68 | `recency_and_seminal_balance_agent` | 平衡最新论文与奠基论文覆盖 | time balance report | 只看新论文或只看经典论文 |
| 69 | `missing_cluster_hunter_agent` | 主动寻找 evidence graph 中连接弱、覆盖弱的可能缺失簇 | missing cluster report | 未探索分支无人发现 |
| 70 | `coverage_scoring_agent` | 汇总多个覆盖证据生成覆盖分 | coverage score | 没有统一停止信号 |
| 71 | `coverage_audit_agent` | 审查覆盖分是否有证据支撑，指出虚高项 | audit report | 自评分过于乐观 |
| 72 | `adversarial_reviewer_agent` | 从反方角度构造最强漏检论证 | adversarial challenge | 系统过早相信自己 |
| 73 | `iteration_decision_agent` | 基于审查、预算、边际收益决定下一轮走哪条 flow | iteration decision | 盲目循环或盲目停止 |
| 74 | `stop_condition_validator_agent` | 在最终停止前检查所有 hard gate 是否满足 | stop validation | 没过质量门却输出最终结果 |

### 4.10 输出与监控

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 75 | `corpus_export_agent` | 生成 CSV、BibTeX、JSON、去重映射 | corpus package | 结果不可复用 |
| 76 | `search_protocol_report_agent` | 输出查询式、数据库、纳入排除、迭代历史 | reproducible search report | 调研过程不可复现 |
| 77 | `coverage_report_agent` | 输出覆盖评分、证据和残余风险 | coverage report | 用户不知道结果能信到什么程度 |
| 78 | `gap_report_agent` | 总结研究空白、弱覆盖区域、后续搜索建议 | gap report | 搜索结果不能指导下一步研究 |
| 79 | `monitoring_query_agent` | 生成后续监控查询、作者/venue/引用提醒 | monitoring config | 调研完成后无法跟踪新论文 |

### 4.11 TODO 执行控制 Agent

TODO mode 是可选执行模式。它不是普通 checklist，而是一个持续执行控制协议：系统维护 active TODO 队列，每次选择一条 TODO 执行，执行完成后删除或移动到 done；如果审查发现还有未解决任务，则继续追加 TODO。只有 active TODO 为空，且续写审查确认没有必要新增 TODO 时，系统才允许进入最终停止检查。

| # | Agent | 不可替代职责 | 独立输出 | 防止的失败模式 |
|---|---|---|---|---|
| 80 | `todo_planner_agent` | 根据用户目标、校准结果、config 和当前 state 生成初始 TODO 队列 | initial TODO queue | TODO mode 启动后没有可执行任务粒度 |
| 81 | `todo_selector_agent` | 从 active TODO 中选择下一条最应该执行的任务 | selected TODO | 低价值或无依赖准备的任务被盲目执行 |
| 82 | `todo_executor_router_agent` | 将选中的 TODO 路由给正确 Stage 或 Agent | TODO routing decision | TODO 被错误 Agent 执行或绕过已有 pipeline |
| 83 | `todo_completion_verifier_agent` | 检查 TODO 是否真的完成，并决定移入 done、阻塞或重试 | TODO completion verdict | TODO 表面执行但没有有效 artifact |
| 84 | `todo_continuation_auditor_agent` | 判断是否需要基于缺口、失败、反方意见继续追加 TODO | continuation audit | 队列为空但仍有可执行缺口，或无限追加低价值任务 |

## 5. Stage 设计

本系统使用 34 个 Stage。Stage 的粒度按“后续决策需要一个独立 artifact”划分，而不是按 Agent 数量划分。

| Stage | 名称 | 主要 Agent | 输入 | 输出 | 实际意义 |
|---|---|---|---|---|---|
| 1 | Run 初始化 | `run_orchestrator_agent`, `state_reducer_agent` | 用户请求 | run plan、初始 state | 建立可追踪任务边界 |
| 2 | 意图拆解 | `intent_decomposition_agent` | 原始请求 | intent frame | 把自然语言拆成可搜索字段 |
| 3 | 领域消歧 | `domain_disambiguation_agent`, `assumption_registry_agent` | intent frame | domain decision、assumptions | 防止跨领域误搜 |
| 4 | 概念定义 | `concept_definition_agent` | intent、domain | concept table | 建立相关性判断标准 |
| 5 | 范围契约 | `scope_boundary_agent`, `depth_contract_agent` | concept table | scope contract、depth contract | 明确纳入、排除、停止阈值 |
| 6 | 初始术语生成 | `seed_keyword_agent`, `translation_alias_agent`, `controlled_vocabulary_agent` | scope contract | seed terms、alias map | 创建第一批入口 |
| 7 | 初始查询编译 | `boolean_query_compiler_agent`, `semantic_query_compiler_agent`, `negative_query_agent` | seed terms | source-specific queries | 查询可执行化 |
| 8 | 查询探针 | `query_probe_agent`, `keyword_gap_auditor_agent` | 查询草案 | probe report、keyword gap | 大规模检索前发现坏查询 |
| 9 | 查询修正 | `query_mutation_agent` | probe report | revised queries | 用小样本反馈修正入口 |
| 10 | 并行数据库检索 | source search agents 25-33 | revised queries | raw records | 多数据源降低偏差 |
| 11 | 全文定位 | `full_text_locator_agent` | raw records | full text links | 为术语和引用挖掘准备材料 |
| 12 | 全文解析 | `pdf_parse_agent`, `reference_section_parser_agent`, `figure_table_signal_agent` | full text links | parsed text、references、signals | 获取摘要之外的真实术语 |
| 13 | 元数据规范化 | `metadata_canonicalization_agent`, `metadata_conflict_resolver_agent` | raw records、parsed text | canonical candidates | 让多源数据可合并 |
| 14 | 身份解析 | `author_identity_resolution_agent`, `venue_identity_resolution_agent` | canonical candidates | author map、venue map | 防止作者和 venue 扩展误差 |
| 15 | 版本关联与去重 | `version_linking_agent`, `deduplication_agent` | canonical candidates | deduplicated corpus、version graph | 合并重复但保留版本关系 |
| 16 | 初筛相关性 | `relevance_screening_agent`, `exclusion_reason_agent` | corpus、scope | in/near/out records | 把核心集合和噪声分开 |
| 17 | Near-miss 挖掘 | `near_miss_mining_agent` | near-scope records | near-miss signals | 从边界论文找隐藏入口 |
| 18 | 真实术语抽取 | `paper_term_extractor_agent`, `term_canonicalization_agent` | in-scope、parsed text | observed terms | 用论文反向修正关键词 |
| 19 | 术语图与漂移 | `term_cooccurrence_graph_agent`, `terminology_drift_agent` | observed terms | term graph、drift report | 发现跨社区和跨年代术语 |
| 20 | 分类建模 | `task_taxonomy_agent`, `method_taxonomy_agent`, `dataset_metric_extraction_agent`, `experimental_setting_agent` | in-scope records | taxonomies、setting table | 判断覆盖不是只靠数量 |
| 21 | 种子论文选择 | `recency_and_seminal_balance_agent`, `frontier_budget_allocator_agent` | taxonomies、quality signals | seed papers、frontier budgets | 为多路径扩展选代表点 |
| 22 | 引用扩展 | `backward_citation_agent`, `forward_citation_agent`, `co_citation_agent`, `bibliographic_coupling_agent` | seed papers | citation frontiers | 发现关键词搜不到的论文 |
| 23 | 作者与机构扩展 | `author_profile_agent`, `lab_institution_agent` | seed authors、author map | author/lab frontiers | 发现同团队换术语论文 |
| 24 | Venue 扩展 | `venue_track_agent`, `workshop_special_issue_agent` | venue map、seed venues | venue frontiers | 发现同社区未命中论文 |
| 25 | 数据集与代码扩展 | `dataset_benchmark_agent`, `code_repository_agent`, `leaderboard_challenge_agent` | dataset table、method names | dataset/code frontiers | 发现同任务不同叫法论文 |
| 26 | 标准与产业术语扩展 | `standard_patent_agent` | core terms、domain | standards frontier | 工程领域补充别名和应用词 |
| 27 | 扩展结果合并 | `state_reducer_agent`, `metadata_canonicalization_agent`, `deduplication_agent` | all frontiers | updated corpus | 把多路径发现并入统一库 |
| 28 | 深度筛选与有效性 | `relevance_screening_agent`, `retraction_errata_agent`, `exclusion_reason_agent` | updated corpus | validated corpus | 清除噪声和失效论文 |
| 29 | Evidence Graph 构建 | `evidence_graph_agent` | validated corpus、terms、taxonomies、frontiers | evidence graph | 为覆盖审查提供结构 |
| 30 | 覆盖分析 | `cluster_coverage_agent`, `citation_closure_agent`, `source_diversity_agent`, `recency_and_seminal_balance_agent` | evidence graph | coverage subreports | 计算多个独立覆盖信号 |
| 31 | 缺失簇主动搜索 | `missing_cluster_hunter_agent` | coverage subreports、evidence graph | missing cluster report | 主动找“没搜到什么” |
| 32 | 覆盖评分与审查 | `coverage_scoring_agent`, `coverage_audit_agent` | subreports、missing clusters | score、audit | 防止自评分虚高 |
| 33 | 反方挑战与迭代决策 | `adversarial_reviewer_agent`, `iteration_decision_agent`, `stop_condition_validator_agent` | score、audit、budget | next action | 决定回到哪个 flow 或停止 |
| 34 | 输出与监控 | `corpus_export_agent`, `search_protocol_report_agent`, `coverage_report_agent`, `gap_report_agent`, `monitoring_query_agent` | final state | final packages | 输出可复用、可复现、可继续监控的结果 |
| 35 | TODO 执行循环 | `todo_planner_agent`, `todo_selector_agent`, `todo_executor_router_agent`, `todo_completion_verifier_agent`, `todo_continuation_auditor_agent` | config、calibration result、current state、active TODO | updated TODO queue、done TODO、continuation decision | 在 TODO mode 下持续执行直到没有可执行任务 |

## 6. 核心 Flow

### 6.0 TODO Mode Flow

触发条件：`execution.todo_mode: true`。

```text
calibrated goal and config
  -> todo_planner_agent
  -> loop:
       todo_selector_agent
       todo_executor_router_agent
       target stage or target agent executes
       todo_completion_verifier_agent
       todo_continuation_auditor_agent
     until active TODO is empty and no new TODO is justified
  -> stop_condition_validator_agent
```

实际意义：

- 用户只需给目标，系统可以把目标拆成可执行任务。
- 每个 TODO 必须有来源、优先级、目标 Agent 或 Stage、完成标准。
- 执行完成的 TODO 必须有 artifact 证据，否则不能删除。
- coverage gap、adversarial challenge、source failure、missing cluster、low confidence assumption 都可以生成新 TODO。
- 低收益或重复 TODO 不能无限追加，应转为 residual risk 或关闭 frontier。

建议 TODO 文件：

```text
workspace/work/deep-paper-search/todo/active.todo
workspace/work/deep-paper-search/todo/done.todo
workspace/work/deep-paper-search/todo/todo_state.json
workspace/work/deep-paper-search/todo/todo_log.md
```

TODO mode 的停止条件：

1. `active.todo` 为空。
2. `todo_continuation_auditor_agent` 输出 `NO_NEW_TODO`.
3. `stop_condition_validator_agent` 通过。
4. 若仍有不可执行风险，写入 residual risks，而不是继续追加低价值 TODO。

### 6.1 Query Bootstrap Flow

触发条件：新任务开始，或反方审查指出关键词缺口。

```text
intent frame
  -> seed_keyword_agent
  -> translation_alias_agent
  -> controlled_vocabulary_agent
  -> boolean_query_compiler_agent
  -> semantic_query_compiler_agent
  -> query_probe_agent
  -> query_mutation_agent
```

实际意义：

- 不假设用户初始词正确。
- 用受控词表和真实探针结果减少自造词。
- 将坏查询挡在大规模检索之前。

回流条件：

- `query_probe_agent` 返回高噪声。
- `keyword_gap_auditor_agent` 指出任务、方法、数据集或指标术语缺失。
- `adversarial_reviewer_agent` 指出“只搜到了某一个术语社区”。

### 6.2 Parallel Source Discovery Flow

触发条件：查询通过探针，或者某一轮生成了新查询。

```text
source-specific queries
  -> semantic_scholar_search_agent
  -> openalex_search_agent
  -> crossref_metadata_agent
  -> arxiv_search_agent
  -> dblp_search_agent
  -> ieee_xplore_search_agent
  -> acm_dl_search_agent
  -> domain_specific_database_agent
  -> scholarly_web_fallback_agent
```

并行策略：

- 每个数据源独立执行，不等待其他源成功。
- 结果统一写入 event log。
- `failure_triage_agent` 判断失败是否要重试、换查询、换数据源或降级。

实际意义：

- 不同数据库覆盖不同学科和论文类型。
- API 限制不会被误认为“无论文”。
- 可衡量数据源偏差。

### 6.3 Paper-Driven Terminology Flow

触发条件：系统得到第一批 in-scope 或 near-scope 论文。

```text
validated papers
  -> full_text_locator_agent
  -> pdf_parse_agent
  -> figure_table_signal_agent
  -> paper_term_extractor_agent
  -> term_canonicalization_agent
  -> term_cooccurrence_graph_agent
  -> terminology_drift_agent
  -> query_mutation_agent
```

实际意义：

- 让论文自己告诉系统领域真实叫法。
- 从图表、实验设置、caption 中发现摘要没有写的关键词。
- 发现旧术语、新术语、不同社区术语。

示例：用户说“频域补全”，论文里可能更常见的是 `CSI reconstruction`、`frequency extrapolation`、`angular-delay domain`、`partial CSI feedback`、`CSI compression`、`OFDM subcarriers`。

### 6.4 Citation Snowball Flow

触发条件：产生种子论文，或 `citation_closure_agent` 判断核心引用网络不闭合。

```text
seed papers
  -> backward_citation_agent
  -> forward_citation_agent
  -> co_citation_agent
  -> bibliographic_coupling_agent
  -> reference_section_parser_agent
  -> relevance_screening_agent
```

实际意义：

- Backward citation 找奠基工作。
- Forward citation 找后续改进。
- Co-citation 找同一知识簇。
- Bibliographic coupling 找平行但不互引的工作。
- 全文 reference parser 修复 API 引用缺口。

### 6.5 Author and Lab Deep Search Flow

触发条件：某些作者在核心 corpus 中高频出现，或反方指出“可能漏掉同团队相关工作”。

```text
core authors
  -> author_identity_resolution_agent
  -> author_profile_agent
  -> lab_institution_agent
  -> relevance_screening_agent
  -> near_miss_mining_agent
```

实际意义：

- 论文作者常在同一主题下换术语、换任务名、换 venue。
- 实验室页面可能列出数据库未收录或标题翻译不同的论文。
- 身份解析是必要步骤，否则同名作者会污染结果。

### 6.6 Venue and Community Flow

触发条件：核心论文集中出现稳定 venue、track、workshop 或 special issue。

```text
seed venues
  -> venue_identity_resolution_agent
  -> venue_track_agent
  -> workshop_special_issue_agent
  -> relevance_screening_agent
  -> method_taxonomy_agent
```

实际意义：

- 同一个研究社区可能不用用户给的关键词。
- Workshop 和 special issue 经常是新方向早期聚集地。
- Track/session 名称能提供比论文标题更稳定的社区标签。

### 6.7 Dataset, Benchmark, Code Flow

触发条件：论文中出现共享数据集、仿真平台、benchmark、代码仓库或 leaderboard。

```text
dataset and method signals
  -> dataset_benchmark_agent
  -> code_repository_agent
  -> leaderboard_challenge_agent
  -> dataset_metric_extraction_agent
  -> experimental_setting_agent
```

实际意义：

- 同一个实验对象可能被不同方法论文用不同术语描述。
- 代码仓库 README 常出现相关论文、复现论文、baseline。
- Leaderboard 能发现数据库还没充分连接的新论文。

### 6.8 Standard and Engineering Vocabulary Flow

触发条件：主题属于通信、硬件、医学、法律、标准化工程等强工程场景。

```text
core terms
  -> standard_patent_agent
  -> translation_alias_agent
  -> controlled_vocabulary_agent
  -> query_mutation_agent
```

实际意义：

- 工程领域的论文术语、标准术语、产品术语经常不同。
- 专利和白皮书不进入核心论文集，但能提供别名、应用场景和缩写。

### 6.9 Coverage Audit and Adversarial Loop

触发条件：每一轮扩展合并后强制执行。

```text
evidence graph
  -> cluster_coverage_agent
  -> citation_closure_agent
  -> source_diversity_agent
  -> recency_and_seminal_balance_agent
  -> missing_cluster_hunter_agent
  -> coverage_scoring_agent
  -> coverage_audit_agent
  -> adversarial_reviewer_agent
  -> iteration_decision_agent
```

实际意义：

- 评分 Agent 不能自己宣布成功。
- 审查 Agent 不能只看分数，必须检查证据链。
- 反方 Agent 必须构造“为什么还可能漏掉关键论文”的最强论证。
- 决策 Agent 根据具体缺口回到具体 Flow，而不是笼统“再搜一轮”。

## 7. Agent 互相鞭策关系

| 被检查对象 | 鞭策 Agent | 检查问题 | 可能回流 |
|---|---|---|---|
| `seed_keyword_agent` | `keyword_gap_auditor_agent` | 初始词是否只覆盖用户措辞 | Stage 6 |
| `translation_alias_agent` | `paper_term_extractor_agent` | 翻译词是否被真实论文使用 | Stage 18 |
| `boolean_query_compiler_agent` | `query_probe_agent` | 查询语法正确但结果是否高噪声 | Stage 9 |
| `semantic_query_compiler_agent` | `query_probe_agent` | 语义查询是否漂移到相邻领域 | Stage 9 |
| source search agents | `source_diversity_agent` | 是否过度依赖单一数据库 | Stage 10 |
| `author_profile_agent` | `author_identity_resolution_agent` | 是否混入同名作者 | Stage 23 |
| `venue_track_agent` | `venue_identity_resolution_agent` | venue 缩写和子会是否误合并 | Stage 24 |
| `deduplication_agent` | `version_linking_agent` | 是否把期刊扩展版错误丢弃 | Stage 15 |
| `relevance_screening_agent` | `near_miss_mining_agent` | 边界论文是否仍有扩展价值 | Stage 17 |
| `method_taxonomy_agent` | `missing_cluster_hunter_agent` | 方法族是否漏分支 | Stage 31 |
| `citation_closure_agent` | `adversarial_reviewer_agent` | 引用闭合是否只在局部成立 | Stage 22 |
| `coverage_scoring_agent` | `coverage_audit_agent` | 覆盖分是否有证据支撑 | Stage 32 |
| `coverage_audit_agent` | `adversarial_reviewer_agent` | 审查是否太宽松 | Stage 33 |
| `iteration_decision_agent` | `stop_condition_validator_agent` | 是否满足硬停止条件 | Stage 33 |

## 8. 迭代决策

`iteration_decision_agent` 不能只输出 continue / stop，必须输出具体回流目标：

```yaml
iteration_decision:
  decision:
    - PASS
    - REVISE_QUERY
    - EXPAND_CITATION
    - EXPAND_AUTHOR
    - EXPAND_VENUE
    - EXPAND_DATASET_CODE
    - EXPAND_STANDARD_TERMS
    - ASK_USER
    - STOP_WITH_RISK
  reason: string
  evidence:
    coverage_score: float
    audit_findings: []
    adversarial_challenges: []
    marginal_yield: {}
  next_stage: int
  budget_delta: {}
```

回流规则：

- 术语缺口：回到 Stage 6 或 Stage 18。
- 查询噪声高：回到 Stage 8-9。
- 引用不闭合：回到 Stage 22。
- 作者网络有未探索高价值节点：回到 Stage 23。
- Venue 覆盖弱：回到 Stage 24。
- 数据集或代码线索强：回到 Stage 25。
- 工程术语和论文术语断裂：回到 Stage 26。
- 评分虚高或证据不足：回到对应产生证据的 Stage，而不是重复全流程。

## 9. 覆盖评分体系

覆盖分必须由多个独立证据构成，不能由论文数量直接决定。

| 维度 | 权重 | 证据来源 | 低分时回流 |
|---|---:|---|---|
| 任务定义覆盖 | 10 | `task_taxonomy_agent` | Stage 6, 18 |
| 方法族覆盖 | 12 | `method_taxonomy_agent`, `missing_cluster_hunter_agent` | Stage 22, 31 |
| 术语覆盖 | 10 | `term_cooccurrence_graph_agent`, `terminology_drift_agent` | Stage 18, 19 |
| 引用闭合 | 12 | `citation_closure_agent` | Stage 22 |
| 作者网络覆盖 | 8 | `author_profile_agent`, `author_identity_resolution_agent` | Stage 23 |
| Venue 社区覆盖 | 8 | `venue_track_agent`, `workshop_special_issue_agent` | Stage 24 |
| 数据集与 benchmark 覆盖 | 8 | `dataset_benchmark_agent`, `leaderboard_challenge_agent` | Stage 25 |
| 代码生态覆盖 | 6 | `code_repository_agent` | Stage 25 |
| 数据源多样性 | 8 | `source_diversity_agent` | Stage 10 |
| 年代平衡 | 6 | `recency_and_seminal_balance_agent` | Stage 22 |
| Near-miss 解释 | 5 | `near_miss_mining_agent`, `exclusion_reason_agent` | Stage 17 |
| 反方审查通过度 | 7 | `coverage_audit_agent`, `adversarial_reviewer_agent` | Stage 31-33 |

建议阈值：

- `>= 90`: 可声称接近系统性搜索，仍需列出残余风险。
- `85-89`: 可作为深度调研结果。
- `75-84`: 可作为强初稿，但不能声称全面。
- `< 75`: 必须继续迭代，除非预算耗尽或用户停止。

## 10. 终止条件

允许终止：

1. 覆盖分达到 depth contract 阈值。
2. `coverage_audit_agent` 没有 high / critical 问题。
3. `adversarial_reviewer_agent` 的最强漏检论证已被解决或降级为 low。
4. `stop_condition_validator_agent` 确认硬门槛满足。
5. 连续两轮边际收益低于阈值，且低收益不是由失败查询或失败数据源造成。

禁止终止：

- 因为论文数量已经很多。
- 因为关键词已经很多。
- 因为某个数据库没有新结果。
- 因为覆盖评分 Agent 单独给了高分。
- 因为预算快耗尽但未输出残余风险。

## 11. 数据结构

### 11.1 Agent Event

```yaml
agent_event:
  event_id: string
  run_id: string
  iteration: int
  stage: int
  agent: string
  input_refs: []
  output_refs: []
  decision: string | null
  confidence: float | null
  failure: null | {}
  timestamp: string
```

### 11.2 Paper Record

```yaml
paper:
  canonical_id: string
  title: string
  authors: []
  author_ids: []
  year: int | null
  venue: string | null
  venue_id: string | null
  doi: string | null
  arxiv_id: string | null
  urls: []
  abstract: string | null
  source_records: []
  versions: []
  references: []
  cited_by: []
  relevance:
    label: in_scope | near_scope | out_of_scope
    score: float
    matched_scope: []
    rationale: string
  taxonomy:
    tasks: []
    methods: []
    datasets: []
    metrics: []
    settings: []
  validity:
    retraction_status: clear | warning | retracted | unknown
    metadata_conflicts: []
```

### 11.3 Term Record

```yaml
term:
  canonical_term: string
  aliases: []
  translations: []
  term_type: task | method | dataset | metric | setting | venue | exclusion | standard
  source_papers: []
  first_seen_iteration: int
  first_seen_source: string
  communities: []
  years_active: []
  confidence: float
  status: accepted | candidate | rejected
```

### 11.4 Frontier Record

```yaml
frontier:
  frontier_id: string
  type: citation | author | venue | dataset | code | standard | term
  seed: string
  generated_by: string
  candidate_records: []
  expected_gain: float
  actual_gain: float | null
  status: open | expanded | deferred | closed
```

## 12. 示例：频域补全与 CSI 反馈

用户输入：

```text
调研频域补全在 CSI 反馈是如何工作的
```

系统关键路径：

1. `domain_disambiguation_agent` 判断主题属于无线通信 / CSI feedback，而不是图像补全。
2. `concept_definition_agent` 把核心概念拆成：CSI feedback、frequency-domain missing / partial observation、reconstruction / extrapolation / compression、OFDM subcarriers、MIMO channel。
3. `translation_alias_agent` 不只直译“frequency-domain completion”，还生成 `frequency extrapolation`、`CSI reconstruction`、`partial CSI feedback` 等候选。
4. 第一轮检索得到少量相关论文后，`paper_term_extractor_agent` 从论文中发现 `CsiNet`、`angular-delay domain`、`channel extrapolation`、`CSI compression`、`compressed sensing based feedback` 等真实术语。
5. `term_cooccurrence_graph_agent` 发现 `frequency domain` 常与 `OFDM subcarriers`、`delay domain`、`angular domain` 共现，因此触发跨域扩展。
6. `backward_citation_agent` 找传统压缩感知和码本反馈基础工作。
7. `forward_citation_agent` 找深度学习 CSI feedback 的后续改进。
8. `dataset_benchmark_agent` 根据 COST 2100、QuaDRiGa、3GPP channel model 等实验设置扩展。
9. `author_profile_agent` 查高频作者同主题论文，避免只覆盖一篇代表作。
10. `venue_track_agent` 查通信领域核心 venue 的相关 session，补上没有使用 completion 一词的论文。
11. `adversarial_reviewer_agent` 质疑：如果只覆盖神经网络重建，是否漏掉 compressed sensing、codebook feedback、channel prediction、transform-domain sparse recovery。
12. `iteration_decision_agent` 根据缺口选择回到引用扩展、术语扩展或 venue 扩展，而不是盲目重搜。

这个例子体现的核心机制是：用户词不决定搜索边界，论文网络和领域实践决定搜索边界。

## 13. MVP 与完整系统

### 13.1 MVP 必须保留的 Agent

MVP 可以不启用所有 79 个 Agent，但以下 Agent 不能删：

- `run_orchestrator_agent`
- `state_reducer_agent`
- `provenance_trace_agent`
- `intent_decomposition_agent`
- `domain_disambiguation_agent`
- `concept_definition_agent`
- `scope_boundary_agent`
- `seed_keyword_agent`
- `translation_alias_agent`
- `paper_term_extractor_agent`
- `term_canonicalization_agent`
- `boolean_query_compiler_agent`
- `semantic_query_compiler_agent`
- `query_probe_agent`
- `semantic_scholar_search_agent`
- `openalex_search_agent`
- `arxiv_search_agent`
- `metadata_canonicalization_agent`
- `version_linking_agent`
- `deduplication_agent`
- `relevance_screening_agent`
- `near_miss_mining_agent`
- `backward_citation_agent`
- `forward_citation_agent`
- `author_profile_agent`
- `venue_track_agent`
- `method_taxonomy_agent`
- `evidence_graph_agent`
- `cluster_coverage_agent`
- `citation_closure_agent`
- `coverage_scoring_agent`
- `coverage_audit_agent`
- `adversarial_reviewer_agent`
- `iteration_decision_agent`
- `search_protocol_report_agent`

### 13.2 完整系统新增价值

完整系统相比 MVP 的关键提升：

- 更强数据源覆盖：IEEE、ACM、DBLP、专用数据库、学术网页。
- 更强全文挖掘：PDF、参考文献、图表 caption、实验设置。
- 更强扩展路径：co-citation、bibliographic coupling、lab、workshop、leaderboard、standard。
- 更强质量控制：作者身份、venue 身份、元数据冲突、撤稿检查。
- 更强覆盖证明：source diversity、年代平衡、缺失簇主动搜索、停止条件验证。

## 14. 实现建议

### 14.1 编排

推荐使用状态机 + DAG：

- DAG 管理可并行任务。
- 状态机管理循环、质量门和回流。
- 所有 Agent 只写 event log，不直接覆盖全局状态。
- `state_reducer_agent` 是唯一生成当前 state 的组件。

适合的实现：

- LangGraph：适合 Agent loop 和 conditional edge。
- Temporal：适合长任务、重试、可靠执行。
- Dagster / Prefect：适合数据管线和可观测性。
- 自研 orchestrator：适合原型，但必须保留 event log、state snapshot、retry policy。

### 14.2 存储

建议组合：

- PostgreSQL：paper、term、agent event、frontier、decision。
- 向量库：标题、摘要、全文片段、query embedding。
- 图数据库或图表：evidence graph。
- 对象存储：PDF、HTML、解析文本、导出包。

### 14.3 去重与版本关联

推荐顺序：

1. DOI / arXiv ID 精确匹配。
2. 规范化标题哈希。
3. 标题 embedding 相似度。
4. 作者重叠和年份接近。
5. venue、页码、版本标识。
6. 不确定合并进入 `metadata_conflict_resolver_agent`。

会议版和期刊扩展版不应被简单合并丢弃，而应进入 `version graph`。

### 14.4 相关性筛选

相关性输出必须可审查：

```yaml
relevance_decision:
  paper_id: string
  label: in_scope
  score: 0.87
  matched_scope:
    - CSI feedback
    - frequency-domain reconstruction
  exclusion_checks:
    - not image completion
    - not generic channel estimation without feedback
  rationale: "The paper studies feedback and reconstruction of downlink CSI over OFDM subcarriers."
```

## 15. 最终输出物

完整系统最终输出：

- `corpus.csv`：去重后的论文库。
- `corpus.bib`：BibTeX。
- `corpus.json`：完整结构化元数据。
- `versions.json`：arXiv、会议版、期刊版关系。
- `excluded.csv`：排除论文和排除理由。
- `near_miss.csv`：边界论文及可用扩展信号。
- `search_protocol.md`：查询式、数据库、迭代路径、纳入排除标准。
- `coverage_report.md`：覆盖评分、证据、审查意见、反方挑战。
- `evidence_graph.json`：论文、术语、作者、venue、数据集、代码、引用图。
- `gap_report.md`：弱覆盖区域和研究空白。
- `monitoring_config.yaml`：后续监控查询。

## 16. 核心原则

1. 不以初始关键词为边界，只以它作为入口。
2. 每一轮都必须让论文内容反向修正搜索空间。
3. 每条扩展路径都必须能解释它发现了什么，以及为什么值得继续。
4. 每个 Agent 都要产出可消费 artifact，而不是一句主观判断。
5. 每个覆盖结论都必须有证据链。
6. 每个停止决定都必须经过审查和反方挑战。
7. 近邻论文、失败查询、排除论文都要保留，因为它们能解释搜索边界。
8. 作者、venue、数据集、代码、标准不是辅助装饰，而是发现隐藏论文的独立入口。
