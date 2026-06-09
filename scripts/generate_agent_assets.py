#!/usr/bin/env python3
"""Generate deep-paper-search Codex agent TOML files and prompt assets.

The source of truth is deep-paper-search-agent-system-design.md. This script
parses the agent tables, stage table, and writes project-local custom agents,
prompt files, plugin assets, marketplace metadata, and a launcher prompt.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "deep-paper-search-agent-system-design.md"
PROJECT_PROMPTS = ROOT / "prompts"
PROJECT_AGENTS = ROOT / ".codex" / "agents"
CODEX_DIR = ROOT / ".codex"
PLUGIN_ROOT = ROOT / "plugins" / "deep-paper-search"
PLUGIN_AGENTS = PLUGIN_ROOT / "assets" / "agents"
PLUGIN_PROJECT_PROMPTS = PLUGIN_ROOT / "assets" / "prompts" / "project"
PLUGIN_CODEX_PROMPTS = PLUGIN_ROOT / "assets" / "prompts" / "codex"
PLUGIN_SKILL = PLUGIN_ROOT / "skills" / "deep-paper-search"
PLUGIN_SCRIPT = PLUGIN_ROOT / "scripts"
AGENT_MANIFEST = PLUGIN_ROOT / "assets" / "agent_manifest.json"
LAUNCHER_NAME = "deep-paper-search-workflow-prompt.md"


@dataclass
class Stage:
    number: int
    name: str
    agents_text: str
    input_text: str
    output_text: str
    meaning: str


@dataclass
class Agent:
    number: int
    snake: str
    kebab: str
    title: str
    phase_heading: str
    phase_slug: str
    responsibility: str
    output: str
    failure_mode: str
    stages: list[Stage] = field(default_factory=list)


PHASE_PACKS = {
    "orchestration_state_reproducibility": {
        "mission": "coordinate execution, preserve state integrity, and make every later research claim traceable to the exact event that created it",
        "inputs": "user requests, prior state snapshots, event logs, budget records, stage outputs, retry requests, and audit decisions",
        "methods": [
            "treat the append-only event log as the only durable history and never silently replace it",
            "separate orchestration decisions from domain claims so reviewers can see which agent made which assertion",
            "allocate budgets by frontier value, uncertainty, and expected marginal gain instead of equal splitting",
            "mark tool failure, empty result, ambiguous scope, and low-yield expansion as different operational states",
            "write clear recovery actions that can be executed without rereading the whole conversation",
        ],
        "handoffs": "downstream agents consume the run plan, state snapshot, budget allocation, provenance graph, and recovery actions",
    },
    "intent_definition_boundaries": {
        "mission": "turn an underspecified user idea into a searchable, auditable scope contract without pretending that early assumptions are facts",
        "inputs": "the user request, conversation context, possible seed papers, domain hints, constraints, examples, and any stated exclusions",
        "methods": [
            "decompose the request into domain, task, object, method, setting, metric, and desired depth",
            "identify words whose meaning changes across fields and record the chosen interpretation",
            "define concepts operationally so later screeners know what evidence makes a paper in scope",
            "separate in-scope, near-scope, out-of-scope, unresolved ambiguity, and provisional assumption",
            "ask for user input only when the ambiguity changes the search boundary and cannot be resolved from evidence",
        ],
        "handoffs": "query builders, screeners, and auditors consume the intent frame, concept table, scope contract, depth contract, and assumption ledger",
    },
    "terminology_keywords_queries": {
        "mission": "create, test, repair, and audit the query language that opens the search space without letting initial wording become a hard boundary",
        "inputs": "intent frame, scope contract, seed terms, aliases, controlled vocabularies, observed paper terms, failed queries, and query probe samples",
        "methods": [
            "distinguish user wording, translated wording, controlled vocabulary terms, and observed paper vocabulary",
            "compile database-specific Boolean queries separately from semantic search prompts",
            "use negative terms only when they remove demonstrable noise without cutting valid near-scope bridges",
            "probe queries before spending large budgets and record precision, drift, and missing-term signals",
            "mutate queries from evidence gathered in papers, term graphs, and adversarial audits",
        ],
        "handoffs": "source search agents consume source-specific queries; coverage agents consume query gaps, rejected terms, and probe evidence",
    },
    "data_source_retrieval": {
        "mission": "retrieve candidate papers from complementary scholarly data sources while preserving source-specific provenance and failure details",
        "inputs": "compiled queries, source budgets, source credentials or access limits, prior source failures, and requested recency or venue constraints",
        "methods": [
            "run only the source assigned to this agent and do not merge or screen results beyond lightweight source hygiene",
            "record every query string, source endpoint, timestamp, result count, pagination boundary, and failure",
            "prefer structured scholarly metadata over web snippets when both are available",
            "return abstracts, citation counts, identifiers, venues, URLs, and source ranking signals when available",
            "distinguish no result, rate limit, permission failure, malformed query, and unavailable metadata",
        ],
        "handoffs": "canonicalization, source diversity, citation expansion, and provenance agents consume raw result batches with complete source evidence",
    },
    "full_text_content": {
        "mission": "obtain and parse legally accessible full-text signals so the system can learn terms, references, datasets, and metrics that abstracts omit",
        "inputs": "candidate paper records, URLs, DOI/arXiv identifiers, open-access links, author pages, PDF files, HTML pages, and parsed metadata",
        "methods": [
            "look for open, legitimate copies and do not bypass access controls or fabricate unavailable text",
            "separate full text, abstract-only text, reference list, figure caption, table caption, appendix, and supplementary material",
            "preserve page, section, figure, and table provenance when extracting terms or references",
            "record parsing confidence and extraction gaps instead of pretending a malformed PDF was fully read",
            "feed extracted references and experiment signals back into frontier expansion and taxonomy agents",
        ],
        "handoffs": "term extraction, reference parsing, dataset extraction, experimental setting, and evidence graph agents consume parsed text and signal records",
    },
    "expansion_frontiers": {
        "mission": "expand beyond keyword search through independent discovery frontiers that reveal papers hidden by terminology mismatch",
        "inputs": "seed papers, validated corpus, authors, labs, venues, workshops, datasets, benchmarks, code repositories, standards, patents, and evidence graph gaps",
        "methods": [
            "expand only from validated seeds or clearly labeled near-scope bridge records",
            "record why each frontier was opened and what marginal discovery it is expected to provide",
            "return candidate records with the expansion path, not just titles",
            "avoid uncontrolled drift by sending every expansion result back through relevance screening",
            "close a frontier only when its yield, closure evidence, or budget rationale is documented",
        ],
        "handoffs": "deduplication, relevance screening, taxonomy, coverage, and iteration decision agents consume frontier records and marginal-yield evidence",
    },
    "normalization_dedup_identity": {
        "mission": "turn noisy multi-source records into stable paper, author, venue, and version identities without destroying meaningful distinctions",
        "inputs": "raw records, parsed metadata, DOI/arXiv IDs, author strings, venue strings, publication versions, source conflicts, and validity warnings",
        "methods": [
            "normalize aggressively enough to merge duplicates but conservatively enough to preserve version relationships",
            "separate identity resolution from relevance decisions",
            "resolve conflicts with evidence rankings rather than first-seen preference",
            "mark uncertain merges for review instead of silently collapsing them",
            "record every canonicalization, merge, split, and conflict resolution as auditable data",
        ],
        "handoffs": "screening, author expansion, venue expansion, citation graph, and final export agents consume canonical records, identity maps, and version graphs",
    },
    "screening_taxonomy_evidence": {
        "mission": "decide what the corpus actually contains, why papers are included or excluded, and how evidence is organized for coverage analysis",
        "inputs": "canonical papers, scope contract, parsed text, near-miss records, exclusion candidates, terms, datasets, settings, and citation edges",
        "methods": [
            "screen papers against the scope contract rather than against the original keyword list",
            "preserve near-miss papers as expansion evidence even when they are not included in the core corpus",
            "extract tasks, methods, datasets, metrics, and settings as separate dimensions",
            "write exclusion reasons that another agent can audit",
            "build evidence graph nodes and edges that support coverage scoring and missing-cluster discovery",
        ],
        "handoffs": "coverage, adversarial review, final report, gap report, and monitoring agents consume relevance decisions, taxonomies, settings, exclusions, and graph edges",
    },
    "coverage_audit_adversarial": {
        "mission": "prove whether the search is broad enough, identify what may still be missing, and prevent premature stopping",
        "inputs": "evidence graph, coverage subreports, citation closure data, source diversity data, taxonomies, exclusions, near-miss signals, budget records, and iteration history",
        "methods": [
            "score coverage from independent evidence channels rather than paper count",
            "challenge any high score that lacks concrete supporting records",
            "look for missing clusters, weak links, isolated communities, time gaps, and single-source bias",
            "translate each serious weakness into a specific loopback target instead of recommending vague additional search",
            "approve stopping only when the depth contract, hard gates, adversarial challenge, and residual-risk statement are aligned",
        ],
        "handoffs": "the orchestrator consumes PASS, loopback, ASK_USER, or STOP_WITH_RISK decisions with the evidence needed to execute them",
    },
    "output_monitoring": {
        "mission": "package the research result into reusable artifacts and set up monitoring without hiding uncertainty or provenance",
        "inputs": "final state, canonical corpus, version graph, exclusions, near-miss table, search protocol, coverage evidence, gap analysis, and monitoring frontiers",
        "methods": [
            "export machine-readable files and human-readable reports from the same state snapshot",
            "include provenance, query history, inclusion and exclusion rules, coverage evidence, and residual risks",
            "make monitoring queries specific enough to catch new papers without recreating the whole workflow",
            "never convert weak coverage into confident prose",
            "verify that final paths, columns, identifiers, and version relationships are present before declaring completion",
        ],
        "handoffs": "users, future workflow runs, and monitoring tasks consume the exported corpus, reports, graph, and alert configuration",
    },
}


PHASE_DISPLAY_NAMES = {
    "orchestration_state_reproducibility": "4.1 Orchestration, State, and Reproducibility",
    "intent_definition_boundaries": "4.2 Intent, Definition, and Boundaries",
    "terminology_keywords_queries": "4.3 Terminology, Keywords, and Queries",
    "data_source_retrieval": "4.4 Data Source Retrieval",
    "full_text_content": "4.5 Full Text and Content Acquisition",
    "expansion_frontiers": "4.6 Expansion Frontiers",
    "normalization_dedup_identity": "4.7 Normalization, Deduplication, and Identity Resolution",
    "screening_taxonomy_evidence": "4.8 Screening, Taxonomy, and Evidence Modeling",
    "coverage_audit_adversarial": "4.9 Coverage Audit and Adversarial Review",
    "output_monitoring": "4.10 Output and Monitoring",
}


AGENT_ENGLISH = {
    "run_orchestrator_agent": {
        "responsibility": "Execute the global workflow DAG, launch parallel tasks, advance loop decisions, and keep stage execution coherent.",
        "output": "run plan and stage status",
        "failure_mode": "Parallel discovery branches may be skipped, duplicated, or integrated in the wrong order.",
    },
    "state_reducer_agent": {
        "responsibility": "Reduce append-only agent events into the current canonical Research State and expose state diffs between iterations.",
        "output": "state snapshot and state diff",
        "failure_mode": "Parallel agents may mutate conflicting state or hide the history behind a decision.",
    },
    "provenance_trace_agent": {
        "responsibility": "Record the source chain for papers, terms, scores, exclusions, frontier decisions, and final claims.",
        "output": "provenance graph",
        "failure_mode": "The workflow may produce claims that cannot be reproduced or audited.",
    },
    "frontier_budget_allocator_agent": {
        "responsibility": "Allocate time, API, download, and model budgets across keyword, citation, author, venue, dataset, code, and standards frontiers.",
        "output": "frontier budget plan",
        "failure_mode": "One attractive frontier may consume the budget while more valuable discovery paths remain unexplored.",
    },
    "failure_triage_agent": {
        "responsibility": "Classify API failures, malformed queries, access denials, empty results, parse failures, and low-yield searches into actionable recovery states.",
        "output": "recovery action",
        "failure_mode": "Tool or access failures may be mistaken for evidence that no relevant literature exists.",
    },
    "intent_decomposition_agent": {
        "responsibility": "Decompose the user request into domain, task, object, method, setting, metric, constraints, and requested depth.",
        "output": "intent frame",
        "failure_mode": "The initial request may be treated as a single keyword instead of a structured research intent.",
    },
    "domain_disambiguation_agent": {
        "responsibility": "Disambiguate terms whose meaning changes across fields and select the domain interpretation supported by the request and evidence.",
        "output": "domain decision",
        "failure_mode": "The search may drift into a different discipline with similar vocabulary.",
    },
    "concept_definition_agent": {
        "responsibility": "Create operational definitions for core concepts and specify what evidence makes a paper relevant to each concept.",
        "output": "concept definition table",
        "failure_mode": "Screening agents may have no stable standard for relevance decisions.",
    },
    "scope_boundary_agent": {
        "responsibility": "Define in-scope, near-scope, out-of-scope, and unresolved boundary cases for the research task.",
        "output": "scope contract",
        "failure_mode": "Expansion agents may drift indefinitely or exclude useful bridge papers without explanation.",
    },
    "depth_contract_agent": {
        "responsibility": "Translate the user's need into search depth, coverage thresholds, stopping gates, and acceptable residual risk.",
        "output": "depth contract",
        "failure_mode": "A quick exploratory task and a near-exhaustive survey may be run with the same stopping criteria.",
    },
    "assumption_registry_agent": {
        "responsibility": "Record provisional assumptions, their evidence status, and the condition that would confirm, revise, or invalidate them.",
        "output": "assumption ledger",
        "failure_mode": "Early guesses may silently control the workflow as if they were verified facts.",
    },
    "seed_keyword_agent": {
        "responsibility": "Generate the first search entry terms from the intent frame without treating them as final boundaries.",
        "output": "seed term set",
        "failure_mode": "The workflow may lack an initial retrieval path into the literature.",
    },
    "translation_alias_agent": {
        "responsibility": "Map multilingual terms, abbreviations, expansions, aliases, and common mistranslations into searchable variants.",
        "output": "alias map",
        "failure_mode": "Literal translation from the user language may miss the vocabulary used by the target community.",
    },
    "controlled_vocabulary_agent": {
        "responsibility": "Compare the task with controlled vocabularies, taxonomies, and database indexing terms relevant to the domain.",
        "output": "controlled term candidates",
        "failure_mode": "The workflow may ignore terms used by scholarly databases to index the target topic.",
    },
    "paper_term_extractor_agent": {
        "responsibility": "Extract observed terminology from real paper titles, abstracts, keywords, introductions, captions, and parsed sections.",
        "output": "observed term set",
        "failure_mode": "The system may rely on invented or user-supplied terms rather than field vocabulary.",
    },
    "term_canonicalization_agent": {
        "responsibility": "Merge aliases, abbreviations, spelling variants, inflections, and capitalization variants into canonical term records.",
        "output": "canonical term table",
        "failure_mode": "The same concept may be counted as multiple unrelated research directions.",
    },
    "term_cooccurrence_graph_agent": {
        "responsibility": "Build a term co-occurrence graph to identify bridge terms, hidden connections, and community-specific neighborhoods.",
        "output": "term graph",
        "failure_mode": "The workflow may miss bridge vocabulary connecting two relevant paper communities.",
    },
    "terminology_drift_agent": {
        "responsibility": "Analyze how terminology varies across years, venues, and communities and identify old and new names for the same idea.",
        "output": "terminology drift report",
        "failure_mode": "The workflow may cover only one time period because it searches only contemporary or legacy terms.",
    },
    "negative_query_agent": {
        "responsibility": "Generate exclusion terms and noise patterns that reduce off-topic results without blocking valid near-scope bridges.",
        "output": "negative query rules",
        "failure_mode": "Search results may be overwhelmed by adjacent disciplines or unrelated senses of shared terms.",
    },
    "query_mutation_agent": {
        "responsibility": "Create query variants from aliases, term graph evidence, failed probes, near-miss signals, and audit feedback.",
        "output": "mutated query set",
        "failure_mode": "The search may stall after the first query set fails or returns biased results.",
    },
    "boolean_query_compiler_agent": {
        "responsibility": "Compile source-specific Boolean queries with correct operators, field selectors, nesting, and exclusions.",
        "output": "source-specific Boolean queries",
        "failure_mode": "Valid concepts may fail because the query syntax is illegal or poorly adapted to a database.",
    },
    "semantic_query_compiler_agent": {
        "responsibility": "Compile natural-language semantic search prompts that express the concept without depending on exact keyword matches.",
        "output": "semantic query set",
        "failure_mode": "Papers using different wording may be missed by keyword-only retrieval.",
    },
    "query_probe_agent": {
        "responsibility": "Run or evaluate small probe result sets to estimate query precision, drift, missing terms, and expected yield.",
        "output": "query probe report",
        "failure_mode": "Large retrieval budgets may be spent on noisy or misdirected queries.",
    },
    "keyword_gap_auditor_agent": {
        "responsibility": "Audit whether query terms cover tasks, methods, datasets, metrics, settings, applications, and community language.",
        "output": "keyword gap report",
        "failure_mode": "Keyword coverage may appear broad while important dimensions remain absent.",
    },
    "semantic_scholar_search_agent": {
        "responsibility": "Retrieve candidates, citation links, and similar papers from Semantic Scholar using the assigned queries.",
        "output": "Semantic Scholar result batch",
        "failure_mode": "The workflow may lack an accessible citation-aware and semantic retrieval source.",
    },
    "openalex_search_agent": {
        "responsibility": "Retrieve works, concepts, institutions, venues, and citation metadata from OpenAlex.",
        "output": "OpenAlex result batch",
        "failure_mode": "The workflow may overdepend on a single commercial or closed scholarly index.",
    },
    "crossref_metadata_agent": {
        "responsibility": "Retrieve DOI, publisher, journal, issue, and publication version metadata from Crossref.",
        "output": "Crossref metadata batch",
        "failure_mode": "Canonical publication metadata and DOI relationships may remain incomplete.",
    },
    "arxiv_search_agent": {
        "responsibility": "Retrieve preprints and recent unpublished or not-yet-indexed work from arXiv.",
        "output": "arXiv result batch",
        "failure_mode": "Recent work may be missed before it appears in formal publication databases.",
    },
    "dblp_search_agent": {
        "responsibility": "Retrieve computer science conference, journal, venue, and author records from DBLP.",
        "output": "DBLP result batch",
        "failure_mode": "Computer science venue metadata and author publication histories may be incomplete.",
    },
    "ieee_xplore_search_agent": {
        "responsibility": "Retrieve communications, signal processing, hardware, and engineering papers from IEEE Xplore when access allows.",
        "output": "IEEE Xplore result batch",
        "failure_mode": "Engineering-heavy topics may miss papers published in the dominant IEEE venues.",
    },
    "acm_dl_search_agent": {
        "responsibility": "Retrieve computing systems, networks, databases, HCI, and software papers from the ACM Digital Library when access allows.",
        "output": "ACM Digital Library result batch",
        "failure_mode": "ACM community papers may be underrepresented or absent.",
    },
    "domain_specific_database_agent": {
        "responsibility": "Select and query domain-specific databases such as PubMed, ACL Anthology, INSPIRE, SSRN, or other field repositories.",
        "output": "domain database result batch",
        "failure_mode": "General-purpose indexes may fail to cover the target discipline's primary archive.",
    },
    "scholarly_web_fallback_agent": {
        "responsibility": "Search scholarly web pages, project pages, lab pages, and course bibliographies when APIs or indexes are insufficient.",
        "output": "scholarly web result batch",
        "failure_mode": "Relevant work not well indexed by APIs may remain invisible.",
    },
    "full_text_locator_agent": {
        "responsibility": "Locate legally accessible PDF, HTML, open-access, preprint, and author-hosted versions of candidate papers.",
        "output": "full text link set",
        "failure_mode": "The workflow may be limited to titles and abstracts and fail to mine deeper terminology or references.",
    },
    "pdf_parse_agent": {
        "responsibility": "Parse accessible PDF or full-text files into sections, metadata, references, tables, figures, and text spans with confidence notes.",
        "output": "parsed paper text",
        "failure_mode": "Full-text information may be unavailable to downstream term, citation, and experiment extractors.",
    },
    "reference_section_parser_agent": {
        "responsibility": "Parse reference lists from full text and recover cited works not exposed through APIs.",
        "output": "parsed reference records",
        "failure_mode": "Key older or poorly indexed cited works may be absent from the citation frontier.",
    },
    "figure_table_signal_agent": {
        "responsibility": "Extract method, dataset, metric, baseline, and experimental clues from figure captions, table captions, and table headers.",
        "output": "figure and table signal records",
        "failure_mode": "Important experimental terminology may be missed because it appears only in figures or tables.",
    },
    "backward_citation_agent": {
        "responsibility": "Expand from seed papers to their references to recover foundational and prerequisite work.",
        "output": "backward citation frontier",
        "failure_mode": "The corpus may omit early foundations behind the visible seed papers.",
    },
    "forward_citation_agent": {
        "responsibility": "Expand from seed papers to later works that cite them.",
        "output": "forward citation frontier",
        "failure_mode": "The corpus may omit later improvements, replications, and recent branches.",
    },
    "co_citation_agent": {
        "responsibility": "Find papers that are frequently co-cited with seed papers to reveal the same knowledge cluster.",
        "output": "co-citation frontier",
        "failure_mode": "Relevant papers in the same intellectual cluster may be missed if they do not directly cite the seed.",
    },
    "bibliographic_coupling_agent": {
        "responsibility": "Find papers that cite many of the same references as the seed papers.",
        "output": "bibliographic coupling frontier",
        "failure_mode": "Parallel work with shared foundations but no direct citation edge may be missed.",
    },
    "author_profile_agent": {
        "responsibility": "Resolve core authors and retrieve their topic-relevant papers across aliases, profiles, and publication records.",
        "output": "author frontier",
        "failure_mode": "Papers by the same researchers using different terminology or venues may be missed.",
    },
    "lab_institution_agent": {
        "responsibility": "Search laboratory, group, institution, and project pages for related papers and project lines.",
        "output": "lab and institution frontier",
        "failure_mode": "Series work not fully indexed by scholarly databases may remain undiscovered.",
    },
    "venue_track_agent": {
        "responsibility": "Expand through core venues, tracks, sessions, and journal issue structures related to the topic.",
        "output": "venue frontier",
        "failure_mode": "Community papers using different wording may be missed by term-based search.",
    },
    "workshop_special_issue_agent": {
        "responsibility": "Search workshops, special issues, challenges, and early community gatherings connected to the topic.",
        "output": "workshop and special issue frontier",
        "failure_mode": "Emerging subfields may be missed because they first appear in workshops or special issues.",
    },
    "dataset_benchmark_agent": {
        "responsibility": "Expand through datasets, simulation platforms, benchmarks, and experimental resources used by seed papers.",
        "output": "dataset and benchmark frontier",
        "failure_mode": "Papers solving the same task with different terminology may be missed.",
    },
    "code_repository_agent": {
        "responsibility": "Mine code repositories, README files, releases, model zoos, and paper-code indexes for paper links and related work.",
        "output": "code repository frontier",
        "failure_mode": "Implementation-centric papers may be missed when repository ecosystems expose them before indexes do.",
    },
    "leaderboard_challenge_agent": {
        "responsibility": "Search leaderboards, competitions, and challenge pages for papers tied to shared evaluation tasks.",
        "output": "leaderboard and challenge frontier",
        "failure_mode": "Benchmark community papers may be missed even when they share the same evaluation target.",
    },
    "standard_patent_agent": {
        "responsibility": "Search standards, patents, white papers, and engineering documents for aliases, application terms, and system vocabulary.",
        "output": "standards and patents frontier",
        "failure_mode": "Engineering terminology may remain disconnected from scholarly terminology.",
    },
    "metadata_canonicalization_agent": {
        "responsibility": "Normalize titles, authors, years, venues, identifiers, URLs, and source-specific metadata into canonical record candidates.",
        "output": "canonical record candidates",
        "failure_mode": "Noisy multi-source metadata may prevent reliable merging, screening, and graph construction.",
    },
    "author_identity_resolution_agent": {
        "responsibility": "Merge aliases for the same author and distinguish same-name authors using ORCID, DBLP, OpenAlex, affiliations, and coauthors.",
        "output": "author identity map",
        "failure_mode": "Author expansion may include unrelated papers by a different person with the same name.",
    },
    "venue_identity_resolution_agent": {
        "responsibility": "Normalize venue abbreviations, full names, subvenues, workshops, tracks, and issue naming variants.",
        "output": "venue identity map",
        "failure_mode": "Venue expansion may miss relevant papers or merge distinct venues incorrectly.",
    },
    "version_linking_agent": {
        "responsibility": "Link arXiv, workshop, conference, journal extension, technical report, and revised versions of the same work.",
        "output": "version graph",
        "failure_mode": "The workflow may duplicate the same paper or discard meaningful extended versions.",
    },
    "deduplication_agent": {
        "responsibility": "Merge duplicate records using identifiers, normalized titles, author overlap, year proximity, venues, and embedding similarity.",
        "output": "deduplicated corpus",
        "failure_mode": "The same paper may be counted multiple times or fragmented across sources.",
    },
    "metadata_conflict_resolver_agent": {
        "responsibility": "Resolve conflicts in year, venue, author order, title variants, identifiers, and publication status using ranked evidence.",
        "output": "metadata conflict resolution log",
        "failure_mode": "Incorrect metadata may contaminate citation graphs, exports, and coverage analysis.",
    },
    "retraction_errata_agent": {
        "responsibility": "Check for retractions, errata, expressions of concern, version warnings, and other validity flags.",
        "output": "validity flags",
        "failure_mode": "Invalid or corrected papers may be treated as reliable core evidence.",
    },
    "relevance_screening_agent": {
        "responsibility": "Classify canonical papers as in scope, near scope, out of scope, unknown, or not applicable using the scope contract.",
        "output": "relevance decisions",
        "failure_mode": "Noise papers may enter the core corpus or valid papers may be excluded without a standard.",
    },
    "near_miss_mining_agent": {
        "responsibility": "Extract useful terms, references, datasets, authors, and venues from near-scope papers while keeping them outside the core corpus.",
        "output": "near-miss signals",
        "failure_mode": "Boundary papers may be discarded even though they reveal hidden search paths.",
    },
    "exclusion_reason_agent": {
        "responsibility": "Write structured, auditable exclusion reasons for out-of-scope papers and rejected records.",
        "output": "exclusion ledger",
        "failure_mode": "Exclusions may be impossible to review, reproduce, or challenge.",
    },
    "task_taxonomy_agent": {
        "responsibility": "Group papers by task definition, problem setting, input-output structure, and target objective.",
        "output": "task taxonomy",
        "failure_mode": "Different tasks may be conflated into one undifferentiated paper set.",
    },
    "method_taxonomy_agent": {
        "responsibility": "Group papers by technical route, model family, theoretical assumption, optimization strategy, or algorithmic mechanism.",
        "output": "method taxonomy",
        "failure_mode": "Coverage of major method families may be unclear or falsely assumed.",
    },
    "dataset_metric_extraction_agent": {
        "responsibility": "Extract datasets, simulators, benchmarks, metrics, baselines, and evaluation protocols from candidate papers.",
        "output": "dataset and metric table",
        "failure_mode": "The experimental context may be missing from taxonomy and coverage decisions.",
    },
    "experimental_setting_agent": {
        "responsibility": "Extract system and experiment settings such as channel model, frequency band, antennas, subcarriers, training regime, hardware, or domain-specific conditions.",
        "output": "experimental setting table",
        "failure_mode": "Papers may look relevant while using incompatible experimental conditions.",
    },
    "evidence_graph_agent": {
        "responsibility": "Build a heterogeneous graph connecting papers, terms, authors, venues, datasets, code, references, claims, and frontiers.",
        "output": "evidence graph",
        "failure_mode": "Coverage gaps, provenance paths, and cluster relationships may be impossible to evaluate.",
    },
    "cluster_coverage_agent": {
        "responsibility": "Compute coverage across task clusters, method clusters, dataset clusters, venue clusters, and evidence graph neighborhoods.",
        "output": "cluster coverage matrix",
        "failure_mode": "A high paper count may hide an uncovered task or method cluster.",
    },
    "citation_closure_agent": {
        "responsibility": "Evaluate whether core citation neighborhoods are sufficiently explored and identify high-value unvisited citation nodes.",
        "output": "citation closure report",
        "failure_mode": "Citation expansion may stop while important connected papers remain unvisited.",
    },
    "source_diversity_agent": {
        "responsibility": "Assess diversity across databases, venues, years, institutions, author groups, publication types, and access paths.",
        "output": "source diversity report",
        "failure_mode": "The corpus may overrepresent one source, team, venue, or time period.",
    },
    "recency_and_seminal_balance_agent": {
        "responsibility": "Balance recent work, foundational work, transitional periods, and mature survey-era papers.",
        "output": "recency and seminal balance report",
        "failure_mode": "The corpus may include only new papers or only classic papers.",
    },
    "missing_cluster_hunter_agent": {
        "responsibility": "Actively search for weakly connected, undercovered, or suspiciously absent clusters in the evidence graph.",
        "output": "missing cluster report",
        "failure_mode": "An entire relevant branch may remain undiscovered because no query or frontier targeted it.",
    },
    "coverage_scoring_agent": {
        "responsibility": "Aggregate independent coverage evidence into a weighted coverage score with dimension-level justification.",
        "output": "coverage score",
        "failure_mode": "The workflow may lack a coherent stopping signal.",
    },
    "coverage_audit_agent": {
        "responsibility": "Audit coverage scores, demand evidence for high ratings, and identify inflated or unsupported coverage claims.",
        "output": "coverage audit report",
        "failure_mode": "Self-scored coverage may be overly optimistic.",
    },
    "adversarial_reviewer_agent": {
        "responsibility": "Construct the strongest plausible argument that important papers, terms, or clusters are still missing.",
        "output": "adversarial challenge",
        "failure_mode": "The system may believe it is complete because no one tested the opposite case.",
    },
    "iteration_decision_agent": {
        "responsibility": "Choose PASS, loopback, user clarification, or STOP_WITH_RISK based on audits, budget, marginal yield, and unresolved challenges.",
        "output": "iteration decision",
        "failure_mode": "The workflow may loop blindly or stop before resolving a concrete deficiency.",
    },
    "stop_condition_validator_agent": {
        "responsibility": "Validate all hard stopping gates before final output is allowed.",
        "output": "stop validation",
        "failure_mode": "The system may publish final results before required quality gates are satisfied.",
    },
    "corpus_export_agent": {
        "responsibility": "Export the final corpus, version graph, identifiers, and metadata into reusable machine-readable formats.",
        "output": "corpus package",
        "failure_mode": "The research result may be difficult to reuse in papers, spreadsheets, databases, or later runs.",
    },
    "search_protocol_report_agent": {
        "responsibility": "Write the reproducible search protocol, including queries, databases, stages, inclusion criteria, exclusions, and loopbacks.",
        "output": "reproducible search report",
        "failure_mode": "The search process may be impossible to reproduce or defend.",
    },
    "coverage_report_agent": {
        "responsibility": "Write the coverage report with scores, evidence, audit findings, adversarial challenges, and residual risks.",
        "output": "coverage report",
        "failure_mode": "Users may not know how much confidence to place in the corpus.",
    },
    "gap_report_agent": {
        "responsibility": "Summarize weakly covered areas, research gaps, unresolved uncertainties, and recommended future search directions.",
        "output": "gap report",
        "failure_mode": "The final result may not help the user decide what to investigate next.",
    },
    "monitoring_query_agent": {
        "responsibility": "Generate monitoring queries and alert targets for new papers, citations, authors, venues, datasets, and retractions.",
        "output": "monitoring configuration",
        "failure_mode": "The literature review may become stale without a targeted update path.",
    },
}


STAGE_ENGLISH = {
    1: ("Run Initialization", "user request", "run plan and initial state", "Create a traceable task boundary."),
    2: ("Intent Decomposition", "raw request", "intent frame", "Turn natural language into searchable fields."),
    3: ("Domain Disambiguation", "intent frame", "domain decision and assumptions", "Prevent cross-domain false retrieval."),
    4: ("Concept Definition", "intent and domain decision", "concept table", "Create relevance standards for later screening."),
    5: ("Scope Contract", "concept table", "scope contract and depth contract", "Define inclusion, exclusion, and stopping thresholds."),
    6: ("Initial Term Generation", "scope contract", "seed terms and alias map", "Create the first retrieval entry points."),
    7: ("Initial Query Compilation", "seed terms", "source-specific queries", "Make queries executable."),
    8: ("Query Probing", "draft queries", "probe report and keyword gap report", "Detect bad queries before large-scale retrieval."),
    9: ("Query Revision", "probe report", "revised queries", "Repair the retrieval entry points using evidence."),
    10: ("Parallel Database Retrieval", "revised queries", "raw records", "Reduce source bias through parallel retrieval."),
    11: ("Full Text Location", "raw records", "full text links", "Prepare materials for term and reference mining."),
    12: ("Full Text Parsing", "full text links", "parsed text, references, and signals", "Recover terminology beyond abstracts."),
    13: ("Metadata Normalization", "raw records and parsed text", "canonical candidates", "Make multi-source data mergeable."),
    14: ("Identity Resolution", "canonical candidates", "author map and venue map", "Prevent author and venue expansion errors."),
    15: ("Version Linking and Deduplication", "canonical candidates", "deduplicated corpus and version graph", "Merge duplicates while preserving version relationships."),
    16: ("Initial Relevance Screening", "corpus and scope contract", "in-scope, near-scope, and out-of-scope records", "Separate core papers from noise."),
    17: ("Near-Miss Mining", "near-scope records", "near-miss signals", "Find hidden entry points in boundary papers."),
    18: ("Observed Term Extraction", "in-scope papers and parsed text", "observed terms", "Use papers to revise the search language."),
    19: ("Term Graph and Drift Analysis", "observed terms", "term graph and drift report", "Discover cross-community and cross-period terminology."),
    20: ("Taxonomy Modeling", "in-scope records", "taxonomies and setting table", "Measure coverage by dimensions, not by count."),
    21: ("Seed Paper Selection", "taxonomies and quality signals", "seed papers and frontier budgets", "Choose representative seeds for multi-path expansion."),
    22: ("Citation Expansion", "seed papers", "citation frontiers", "Find papers that keyword search misses."),
    23: ("Author and Institution Expansion", "seed authors and author map", "author and lab frontiers", "Find same-team work that uses different terminology."),
    24: ("Venue Expansion", "venue map and seed venues", "venue frontiers", "Find community papers not reached by keywords."),
    25: ("Dataset and Code Expansion", "dataset table and method names", "dataset and code frontiers", "Find papers with the same task but different wording."),
    26: ("Standards and Engineering Vocabulary Expansion", "core terms and domain", "standards frontier", "Add engineering aliases and application vocabulary."),
    27: ("Expansion Result Merge", "all frontiers", "updated corpus", "Integrate multi-path discoveries into one corpus."),
    28: ("Deep Screening and Validity Check", "updated corpus", "validated corpus", "Remove noise and invalid papers."),
    29: ("Evidence Graph Construction", "validated corpus, terms, taxonomies, and frontiers", "evidence graph", "Provide structure for coverage audit."),
    30: ("Coverage Analysis", "evidence graph", "coverage subreports", "Compute independent coverage signals."),
    31: ("Missing Cluster Search", "coverage subreports and evidence graph", "missing cluster report", "Actively search for what has not been found."),
    32: ("Coverage Scoring and Audit", "subreports and missing clusters", "coverage score and audit report", "Prevent inflated self-assessment."),
    33: ("Adversarial Challenge and Iteration Decision", "score, audit, and budget", "next action", "Route the workflow back to the right flow or stop."),
    34: ("Output and Monitoring", "final state", "final packages", "Produce reusable, reproducible, and monitorable outputs."),
}


PHASE_SLUG_RULES = [
    ("编排", "orchestration_state_reproducibility"),
    ("意图", "intent_definition_boundaries"),
    ("术语", "terminology_keywords_queries"),
    ("数据源", "data_source_retrieval"),
    ("全文", "full_text_content"),
    ("扩展", "expansion_frontiers"),
    ("规范化", "normalization_dedup_identity"),
    ("筛选", "screening_taxonomy_evidence"),
    ("覆盖", "coverage_audit_adversarial"),
    ("输出", "output_monitoring"),
]


def clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("|").strip())


def title_from_snake(snake: str) -> str:
    return snake.replace("_agent", "").replace("_", " ").title()


def kebab_from_snake(snake: str) -> str:
    return snake.replace("_", "-")


def phase_slug(heading: str) -> str:
    for needle, slug in PHASE_SLUG_RULES:
        if needle in heading:
            return slug
    raise ValueError(f"Unknown phase heading: {heading}")


def parse_design() -> tuple[list[Agent], list[Stage]]:
    text = DESIGN.read_text(encoding="utf-8").splitlines()
    agents: list[Agent] = []
    stages: list[Stage] = []
    current_phase = ""
    in_stage_table = False
    for line in text:
        if line.startswith("### 4."):
            current_phase = line.replace("### ", "").strip()
            continue
        row = re.match(
            r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|$",
            line,
        )
        if row and current_phase:
            number = int(row.group(1))
            snake = row.group(2).strip()
            if snake not in AGENT_ENGLISH:
                raise ValueError(f"Missing English metadata for {snake}")
            meta = AGENT_ENGLISH[snake]
            agents.append(
                Agent(
                    number=number,
                    snake=snake,
                    kebab=kebab_from_snake(snake),
                    title=title_from_snake(snake),
                    phase_heading=PHASE_DISPLAY_NAMES[phase_slug(current_phase)],
                    phase_slug=phase_slug(current_phase),
                    responsibility=meta["responsibility"],
                    output=meta["output"],
                    failure_mode=meta["failure_mode"],
                )
            )
            continue
        if line.startswith("## 5. Stage"):
            in_stage_table = True
            continue
        if in_stage_table and line.startswith("## 6."):
            in_stage_table = False
            continue
        if in_stage_table:
            parts = [clean_cell(p) for p in line.split("|")[1:-1]]
            if len(parts) == 6 and parts[0].isdigit():
                stage_number = int(parts[0])
                if stage_number not in STAGE_ENGLISH:
                    raise ValueError(f"Missing English metadata for stage {stage_number}")
                stage_name, stage_input, stage_output, stage_meaning = STAGE_ENGLISH[stage_number]
                stages.append(
                    Stage(
                        number=stage_number,
                        name=stage_name,
                        agents_text=parts[2],
                        input_text=stage_input,
                        output_text=stage_output,
                        meaning=stage_meaning,
                    )
                )
    by_name = {agent.snake: agent for agent in agents}
    for stage in stages:
        explicit = re.findall(r"`([^`]+_agent)`", stage.agents_text)
        for name in explicit:
            if name in by_name:
                by_name[name].stages.append(stage)
        range_match = re.search(r"agents\s+(\d+)-(\d+)", stage.agents_text)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            for agent in agents:
                if start <= agent.number <= end:
                    agent.stages.append(stage)
    return agents, stages


def stage_summary(agent: Agent) -> str:
    if not agent.stages:
        return "This agent is a phase-level support agent. It may be invoked when its output is needed by a stage, flow, audit, or loopback decision, even when it is not named in the compact stage table."
    lines = []
    for stage in agent.stages:
        lines.append(
            f"- Stage {stage.number}: {stage.name}. Input: {stage.input_text}. Output: {stage.output_text}. Why it matters: {stage.meaning}."
        )
    return "\n".join(lines)


def phase_methods(agent: Agent) -> str:
    pack = PHASE_PACKS[agent.phase_slug]
    return "\n".join(f"{idx}. {method}." for idx, method in enumerate(pack["methods"], 1))


def agent_questions(agent: Agent) -> list[str]:
    words = [w for w in re.split(r"[_\-\s]+", agent.snake.replace("_agent", "")) if w]
    subject = " ".join(words)
    return [
        f"What exact evidence proves that the {subject} output is needed in this run rather than merely convenient?",
        f"Which input records, stage artifacts, or prior decisions directly support each claim made by {agent.snake}?",
        f"What would be the concrete search failure if this agent skipped its work or produced a shallow answer?",
        f"Which downstream agent will consume the {agent.output}, and in what structured form must that consumer receive it?",
        f"What uncertainty remains after this agent finishes, and should that uncertainty become an assumption, a warning, a loopback, or a user question?",
        f"Could this output accidentally narrow the search space too early, and what guardrail prevents that narrowing?",
        f"Could this output expand the search space without control, and what scope rule prevents uncontrolled drift?",
        f"What fields must be present so that provenance, coverage scoring, and adversarial review can audit the decision later?",
    ]


PHASE_FIELD_CONTRACTS = {
    "orchestration_state_reproducibility": [
        "execution_context",
        "stage_or_frontier_status",
        "state_or_budget_delta",
        "blocking_condition",
        "recovery_or_next_action",
    ],
    "intent_definition_boundaries": [
        "interpreted_user_intent",
        "domain_or_scope_decision",
        "evidence_for_interpretation",
        "assumptions_and_open_questions",
        "downstream_constraints",
    ],
    "terminology_keywords_queries": [
        "term_or_query_record",
        "source_of_term",
        "query_variant_or_rule",
        "noise_or_gap_signal",
        "recommended_query_action",
    ],
    "data_source_retrieval": [
        "source_name",
        "query_submitted",
        "result_records",
        "pagination_or_rate_limit_state",
        "source_failures",
    ],
    "full_text_content": [
        "paper_identifier",
        "artifact_location",
        "parsed_sections_or_signals",
        "parse_confidence",
        "unavailable_content_reason",
    ],
    "expansion_frontiers": [
        "frontier_type",
        "seed_record",
        "expansion_path",
        "candidate_records",
        "expected_and_actual_gain",
    ],
    "normalization_dedup_identity": [
        "input_record_group",
        "identity_keys",
        "merge_split_or_conflict_decision",
        "confidence",
        "records_requiring_review",
    ],
    "screening_taxonomy_evidence": [
        "paper_or_graph_record",
        "scope_or_taxonomy_label",
        "supporting_evidence",
        "uncertainty_or_exclusion_reason",
        "graph_or_table_update",
    ],
    "coverage_audit_adversarial": [
        "coverage_dimension",
        "score_or_challenge",
        "supporting_evidence",
        "unsupported_claims",
        "loopback_or_stop_recommendation",
    ],
    "output_monitoring": [
        "export_or_report_path",
        "source_state_snapshot",
        "included_records",
        "omitted_records_and_reason",
        "future_monitoring_action",
    ],
}


PHASE_SPECIFIC_CHECKS = {
    "orchestration_state_reproducibility": [
        "Confirm that every stage or frontier status has a single current value and a traceable event history.",
        "Confirm that recovery actions distinguish missing input, tool failure, low yield, and user clarification.",
        "Confirm that any budget change names the frontier receiving or losing budget and why.",
    ],
    "intent_definition_boundaries": [
        "Confirm that the output uses the intended academic domain rather than a same-word neighboring domain.",
        "Confirm that boundary decisions do not exclude near-scope bridge papers too early.",
        "Confirm that unresolved ambiguity is recorded as an assumption or user question, not hidden inside the scope.",
    ],
    "terminology_keywords_queries": [
        "Confirm that user wording, observed paper wording, controlled vocabulary, aliases, and exclusions are not mixed without labels.",
        "Confirm that each query variant has an intended retrieval purpose and a noise-risk note.",
        "Confirm that failed or noisy probes become evidence for mutation rather than disappearing.",
    ],
    "data_source_retrieval": [
        "Confirm that the source query, source name, time, result count, and failure state are recorded.",
        "Confirm that missing abstracts, missing citation counts, and access failures are labeled separately.",
        "Confirm that source ranking or relevance signals are preserved without treating them as final relevance labels.",
    ],
    "full_text_content": [
        "Confirm that only legally accessible artifacts are used and that unavailable content is not guessed.",
        "Confirm that section, page, figure, table, or reference provenance is retained when available.",
        "Confirm that parse failures and partial parses are explicit enough for downstream agents to handle.",
    ],
    "expansion_frontiers": [
        "Confirm that every expansion candidate records the seed and path that discovered it.",
        "Confirm that frontier drift is controlled by the scope contract and later relevance screening.",
        "Confirm that frontier yield can be measured after deduplication and screening.",
    ],
    "normalization_dedup_identity": [
        "Confirm that exact identifiers, fuzzy matches, and inferred relationships are not treated as equally certain.",
        "Confirm that uncertain merges are flagged instead of silently merged.",
        "Confirm that version relationships are preserved even when records are deduplicated.",
    ],
    "screening_taxonomy_evidence": [
        "Confirm that labels come from the scope contract and not merely from keyword overlap.",
        "Confirm that near-scope material is mined for signals without entering the core corpus by accident.",
        "Confirm that extracted taxonomies and graph edges include enough evidence for coverage scoring.",
    ],
    "coverage_audit_adversarial": [
        "Confirm that high scores are supported by records, clusters, sources, and closure evidence.",
        "Confirm that each serious weakness points to a concrete loopback target.",
        "Confirm that stopping is not allowed until audit and adversarial conditions are both satisfied.",
    ],
    "output_monitoring": [
        "Confirm that generated files derive from the same final state snapshot.",
        "Confirm that missing optional outputs are documented with their upstream cause.",
        "Confirm that monitoring queries target concrete terms, authors, venues, datasets, citations, or validity risks.",
    ],
}


def yaml_key(value: str) -> str:
    key = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return key or "payload"


def agent_specific_contract(agent: Agent) -> str:
    fields = PHASE_FIELD_CONTRACTS[agent.phase_slug]
    checks = PHASE_SPECIFIC_CHECKS[agent.phase_slug]
    stage_hint = (
        f"The first directly named stage for this agent is Stage {agent.stages[0].number}: {agent.stages[0].name}."
        if agent.stages
        else "This agent is invoked as a support role when its phase artifact is required by another stage or audit."
    )
    field_lines = "\n".join(f"- `{field}`" for field in fields)
    check_lines = "\n".join(f"- {check}" for check in checks)
    payload_key = yaml_key(agent.output)
    return f"""## Agent-Specific Contract

This prompt is long because the agent boundary must be operationally complete, not because filler text is acceptable. For `{agent.snake}`, the essential artifact is `{agent.output}`. That artifact exists to prevent this failure mode: {agent.failure_mode.rstrip(".")}. {stage_hint} The output must therefore contain enough detail for a later agent to decide whether to trust it, challenge it, or send the workflow back to a specific stage.

The artifact payload for this agent must include these fields whenever the input evidence permits:

{field_lines}

For this particular agent, the central payload key should be `{payload_key}`. Use it to hold the records, decisions, scores, candidates, or configuration entries that embody the agent's main contribution. If the key is empty, the artifact is incomplete. If evidence does not support a value, set the field to `UNKNOWN` and explain the missing evidence instead of inventing a value.

Agent-specific review checks:

{check_lines}

The minimum useful result from `{agent.snake}` is not a narrative summary. It is a reusable decision object that says what was done, what evidence supports it, what uncertainty remains, and which downstream consumer should receive it. If the artifact cannot support that handoff, mark it `NEEDS_LOOPBACK` or `BLOCKED_INPUT_MISSING`.
"""


def build_prompt(agent: Agent) -> str:
    pack = PHASE_PACKS[agent.phase_slug]
    questions = "\n".join(f"- {q}" for q in agent_questions(agent))
    stage_text = stage_summary(agent)
    methods = phase_methods(agent)
    specific_contract = agent_specific_contract(agent)
    workspace_path = f"workspace/work/deep-paper-search/{agent.phase_slug}/{agent.snake}.md"
    json_path = f"workspace/work/deep-paper-search/{agent.phase_slug}/{agent.snake}.json"
    responsibility = agent.responsibility.rstrip(".")
    failure_mode = agent.failure_mode.rstrip(".")
    return f"""# {agent.title} Prompt

**Agent ID**: {agent.number}
**Agent name**: `{agent.snake}`
**Custom agent name**: `{agent.kebab}`
**Phase**: {agent.phase_heading}
**Primary artifact**: `{workspace_path}`
**Optional structured artifact**: `{json_path}`

## Role

You are `{agent.snake}`, a specialist subagent in the Deep Paper Search workflow. Your non-substitutable responsibility is: {responsibility}. You are included because the workflow would otherwise fail in this concrete way: {failure_mode}. Your normal output is: {agent.output}. Treat that output as an artifact that another agent must be able to inspect, parse, challenge, and reuse. You are not a generic literature reviewer, not a casual brainstorming assistant, and not a report writer unless the artifact explicitly requires prose. Your task is to perform the narrow role defined here with enough evidence, structure, and operational detail that the global orchestrator can make a reliable next decision.

## Workflow Context

The overall system starts from an incomplete user research idea and progressively discovers real field vocabulary, papers, citation paths, authors, venues, datasets, code ecosystems, standards, and missing clusters. The key design principle is that initial keywords are only an entry point. The search boundary is shaped by evidence from papers and scholarly networks, not by the first wording supplied by the user. Every agent writes auditable artifacts under `workspace/work/deep-paper-search/`. Every claim must point to input evidence, prior state, a source record, a query, a parsed paper section, a graph edge, or a clearly labeled assumption. If evidence is missing, state that it is missing and route the gap rather than inventing it.

Your phase mission is to {pack["mission"]}. The inputs normally available to this phase are {pack["inputs"]}. The principal handoff expectation is: {pack["handoffs"]}. Work locally inside the repository. Do not modify unrelated user files. Do not overwrite artifacts from other agents unless the orchestrator has explicitly assigned you a replacement run. When the same artifact already exists, append a dated revision section or write a new iteration-specific file if the orchestrator has provided an iteration identifier.

## Stage Placement

{stage_text}

If you are invoked outside the stage listed above, continue only when the request is consistent with your role. If the user or orchestrator asks you to do another agent's job, write a short handoff note naming the correct agent and the missing artifact. Do not silently expand your mandate. The system depends on sharp agent boundaries because coverage and adversarial review need to know who made each decision.

## Required Inputs

Before you begin, identify the exact inputs you used. Acceptable inputs include the latest user request, the locked scope contract, the depth contract, current `research_state`, previous agent artifacts, raw source batches, canonical paper records, parsed text, evidence graph slices, query logs, frontier records, audit reports, and iteration decisions. If a required input is absent, produce `STATUS: BLOCKED_INPUT_MISSING` and list the missing input names. Do not continue with a pretend version of an absent artifact. If a useful but nonessential input is absent, proceed and record it under residual uncertainty.

For `{agent.snake}`, pay special attention to the following input questions:

{questions}

These questions are not decorative. They are a completeness checklist for deciding whether the artifact will be useful to downstream agents. If you cannot answer one of them, state the limitation and whether it requires loopback, user clarification, or a lower confidence score.

{specific_contract}

## Operating Procedure

1. Restate the active task in one paragraph using the locked scope language, not loose user wording.
2. List the concrete input artifacts and their paths or identifiers.
3. Extract the facts that are relevant to your role and ignore facts that belong to other agents.
4. Apply the phase methods below in order, adapting them to the evidence you actually have.
5. Produce structured decisions, not only prose. Tables, bullet lists, YAML blocks, and explicit status labels are preferred when they make the result machine-consumable.
6. Attach provenance to every important decision. A decision without provenance is a candidate for rejection by the coverage auditor.
7. Separate evidence, inference, assumption, and recommendation. Do not let a plausible inference masquerade as a source fact.
8. Identify the downstream agent or stage that should consume your output.
9. Write the artifact to `{workspace_path}`. If your output contains records that would be easier to parse as data, also write `{json_path}`.
10. Finish with a compact handoff section that says `READY`, `NEEDS_LOOPBACK`, `NEEDS_USER_INPUT`, or `BLOCKED_INPUT_MISSING`.

## Phase Methods

{methods}

Apply these methods concretely. For example, if you are creating a budget plan, give frontier budgets and rationale. If you are screening papers, give inclusion labels and exclusion reasons. If you are querying a source, preserve the source query and failure conditions. If you are auditing coverage, identify which evidence channels support each score and which channels are weak. The method list is a set of required operational moves, not a topic outline.

## Output Contract

Your artifact must use this Markdown structure unless the orchestrator provided a stricter schema:

````markdown
## STATUS
STATUS: READY | NEEDS_LOOPBACK | NEEDS_USER_INPUT | BLOCKED_INPUT_MISSING

## Agent Identity
- Agent:
- Phase:
- Iteration:
- Trigger:

## Inputs Used
- [path or identifier] - [why it was needed]

## Core Decision Or Finding
- [the main output in the vocabulary of this agent]

## Evidence
| Claim | Evidence Source | Confidence | Notes |
|---|---|---:|---|

## Structured Output
```yaml
agent: {agent.snake}
artifact_type: "{agent.output}"
records: []
assumptions: []
uncertainties: []
downstream_consumers: []
```

## Quality Checks
- [check performed]

## Handoff
- Next Consumer:
- Recommended Next Stage:
- Loopback Needed:
- User Question Needed:
```

When writing YAML inside the artifact, keep it syntactically simple. Prefer strings, lists, and dictionaries. If a value is unknown, use `UNKNOWN` and explain why. Do not omit a required field just because the value is inconvenient.

## Quality Gates

Your output can be rejected if any of these conditions are true:

- It does not write the required artifact path.
- It performs another agent's role and hides the boundary crossing.
- It gives confident claims without evidence or provenance.
- It collapses `in_scope`, `near_scope`, `out_of_scope`, `unknown`, and `not_applicable` into a single vague category.
- It treats an API failure, missing PDF, missing metadata, or failed parse as evidence that no relevant paper exists.
- It expands the search space without tying the expansion to scope, evidence, or a frontier record.
- It narrows the search space without recording the exclusion logic.
- It fails to name the downstream consumer of the artifact.
- It ends with a generic summary instead of a status and handoff.

## Boundaries

Do not fabricate papers, citations, abstracts, code repositories, datasets, benchmarks, venues, author identities, DOI values, citation counts, or standard names. Do not bypass paywalls, authentication, or access controls. Do not ask the user to paste secrets. If private access, credentials, institutional subscriptions, or tokens are needed, state the access requirement and stop at the correct boundary. Do not delete or rewrite prior artifacts unless explicitly instructed. Do not claim that coverage is sufficient unless your role is one of the coverage decision agents and the required audit evidence is present.

## Handling Uncertainty

Uncertainty is useful when it is explicit. Classify uncertainty as `missing_input`, `source_failure`, `ambiguous_scope`, `weak_evidence`, `conflicting_metadata`, `low_yield_frontier`, or `requires_user_choice`. Each uncertainty must have a proposed resolution. If the resolution is another agent, name it. If the resolution is another stage, name the stage. If the resolution requires user judgment, ask no more than three concise questions and do not continue to later stages.

## Final Handoff Rule

The final lines of your artifact must be:

```text
HANDOFF_STATUS: READY | NEEDS_LOOPBACK | NEEDS_USER_INPUT | BLOCKED_INPUT_MISSING
HANDOFF_TARGET: <agent or stage>
HANDOFF_REASON: <one sentence>
```
````

This makes the artifact usable by the orchestrator and by later automated checks. If you cannot produce the artifact because the request is outside your role, still write a short artifact with `HANDOFF_STATUS: NEEDS_LOOPBACK` and explain which agent should receive the task.
"""


def toml_escape(value: str) -> str:
    return value.replace('"""', '\\"\\"\\"')


def build_toml(agent: Agent) -> str:
    prompt_path = f"prompts/{agent.snake}.md"
    output_path = f"workspace/work/deep-paper-search/{agent.phase_slug}/{agent.snake}.md"
    instructions = f"""You are Agent {agent.number}: {agent.title}.

Authoritative prompt:
- Read {prompt_path} and follow it strictly.

Role:
- {agent.responsibility}

Expected output:
- Write {output_path}.
- If structured records are produced, also write workspace/work/deep-paper-search/{agent.phase_slug}/{agent.snake}.json.

Rules:
- Stay inside this agent's boundary.
- Use the current Deep Paper Search state and prior artifacts as inputs.
- Preserve provenance for every important decision.
- Do not fabricate papers, metadata, citations, abstracts, datasets, repositories, venues, or coverage evidence.
- If required inputs are missing, write STATUS: BLOCKED_INPUT_MISSING instead of guessing.
- Finish with HANDOFF_STATUS, HANDOFF_TARGET, and HANDOFF_REASON.
"""
    return (
        f'name = "{agent.kebab}"\n'
        f'description = "Deep Paper Search Agent {agent.number}. {agent.responsibility}"\n'
        f'developer_instructions = """\n{toml_escape(instructions)}"""\n'
    )


def build_launcher_prompt(agents: list[Agent], stages: list[Stage]) -> str:
    phase_lines = []
    for slug in PHASE_PACKS:
        phase_agents = [a for a in agents if a.phase_slug == slug]
        if not phase_agents:
            continue
        phase_lines.append(
            f"- `{slug}`: " + ", ".join(f"`{a.snake}`" for a in phase_agents)
        )
    stage_lines = "\n".join(
        f"{stage.number}. {stage.name}: output `{stage.output_text}`; purpose: {stage.meaning}."
        for stage in stages
    )
    agent_lines = "\n".join(phase_lines)
    return f"""# Deep Paper Search Workflow Launcher Prompt

Use the Deep Paper Search custom agents installed in this repository to run an iterative, evidence-driven paper discovery workflow. This launcher is intentionally separate from the individual agent prompts. It describes how to coordinate the system, when to ask the user for clarification, how to route loopbacks, and how to prevent premature stopping. The individual authoritative prompt for each agent lives under `prompts/<agent_name>.md`, and each active custom agent is configured under `.codex/agents/<agent_name>.toml`.

## Mission

The workflow starts from a research idea that may be incomplete, translated poorly, or expressed with terms that are not used by the target academic community. Your job as the workflow controller is not to run a one-pass keyword search. Your job is to build a stateful research process that learns from papers, citations, authors, venues, datasets, code, standards, and audit feedback. Initial keywords are only a launch point. The final search boundary must be justified by evidence and must survive coverage audit and adversarial challenge.

## Agent Groups

{agent_lines}

## Stage Protocol

The workflow has these stages:

{stage_lines}

Run stages in order only when their required inputs exist. Many stages contain parallel agents. Parallelism is expected for source retrieval, citation expansion, author expansion, venue expansion, dataset/code expansion, and coverage subreports. Do not wait for a slow or failed data source before preserving successful results from other sources. Instead, record the failure and let `failure_triage_agent` decide whether retry, downgrade, or loopback is appropriate.

## State and Artifacts

All workflow outputs must stay under `workspace/work/deep-paper-search/` unless the user explicitly requests a different output location. The event log is the durable history. Agents must not silently overwrite each other. Every artifact must include status, inputs used, evidence, structured output, quality checks, and handoff lines. The orchestrator may generate a state snapshot from those artifacts, but the snapshot is not a substitute for provenance.

## Clarification Policy

Ask the user only when the missing information changes the research boundary, legal access, budget, or final output expectation. Do not ask the user to provide obvious terms that the system can discover from papers. Do not ask the user to paste credentials, private keys, API tokens, or paid content. If access is needed, ask the user to configure the local environment and stop at the access boundary. Ask no more than three concise questions at a time.

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
"""


def build_plugin_json() -> str:
    data = {
        "name": "deep-paper-search",
        "version": "0.1.0",
        "description": "Evidence-driven multi-agent deep paper search workflow with query expansion, citation snowballing, author and venue exploration, coverage audit, and adversarial loopback.",
        "author": {"name": "Deep Paper Search"},
        "repository": "https://github.com/zclu-zju/paper-deep-research",
        "keywords": [
            "codex",
            "research",
            "literature-review",
            "paper-search",
            "subagents",
            "coverage-audit",
        ],
        "skills": "./skills/",
        "interface": {
            "displayName": "Deep Paper Search",
            "shortDescription": "Iterative multi-agent paper discovery.",
            "longDescription": "Installs custom agents and prompts for a deep paper search workflow that expands from user intent into terms, citations, authors, venues, datasets, code, standards, evidence graphs, coverage audit, and adversarial loopback.",
            "developerName": "Deep Paper Search",
            "category": "Productivity",
            "capabilities": ["Interactive", "Write"],
            "defaultPrompt": [
                "Run the deep-paper-search workflow for my research direction.",
                "Use the Deep Paper Search agents to discover papers beyond initial keywords.",
                "Install Deep Paper Search workflow agents.",
            ],
        },
    }
    return json.dumps(data, indent=2) + "\n"


def build_skill() -> str:
    return """---
name: deep-paper-search
description: Use for evidence-driven deep paper search in a Codex repo. Installs repo-local custom agents and prompts for a multi-agent workflow that expands from initial user intent into domain terms, citations, authors, venues, datasets, code ecosystems, standards, coverage audits, adversarial loopbacks, and reproducible search packages.
---

# Deep Paper Search

This skill installs and launches the Deep Paper Search workflow agents.

The workflow is designed for cases where a user's first keywords are incomplete or not aligned with the vocabulary used by the target research community. It is intentionally iterative. The system learns terms from papers, expands through citation, author, venue, dataset, code, and standards frontiers, then runs coverage audit and adversarial challenge before stopping.

## Install Agents

From a local checkout:

```bash
python3 plugins/deep-paper-search/scripts/install_project_agents.py --repo .
```

From an installed plugin cache, resolve the installer relative to this skill directory:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo>
```

The installer copies generated agent TOML files to `.codex/agents/`, project prompts to `prompts/`, and the launcher prompt to `.codex/`. It is conservative by default and reports conflicts without overwriting unless `--force` is used.

## Launch

After installing agents, invoke:

```text
Use the deep-paper-search workflow custom agents and execute the evidence-driven paper search workflow.
```

Or use the launcher file:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/deep-paper-search-workflow-prompt.md
```

## Outputs

Workflow artifacts are written under:

```text
workspace/work/deep-paper-search/
```

Final outputs may include `corpus.csv`, `corpus.bib`, `corpus.json`, `versions.json`, `excluded.csv`, `near_miss.csv`, `search_protocol.md`, `coverage_report.md`, `evidence_graph.json`, `gap_report.md`, and `monitoring_config.yaml`.
"""


def build_installer() -> str:
    return """#!/usr/bin/env python3
\"\"\"Install deep-paper-search workflow templates into a target repository.\"\"\"

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ASSETS = PLUGIN_ROOT / "assets"


def copy_tree_contents(src_dir: Path, dst_dir: Path, force: bool) -> tuple[int, int, int]:
    copied = unchanged = conflicts = 0
    for src in sorted(src_dir.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
            continue
        if filecmp.cmp(src, dst, shallow=False):
            unchanged += 1
            continue
        if force:
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"CONFLICT skip: {dst} differs from plugin asset")
            conflicts += 1
    return copied, unchanged, conflicts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--force", action="store_true", help="Overwrite conflicting files.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"Target repo does not exist: {repo}")

    targets = [
        (ASSETS / "agents", repo / ".codex" / "agents"),
        (ASSETS / "prompts" / "codex", repo / ".codex"),
        (ASSETS / "prompts" / "project", repo / "prompts"),
    ]

    total = {"copied": 0, "unchanged": 0, "conflicts": 0}
    for src, dst in targets:
        copied, unchanged, conflicts = copy_tree_contents(src, dst, args.force)
        total["copied"] += copied
        total["unchanged"] += unchanged
        total["conflicts"] += conflicts

    print(f"Installed into: {repo}")
    print(f"Copied: {total['copied']}")
    print(f"Unchanged: {total['unchanged']}")
    print(f"Conflicts: {total['conflicts']}")
    if total["conflicts"]:
        print("Re-run with --force only if overwriting is intentional.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def build_user_parameters_doc() -> str:
    return """# User-Required Parameters

This document defines the parameters the Deep Paper Search workflow may need from the user. The workflow should not ask for all of these at once. It should collect the minimal set required for the requested depth and only ask follow-up questions when the missing answer changes the search boundary, access model, budget, or final output.

## Required Before Search

These parameters are required before the workflow starts literature retrieval:

1. **Research seed type**: one of `DIRECTION`, `KEYWORDS`, `SEED_PAPER`, `MIXED`, or `UNKNOWN`.
2. **Research seed content**: the research direction, keyword set, seed paper path, seed paper title, seed paper abstract, or short description.
3. **Target domain or disambiguation hint**: the field or community the user intends, especially when terms are ambiguous across domains.
4. **Primary research objective**: what the search should explain or collect, such as mechanism understanding, survey corpus, benchmark comparison, method taxonomy, code-bearing papers, or near-exhaustive related work.
5. **Desired search depth**: `EXPLORATORY`, `DEEP_SURVEY`, `SYSTEMATIC_LIKE`, or `NEAR_EXHAUSTIVE`.
6. **Approximate output size**: target number of core papers, or permission for the workflow to choose a count from the depth contract.
7. **Time or recency requirement**: year range, recent-years window, include-foundational-work requirement, or no year restriction.
8. **Inclusion criteria**: required tasks, methods, datasets, venues, publication types, languages, or evidence standards.
9. **Exclusion criteria**: explicitly unwanted fields, tasks, application domains, paper types, or noisy meanings of shared terms.
10. **Final output format**: at minimum whether the user wants Markdown only, CSV/BibTeX/JSON, evidence graph, monitoring configuration, or all standard outputs.

If any of the above are absent, the first-stage agents should either infer a provisional value from evidence and record it as an assumption, or ask the user no more than three concise questions when the missing value would change the search boundary.

## Required Only For Code-Oriented Runs

Ask these only if the user wants code availability, repository verification, repository cloning, benchmark reproduction, or implementation-oriented analysis:

1. **Code requirement level**: `IGNORE_CODE`, `RECORD_CODE_SIGNALS`, `VERIFY_CODE_LINKS`, or `REQUIRE_CODE_AVAILABLE`.
2. **Repository cloning policy**: `DO_NOT_CLONE`, `CLONE_SELECTED`, `CLONE_ALL_VERIFIED`, or `ASK_BEFORE_EACH_CLONE`.
3. **Clone target directory**: default may be `workspace/work/deep-paper-search/code/` if the user accepts defaults.
4. **Repository access expectation**: public-only, private allowed, institution-hosted, unknown, or user-managed.
5. **Git LFS and submodule policy**: skip, fetch if needed, or ask before fetching.
6. **Reproducibility depth**: record repository only, inspect README, verify commit, run tests, or reproduce experiments.

The workflow must not ask the user to paste secrets. If authentication is required, ask the user to configure SSH, Git credential helper, GitHub CLI, or an environment variable in the local environment.

## Required Only For Paper Artifact Retrieval

Ask these only if the user wants local PDFs, TeX sources, supplementary files, or compiled paper artifacts:

1. **Artifact retrieval policy**: `DO_NOT_DOWNLOAD`, `DOWNLOAD_SELECTED`, `DOWNLOAD_ALL_IN_SCOPE`, or `DOWNLOAD_VERIFIED_CODE_ONLY`.
2. **Artifact types**: PDF, HTML snapshot, TeX source, supplementary files, dataset links, or all available public artifacts.
3. **Artifact target directory**: default may be `workspace/work/deep-paper-search/artifacts/` if the user accepts defaults.
4. **TeX compile policy**: `DOWNLOAD_ONLY`, `COMPILE_IF_ENV_AVAILABLE`, or `REQUIRE_COMPILE_SUCCESS`.
5. **Missing dependency policy**: skip and record, ask user to install, or fail the artifact stage.

The workflow may only download publicly accessible artifacts or artifacts the user is authorized to access. It must not bypass access controls.

## Optional Quality Preferences

These improve output quality but should not block search unless the user marks them as required:

1. Preferred databases or sources.
2. Preferred venues or excluded venues.
3. Citation-count preference or tolerance for new low-citation papers.
4. Whether to include preprints.
5. Whether to include surveys.
6. Whether to include patents, standards, and white papers as terminology evidence.
7. Preferred citation style for final reports.
8. Preferred language of final human-readable reports.
9. Maximum runtime, API budget, download budget, or token budget.
10. Whether the workflow should continue monitoring after the first run.

## Minimal Clarification Set

When the user gives only a rough topic, the workflow should usually ask these three questions first:

1. What search depth do you want: exploratory, deep survey, systematic-like, or near-exhaustive?
2. What final output do you want: paper list only, CSV/BibTeX/JSON package, evidence graph, coverage report, or all standard outputs?
3. Are there any hard inclusion or exclusion criteria, such as year range, target domain, paper type, dataset, method family, or venue?

If the answer gives permission to use sensible defaults, the workflow may proceed with a recorded default depth contract and ask fewer questions.
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def mirror_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def word_count(path: Path) -> int:
    return len(re.findall(r"\b[\w'-]+\b", path.read_text(encoding="utf-8")))


def main() -> int:
    agents, stages = parse_design()
    if len(agents) != 79:
        raise SystemExit(f"Expected 79 agents, parsed {len(agents)}")
    if len(stages) != 34:
        raise SystemExit(f"Expected 34 stages, parsed {len(stages)}")

    for directory in [
        PROJECT_PROMPTS,
        PROJECT_AGENTS,
        PLUGIN_AGENTS,
        PLUGIN_PROJECT_PROMPTS,
        PLUGIN_CODEX_PROMPTS,
        PLUGIN_SKILL,
        PLUGIN_SCRIPT,
        ROOT / ".agents" / "plugins",
        ROOT / "docs",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    for agent in agents:
        prompt = build_prompt(agent)
        toml = build_toml(agent)
        prompt_path = PROJECT_PROMPTS / f"{agent.snake}.md"
        toml_path = PROJECT_AGENTS / f"{agent.snake}.toml"
        write(prompt_path, prompt)
        write(toml_path, toml)
        mirror_file(prompt_path, PLUGIN_PROJECT_PROMPTS / prompt_path.name)
        mirror_file(toml_path, PLUGIN_AGENTS / toml_path.name)

    launcher = build_launcher_prompt(agents, stages)
    launcher_path = CODEX_DIR / LAUNCHER_NAME
    write(launcher_path, launcher)
    mirror_file(launcher_path, PLUGIN_CODEX_PROMPTS / LAUNCHER_NAME)

    manifest = [
        {
            "id": agent.number,
            "agent": agent.snake,
            "custom_agent_name": agent.kebab,
            "phase": agent.phase_heading,
            "phase_slug": agent.phase_slug,
            "responsibility": agent.responsibility,
            "output": agent.output,
            "failure_mode": agent.failure_mode,
            "prompt": f"prompts/{agent.snake}.md",
            "toml": f".codex/agents/{agent.snake}.toml",
            "stages": [stage.number for stage in agent.stages],
        }
        for agent in agents
    ]
    write(AGENT_MANIFEST, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    plugin_json = build_plugin_json()
    write(PLUGIN_ROOT / ".codex-plugin" / "plugin.json", plugin_json)
    marketplace = {
        "plugins": [
            {
                "name": "deep-paper-search",
                "path": "plugins/deep-paper-search",
                "enabled": True,
                "version": "0.1.0",
            }
        ]
    }
    write(ROOT / "marketplace.json", json.dumps(marketplace, indent=2) + "\n")
    write(ROOT / ".agents" / "plugins" / "marketplace.json", json.dumps(marketplace, indent=2) + "\n")
    write(PLUGIN_SKILL / "SKILL.md", build_skill())
    installer_path = PLUGIN_SCRIPT / "install_project_agents.py"
    write(installer_path, build_installer())
    installer_path.chmod(0o755)

    short_doc = f"""# Generated Agent Assets

This repository follows the `paper-tool` research branch layout while using original Deep Paper Search content.

- Project agent TOML: `.codex/agents/*.toml`
- Project prompts: `prompts/*.md`
- Launcher prompt: `.codex/{LAUNCHER_NAME}`
- Plugin assets: `plugins/deep-paper-search/assets/`
- Plugin installer: `plugins/deep-paper-search/scripts/install_project_agents.py`
- Agent manifest: `plugins/deep-paper-search/assets/agent_manifest.json`

The generator parses `deep-paper-search-agent-system-design.md` and writes {len(agents)} agent TOML files plus {len(agents)} project prompt files. Each project agent prompt is expected to be at least 1000 words.
"""
    write(ROOT / "docs" / "generated-agent-assets.md", short_doc)
    write(ROOT / "docs" / "user-required-parameters.md", build_user_parameters_doc())

    too_short = []
    for path in sorted(PROJECT_PROMPTS.glob("*.md")):
        count = word_count(path)
        if count < 1000:
            too_short.append((path.name, count))
    launcher_count = word_count(launcher_path)
    if launcher_count < 1000:
        too_short.append((LAUNCHER_NAME, launcher_count))
    if too_short:
        detail = "\n".join(f"{name}: {count}" for name, count in too_short)
        raise SystemExit(f"Prompts below 1000 words:\n{detail}")

    print(f"Generated {len(agents)} agents, {len(stages)} stages, launcher words={launcher_count}")
    print(f"Shortest project prompt words={min(word_count(path) for path in PROJECT_PROMPTS.glob('*.md'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
