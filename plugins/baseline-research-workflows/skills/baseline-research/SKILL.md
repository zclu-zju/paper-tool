---
name: baseline-research
description: Use for paper-based baseline discovery or direction-based literature research in a Codex repo. Installs repo-local custom agents from this plugin when missing, routes paper requests to baseline-orchestrator, and routes direction/topic/prompt research requests to direction-research-orchestrator with mandatory scope clarification before search.
---

# Baseline Research

This skill is the entry point for two repo-local Codex workflows:

1. **Paper baseline discovery**: audit the current paper and find verified public-code baselines.
2. **Direction literature research**: clarify a user-provided direction first, then research literature under the locked scope.

The plugin carries custom agent templates in `assets/agents/`, but those agents become usable only after they are installed into the target repo's `.codex/agents/`.

## Quick Start

Before launching a workflow, ensure project agents are installed:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo .
```

If this skill is installed from a Codex plugin cache, resolve the installer relative to this skill directory:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo>
```

From a local clone of this repository, use:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo <target-repo>
```

The installer is conservative: it copies missing files, leaves identical files unchanged, and reports conflicts without overwriting.

## Routing

Use the paper workflow when the user asks to:
- find baselines for a paper;
- audit an existing manuscript's comparisons;
- run the existing baseline discovery workflow;
- verify public-code baselines for the paper in `paper/`.

After installing agents, invoke:

```text
Use the baseline-orchestrator custom agent and execute the full baseline discovery workflow.
```

Use the direction workflow when the user asks to:
- research a topic, direction, keyword, proposal, or prompt;
- collect literature without starting from a specific paper;
- clarify ambiguous terminology before searching;
- compare sub-directions or map a field.

After installing agents, invoke:

```text
Use the direction-research-orchestrator custom agent and execute the direction-based literature research workflow.
```

For ambiguous user intent, invoke:

```text
Use the research-workflow-router custom agent.
```

## Hard Rules

- Do not run direction literature search before `direction-scope-locker` outputs `STATUS: LOCKED`.
- If `scope_report.md` outputs `STATUS: NEEDS_USER_CONFIRMATION`, ask the user the listed questions and stop.
- Keep paper workflow outputs under `workspace/reports/` and `workspace/baselines/`.
- Keep direction workflow outputs under `workspace/direction_research/reports/` and `workspace/direction_research/baselines/`.
- Never execute third-party code from retrieved repositories.
- Do not overwrite existing `.codex/agents/` files unless the user explicitly asks for forced sync.

## Files

- Agent templates: `assets/agents/*.toml`
- Codex prompt launchers: `assets/prompts/codex/*.md`
- Project prompts: `assets/prompts/project/*.md`
- Installer: `scripts/install_project_agents.py`

See `references/workflows.md` for the workflow map and command examples.
