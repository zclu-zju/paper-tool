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

1. Run Initialization: output `run plan and initial state`; purpose: Create a traceable task boundary..
2. Intent Decomposition: output `intent frame`; purpose: Turn natural language into searchable fields..
3. Domain Disambiguation: output `domain decision and assumptions`; purpose: Prevent cross-domain false retrieval..
4. Concept Definition: output `concept table`; purpose: Create relevance standards for later screening..
5. Scope Contract: output `scope contract and depth contract`; purpose: Define inclusion, exclusion, and stopping thresholds..
6. Initial Term Generation: output `seed terms and alias map`; purpose: Create the first retrieval entry points..
7. Initial Query Compilation: output `source-specific queries`; purpose: Make queries executable..
8. Query Probing: output `probe report and keyword gap report`; purpose: Detect bad queries before large-scale retrieval..
9. Query Revision: output `revised queries`; purpose: Repair the retrieval entry points using evidence..
10. Parallel Database Retrieval: output `raw records`; purpose: Reduce source bias through parallel retrieval..
11. Full Text Location: output `full text links`; purpose: Prepare materials for term and reference mining..
12. Full Text Parsing: output `parsed text, references, and signals`; purpose: Recover terminology beyond abstracts..
13. Metadata Normalization: output `canonical candidates`; purpose: Make multi-source data mergeable..
14. Identity Resolution: output `author map and venue map`; purpose: Prevent author and venue expansion errors..
15. Version Linking and Deduplication: output `deduplicated corpus and version graph`; purpose: Merge duplicates while preserving version relationships..
16. Initial Relevance Screening: output `in-scope, near-scope, and out-of-scope records`; purpose: Separate core papers from noise..
17. Near-Miss Mining: output `near-miss signals`; purpose: Find hidden entry points in boundary papers..
18. Observed Term Extraction: output `observed terms`; purpose: Use papers to revise the search language..
19. Term Graph and Drift Analysis: output `term graph and drift report`; purpose: Discover cross-community and cross-period terminology..
20. Taxonomy Modeling: output `taxonomies and setting table`; purpose: Measure coverage by dimensions, not by count..
21. Seed Paper Selection: output `seed papers and frontier budgets`; purpose: Choose representative seeds for multi-path expansion..
22. Citation Expansion: output `citation frontiers`; purpose: Find papers that keyword search misses..
23. Author and Institution Expansion: output `author and lab frontiers`; purpose: Find same-team work that uses different terminology..
24. Venue Expansion: output `venue frontiers`; purpose: Find community papers not reached by keywords..
25. Dataset and Code Expansion: output `dataset and code frontiers`; purpose: Find papers with the same task but different wording..
26. Standards and Engineering Vocabulary Expansion: output `standards frontier`; purpose: Add engineering aliases and application vocabulary..
27. Expansion Result Merge: output `updated corpus`; purpose: Integrate multi-path discoveries into one corpus..
28. Deep Screening and Validity Check: output `validated corpus`; purpose: Remove noise and invalid papers..
29. Evidence Graph Construction: output `evidence graph`; purpose: Provide structure for coverage audit..
30. Coverage Analysis: output `coverage subreports`; purpose: Compute independent coverage signals..
31. Missing Cluster Search: output `missing cluster report`; purpose: Actively search for what has not been found..
32. Coverage Scoring and Audit: output `coverage score and audit report`; purpose: Prevent inflated self-assessment..
33. Adversarial Challenge and Iteration Decision: output `next action`; purpose: Route the workflow back to the right flow or stop..
34. Output and Monitoring: output `final packages`; purpose: Produce reusable, reproducible, and monitorable outputs..
35. TODO Execution Loop: output `updated TODO queue, done TODO log, and continuation decision`; purpose: Continue TODO-mode execution until no useful executable task remains..

Run stages in order only when their required inputs exist. Many stages contain parallel agents. Parallelism is expected for source retrieval, citation expansion, author expansion, venue expansion, dataset/code expansion, and coverage subreports. Do not wait for a slow or failed data source before preserving successful results from other sources. Instead, record the failure and let `failure_triage_agent` decide whether retry, downgrade, or loopback is appropriate.

## State and Artifacts

All workflow outputs must stay under `workspace/work/deep-paper-search/` unless the user explicitly requests a different output location. The event log is the durable history. Agents must not silently overwrite each other. Every artifact must include status, inputs used, evidence, structured output, quality checks, and handoff lines. The orchestrator may generate a state snapshot from those artifacts, but the snapshot is not a substitute for provenance.

## Configuration Policy

Use a calibration-first configuration policy. The user should initially provide a research goal, direction, keyword idea, or seed paper. Do not demand a complete config before any research happens. First run a lightweight calibration pass through intent decomposition, domain disambiguation, initial term generation, query compilation, query probing, and small-sample retrieval. The purpose of this pass is not to produce the final corpus. It is to test whether the direction is understandable, whether the first keywords are aligned with real scholarly vocabulary, and which candidate scope options should be confirmed by the user.

After the calibration pass, create or update `config/deep-paper-search.yaml` from `config/deep-paper-search.example.yaml`. Fill defaults wherever safe. Present the user with a compact confirmation bundle containing: interpreted direction, candidate domain, candidate keyword groups, near-scope and out-of-scope boundaries, minimum paper count, year policy, search depth, and paper artifact download policy. Ask the user to confirm or edit those fields before the full deep search. This should be one confirmation checkpoint, not repeated questioning.

The default behavior is:

- include a paper when the title, abstract, keywords, or available full text clearly match the user's direction or a discovered equivalent term;
- keep near-scope papers as signals, not as core papers;
- record whether open-source code exists, but do not clone repositories unless the user explicitly enables cloning;
- produce the standard output package without asking the user to choose formats;
- ask before downloading PDFs, TeX sources, or other paper artifacts;
- use the minimum paper count and year policy from config as hard run constraints.

Ask the user only when the calibration pass reveals multiple plausible interpretations, missing hard lower bounds, artifact download choices, or a year policy that cannot be safely defaulted. Do not ask the user to provide obvious terms that the system can discover from papers. Do not ask the user to paste credentials, private keys, API tokens, or paid content. If access is needed, ask the user to configure the local environment and stop at the access boundary. Ask no more than three concise questions at a time.

## TODO Mode

If `execution.todo_mode` is true, the workflow enters TODO-mode execution after calibration and config confirmation. TODO mode is a goal-like execution loop, not a simple note list. The workflow must maintain `workspace/work/deep-paper-search/todo/active.todo`, `done.todo`, `todo_state.json`, and `todo_log.md`. Each TODO must have an identifier, source, priority, dependency state, target stage or agent, and completion criteria.

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

The final package should include `corpus.csv`, `corpus.bib`, `corpus.json`, `versions.json`, `excluded.csv`, `near_miss.csv`, `search_protocol.md`, `coverage_report.md`, `evidence_graph.json`, `gap_report.md`, and `monitoring_config.yaml` when the required upstream artifacts exist. If a file cannot be produced, the final report must say exactly which upstream artifact is missing and whether the absence affects correctness or only convenience.

## Execution Rule

When launching from this file, first inspect whether `.codex/agents/` and `prompts/` contain the generated Deep Paper Search assets. If not, run the plugin installer or ask the user to install the assets. Then begin at Stage 1 and proceed through the stage protocol. Use subagents for bounded, independent tasks, especially source-specific retrieval, frontier expansion, and independent audit subreports. Keep integration, loopback decisions, and final stopping local to the orchestrator so the workflow remains coherent.
