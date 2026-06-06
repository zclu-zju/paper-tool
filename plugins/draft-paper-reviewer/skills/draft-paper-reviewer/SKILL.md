---
name: draft-paper-reviewer
description: Use for TeX-only academic draft review and revision in a Codex repo. Installs repo-local custom agents from this plugin, rejects non-TeX submitted manuscripts, confirms all workflow parameters with defaults, infers and asks the user to confirm the paper topic, discovers related papers by topic and citation rank, downloads public artifacts according to all/top-X/required-only policy, mines downloaded papers for writing/table/figure/term conventions, gates figure/table deletion, builds a local evidence map, runs material reviewer and specialist audits, synthesizes scores and decisions, revises copied TeX files through one-to-one reviewer/reviser loops, records every round in an XLSX ledger, verifies revisions, writes a numbered 99 ultimate summary, can run post-core latexdiff change-rationale auditing, and loops back until quality gates pass or objective limitations are deferred.
---

# Draft Paper Reviewer

This skill installs and launches an iterative TeX draft review workflow. It is designed for the user's own research workflow, not for generic peer-review roleplay.

The workflow accepts:
- a TeX source folder;
- an explicit `.tex` root file;
- optional target venue, target tier, review strictness, desired language, manuscript maturity, incomplete-part notes, and revision preference.

The workflow rejects submitted manuscripts that are only PDF, Word, Markdown, plain text, image files, or otherwise lack TeX source. A compiled PDF may be used only as an optional inspection artifact after TeX source is accepted.

Stage 0 must first confirm all workflow parameters with explicit defaults. Stage 2 then infers the manuscript topic and comparison boundary, and Stage 3 asks the user whether the inferred topic is accurate. The workflow must not search or review until requirements are ready and the topic scope is confirmed.

The workflow is for improving the user's own draft. Missing experiments, incomplete tables, unfinished figures, and absent numeric results constrain only the affected result claims. They must not automatically weaken the motivation, method framing, contribution language, literature positioning, terminology, or field-style confidence. Agents must surface validated strengths and state them confidently within evidence boundaries.

Related literature is used both as review evidence and as writing evidence. Discovery groups papers by topic and citation rank; artifact collection downloads public PDFs or TeX/source according to the confirmed all/top-X/required-only policy. Downloaded local papers are then mined for section-level examples of abstract structure, introduction moves, contribution framing, method exposition, formula/notation explanation patterns, experiment/table/figure narration, limitation framing, and term usage so the paired revisers can adapt field-standard writing moves from durable local context.

For computer-science manuscripts, formula-symbol usage is convention-calibrated. Stage 1 extracts `01_formula_symbol_inventory.csv`. Stage 6 mines downloaded papers for notation practices, including symbols that are normally explained and symbols that are commonly left unexplained because they are conventional or used only once. Downstream reviewers, auditors, planners, paired revisers, and verifiers must fix duplicate/conflicting definitions and require explanations only when local paper conventions or manuscript clarity call for them.

Figure and table changes are gated. Existing tables, figures, algorithms, proofs, appendix evidence, and other evidence carriers cannot be deleted, merged, moved, or replaced unless the retention gate says the proof chain and paper structure remain sufficient. New or redesigned tables/figures must be supported by downloaded-paper convention evidence or escalated for user decision.

After the core workflow writes `99_ultimate_summary.md`, Stage 18 can compare the original accepted TeX source and the revised TeX source with latexdiff according to the confirmed Stage 0 policy. The installed `latexdiff_revision_audit.py` tool writes `workspace/draft_paper_review/diff/latexdiff.tex`, `100_latexdiff_changes.csv`, and `100_latexdiff_extraction.md/.tex`; then `latexdiff-change-auditor` writes `101_change_rationale_audit.md/.tex` explaining what changed, why, and which earlier stage should recheck weakly justified edits.

## Install Agents

The plugin carries custom agent templates in `assets/agents/`, prompt protocols in `assets/prompts/`, and an installer script.

From a local clone:

```bash
python3 plugins/draft-paper-reviewer/scripts/install_project_agents.py --repo .
```

From an installed plugin cache, resolve the installer relative to this skill directory:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo>
```

Known obsolete files from older local versions are cleaned by default so prompts do not remain in a visible repository-root `prompts/` directory. Preserve them only when requested:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo> --keep-obsolete
```

The installer is conservative about current files. It copies missing files, leaves identical files unchanged, reports conflicts without overwriting, and removes only known obsolete draft-paper-reviewer files by default.

Project prompts are installed under `.codex/prompts/draft-paper-reviewer/`. Tooling, including the related-paper artifact downloader/text extractor and XLSX revision ledger builder, is installed under `.codex/tools/draft-paper-reviewer/`.

## Launch

After installing agents, invoke:

```text
Use the draft-paper-reviewer-orchestrator custom agent and execute the evidence-based paper review workflow.
```

Or use the launcher file:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/draft-paper-review-workflow-prompt.md
```

## Interaction Contract

Stage 0 must collect required parameters before any paper search or review:
- manuscript source type and path;
- TeX root file or source-root detection result;
- whether the workflow may compile TeX if a TeX source is provided;
- manuscript maturity and known incomplete parts;
- target field, venue, or tier if known;
- workflow goal and revision mode;
- target review strictness and desired output language;
- minimum related-paper count;
- minimum recent/SOTA related-paper count;
- related-paper artifact retrieval policy: all discovered public artifacts, top-cited per topic, top-cited overall, required evidence only, or no new downloads;
- artifact download top-X when a top-cited policy is selected;
- topic grouping policy for discovered literature;
- local artifact evidence policy for writing/style/table/figure/term/common-practice decisions;
- formula-symbol convention policy: duplicate/conflicting definitions must be fixed, and unexplained symbols are judged against downloaded-paper notation conventions;
- report materiality policy with fixed numbering and no user-facing records for unwritten reports;
- figure/table deletion policy requiring retention-gate approval;
- post-core latexdiff audit policy: run when revised TeX exists, run only when the user provides revised TeX, or do not run;
- revised TeX source path when the user is asking to compare an already revised article;
- whether manuscript revision is requested or review-only mode is desired;
- paired revision granularity, active scopes, pair acceptance threshold, and maximum rounds per pair;
- final quality threshold, with 3.5/5 as the default only after stating it;
- maximum total workflow iterations, if the user wants a global cap;
- maximum repeated iterations for the same stage/problem pair, with 3 as the default after stating it;
- objective limitation policy for issues that cannot be fixed from the current manuscript, such as missing experiments, unavailable raw data, missing human-subject approvals, or unavailable proprietary artifacts;
- missing score policy for dimensions that cannot be assessed because required evidence is objectively absent;
- any inclusion/exclusion constraints for related literature.

Stage 2 infers the topic. Stage 3 must ask the user to confirm the inferred topic and excluded adjacent areas. The workflow must stop there until the user confirms or corrects the scope.

Only after:

```text
00_requirements.md: STATUS: READY
02_topic_scope.md: STATUS: USER_CONFIRMED
```

may the workflow search related papers.

After the integrity gate passes, Stage 17 must run the final summary agent and write:

```text
workspace/draft_paper_review/reports/99_ultimate_summary.md
```

That report is the first report the user should read. Stage 18 runs after it only when the confirmed latexdiff policy allows comparison and a revised TeX source exists.

## Evidence Rule

All review and audit conclusions must be traceable to:
- a manuscript location, such as page/section/paragraph, line, figure, table, claim ID, or TeX file path;
- one or more entries in `workspace/draft_paper_review/reports/07_evidence_map.csv`;
- downloaded or verified related literature when the issue concerns novelty, terminology, field norms, literature positioning, SOTA comparison, methods, or writing style.

Generic comments such as "the novelty is weak" are invalid unless they name the overlapping prior work and explain the specific overlap.

## Outputs

All generated outputs go under:

```text
workspace/draft_paper_review/
```

Main report paths:

```text
workspace/draft_paper_review/reports/00_requirements.md
workspace/draft_paper_review/reports/01_manuscript_inventory.md
workspace/draft_paper_review/reports/01_formula_symbol_inventory.csv
workspace/draft_paper_review/reports/02_topic_scope.md
workspace/draft_paper_review/reports/03_literature_candidates.csv
workspace/draft_paper_review/reports/04_paper_artifacts.csv
workspace/draft_paper_review/reports/05_downloaded_paper_conventions.csv
workspace/draft_paper_review/reports/06_figure_table_retention_gate.csv
workspace/draft_paper_review/reports/07_evidence_map.csv
workspace/draft_paper_review/reports/08_reviewer_configuration.md
workspace/draft_paper_review/reports/reviewer_reports/
workspace/draft_paper_review/reports/specialist_audits/
workspace/draft_paper_review/reports/specialist_audits/17_term_usage_consistency_audit.md
workspace/draft_paper_review/reports/25_editorial_decision.md
workspace/draft_paper_review/reports/26_revision_plan.md
workspace/draft_paper_review/reports/27_paired_revision_summary.md
workspace/draft_paper_review/reports/28_revision_changes.md
workspace/draft_paper_review/reports/29_revision_ledger.jsonl
workspace/draft_paper_review/reports/29_revision_ledger.xlsx
workspace/draft_paper_review/reports/29_revision_ledger_csv/
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
workspace/draft_paper_review/revision/
workspace/draft_paper_review/literature/papers/
```

## Score And Decision Contract

The final score uses seven 1-5 dimensions:

```text
Originality 15%
Methodological Rigor 25%
Evidence Sufficiency 20%
Argument Coherence 15%
Writing Quality 10%
Literature Integration 10%
Significance And Impact 5%
```

Default decision mapping:

```text
4.5-5.0 Accept-ready
3.5-4.4 Minor revision
2.5-3.4 Major revision
1.5-2.4 Reject / rebuild
1.0-1.4 Not review-ready
```

Hard gates:
- Devil's Advocate CRITICAL issue unresolved: cannot finalize unless the issue is objectively unfixable in the current manuscript cycle and has reached the configured repeated-issue iteration cap, in which case it must be marked `DEFERRED_OBJECTIVE_LIMITATION` and surfaced as a final risk.
- Methodology score <= 2: cannot finalize unless the low score is driven by objectively missing experiments/data that the workflow cannot create; then mark the dimension `N/A_OBJECTIVE_MISSING` or `DEFERRED_OBJECTIVE_LIMITATION` instead of forcing endless loopback.
- Literature Integration score <= 2: return to literature discovery, evidence map, or revision unless the configured repeated-issue cap has been reached for the same issue.
- Originality score <= 2 without a defensible repositioning path: cannot finalize as publish-ready; it may continue only as not-ready or deferred if the missing contribution requires new experiments or new data.
- Writing Quality score <= 2: must run revision/polish if revision is allowed; if review-only, mark not publish-ready.
- Any major review conclusion without evidence-map support: return to evidence-map building or review until the repeated-issue cap is reached, then mark the specific unsupported conclusion as excluded from scoring.

## Loopback

The integrity reviewer can reject and return to:
- Stage 0 Requirement Collector;
- Stage 1 Manuscript Ingestor;
- Stage 2 Topic Scope Analyst;
- Stage 3 User Scope Confirmation Gate;
- Stage 4 Literature Discovery Scout;
- Stage 5 Paper Artifact Collector;
- Stage 6 Downloaded Paper Convention Miner;
- Stage 7 Figure And Table Retention Gatekeeper;
- Stage 8 Evidence Map Builder;
- Stage 9 Reviewer Panel Configurator;
- Stage 10 Reviewer Panel;
- Stage 11 Specialist Diagnostic Panel;
- Stage 12 Editorial Synthesizer And Scorer;
- Stage 13 Revision Planner;
- Stage 14 Paired Revision Coordinator;
- Stage 15 Revision Verifier.

If no new user input is required, the orchestrator retries automatically subject to the configured iteration policy. By default, the workflow has no global iteration cap, but the same stage/problem pair is retried at most 3 times unless the user sets another value. When the cap is reached, the issue is recorded in `32_iteration_log.md` and `33_deferred_issues.md`, excluded from further loopback, and carried into the final risk summary.
