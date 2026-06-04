# Baseline Research Workflows

Codex plugin and repo-local custom agents for interactive, loopback-capable literature research.

This repository provides one unified workflow. The user may start from either:

- a **research direction** such as "CSI feedback for FDD massive MIMO"; or
- a **seed paper**, which Codex uses to infer the research direction, evaluation context, and comparison boundary.

The workflow does not immediately search. It first collects the parameters needed by the agents, then locks the scope, then searches papers, verifies open-source code availability, optionally clones verified repositories to local storage, writes a CSV, and runs an integrity review. If a later stage fails, the orchestrator loops back to the failed stage and retries.

## Workflow

The main entry agent is:

```text
literature-research-orchestrator
```

Stages:

```text
Stage 0  research-requirement-collector   collect required user parameters
Stage 1  research-scope-locker            lock direction or seed-paper scope
Stage 2  paper-discovery-scout            search and shortlist papers
Stage 3  code-availability-verifier       verify code links when required
Stage 4  repository-cloner                clone verified repositories when requested
Stage 5  research-csv-writer              write final_papers.csv
Stage 6  research-integrity-reviewer      review and loop back on failures
```

The core behavior is iterative:

```text
stage output -> integrity review -> GO or REJECT -> loop back to target stage
```

Stage 0 and Stage 1 may stop for user input. Stage 2, Stage 3, Stage 4, and Stage 5 can be rejected and redone automatically when no new user input is required.

## Install From GitHub

With Codex CLI installed and authenticated:

```bash
codex plugin marketplace add git@github.com:zcluu/baseline-research.git --ref main
codex plugin add baseline-research-workflows@baseline-research
```

If SSH access is not configured:

```bash
codex plugin marketplace add https://github.com/zcluu/baseline-research.git --ref main
codex plugin add baseline-research-workflows@baseline-research
```

Start a new Codex session after installation.

## Install Agents Into A Target Repo

The plugin carries `.toml` custom agent templates as assets. They become active only after being installed into the target repository's `.codex/agents/` directory.

If you cloned this repository locally:

```bash
python3 /path/to/baseline-research/plugins/baseline-research-workflows/scripts/install_project_agents.py --repo /path/to/target-repo
```

If you installed the plugin through Codex, ask Codex in the target repo:

```text
Use baseline-research.

Install the literature research workflow agents into this repository.
If this repository has files from an older baseline-research workflow release, clean obsolete files first.
```

For a local clone, the clean upgrade command is:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo . --clean-obsolete
```

The installer is conservative:

- missing files are copied;
- identical files are left unchanged;
- existing files with different content are reported as conflicts and are not overwritten;
- obsolete files from older releases are removed only when `--clean-obsolete` is passed.

## Run The Workflow

Interactive mode is recommended:

```bash
cd /path/to/target-repo
codex --search --sandbox workspace-write --ask-for-approval never
```

Then say:

```text
Use baseline-research.

Research papers for this direction: <your direction>.
Before searching, collect the required parameters from me, including minimum paper count, minimum open-source/code paper count, target years, code verification level, whether verified repositories should be cloned locally, inclusion criteria, exclusion criteria, and final CSV requirements.
```

Or, if using a seed paper:

```text
Use baseline-research.

Use the paper in paper/main.tex as the seed. First infer the research direction and experimental context, then ask me for any missing parameters before searching papers.
```

To request local repository cloning:

```text
Use baseline-research.

Research papers about <your direction>.
I need at least 30 papers from 2022-2026, including at least 10 with verified public code.
Clone the verified repositories for the selected papers into workspace/literature_research/code/.
If SSH, tokens, private repository access, Git LFS, or submodules are needed, stop and tell me what local access I need to configure before cloning.
Output the final CSV with local clone paths and commit hashes.
```

You can also invoke the custom agent directly:

```text
Use the literature-research-orchestrator custom agent and execute the interactive literature research workflow.
```

Or with the launcher file after installing agents:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/literature-research-workflow-prompt.md
```

## Required Interaction

Stage 0 must collect:

- input type or seed source;
- research direction or seed paper;
- minimum total paper count;
- minimum open-source/code paper count;
- target year range or recency window;
- whether code links must be verified;
- whether verified repositories should be cloned locally;
- if cloning is requested: clone scope, target directory, public/private access expectations, auth setup, Git LFS policy, and submodule policy;
- output format, CSV by default;
- inclusion and exclusion constraints when available.

If required parameters are missing, Codex asks concise questions and stops. It must not search.

Stage 1 locks the scope. If the direction or seed-paper interpretation is ambiguous, Codex asks clarification questions and stops. It must not search.

Only after:

```text
requirements.md: STATUS: READY
scope_report.md: STATUS: LOCKED
```

may Stage 2 search papers.

## Outputs

All generated outputs go under:

```text
workspace/literature_research/
```

Main files:

```text
workspace/literature_research/reports/requirements.md
workspace/literature_research/reports/scope_report.md
workspace/literature_research/reports/paper_candidates.csv
workspace/literature_research/reports/code_verification.csv
workspace/literature_research/reports/repository_clones.csv
workspace/literature_research/reports/final_papers.csv
workspace/literature_research/reports/research_summary.md
workspace/literature_research/reports/integrity_report.md
workspace/literature_research/reports/iteration_log.md
```

The final CSV contains at least:

```csv
title,year,venue,publication_type,paper_url,arxiv_id,code_available,code_url,code_evidence,source_query,relevance_rationale,clone_requested,clone_status,local_clone_path,commit_hash,status
```

## Safe Code Policy

The code verifier checks public code evidence. It does not execute third-party code.

By default, it verifies links and repository evidence only. It does not clone repositories unless the user explicitly asks for local repository retrieval.

When cloning is requested, repositories are cloned under:

```text
workspace/literature_research/code/
```

If authentication or access setup is needed, the workflow stops before cloning and asks the user to configure local access, such as SSH keys, Git credential helper, GitHub CLI auth, or an environment variable such as `GITHUB_TOKEN`. Tokens, passwords, and private keys must not be pasted into workflow reports or prompts.

Not allowed by default:

```text
dependency installation
script execution
submodule initialization
Git LFS downloads
training or inference runs
```

## Repository Contents

```text
.codex/agents/                         repo-local custom agent definitions
.codex/literature-research-workflow-prompt.md
prompts/                               stage prompts used by the agents
plugins/baseline-research-workflows/   GitHub-installable Codex plugin package
.agents/plugins/marketplace.json       Codex marketplace manifest
marketplace.json                       compatibility copy of the marketplace manifest
docs/literature-research-workflow.md    detailed workflow documentation
```

This repository intentionally excludes private manuscript material and runtime artifacts:

```text
paper/
workspace/
.env
backups/
```

## Development Checks

Parse TOML and JSON:

```bash
python3 - <<'PY'
import json, pathlib, tomllib
for p in pathlib.Path('.codex/agents').glob('*.toml'):
    tomllib.loads(p.read_text())
for p in pathlib.Path('plugins/baseline-research-workflows/assets/agents').glob('*.toml'):
    tomllib.loads(p.read_text())
json.loads(pathlib.Path('plugins/baseline-research-workflows/.codex-plugin/plugin.json').read_text())
json.loads(pathlib.Path('.agents/plugins/marketplace.json').read_text())
json.loads(pathlib.Path('marketplace.json').read_text())
print('TOML and JSON parse checks passed')
PY
```

Check installer behavior in this repository:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo .
```

Expected synchronized result:

```text
Conflicts: 0
```
