# Baseline Research Workflows

## Paper Baseline Discovery

Entry agent:
- `baseline-orchestrator`

Main stages:
1. `paper-auditor`
2. `literature-scout-arxiv`, `literature-scout-pwc`, `literature-scout-venues`
3. `oss-verifier`
4. `experiment-designer`
5. `integrity-reviewer`

Outputs:
- `workspace/reports/audit_report.md`
- `workspace/reports/literature_candidates.md`
- `workspace/reports/oss_verification.json`
- `workspace/reports/baseline_registry.json`
- `workspace/reports/experiment_protocol.md`
- `workspace/reports/integrity_report.md`
- `workspace/baselines/`

Launcher:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/baseline-workflow-prompt.md
```

## Direction Literature Research

Entry agent:
- `direction-research-orchestrator`

Main stages:
1. `direction-scope-locker`
2. `direction-literature-scout-arxiv`, `direction-literature-scout-pwc`, `direction-literature-scout-venues`
3. `direction-oss-verifier` when public code is required
4. `direction-report-writer`
5. `direction-integrity-reviewer`

Outputs:
- `workspace/direction_research/reports/scope_report.md`
- `workspace/direction_research/reports/literature_candidates.md`
- `workspace/direction_research/reports/oss_verification.json` when code verification runs
- `workspace/direction_research/reports/baseline_registry.json` when code verification runs
- `workspace/direction_research/reports/direction_research_report.md`
- `workspace/direction_research/reports/integrity_report.md`
- `workspace/direction_research/baselines/`

Launcher:

```bash
codex --search --sandbox workspace-write --ask-for-approval never
```

Then prompt:

```text
Use the direction-research-orchestrator custom agent.

我要根据研究方向做文献调研：<your direction>.
开始搜索前必须先澄清术语歧义、同义词、包含范围、排除范围、目标年份、是否需要公开代码和最终输出形式。
```

## Router

Entry agent:
- `research-workflow-router`

Use when the user wants a single entry point and may request either workflow.

Launcher:

```bash
codex --search --sandbox workspace-write --ask-for-approval never \
  "Use the research-workflow-router custom agent. <your request>"
```
