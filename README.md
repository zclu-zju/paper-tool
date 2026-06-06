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

The workflow must confirm all parameters with defaults in Stage 0, including whether post-core latexdiff auditing should run when revised TeX exists. It then confirms the inferred topic scope with the user before searching related literature. Stage 4 groups literature by topic and citation rank. Stage 5 downloads public related-paper artifacts according to the confirmed policy: all discovered public artifacts, top X by citation per topic, top X overall, required evidence only, or no new downloads.

Downloaded papers are the durable local context for later agents. Writing style, terminology, table/figure conventions, section structure, and figure/table deletion or creation decisions must use downloaded/local papers through `05_downloaded_paper_conventions.*`, not transient memory from search.

For computer-science manuscripts, formulas and notation are checked explicitly. Stage 1 writes `01_formula_symbol_inventory.csv`; Stage 6 learns notation practices from downloaded papers. Downstream review, audit, revision, and verification fix duplicate/conflicting symbol definitions and judge unexplained symbols against local downloaded-paper conventions, so conventional or one-off symbols may remain unexplained when comparable papers do the same.

Reports are numbered in fixed reading order from `00_` onward. Low-value human-facing diagnostic reports may be omitted by `report-materiality-gatekeeper`, but later report numbers are not compacted or reused. The workflow does not explain omitted reports. The core final report is `workspace/draft_paper_review/reports/99_ultimate_summary.md`, which is intended to be read first after a run completes.

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
workspace/draft_paper_review/reports/33_deferred_issues.md
```

Objective limitations such as missing experiments, unavailable raw data, absent approvals, missing model checkpoints, proprietary datasets, placeholder tables, or unfinished figures can be deferred instead of causing endless loopback. Deferred issues remain visible in the final risk summary.

If a score dimension cannot be assessed because required evidence is objectively absent, the synthesizer can mark it `N/A_OBJECTIVE_MISSING` according to the missing-score policy rather than assigning an artificial low score.

Missing experiments, placeholder tables, unfinished figures, and absent numeric results constrain only the affected result claims. They must not automatically weaken the manuscript's motivation, method framing, contribution language, literature positioning, or terminology. The workflow asks agents to surface validated strengths and help the draft state them confidently while preserving evidence boundaries.

## Writing And Revision Policy

The revision workflow uses one-to-one reviewer/reviser pairs for fixed or issue-based scopes such as abstract/contribution, introduction, motivation, related positioning, method exposition, formula/notation cleanup, experiment setup, results/tables, terminology/style, and limitations/reproducibility. Each pair alternates reviewer -> writer -> same reviewer until accepted, capped, deferred, or blocked on user input.

Every paired round is recorded in:

```text
workspace/draft_paper_review/reports/29_revision_ledger.jsonl
workspace/draft_paper_review/reports/29_revision_ledger.xlsx
workspace/draft_paper_review/reports/29_revision_ledger_csv/
```

The primary ledger format is `.xlsx`, generated with Python `openpyxl`. CSV exports are fallback artifacts. Downloaded PDF text extraction uses `pypdf` when available.

The revision prompts incorporate ML paper writing guidance:

- preserve a clear one-sentence contribution;
- keep the "what / why evidence / so what" narrative visible;
- make contribution bullets specific and falsifiable;
- learn section-level writing moves from downloaded related papers, including abstract structure, introduction moves, contribution framing, method exposition, experiment/table/figure narration, limitations, and field term usage;
- strengthen defensible claims instead of only qualifying risky ones;
- avoid inventing experiment results, citations, or BibTeX;
- verify citations through metadata sources or mark explicit placeholders;
- preserve honest limitations;
- add or check reproducibility, compute, data/code access, ethics/broader-impact, and venue checklist text when relevant.

Stage 7 includes a figure/table retention gate. It decides whether each figure, table, algorithm, appendix evidence artifact, or proof carrier must be kept, revised, moved, merged, or may be deleted. High-risk artifacts such as primary comparison tables, ablations, dataset/protocol tables, method overview figures, qualitative evidence, and proof/appendix artifacts cannot be deleted casually.

Stage 11 includes a dedicated term-usage consistency auditor. It extracts technical terms, formula symbols, notation tokens, acronyms, dataset names, method names, metric names, proper nouns, and related variants, checks contextual consistency across the manuscript, compares usage against downloaded-paper conventions where relevant, and writes `workspace/draft_paper_review/reports/specialist_audits/17_term_usage_consistency_audit.md` when material.

## Latexdiff Change Audit

After the core workflow finishes, Stage 18 can compare the original accepted TeX source with the revised TeX source when the Stage 0 policy allows it. It uses `latexdiff --flatten` when the command is installed; if `latexdiff` is unavailable, the tool still writes a unified-diff fallback and marks the status. The structured change extraction expands `\input{}` and `\include{}` files so multi-file TeX manuscripts are audited beyond the root file.

```bash
python3 .codex/tools/draft-paper-reviewer/latexdiff_revision_audit.py \
  --old-root <original TeX root or source directory> \
  --new-root <revised TeX root or source directory> \
  --out-root workspace/draft_paper_review
```

Then run `latexdiff-change-auditor`. It reads the diff, revision plan, ledger, verifier, and reviewer/audit reports, then writes author-facing rationale reports:

```text
workspace/draft_paper_review/diff/latexdiff.tex
workspace/draft_paper_review/reports/100_latexdiff_changes.csv
workspace/draft_paper_review/reports/100_latexdiff_extraction.md
workspace/draft_paper_review/reports/100_latexdiff_extraction.tex
workspace/draft_paper_review/reports/101_change_rationale_audit.md
workspace/draft_paper_review/reports/101_change_rationale_audit.tex
```

The `101` report explains what was added, deleted, or replaced, why each edit happened, which review task or ledger row supports it, and which earlier stage should recheck weak or questionable edits.

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

If the xlsx ledger or PDF text extraction dependency is missing in the target environment, install it with:

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
workspace/draft_paper_review/reports/01_formula_symbol_inventory.csv
workspace/draft_paper_review/reports/02_topic_scope.md
workspace/draft_paper_review/reports/03_literature_candidates.csv
workspace/draft_paper_review/reports/03_literature_discovery.md
workspace/draft_paper_review/reports/04_paper_artifacts.csv
workspace/draft_paper_review/reports/04_paper_artifacts.md
workspace/draft_paper_review/reports/05_downloaded_paper_conventions.csv
workspace/draft_paper_review/reports/05_downloaded_paper_conventions.md
workspace/draft_paper_review/reports/06_figure_table_retention_gate.csv
workspace/draft_paper_review/reports/06_figure_table_retention_gate.md
workspace/draft_paper_review/reports/07_evidence_map.csv
workspace/draft_paper_review/reports/07_evidence_map.md
workspace/draft_paper_review/reports/08_reviewer_configuration.md
workspace/draft_paper_review/reports/reviewer_reports/
workspace/draft_paper_review/reports/specialist_audits/
workspace/draft_paper_review/reports/25_editorial_decision.md
workspace/draft_paper_review/reports/26_revision_plan.md
workspace/draft_paper_review/reports/27_paired_revision_summary.md
workspace/draft_paper_review/reports/29_revision_ledger.xlsx
workspace/draft_paper_review/reports/30_revision_verification.md
workspace/draft_paper_review/reports/31_integrity_report.md
workspace/draft_paper_review/reports/32_iteration_log.md
workspace/draft_paper_review/reports/33_deferred_issues.md
workspace/draft_paper_review/reports/34_report_materiality_index.md
workspace/draft_paper_review/reports/99_ultimate_summary.md
workspace/draft_paper_review/reports/100_latexdiff_changes.csv
workspace/draft_paper_review/reports/100_latexdiff_extraction.md
workspace/draft_paper_review/reports/100_latexdiff_extraction.tex
workspace/draft_paper_review/reports/101_change_rationale_audit.md
workspace/draft_paper_review/reports/101_change_rationale_audit.tex
workspace/draft_paper_review/diff/latexdiff.tex
```
