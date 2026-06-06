# Paper Tool

This repository is a single-repository, multi-branch Codex marketplace for paper workflows.

## Branches

```text
main        aggregate marketplace branch
research    source branch for plugins/paper-research
reviewer    source branch for plugins/paper-reviewer
experiment  source branch for plugins/paper-experiment
```

Develop plugin behavior on the matching plugin branch. The `main` branch is the installable marketplace branch and should normally be updated by automation.

## Install

```bash
codex plugin marketplace add git@github.com:zclu-zju/paper-tool.git --ref main
codex plugin add paper-research@paper-tool
codex plugin add paper-reviewer@paper-tool
codex plugin add paper-experiment@paper-tool
```

Install only the plugins needed for the target workflow.

## Development Workflow

Develop each plugin on its own branch:

```bash
git checkout research
# edit the branch like git@github.com:zcluu/paper-research.git
git push origin research
```

```bash
git checkout reviewer
# edit the branch like git@github.com:zcluu/paper-reviewer.git
git push origin reviewer
```

```bash
git checkout experiment
# edit the branch like git@github.com:zcluu/paper-experiment.git
git push origin experiment
```

When one of those branches is pushed, GitHub Actions syncs the matching plugin package into the `main` branch. You can also run the sync manually:

```bash
git checkout main
python3 scripts/sync_plugins_from_branches.py
```

## Workspace Contract

Reports remain plugin-scoped:

```text
workspace/report/paper-research/
workspace/report/paper-reviewer/
workspace/report/paper-experiment/
```

Shared researched-paper artifacts are stored under:

```text
workspace/paper/pdf/{title}/paper.pdf
workspace/paper/tex/{title}/
workspace/paper/summary/{title}/
```

Non-report execution artifacts are plugin-scoped:

```text
workspace/work/{plugin}/
```
