---
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
