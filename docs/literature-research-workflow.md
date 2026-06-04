# Literature Research Workflow

This document describes the unified interactive workflow installed by the Baseline Research plugin.

## Design Goal

The workflow is a global research loop, not a one-pass serial service.

It must:

- ask for missing research parameters before searching;
- detect ambiguous directions before searching;
- use a seed paper as a way to infer the user's research focus when a paper is provided;
- search papers under the locked scope;
- verify code availability when the user requests an open-source quota;
- write a final CSV;
- review the whole run;
- loop back to the failed stage when review fails.

## Stages

### Stage 0: Requirement Collection

Agent:

```text
research-requirement-collector
```

Output:

```text
workspace/literature_research/reports/requirements.md
```

Required fields:

- input type or seed source;
- research direction or seed paper;
- minimum total paper count;
- minimum open-source/code paper count;
- target years;
- code verification level;
- output format;
- inclusion/exclusion constraints when available.

If anything required is missing:

```text
STATUS: NEEDS_USER_INPUT
```

The orchestrator asks the user and stops.

### Stage 1: Scope Lock

Agent:

```text
research-scope-locker
```

Output:

```text
workspace/literature_research/reports/scope_report.md
```

If a seed paper is provided, the paper is used to infer the field, task, data/modality, dataset or benchmark family, metrics, and comparison boundary.

If a direction is provided, the agent checks ambiguous terms, aliases, synonyms, acronyms, translations, and adjacent fields.

If ambiguity remains:

```text
STATUS: NEEDS_USER_CLARIFICATION
```

The orchestrator asks the user and stops.

### Stage 2: Paper Discovery

Agent:

```text
paper-discovery-scout
```

Outputs:

```text
workspace/literature_research/reports/paper_candidates.csv
workspace/literature_research/reports/paper_candidates.md
```

The scout searches with a buffer above the requested count so later code verification can reject weak candidates without immediately failing the run.

### Stage 3: Code Availability Verification

Agent:

```text
code-availability-verifier
```

Outputs:

```text
workspace/literature_research/reports/code_verification.csv
workspace/literature_research/reports/code_verification.md
```

Code counts only when there is concrete public evidence, such as an official project link, Papers With Code entry, repository README evidence, paper title, arXiv ID, BibTeX, or author/project linkage.

### Stage 4: CSV Writer

Agent:

```text
research-csv-writer
```

Outputs:

```text
workspace/literature_research/reports/final_papers.csv
workspace/literature_research/reports/research_summary.md
```

Required CSV columns:

```csv
title,year,venue,publication_type,paper_url,arxiv_id,code_available,code_url,code_evidence,source_query,relevance_rationale,status
```

### Stage 5: Integrity Review

Agent:

```text
research-integrity-reviewer
```

Output:

```text
workspace/literature_research/reports/integrity_report.md
```

The reviewer checks requirement completeness, scope lock, ambiguity handling, paper traceability, scope discipline, total count, code count, code evidence, CSV schema, and loopback readiness.

If any required check fails:

```text
VERDICT: REJECT
```

The report specifies one target stage and whether user input is required.

## Loopback

When Stage 5 rejects:

1. The orchestrator reads the target stage.
2. It logs the retry in:

```text
workspace/literature_research/reports/iteration_log.md
```

3. It reruns the target stage with the review critique as a high-priority constraint.
4. It reruns downstream affected stages.
5. It returns to Stage 5.

If user input is required, the orchestrator asks the user and stops.

## Example Prompt

```text
Use baseline-research.

Research papers about CSI feedback for FDD massive MIMO.
I need at least 30 papers from 2022-2026, including at least 10 with verified public code.
Output a CSV with title, year, venue, paper URL, arXiv ID, whether code is open source, code URL, and relevance rationale.
Before searching, check whether the direction has ambiguous terms or adjacent fields.
```

## Seed Paper Example

```text
Use baseline-research.

Use paper/main.tex as the seed paper. Infer the research direction and experiment context from the paper, then ask me for any missing parameters before searching. I need at least 25 related papers, including at least 8 with verified public code, from 2021-2026.
```
