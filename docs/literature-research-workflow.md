# Paper Research Workflow

This document mirrors the current `paper-research` workspace contract. The stage order is unchanged from the original literature research workflow; only plugin names and filesystem roots have been normalized.

## Stages

```text
Stage 0  research-requirement-collector
Stage 1  research-scope-locker
Stage 2  paper-discovery-scout
Stage 3  code-availability-verifier
Stage 4  repository-cloner
Stage 5  paper-artifact-collector
Stage 6  research-csv-writer
Stage 7  research-integrity-reviewer
```

Stage 0 and Stage 1 may stop for user input. Stage 2 through Stage 6 can be rejected by Stage 7 and rerun automatically when no new user input is required.

## Required Roots

Reports:

```text
workspace/report/paper-research/
```

Plugin work files and cloned repositories:

```text
workspace/work/paper-research/
workspace/work/paper-research/code/
```

Shared researched-paper artifacts:

```text
workspace/paper/pdf/{title}/paper.pdf
workspace/paper/tex/{title}/
workspace/paper/summary/{title}/
```

`workspace/paper/summary/{title}/` stores derived paper artifacts such as extracted text, metadata, summaries, compile logs, and compiled PDFs. The user's own manuscript must not be stored under `workspace/paper/`.

## Main Reports

```text
workspace/report/paper-research/requirements.md
workspace/report/paper-research/scope_report.md
workspace/report/paper-research/paper_candidates.csv
workspace/report/paper-research/paper_candidates.md
workspace/report/paper-research/code_verification.csv
workspace/report/paper-research/code_verification.md
workspace/report/paper-research/repository_clones.csv
workspace/report/paper-research/repository_clones.md
workspace/report/paper-research/paper_artifacts.csv
workspace/report/paper-research/paper_artifacts.md
workspace/report/paper-research/final_papers.csv
workspace/report/paper-research/research_summary.md
workspace/report/paper-research/integrity_report.md
workspace/report/paper-research/iteration_log.md
```

## Example Invocation

```text
Use paper-research.

Research papers about <your direction>. Include abstracts and citation counts, verify public code links, optionally clone verified repositories under workspace/work/paper-research/code/, and download paper artifacts under workspace/paper/pdf/{title}/, workspace/paper/tex/{title}/, and workspace/paper/summary/{title}/.
```
