# Paper Research

Codex plugin and repo-local custom agents for interactive, loopback-capable literature research.

The workflow can start from either a research direction or a seed paper. It collects required parameters, locks the scope, searches papers with abstracts and citation counts, verifies public code links when requested, optionally clones verified repositories, optionally downloads paper PDFs or TeX sources, writes CSV reports, and runs an integrity review with loopback.

## Install From GitHub

```bash
codex plugin marketplace add git@github.com:zcluu/paper-research.git --ref main
codex plugin add paper-research@paper-research
```

If SSH access is not configured:

```bash
codex plugin marketplace add https://github.com/zcluu/paper-research.git --ref main
codex plugin add paper-research@paper-research
```

Start a new Codex session after installation.

## Development Source

This repository is the source of truth for the `paper-research` plugin package. Develop prompts, agents, installer behavior, and the skill under:

```text
plugins/paper-research/
```

The `paper-tool` repository is only the aggregate marketplace and integration-test target. After changing this repository, run the sync script from `paper-tool` to copy the plugin package into the aggregate marketplace.

## Install Agents Into A Target Repo

For a local clone:

```bash
python3 plugins/paper-research/scripts/install_project_agents.py --repo /path/to/target-repo --clean-obsolete
```

If installed through Codex, ask Codex in the target repo:

```text
Use paper-research.

Install the paper research workflow agents into this repository.
```

The installer is conservative: it copies missing files, leaves identical files unchanged, reports conflicts without overwriting, and removes known obsolete files only when `--clean-obsolete` is passed.

## Run The Workflow

Interactive mode is recommended:

```bash
cd /path/to/target-repo
codex --search --sandbox workspace-write --ask-for-approval never
```

Then say:

```text
Use paper-research.

Research papers about <your direction>. Collect the required parameters first, including paper count, year range, code verification needs, whether verified repositories should be cloned, whether PDFs or TeX sources should be downloaded, inclusion/exclusion criteria, and final CSV requirements. Include abstracts and citation counts.
```

To request local repository cloning:

```text
Use paper-research.

Research papers about <your direction>. I need at least 30 papers from 2022-2026, including at least 10 with verified public code. Clone verified repositories under workspace/work/paper-research/code/. Output the final CSV with local clone paths and commit hashes.
```

To request paper artifact retrieval:

```text
Use paper-research.

Research papers about <your direction>. Download available PDFs under workspace/paper/pdf/{title}/paper.pdf and TeX sources under workspace/paper/tex/{title}/. Put extracted text, metadata, summaries, compile logs, and compiled PDFs under workspace/paper/summary/{title}/. Output the final CSV with local artifact paths.
```

You can also invoke the custom agent directly:

```text
Use the literature-research-orchestrator custom agent and execute the interactive literature research workflow.
```

Or with the launcher file after installing agents:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/literature-research-workflow-prompt.md
```

## Workflow

```text
Stage 0  research-requirement-collector   collect required user parameters
Stage 1  research-scope-locker            lock direction or seed-paper scope
Stage 2  paper-discovery-scout            search and shortlist papers
Stage 3  code-availability-verifier       verify code links when required
Stage 4  repository-cloner                clone verified repositories when requested
Stage 5  paper-artifact-collector         download PDFs/TeX and compile TeX when requested
Stage 6  research-csv-writer              write final_papers.csv
Stage 7  research-integrity-reviewer      review and loop back on failures
```

## Workspace Contract

Reports are plugin-scoped:

```text
workspace/report/paper-research/requirements.md
workspace/report/paper-research/scope_report.md
workspace/report/paper-research/paper_candidates.csv
workspace/report/paper-research/code_verification.csv
workspace/report/paper-research/repository_clones.csv
workspace/report/paper-research/paper_artifacts.csv
workspace/report/paper-research/final_papers.csv
workspace/report/paper-research/research_summary.md
workspace/report/paper-research/integrity_report.md
workspace/report/paper-research/iteration_log.md
```

Shared researched-paper artifacts are stored outside the plugin report folder:

```text
workspace/paper/pdf/{title}/paper.pdf
workspace/paper/tex/{title}/
workspace/paper/summary/{title}/
```

Non-report execution artifacts are plugin-scoped:

```text
workspace/work/paper-research/code/
```

The final CSV contains at least:

```csv
title,year,venue,publication_type,paper_url,abstract,citation_count,citation_source,arxiv_id,code_available,code_url,code_evidence,source_query,relevance_rationale,clone_requested,clone_status,local_clone_path,commit_hash,artifact_requested,pdf_download_status,local_pdf_path,tex_download_status,local_tex_source_path,tex_compile_status,compiled_pdf_path,status
```

## Safe Code Policy

The code verifier checks public code evidence. It does not execute third-party code. Cloning is opt-in and stops for local authentication, Git LFS, submodule, or private-access setup when required.

Not allowed by default:

```text
dependency installation
script execution
submodule initialization
Git LFS downloads
training or inference runs
TeX shell escape
```
