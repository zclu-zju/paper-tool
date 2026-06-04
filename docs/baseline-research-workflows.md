# Baseline Research Workflows

This repository now supports two independent Codex custom-agent workflows:

1. **Paper baseline discovery**: start from `paper/` and find verified public-code baselines.
2. **Direction literature research**: start from a user-provided direction/prompt, clarify ambiguity first, then research literature under the locked scope.

The workflows share some concepts, but their outputs are intentionally isolated.

## Backup

Before the new workflow files were added, the original `.codex` directory was backed up to:

```bash
workspace/backups/codex-backup-20260604T033902Z.tar.gz
```

Restore manually only if you intentionally want to return to the previous `.codex` state.

## Repo-Local Agents

The current repo has these workflow entry agents:

- `baseline-orchestrator`: paper -> verified baseline workflow.
- `direction-research-orchestrator`: direction/prompt -> scope-locked literature research workflow.
- `research-workflow-router`: single entry point that chooses between the two workflows.

Direction research adds these workers:

- `direction-scope-locker`
- `direction-literature-scout-arxiv`
- `direction-literature-scout-pwc`
- `direction-literature-scout-venues`
- `direction-oss-verifier`
- `direction-report-writer`
- `direction-integrity-reviewer`

## Output Locations

Paper baseline workflow:

```text
workspace/reports/
workspace/baselines/
```

Direction literature workflow:

```text
workspace/direction_research/reports/
workspace/direction_research/baselines/
```

This separation prevents the direction workflow from overwriting the existing paper-baseline reports.

## Direct Execution In This Repo

Run the existing paper-baseline workflow:

```bash
cd /nfs4/lzc/LLMWorkSpace/baseline-research
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/baseline-workflow-prompt.md
```

Run the direction workflow interactively:

```bash
cd /nfs4/lzc/LLMWorkSpace/baseline-research
codex --search --sandbox workspace-write --ask-for-approval never
```

Then enter:

```text
Use the direction-research-orchestrator custom agent.

我要根据研究方向做文献调研：<你的方向>。
开始搜索前必须先澄清术语歧义、同义词、包含范围、排除范围、目标年份、是否需要公开代码和最终输出形式。
```

Use the router entry point when you want Codex to choose the workflow:

```bash
cd /nfs4/lzc/LLMWorkSpace/baseline-research
codex --search --sandbox workspace-write --ask-for-approval never \
  "Use the research-workflow-router custom agent. 帮我根据当前 paper 找 baseline。"
```

Or:

```bash
codex --search --sandbox workspace-write --ask-for-approval never \
  "Use the research-workflow-router custom agent. 我想调研一个方向：<你的方向>。开始前先澄清范围。"
```

## Direction Workflow Rule

The direction workflow must not search immediately.

It first writes:

```text
workspace/direction_research/reports/scope_report.md
```

If the report says:

```text
STATUS: NEEDS_USER_CONFIRMATION
```

Codex must stop and ask the listed questions.

Only after:

```text
STATUS: LOCKED
```

may the literature scouts begin.

## Plugin Package

A plugin-style package is available at:

```text
plugins/baseline-research-workflows/
```

It includes:

```text
.codex-plugin/plugin.json
skills/baseline-research/SKILL.md
assets/agents/*.toml
assets/prompts/codex/*.md
assets/prompts/project/*.md
scripts/install_project_agents.py
```

The plugin does not make `.toml` custom agents active by hiding them inside `assets/`.
To make the subagents active in a target repo, install the templates into that repo:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo .
```

The installer is conservative:

- missing files are copied;
- identical files are unchanged;
- existing files with different content are reported as conflicts and are not overwritten;
- use `--force` only when you intentionally want to overwrite.

## Installing The Plugin From GitHub

This repository has a root marketplace file:

```text
marketplace.json
```

Install it from GitHub:

```bash
codex plugin marketplace add git@github.com:zcluu/baseline-research.git --ref main
codex plugin add baseline-research-workflows@baseline-research
```

If SSH is not configured:

```bash
codex plugin marketplace add https://github.com/zcluu/baseline-research.git --ref main
codex plugin add baseline-research-workflows@baseline-research
```

After plugin installation, in a new Codex session you can ask:

```text
使用 baseline-research，帮我根据当前论文找 baseline。
```

or:

```text
使用 baseline-research，帮我调研方向：<你的方向>。必须先澄清术语和边界。
```

If the target repo does not already have the custom agents, ask Codex to run:

```bash
python3 <installed-plugin-root>/scripts/install_project_agents.py --repo <target-repo>
```

For this repo, the direct path is:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo .
```

## Development Checks

Basic structural checks:

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

Conservative installer check:

```bash
python3 plugins/baseline-research-workflows/scripts/install_project_agents.py --repo .
```

Expected result in this repo after synchronization:

```text
Copied: 0
Conflicts: 0
```
