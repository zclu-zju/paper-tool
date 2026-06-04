# Baseline Research Workflows

Codex workflow package for research baseline discovery and direction-based literature review.

This repository provides a GitHub-installable Codex plugin plus repo-local custom agent templates. It supports two independent workflows:

1. **Paper baseline discovery**: start from a paper in the target repository, audit its evaluation context, discover in-domain baselines, verify public code, and write a fair comparison protocol.
2. **Direction literature research**: start from a user-provided research direction or prompt, clarify ambiguous terminology first, lock the scope, then search and synthesize literature.

The workflows share reusable worker agents, but their outputs are isolated.

## What Is Included

```text
.codex/agents/                         # Repo-local custom agent definitions
.codex/*workflow-prompt.md             # Direct launcher prompts
prompts/                               # Stage prompts used by the agents
plugins/baseline-research-workflows/   # Codex plugin package
marketplace.json                       # GitHub-installable plugin marketplace
docs/baseline-research-workflows.md    # Detailed usage notes
```

This repository intentionally excludes private manuscript material and runtime artifacts:

```text
paper/
workspace/
.env
```

## Install From GitHub

On another machine with Codex CLI installed and authenticated:

```bash
codex plugin marketplace add git@github.com:zcluu/baseline-research.git --ref main
codex plugin add baseline-research-workflows@baseline-research
```

If SSH access is not configured, use the HTTPS form:

```bash
codex plugin marketplace add https://github.com/zcluu/baseline-research.git --ref main
codex plugin add baseline-research-workflows@baseline-research
```

Start a new Codex session after installation.

## Install Agents Into A Target Repo

The plugin carries `.toml` custom agent templates as assets. They become active only after being installed into the target repository's `.codex/agents/` directory.

If you cloned this repository locally, run this from the target repo:

```bash
python3 /path/to/baseline-research/plugins/baseline-research-workflows/scripts/install_project_agents.py --repo .
```

If you are using the installed plugin through Codex, ask Codex:

```text
Use baseline-research. Install the baseline research workflow agents into this repository, then confirm the installed files.
```

The installer is conservative:

- missing files are copied;
- identical files are left unchanged;
- existing files with different content are reported as conflicts and are not overwritten;
- use `--force` only when you intentionally want to overwrite target files.

## Use Workflow 1: Paper Baseline Discovery

Use this when the target repository contains a paper under `paper/`.

Direct CLI launcher:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/baseline-workflow-prompt.md
```

Interactive prompt:

```text
Use the baseline-orchestrator custom agent and execute the full baseline discovery workflow.
```

Default outputs:

```text
workspace/reports/
workspace/baselines/
```

## Use Workflow 2: Direction Literature Research

Use this when you have a topic, direction, keyword set, proposal, or open-ended research prompt rather than a specific paper.

Interactive launcher:

```bash
codex --search --sandbox workspace-write --ask-for-approval never
```

Then prompt:

```text
Use the direction-research-orchestrator custom agent.

Research this direction: <your direction>.
Before searching, clarify ambiguous terms, synonyms, included scope, excluded scope, target years, public-code requirements, and expected output format.
```

The direction workflow must not search immediately. It first writes:

```text
workspace/direction_research/reports/scope_report.md
```

If the scope report contains:

```text
STATUS: NEEDS_USER_CONFIRMATION
```

Codex must ask the clarification questions and stop. Literature search starts only after:

```text
STATUS: LOCKED
```

Default outputs:

```text
workspace/direction_research/reports/
workspace/direction_research/baselines/
```

## Use The Router

Use the router when you want one entry point and want Codex to choose the correct workflow:

```bash
codex --search --sandbox workspace-write --ask-for-approval never \
  "Use the research-workflow-router custom agent. Find baselines for the paper in this repository."
```

Or:

```bash
codex --search --sandbox workspace-write --ask-for-approval never \
  "Use the research-workflow-router custom agent. Research the direction: <your direction>. Clarify scope before searching."
```

## Safe Retrieval Policy

Repository verification agents may shallow-clone public-code baselines, but they must not execute third-party code.

Allowed:

```bash
git clone --depth 1 <repo> <target>
git rev-parse HEAD
```

Not allowed:

```text
dependency installation
script execution
submodule initialization
Git LFS downloads
training or inference runs
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
Copied: 0
Conflicts: 0
```

## Notes

- The plugin is the installation and entry layer.
- The active subagent behavior comes from `.codex/agents/*.toml` in the target repository.
- Paper workflow outputs and direction workflow outputs are intentionally separated.
- Private papers, generated reports, cloned baselines, backups, and `.env` files should not be committed.
