# Draft Paper Reviewer

This repository contains a local Codex plugin:

```text
plugins/draft-paper-reviewer/
```

The plugin implements a TeX-only draft-paper review and revision workflow. It is built for helping the user develop their own manuscript, including incomplete drafts with missing experiments, placeholder tables, unfinished figures, or partial sections.

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
Stage 12 paired-revision-coordinator
Stage 13 revision-verifier
Stage 14 evidence-review-integrity-reviewer
Stage 15 ultimate-report-synthesizer
```

Stage 0 accepts only a TeX source folder or explicit `.tex` root file. If the submitted manuscript is PDF, Word, Markdown, plain text, image-only, or has no `.tex` source, the workflow writes `STATUS: UNSUPPORTED_INPUT` and stops.

The workflow must confirm all parameters with defaults in Stage 0, then confirm the inferred topic scope with the user before searching related literature. Review findings must cite manuscript locations and evidence-map rows.

Reports are numbered in reading order from `00_` onward. The final report is `workspace/draft_paper_review/reports/99_ultimate_summary.md`, which is intended to be read first after a run completes.

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
workspace/draft_paper_review/reports/31_deferred_issues.md
```

Objective limitations such as missing experiments, unavailable raw data, absent approvals, missing model checkpoints, proprietary datasets, placeholder tables, or unfinished figures can be deferred instead of causing endless loopback. Deferred issues remain visible in the final risk summary.

If a score dimension cannot be assessed because required evidence is objectively absent, the synthesizer can mark it `N/A_OBJECTIVE_MISSING` according to the missing-score policy rather than assigning an artificial low score.

Missing experiments, placeholder tables, unfinished figures, and absent numeric results constrain only the affected result claims. They must not automatically weaken the manuscript's motivation, method framing, contribution language, literature positioning, or terminology. The workflow asks agents to surface validated strengths and help the draft state them confidently while preserving evidence boundaries.

## Writing And Revision Policy

The revision workflow uses one-to-one reviewer/reviser pairs for fixed or issue-based scopes such as abstract/contribution, introduction, motivation, related positioning, method exposition, experiment setup, results/tables, terminology/style, and limitations/reproducibility. Each pair alternates reviewer -> writer -> same reviewer until accepted, capped, deferred, or blocked on user input.

Every paired round is recorded in:

```text
workspace/draft_paper_review/reports/27_revision_ledger.jsonl
workspace/draft_paper_review/reports/27_revision_ledger.xlsx
workspace/draft_paper_review/reports/27_revision_ledger_csv/
```

The primary ledger format is `.xlsx`, generated with Python `openpyxl`. CSV exports are fallback artifacts.

The revision prompts incorporate ML paper writing guidance:

- preserve a clear one-sentence contribution;
- keep the "what / why evidence / so what" narrative visible;
- make contribution bullets specific and falsifiable;
- learn section-level writing moves from related papers, including abstract structure, introduction moves, contribution framing, method exposition, experiment/table narration, limitations, and field term usage;
- strengthen defensible claims instead of only qualifying risky ones;
- avoid inventing experiment results, citations, or BibTeX;
- verify citations through metadata sources or mark explicit placeholders;
- preserve honest limitations;
- add or check reproducibility, compute, data/code access, ethics/broader-impact, and venue checklist text when relevant.

Stage 9 includes a dedicated term-usage consistency auditor. It extracts technical terms, acronyms, dataset names, method names, metric names, proper nouns, and related variants, checks contextual consistency across the manuscript, compares usage against related literature, and writes `workspace/draft_paper_review/reports/specialist_audits/15_term_usage_consistency_audit.md`.

## Install Agents Into A Target Repo

```bash
python3 plugins/draft-paper-reviewer/scripts/install_project_agents.py --repo /path/to/target-repo
```

The installer copies:

```text
assets/agents/           -> .codex/agents/
assets/prompts/codex/    -> .codex/
assets/prompts/project/  -> .codex/prompts/draft-paper-reviewer/
assets/tools/            -> .codex/tools/draft-paper-reviewer/
```

It is conservative about current files: existing different files are reported as conflicts and are not overwritten unless `--force` is used. Known obsolete files from older versions are removed by default so plugin prompts do not remain under a visible repository-root `prompts/` directory. Use `--keep-obsolete` only when intentionally preserving old local installs.

If the xlsx ledger dependency is missing in the target environment, install it with:

```bash
python3 -m pip install -r .codex/tools/draft-paper-reviewer/requirements.txt
```

## Run

After installing agents into the target repo:

```text
Use draft-paper-reviewer.

Review the TeX manuscript at <TeX source folder or .tex root file>. Confirm all workflow parameters first, infer the topic, ask me to confirm it, then search related literature, build an evidence map, run the review/audit workflow, and revise copied TeX files with paired reviewer/reviser loops if needed.
```

Or:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/draft-paper-review-workflow-prompt.md
```

## Outputs

All workflow outputs go under:

```text
workspace/draft_paper_review/
```

Key reports:

```text
workspace/draft_paper_review/reports/00_requirements.md
workspace/draft_paper_review/reports/01_manuscript_inventory.md
workspace/draft_paper_review/reports/02_topic_scope.md
workspace/draft_paper_review/reports/03_literature_candidates.csv
workspace/draft_paper_review/reports/03_literature_discovery.md
workspace/draft_paper_review/reports/04_paper_artifacts.csv
workspace/draft_paper_review/reports/04_paper_artifacts.md
workspace/draft_paper_review/reports/05_evidence_map.csv
workspace/draft_paper_review/reports/05_evidence_map.md
workspace/draft_paper_review/reports/06_reviewer_configuration.md
workspace/draft_paper_review/reports/reviewer_reports/
workspace/draft_paper_review/reports/specialist_audits/
workspace/draft_paper_review/reports/23_editorial_decision.md
workspace/draft_paper_review/reports/24_revision_plan.md
workspace/draft_paper_review/reports/25_paired_revision_summary.md
workspace/draft_paper_review/reports/27_revision_ledger.xlsx
workspace/draft_paper_review/reports/28_revision_verification.md
workspace/draft_paper_review/reports/29_integrity_report.md
workspace/draft_paper_review/reports/30_iteration_log.md
workspace/draft_paper_review/reports/31_deferred_issues.md
workspace/draft_paper_review/reports/99_ultimate_summary.md
```
