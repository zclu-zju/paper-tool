---
name: paper-research
description: Use for interactive literature research in a Codex repo. Installs repo-local custom agents from this plugin, then runs a loopback workflow that collects required parameters, locks scope from a user direction or seed paper, discovers papers with abstracts and citation counts, verifies code availability while prioritizing high-citation in-scope papers for GitHub searches, optionally clones verified repositories, optionally downloads paper PDFs/TeX sources, writes a CSV, and sends failed stages back for revision.
---

# Paper Research

This skill installs and launches a single interactive literature research workflow.

The workflow accepts either:
- a research direction, topic, keyword set, or prompt; or
- a seed paper in the target repository, which is used to infer the research direction and experimental context.

It is intentionally iterative rather than one-pass. Stage 7 can reject earlier stages and send the orchestrator back to redo only the failed stage.

## Install Agents

The plugin carries custom agent templates in `assets/agents/`, but those agents become active only after they are installed into the target repo's `.codex/agents/`.

From a local clone:

```bash
python3 plugins/paper-research/scripts/install_project_agents.py --repo .
```

From an installed plugin cache, resolve the installer relative to this skill directory:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo>
```

When upgrading from the older two-workflow release, clean obsolete files:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo> --clean-obsolete
```

The installer is conservative. It copies missing files, leaves identical files unchanged, reports conflicts without overwriting, and removes old known files only when `--clean-obsolete` is passed.

## Launch

After installing agents, invoke:

```text
Use the literature-research-orchestrator custom agent and execute the interactive literature research workflow.
```

Or use the launcher file:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/literature-research-workflow-prompt.md
```

## Interaction Contract

Stage 0 must collect required parameters before any search:
- input type or seed source;
- direction or seed paper;
- minimum total paper count;
- minimum open-source/code paper count;
- target year range;
- code verification level;
- whether verified repositories should be cloned locally;
- if cloning is requested: clone scope, target directory, public/private access expectations, auth setup, Git LFS policy, and submodule policy;
- whether paper PDFs or TeX sources should be downloaded locally;
- if paper artifact retrieval is requested: artifact scope, artifact types, target directory, TeX compile policy, and missing dependency handling;
- final output format, CSV by default;
- inclusion and exclusion constraints when available.

If required parameters are missing, the orchestrator asks concise questions and stops.

Stage 1 locks the scope. If the direction or seed-paper interpretation is ambiguous, the orchestrator asks clarification questions and stops.

Only after requirements are `READY` and scope is `LOCKED` can the workflow search papers.

## Outputs

All generated outputs go under:

```text
workspace/work/paper-research/
```

The main final output is:

```text
workspace/report/paper-research/final_papers.csv
```

Required CSV columns:

```csv
title,year,venue,publication_type,paper_url,abstract,citation_count,citation_source,arxiv_id,code_available,code_url,code_evidence,source_query,relevance_rationale,clone_requested,clone_status,local_clone_path,commit_hash,artifact_requested,pdf_download_status,local_pdf_path,tex_download_status,local_tex_source_path,tex_compile_status,compiled_pdf_path,status
```

Selected papers must include non-empty abstracts. If abstracts are missing, the integrity reviewer sends the workflow back to Stage 2 for abstract replenishment or paper replacement.

Selected papers must include `citation_count` and `citation_source`. If citation counts are unavailable after lookup, Stage 2 records `UNKNOWN` with the failed lookup source. When Stage 3 searches GitHub or other repository hosts for code, it prioritizes higher-citation in-scope candidates first.

## Repository Cloning

Repository cloning is opt-in. The workflow must ask whether local repository retrieval is required before searching if the user has not already specified it.

When cloning is requested, Stage 4 clones verified repositories under:

```text
workspace/work/paper-research/code/
```

If SSH keys, API tokens, private repository access, Git credential helper setup, GitHub CLI auth, Git LFS, or submodules are needed, the workflow stops and asks the user to configure the required local access mechanism before retrying Stage 4. Do not ask the user to paste secrets into prompts or reports.

## Paper Artifact Retrieval

Paper artifact retrieval is opt-in. The workflow must ask whether PDF/TeX retrieval is required before searching if the user has not already specified it.

When requested, Stage 5 downloads public PDFs or public TeX/source archives under:

```text
workspace/paper/summary/
```

If TeX compilation is requested, Stage 5 compiles only when a local TeX toolchain is available. If no TeX environment exists and the policy is `COMPILE_IF_ENV_AVAILABLE`, it records `SKIPPED_NO_TEX_ENV` and continues. If compilation is attempted, the workflow verifies that the compiled PDF exists.

## Loopback

The integrity reviewer can reject and return to:
- Stage 0 Requirement Collector;
- Stage 1 Scope Locker;
- Stage 2 Paper Discovery Scout;
- Stage 3 Code Availability Verifier;
- Stage 4 Repository Cloner;
- Stage 5 Paper Artifact Collector;
- Stage 6 CSV Writer.

If no new user input is required, the orchestrator retries automatically.
