# Paper Reviewer

This repository contains the `paper-reviewer` Codex plugin:

```text
plugins/paper-reviewer/
```

The plugin implements a TeX-only draft-paper review and revision workflow. It is built for helping the user develop their own manuscript, including incomplete drafts with missing experiments, placeholder tables, unfinished figures, or partial sections.

## Install From GitHub

```bash
codex plugin marketplace add git@github.com:zcluu/paper-reviewer.git --ref main
codex plugin add paper-reviewer@paper-reviewer
```

Start a new Codex session after installation.

## Development Source

This repository is the source of truth for the `paper-reviewer` plugin package. Develop prompts, agents, tools, installer behavior, and the skill under:

```text
plugins/paper-reviewer/
```

The `paper-tool` repository is only the aggregate marketplace and integration-test target. After changing this repository, run the sync script from `paper-tool` to copy the plugin package into the aggregate marketplace.

## Core Workflow

```text
Stage 0  review-requirement-collector
Stage 1  manuscript-ingestor
Stage 2  topic-scope-analyst
Stage 3  user-scope-confirmation-gate
Stage 4  literature-discovery-scout
Stage 5  review-paper-artifact-collector
Stage 6  downloaded-paper-convention-miner
Stage 7  figure-table-retention-gatekeeper
Stage 8  evidence-map-builder
Stage 9  reviewer-panel-configurator
Stage 10 evidence-reviewer-panel-coordinator
Stage 11 specialist-diagnostic-panel-coordinator
Stage 12 editorial-synthesizer-scorer
Stage 13 revision-planner
Stage 14 paired-revision-coordinator
Stage 15 revision-verifier
Stage 16 evidence-review-integrity-reviewer
Stage 17 ultimate-report-synthesizer
Stage 18 latexdiff-change-auditor
```

Stage 0 accepts only a TeX source folder or explicit `.tex` root file. If the submitted manuscript is PDF, Word, Markdown, plain text, image-only, or has no `.tex` source, the workflow writes `STATUS: UNSUPPORTED_INPUT` and stops.

## Install Agents Into A Target Repo

```bash
python3 plugins/paper-reviewer/scripts/install_project_agents.py --repo /path/to/target-repo
```

The installer copies:

```text
assets/agents/           -> .codex/agents/
assets/prompts/codex/    -> .codex/
assets/prompts/project/  -> .codex/prompts/draft-paper-reviewer/
assets/tools/            -> .codex/tools/draft-paper-reviewer/
```

The internal installed prompt/tool directory remains `draft-paper-reviewer` for compatibility with the existing custom-agent names. The public plugin name is `paper-reviewer`.

If the xlsx ledger or PDF text extraction dependency is missing in the target environment, install it with:

```bash
python3 -m pip install -r .codex/tools/draft-paper-reviewer/requirements.txt
```

## Run

After installing agents into the target repo:

```text
Use paper-reviewer.

Review the TeX manuscript at <TeX source folder or .tex root file>. Confirm all workflow parameters first, infer the topic, ask me to confirm it, then search related literature, build an evidence map, run the review/audit workflow, and revise copied TeX files with paired reviewer/reviser loops if needed.
```

Or:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/draft-paper-review-workflow-prompt.md
```

## Workspace Contract

Reports are plugin-scoped:

```text
workspace/report/paper-reviewer/
```

Shared researched-paper artifacts are stored outside the plugin report folder:

```text
workspace/paper/pdf/{title}/paper.pdf
workspace/paper/tex/{title}/
workspace/paper/summary/{title}/
```

The user's own manuscript, copied TeX revisions, and latexdiff files are not stored under `workspace/paper/`; they go under plugin-scoped work directories:

```text
workspace/work/paper-reviewer/revision/
workspace/work/paper-reviewer/diff/
```

Key reports:

```text
workspace/report/paper-reviewer/00_requirements.md
workspace/report/paper-reviewer/01_manuscript_inventory.md
workspace/report/paper-reviewer/01_formula_symbol_inventory.csv
workspace/report/paper-reviewer/02_topic_scope.md
workspace/report/paper-reviewer/03_literature_candidates.csv
workspace/report/paper-reviewer/03_literature_discovery.md
workspace/report/paper-reviewer/04_paper_artifacts.csv
workspace/report/paper-reviewer/04_paper_artifacts.md
workspace/report/paper-reviewer/05_downloaded_paper_conventions.csv
workspace/report/paper-reviewer/05_downloaded_paper_conventions.md
workspace/report/paper-reviewer/06_figure_table_retention_gate.csv
workspace/report/paper-reviewer/06_figure_table_retention_gate.md
workspace/report/paper-reviewer/07_evidence_map.csv
workspace/report/paper-reviewer/07_evidence_map.md
workspace/report/paper-reviewer/08_reviewer_configuration.md
workspace/report/paper-reviewer/reviewer_reports/
workspace/report/paper-reviewer/specialist_audits/
workspace/report/paper-reviewer/25_editorial_decision.md
workspace/report/paper-reviewer/26_revision_plan.md
workspace/report/paper-reviewer/27_paired_revision_summary.md
workspace/report/paper-reviewer/29_revision_ledger.xlsx
workspace/report/paper-reviewer/30_revision_verification.md
workspace/report/paper-reviewer/31_integrity_report.md
workspace/report/paper-reviewer/32_iteration_log.md
workspace/report/paper-reviewer/33_deferred_issues.md
workspace/report/paper-reviewer/34_report_materiality_index.md
workspace/report/paper-reviewer/99_ultimate_summary.md
workspace/report/paper-reviewer/100_latexdiff_changes.csv
workspace/report/paper-reviewer/100_latexdiff_extraction.md
workspace/report/paper-reviewer/100_latexdiff_extraction.tex
workspace/report/paper-reviewer/101_change_rationale_audit.md
workspace/report/paper-reviewer/101_change_rationale_audit.tex
workspace/work/paper-reviewer/diff/latexdiff.tex
workspace/work/paper-reviewer/diff/latexdiff.pdf
```
