# Literature Research Workflow

This document describes the unified interactive workflow installed by the Baseline Research plugin.

## Design Goal

The workflow is a global research loop, not a one-pass serial service.

It must:

- ask for missing research parameters before searching;
- detect ambiguous directions before searching;
- use a seed paper as a way to infer the user's research focus when a paper is provided;
- search papers under the locked scope and preserve abstracts plus citation counts;
- verify code availability when the user requests an open-source quota, prioritizing high-citation in-scope papers for GitHub/repository searches;
- optionally clone verified repositories to local storage when the user explicitly requests it;
- optionally download paper PDFs or TeX sources when the user explicitly requests it;
- compile downloaded TeX sources to PDF only when requested and when the local TeX environment supports it;
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
- local repository retrieval preference;
- clone scope, target directory, authentication/access expectations, Git LFS policy, and submodule policy when cloning is requested;
- paper artifact retrieval preference;
- artifact scope, artifact types, target directory, TeX compile policy, and missing dependency policy when paper artifact retrieval is requested;
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

The scout searches with a buffer above the requested count so later code verification can reject weak candidates without immediately failing the run. Every candidate intended for selection must preserve an abstract, abstract source, citation count, and citation source.

If paper artifact retrieval is requested, the scout preserves available `pdf_url` and `tex_source_url` signals. These signals are not treated as verified downloads.

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

Stage 3 does not clone repositories. It records cloneable repository URLs and authentication signals for Stage 4 when local retrieval is requested. When searching GitHub or other repository hosts, Stage 3 prioritizes in-scope candidates with higher `citation_count` first.

### Stage 4: Repository Cloning

Agent:

```text
repository-cloner
```

Outputs:

```text
workspace/literature_research/reports/repository_clones.csv
workspace/literature_research/reports/repository_clones.md
workspace/literature_research/code/
```

This stage runs only when Stage 0 explicitly records that local repository retrieval is requested. It clones verified repositories only, normally under `workspace/literature_research/code/`.

If private access, SSH keys, API tokens, Git credential helper setup, GitHub CLI auth, Git LFS credentials, or submodule access are needed, the stage reports:

```text
STATUS: NEEDS_USER_AUTH
```

and the orchestrator asks the user to configure local access before retrying. The workflow must not ask the user to paste tokens, passwords, or private keys into reports.

Safety rules:

- do not execute third-party code;
- do not install dependencies;
- do not initialize submodules unless explicitly requested;
- do not download Git LFS objects unless explicitly requested;
- do not overwrite existing local directories.

### Stage 5: Paper Artifact Collection

Agent:

```text
paper-artifact-collector
```

Outputs:

```text
workspace/literature_research/reports/paper_artifacts.csv
workspace/literature_research/reports/paper_artifacts.md
workspace/literature_research/papers/pdf/
workspace/literature_research/papers/tex/
workspace/literature_research/papers/compiled_pdf/
```

This stage runs only when Stage 0 explicitly records that paper PDF/TeX artifact retrieval is requested. It downloads public PDFs or public TeX/source archives for in-scope papers according to the locked artifact scope.

If TeX compilation is requested, the stage checks whether a local toolchain such as `latexmk`, `tectonic`, `pdflatex`, or `xelatex` is available. When the compile policy is `COMPILE_IF_ENV_AVAILABLE`, missing TeX tooling is recorded as:

```text
SKIPPED_NO_TEX_ENV
```

and the workflow continues. When compilation is attempted, the stage checks that the compiled PDF exists before marking the artifact as compiled.

Safety rules:

- do not modify `paper/`;
- do not execute arbitrary third-party scripts;
- do not install dependencies or TeX packages;
- do not use TeX shell escape;
- do not invent local paths or compile results.

### Stage 6: CSV Writer

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
title,year,venue,publication_type,paper_url,abstract,citation_count,citation_source,arxiv_id,code_available,code_url,code_evidence,source_query,relevance_rationale,clone_requested,clone_status,local_clone_path,commit_hash,artifact_requested,pdf_download_status,local_pdf_path,tex_download_status,local_tex_source_path,tex_compile_status,compiled_pdf_path,status
```

### Stage 7: Integrity Review

Agent:

```text
research-integrity-reviewer
```

Output:

```text
workspace/literature_research/reports/integrity_report.md
```

The reviewer checks requirement completeness, scope lock, ambiguity handling, paper traceability, abstract completeness, citation count completeness, scope discipline, total count, code count, code evidence and citation-aware GitHub search priority, repository clone output and safety when requested, paper artifact retrieval and TeX compilation when requested, CSV schema, and loopback readiness.

If any required check fails:

```text
VERDICT: REJECT
```

The report specifies one target stage and whether user input is required.

## Loopback

When Stage 7 rejects:

1. The orchestrator reads the target stage.
2. It logs the retry in:

```text
workspace/literature_research/reports/iteration_log.md
```

3. It reruns the target stage with the review critique as a high-priority constraint.
4. It reruns downstream affected stages.
5. It returns to Stage 7.

If user input is required, the orchestrator asks the user and stops.

## Example Prompt

```text
Use baseline-research.

Research papers about CSI feedback for FDD massive MIMO.
I need at least 30 papers from 2022-2026, including at least 10 with verified public code.
Output a CSV with title, year, venue, paper URL, arXiv ID, whether code is open source, code URL, and relevance rationale.
The CSV must include the abstract and citation count for every selected paper. When searching GitHub code, prioritize high-citation in-scope papers.
Before searching, check whether the direction has ambiguous terms or adjacent fields.
```

## Clone Retrieval Example

```text
Use baseline-research.

Research papers about CSI feedback for FDD massive MIMO.
I need at least 30 papers from 2022-2026, including at least 10 with verified public code.
Clone the selected verified-code repositories into workspace/literature_research/code/.
If SSH, tokens, private repository access, Git LFS, or submodules are needed, stop and tell me what local setup is required before cloning.
Output a CSV with paper metadata, code links, local clone paths, and commit hashes.
```

## Paper Artifact Example

```text
Use baseline-research.

Research papers about CSI feedback for FDD massive MIMO.
I need at least 30 papers from 2022-2026, including at least 10 with verified public code.
Download PDFs and TeX sources for the selected final papers into workspace/literature_research/papers/.
Compile TeX sources only if this machine already has a TeX toolchain. If not, skip compilation and record the missing environment.
Output a CSV with paper metadata, local PDF paths, local TeX source paths, TeX compile status, and compiled PDF paths.
```

## Seed Paper Example

```text
Use baseline-research.

Use paper/main.tex as the seed paper. Infer the research direction and experiment context from the paper, then ask me for any missing parameters before searching. I need at least 25 related papers, including at least 8 with verified public code, from 2021-2026.
```
