# Evidence Based Paper Review Workflows

This repository contains a local Codex plugin:

```text
plugins/evidence-based-paper-review-workflows/
```

The plugin implements an evidence-driven manuscript review workflow modeled after `baseline-research`, but specialized for reviewing and revising academic papers using a local related-literature evidence pack.

## Core Workflow

```text
Stage 0  review-requirement-collector
Stage 1  manuscript-ingestor
Stage 2  topic-scope-analyst
Stage 3  user-scope-confirmation-gate
Stage 4  literature-discovery-scout
Stage 5  review-paper-artifact-collector
Stage 6  evidence-map-builder
Stage 7  reviewer-panel-configurator
Stage 8  evidence-reviewer-panel-coordinator
Stage 9  specialist-diagnostic-panel-coordinator
Stage 10 editorial-synthesizer-scorer
Stage 11 revision-planner
Stage 12 manuscript-polisher-reviser
Stage 13 revision-verifier
Stage 14 evidence-review-integrity-reviewer
```

The workflow must confirm the inferred topic scope with the user before searching related literature. Review findings must cite manuscript locations and evidence-map rows.

## Iteration Policy

The workflow supports configurable loopback controls:

```text
Maximum Total Workflow Iterations: UNLIMITED or integer
Maximum Same Stage/Problem Iterations: integer, default 3
Objective Limitation Policy: DEFER_AND_CONTINUE / ASK_USER / BLOCK
Missing Score Policy: MARK_NA_AND_REWEIGHT / MARK_NA_NO_REWEIGHT / BLOCK
```

When the same stage/problem pair reaches the configured cap, the orchestrator records the issue in:

```text
workspace/evidence_paper_review/reports/deferred_issues.md
```

Objective limitations such as missing experiments, unavailable raw data, absent approvals, missing model checkpoints, proprietary datasets, or unavailable TeX source can be deferred instead of causing endless loopback. Deferred issues remain visible in the final risk summary.

If a score dimension cannot be assessed because required evidence is objectively absent, the synthesizer can mark it `N/A_OBJECTIVE_MISSING` according to the missing-score policy rather than assigning an artificial low score.

## Writing And Revision Policy

The revision prompts incorporate ML paper writing guidance:

- preserve a clear one-sentence contribution;
- keep the "what / why evidence / so what" narrative visible;
- make contribution bullets specific and falsifiable;
- avoid inventing experiment results, citations, or BibTeX;
- verify citations through metadata sources or mark explicit placeholders;
- preserve honest limitations;
- add or check reproducibility, compute, data/code access, ethics/broader-impact, and venue checklist text when relevant.

## Install Agents Into A Target Repo

```bash
python3 plugins/evidence-based-paper-review-workflows/scripts/install_project_agents.py --repo /path/to/target-repo
```

The installer copies:

```text
assets/agents/           -> .codex/agents/
assets/prompts/codex/    -> .codex/
assets/prompts/project/  -> prompts/
```

It is conservative by default: existing different files are reported as conflicts and are not overwritten unless `--force` is used.

## Run

After installing agents into the target repo:

```text
Use evidence-paper-review.

Review the paper at <PDF or TeX source folder>. Infer the topic first, ask me to confirm it, then search related literature, build an evidence map, run the review/audit workflow, and revise the manuscript if needed.
```

Or:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/evidence-paper-review-workflow-prompt.md
```

## Outputs

All workflow outputs go under:

```text
workspace/evidence_paper_review/
```

Key reports:

```text
workspace/evidence_paper_review/reports/evidence_map.csv
workspace/evidence_paper_review/reports/reviewer_reports/
workspace/evidence_paper_review/reports/specialist_audits/
workspace/evidence_paper_review/reports/editorial_decision.md
workspace/evidence_paper_review/reports/revision_plan.md
workspace/evidence_paper_review/reports/revision_verification.md
workspace/evidence_paper_review/reports/integrity_report.md
workspace/evidence_paper_review/reports/deferred_issues.md
```
