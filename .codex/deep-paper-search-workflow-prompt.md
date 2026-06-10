# Deep Paper Search Workflow Launcher Prompt

Use the Deep Paper Search custom agents installed in this repository to run an iterative, evidence-driven paper discovery workflow. This launcher is intentionally separate from the individual agent prompts. It describes how to coordinate the system, when to ask the user for clarification, how to route loopbacks, and how to prevent premature stopping. The individual authoritative prompt for each agent lives under `prompts/<agent_name>.md`, and each active custom agent is configured under `.codex/agents/<agent_name>.toml`.

## Mission

The workflow starts from a research idea that may be incomplete, translated poorly, or expressed with terms that are not used by the target academic community. Your job as the workflow controller is not to run a one-pass keyword search. Your job is to build a stateful research process that learns from papers, citations, authors, venues, datasets, code, standards, and audit feedback. Initial keywords are only a launch point. The final search boundary must be justified by evidence and must survive coverage audit and adversarial challenge.

## Agent Groups

- `orchestration_state_reproducibility`: `run_orchestrator_agent`, `state_reducer_agent`, `provenance_trace_agent`, `frontier_budget_allocator_agent`, `failure_triage_agent`
- `intent_definition_boundaries`: `intent_decomposition_agent`, `domain_disambiguation_agent`, `concept_definition_agent`, `scope_boundary_agent`, `depth_contract_agent`, `assumption_registry_agent`
- `terminology_keywords_queries`: `seed_keyword_agent`, `translation_alias_agent`, `controlled_vocabulary_agent`, `paper_term_extractor_agent`, `term_canonicalization_agent`, `term_cooccurrence_graph_agent`, `terminology_drift_agent`, `negative_query_agent`, `query_mutation_agent`, `boolean_query_compiler_agent`, `semantic_query_compiler_agent`, `query_probe_agent`, `keyword_gap_auditor_agent`
- `data_source_retrieval`: `semantic_scholar_search_agent`, `openalex_search_agent`, `crossref_metadata_agent`, `arxiv_search_agent`, `dblp_search_agent`, `ieee_xplore_search_agent`, `acm_dl_search_agent`, `domain_specific_database_agent`, `scholarly_web_fallback_agent`
- `full_text_content`: `full_text_locator_agent`, `pdf_parse_agent`, `reference_section_parser_agent`, `figure_table_signal_agent`
- `expansion_frontiers`: `backward_citation_agent`, `forward_citation_agent`, `co_citation_agent`, `bibliographic_coupling_agent`, `author_profile_agent`, `lab_institution_agent`, `venue_track_agent`, `workshop_special_issue_agent`, `dataset_benchmark_agent`, `code_repository_agent`, `leaderboard_challenge_agent`, `standard_patent_agent`
- `normalization_dedup_identity`: `metadata_canonicalization_agent`, `author_identity_resolution_agent`, `venue_identity_resolution_agent`, `version_linking_agent`, `deduplication_agent`, `metadata_conflict_resolver_agent`, `retraction_errata_agent`
- `screening_taxonomy_evidence`: `relevance_screening_agent`, `near_miss_mining_agent`, `exclusion_reason_agent`, `task_taxonomy_agent`, `method_taxonomy_agent`, `dataset_metric_extraction_agent`, `experimental_setting_agent`, `evidence_graph_agent`
- `coverage_audit_adversarial`: `cluster_coverage_agent`, `citation_closure_agent`, `source_diversity_agent`, `recency_and_seminal_balance_agent`, `missing_cluster_hunter_agent`, `coverage_scoring_agent`, `coverage_audit_agent`, `adversarial_reviewer_agent`, `iteration_decision_agent`, `stop_condition_validator_agent`
- `output_monitoring`: `corpus_export_agent`, `search_protocol_report_agent`, `coverage_report_agent`, `gap_report_agent`, `monitoring_query_agent`
- `todo_execution_control`: `todo_planner_agent`, `todo_selector_agent`, `todo_executor_router_agent`, `todo_completion_verifier_agent`, `todo_continuation_auditor_agent`

## Stage Protocol

The workflow has these stages:

1. Run Setup and Goal Calibration: output `run plan, initial ledgers, calibrated direction, and unresolved parameter list`; purpose: Start with a lightweight calibration pass so the system can test the user's direction before asking for detailed configuration..
2. Domain, Scope, and Depth Contract: output `domain decision, concept definitions, scope boundary, depth contract, and assumption ledger`; purpose: Lock the meaning of the task, paper-count lower bound, year policy, and stopping standard before full search..
3. Seed Terms and Query Compilation: output `seed terms, alias map, negative rules, Boolean queries, and semantic queries`; purpose: Create executable search entries without treating the user's first wording as the final boundary..
4. Query Probe, Keyword Audit, and Repair: output `probe report, keyword gap report, revised query set, and config confirmation bundle`; purpose: Use small samples to detect wrong vocabulary, high-noise queries, and missing term families before large retrieval..
5. Parallel Scholarly Source Retrieval: output `raw candidate records with abstracts, citation metadata when available, source failures, and query ledger entries`; purpose: Retrieve candidates from complementary indexes while preserving enough provenance to debug each source..
6. Artifact Access, Parsing, and Abstract Extraction: output `abstract-enriched paper records, parsed text signals, reference records, parse confidence, and artifact index updates`; purpose: Move beyond download-only behavior by extracting abstracts and useful text signals from legal metadata, HTML, PDF, or TeX artifacts..
7. Metadata Identity, Versioning, and Deduplication: output `canonical records, author identities, venue identities, version graph, deduplicated corpus, and conflict notes`; purpose: Turn noisy multi-source records into stable paper identities while preserving meaningful versions..
8. Relevance Screening and Near-Miss Mining: output `in-scope, near-scope, out-of-scope, unknown labels, exclusion reasons, and near-miss expansion signals`; purpose: Protect corpus quality while still using boundary papers to discover hidden terminology and paths..
9. Paper-Driven Terminology Refresh: output `observed terms, canonical term table, term graph, terminology drift notes, and query mutations`; purpose: Let real papers update the vocabulary, including old terms, new terms, aliases, and cross-community bridge terms..
10. Taxonomy, Settings, and Evidence Graph: output `task taxonomy, method taxonomy, dataset/metric table, experimental settings, and evidence graph`; purpose: Organize papers by what they actually do so coverage can be judged by substance rather than count..
11. Citation Snowball Expansion: output `backward, forward, co-citation, and bibliographic-coupling frontiers with relevance candidates`; purpose: Recover foundational, parallel, and follow-up work that keyword search cannot reliably find..
12. Author and Lab Expansion: output `author profile frontier, lab frontier, identity warnings, and candidate records`; purpose: Find related papers from the same researchers or groups when terminology changes across a project line..
13. Venue and Community Expansion: output `venue, track, workshop, and special-issue frontiers with candidate records`; purpose: Search the research community around the topic, not only the literal terms..
14. Dataset, Code, Benchmark, and Standards Expansion: output `dataset/code/leaderboard/standards frontiers, code availability signals, and engineering alias terms`; purpose: Expose papers connected through shared evaluation objects, implementations, and engineering vocabulary..
15. Expansion Merge and Validity Check: output `updated corpus, deduplicated expansion records, retraction or errata flags, and low-yield frontier notes`; purpose: Integrate expansion results without polluting the corpus or hiding invalid records..
16. Citation, Code, and Paper-Value Enrichment: output `citation counts, citation source, code URL, code evidence, value score, quality notes, limitations, and idea relation fields`; purpose: Make paper value and implementation availability visible in the same record that will reach the user..
17. Coverage Subreports: output `cluster coverage, citation closure, source diversity, and recency/seminal balance subreports`; purpose: Separate coverage evidence into independent dimensions so paper count cannot masquerade as completeness..
18. Missing-Cluster Hunt and Adversarial Audit: output `missing-cluster report, coverage audit objections, adversarial challenge, and concrete loopback targets`; purpose: Actively search for what may still be missing and challenge weak stopping claims..
19. Iteration Decision and Stop Validation: output `PASS, specific loopback target, ASK_USER, or STOP_WITH_RISK decision`; purpose: Route the next loop to a concrete stage or stop only when the configured gates are satisfied..
20. Unified Final Table Generation: output `final_papers.csv and optional final_papers.xlsx with summary_zh as the final column`; purpose: Put the user's useful paper information into one primary table including abstract, citations, code, relevance, limitations, motivation, and Chinese summary..
21. Execution Ledgers and Minimal Support Outputs: output `run_ledger.jsonl, stage_ledger.csv/jsonl, agent_ledger.jsonl, query_ledger.jsonl, artifact_index.json, and concise run_summary.md`; purpose: Keep enough observability to locate subagent progress and failures without scattering noisy narrative logs..
22. Optional Monitoring Package: output `monitoring queries and update targets when monitoring is enabled`; purpose: Support future refreshes without forcing monitoring artifacts into every run..
23. Optional TODO Execution Loop: output `updated TODO queue, done TODO log, todo_state.json, and continuation decision`; purpose: Continue TODO-mode execution until no useful executable task remains and stop validation passes..

Run stages in order only when their required inputs exist. Many stages contain parallel agents. Parallelism is expected for source retrieval, citation expansion, author expansion, venue expansion, dataset/code expansion, and coverage subreports. Do not wait for a slow or failed data source before preserving successful results from other sources. Instead, record the failure and let `failure_triage_agent` decide whether retry, downgrade, or loopback is appropriate.

## State and Artifacts

All workflow outputs must stay under `workspace/work/deep-paper-search/` unless the user explicitly requests a different output location. The system has two output layers.

The primary user-facing output is `workspace/work/deep-paper-search/final/final_papers.csv`, plus `final_papers.xlsx` when spreadsheet export is enabled. This table is the place for paper title, abstract, citation count, code availability, relevance, value notes, limitations, motivation, source path, and `summary_zh` as the final column.

The execution-observability layer is mandatory because subagent mode must be debuggable. Preserve these compact ledgers by default:

- `workspace/work/deep-paper-search/ledgers/run_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/stage_ledger.csv`
- `workspace/work/deep-paper-search/ledgers/stage_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/agent_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/query_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/artifact_index.json`
- `workspace/work/deep-paper-search/ledgers/failure_ledger.jsonl`

These ledgers replace scattered progress logs. They must show which stage and agent ran, what inputs were used, what outputs were produced, whether the step passed, failed, blocked, or looped back, and where the next action is routed. Detailed agent artifacts may be written under `workspace/work/deep-paper-search/agent_artifacts/` only when they are actual handoff artifacts, not routine progress logs. The orchestrator may generate a state snapshot from ledgers and artifacts, but the snapshot is not a substitute for provenance.

## Configuration Policy

Use a calibration-first configuration policy. The user should initially provide a research goal, direction, keyword idea, or seed paper. Do not demand a complete config before any research happens. First run a lightweight calibration pass through intent decomposition, domain disambiguation, initial term generation, query compilation, query probing, and small-sample retrieval. The purpose of this pass is not to produce the final corpus. It is to test whether the direction is understandable, whether the first keywords are aligned with real scholarly vocabulary, and which candidate scope options should be confirmed by the user.

After the calibration pass, create or update `config/deep-paper-search.yaml` from `config/deep-paper-search.example.yaml`. Fill defaults wherever safe. Present the user with a compact confirmation bundle containing: interpreted direction, candidate domain, candidate keyword groups, near-scope and out-of-scope boundaries, minimum paper count, year policy, search depth, and paper artifact download policy. Ask the user to confirm or edit those fields before the full deep search. This should be one confirmation checkpoint, not repeated questioning.

The default behavior is:

- include a paper when the title, abstract, keywords, or available full text clearly match the user's direction or a discovered equivalent term;
- keep near-scope papers as signals, not as core papers;
- record whether open-source code exists, but do not clone repositories unless the user explicitly enables cloning;
- produce the unified final paper table and compact ledgers without asking the user to choose formats;
- ask before downloading PDFs, TeX sources, or other paper artifacts;
- use the minimum paper count and year policy from config as hard run constraints.

Ask the user only when the calibration pass reveals multiple plausible interpretations, missing hard lower bounds, artifact download choices, or a year policy that cannot be safely defaulted. Do not ask the user to provide obvious terms that the system can discover from papers. Do not ask the user to paste credentials, private keys, API tokens, or paid content. If access is needed, ask the user to configure the local environment and stop at the access boundary. Ask no more than three concise questions at a time.

## TODO Mode

If `execution.todo_mode` is true, the workflow enters TODO-mode execution after calibration and config confirmation. TODO mode is a goal-like execution loop, not a simple note list. The workflow must maintain `workspace/work/deep-paper-search/todo/active.todo`, `workspace/work/deep-paper-search/todo/done.todo`, `workspace/work/deep-paper-search/todo/todo_state.json`, and `workspace/work/deep-paper-search/todo/todo_log.md`. Each TODO must have an identifier, source, priority, dependency state, target stage or agent, and completion criteria. TODO status changes must also appear in `agent_ledger.jsonl` or `stage_ledger.jsonl` so progress can be inspected without opening TODO files.

TODO-mode loop:

1. `todo_planner_agent` creates the initial queue from the confirmed goal, config, and calibration evidence.
2. `todo_selector_agent` chooses the next ready and valuable TODO.
3. `todo_executor_router_agent` maps that TODO to an existing stage or agent and defines the expected artifact.
4. The target stage or agent executes the work.
5. `todo_completion_verifier_agent` checks whether completion evidence exists before the TODO is removed from `active.todo`.
6. `todo_continuation_auditor_agent` decides whether gaps, failures, weak coverage, or adversarial findings justify new TODOs.

The workflow may stop in TODO mode only when the active queue is empty, the continuation auditor returns `NO_NEW_TODO`, and stop-condition validation passes. Repeated, duplicate, or low-value tasks should be merged, rejected, or converted into residual risk rather than appended forever.

## Loopback Policy

Every loopback must name a specific target stage or agent. Never say only "search more." Use the evidence to choose a route:

- Terminology gap: return to query generation or paper-driven terminology extraction.
- Query drift or high noise: return to query probing and mutation.
- Weak source diversity: return to parallel source discovery.
- Missing references or citation closure failure: return to citation expansion.
- Strong author or lab signals: return to author and lab deep search.
- Weak venue or workshop coverage: return to venue and community expansion.
- Dataset, benchmark, code, or leaderboard signals: return to dataset and code expansion.
- Standards or engineering vocabulary mismatch: return to standard and patent terminology expansion.
- Metadata conflict: return to normalization and identity resolution.
- Relevance ambiguity: return to screening and near-miss mining.
- Coverage score unsupported: return to the subreport that lacks evidence.

## Stopping Policy

The workflow may stop only when the depth contract is satisfied, coverage score meets the configured threshold, the coverage auditor has no high or critical objections, the adversarial reviewer has no unresolved strong missed-literature argument, and the stop-condition validator confirms the hard gates. If budget is exhausted first, stop with `STOP_WITH_RISK` and write residual risks. Never stop because the number of papers is large, because one source has no new results, because the keyword list is long, or because a single scoring agent says the result is good.

## Output Package

The default final package is intentionally compact:

- `workspace/work/deep-paper-search/final/final_papers.csv`: required primary table.
- `workspace/work/deep-paper-search/final/final_papers.xlsx`: optional spreadsheet mirror when enabled.
- `workspace/work/deep-paper-search/final/run_summary.md`: concise human-readable summary of status, coverage, residual risks, and next actions.
- `workspace/work/deep-paper-search/support/search_protocol.md`: concise reproducibility record derived from `query_ledger.jsonl` and stage decisions.
- `workspace/work/deep-paper-search/support/coverage_report.md`: compact coverage and adversarial-audit report when coverage artifacts exist.
- `workspace/work/deep-paper-search/support/gap_report.md`: compact gap notes when gap artifacts exist.
- Mandatory ledgers under `workspace/work/deep-paper-search/ledgers/` as listed above.

The final table must include at least these columns, with `summary_zh` last: `paper_id`, `title`, `authors`, `year`, `venue`, `publication_type`, `doi`, `arxiv_id`, `paper_url`, `abstract`, `abstract_source`, `citation_count`, `citation_source`, `code_available`, `code_url`, `code_evidence`, `relevance_label`, `relevance_score`, `reference_value_score`, `idea_relation`, `quality_notes`, `limitations`, `motivation`, `source_query`, `discovery_path`, `summary_zh`. The Chinese-language summary must describe what the paper does, how closely it matches the user's direction or idea, its motivation, limitations, whether it collides with or supports the user's idea when an idea was provided, and what inspiration it gives.

Verbose per-agent reports, raw dumps, large debug graphs, and extra exports such as BibTeX or JSON should be written only when config enables `outputs.debug_artifacts` or the user requests them. If a required output cannot be produced, the run summary must say exactly which upstream artifact is missing and whether the absence affects correctness or only convenience.

## Execution Rule

When launching from this file, first inspect whether `.codex/agents/` and `prompts/` contain the generated Deep Paper Search assets. If not, run the plugin installer or ask the user to install the assets. Then begin at Stage 1 and proceed through the stage protocol. Use subagents for bounded, independent tasks, especially source-specific retrieval, frontier expansion, and independent audit subreports. Keep integration, loopback decisions, and final stopping local to the orchestrator so the workflow remains coherent.
