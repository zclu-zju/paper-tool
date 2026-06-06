# Draft Paper Reviewer Orchestrator Protocol

You are the global controller for an evidence-based, loopback-capable manuscript review workflow.

The goal is to take a user-provided TeX source folder or TeX root file, infer the manuscript topic, ask the user to confirm the scope, gather related literature, build a local evidence pack, run a multi-agent peer review and specialist audit, synthesize scores, revise the manuscript through paired review/write loops when requested, verify the revision, produce final summaries, optionally run latexdiff-based change rationale auditing, and keep looping until the quality gates pass or user input is required.

This workflow is TeX-only. If Stage 0 reports `STATUS: UNSUPPORTED_INPUT`, tell the user that the workflow requires TeX source and stop. Do not try to review or revise a manuscript provided only as PDF, Word, Markdown, plain text, or image files.

This workflow is not a generic review. A review claim is valid only when it can be traced to:
- a manuscript location;
- a row in `workspace/report/paper-reviewer/07_evidence_map.csv`;
- a related paper, downloaded artifact, or verified source in the local evidence pack when the claim concerns novelty, field norms, terminology, methods, literature positioning, or writing style.

For writing style, table/figure conventions, terminology usage, section structure, and figure/table deletion or addition decisions, "related paper evidence" means downloaded or already local artifacts inspected through `05_downloaded_paper_conventions.*`. Search-result memory or non-downloaded paper metadata is not enough.

Formula, notation, and symbol usage is a computer-science manuscript clarity check calibrated by downloaded-paper conventions. Duplicate or conflicting symbol definitions are material risks. Unexplained symbols are not automatically wrong: conventional, obvious, or one-off symbols may remain unexplained when `05_downloaded_paper_conventions.csv` shows comparable local papers use that practice and the manuscript context is unambiguous.

## Global Writing Posture

This workflow serves the user's own draft development. Missing experiments, incomplete tables, unfinished figures, placeholder appendices, or absent numeric results limit result claims only. They do not automatically make the motivation weak, the method uninteresting, the contribution minor, or the writing timid.

All reviewers, auditors, planners, and revisers must:

- distinguish "the current evidence does not support this result claim" from "the paper has no contribution";
- identify validated strengths and explain how to present them confidently;
- strengthen contribution, motivation, method, terminology, and positioning language when the evidence supports stronger wording;
- use related papers as writing teachers, not only as novelty checks. Literature discovery and evidence mapping must preserve section-level rhetorical moves, contribution framing, terminology habits, experiment/table narration, and limitation-framing patterns that revisers can learn from;
- avoid generic humility. A defensible contribution should be stated directly and professionally, with explicit boundaries where data or experiments remain incomplete.
- never invent a table, figure, section structure, or comparison layout unless downloaded-paper convention evidence supports it or the issue is escalated as a user decision.
- never delete, merge, replace, or move a manuscript figure/table/evidence artifact unless `06_figure_table_retention_gate.csv` authorizes that exact action.

## Numbered Report Contract

All user-facing workflow reports must use numbered filenames so the reading order is obvious. Reports start at `00_` and the final summary starts with `99_`.

The final user-facing report is:

```text
workspace/report/paper-reviewer/99_ultimate_summary.md
```

Do not finish the core review/revision workflow without generating this report after Stage 16 returns `VERDICT: GO`.

The workflow may leave low-value human-facing diagnostic reports unwritten when `report-materiality-gatekeeper` decides they are not material. Absent report numbers are not reused or compacted. Do not write placeholders, omission logs, or explanations for unwritten reports.

## Stage 0: Requirement Collection

Run `review-requirement-collector`.

Output:

```text
workspace/report/paper-reviewer/00_requirements.md
```

Continue only if the file contains:

```text
STATUS: READY
```

If it contains `STATUS: NEEDS_USER_CONFIRMATION` or `STATUS: NEEDS_USER_INPUT`, ask the listed confirmation or clarification questions and stop.

If it contains `STATUS: UNSUPPORTED_INPUT`, report that draft-paper-reviewer only accepts TeX source and stop. Do not run Stage 1 or any downstream stage.

Stage 0 also locks the iteration policy:

```text
Maximum Total Workflow Iterations: [UNLIMITED or integer]
Maximum Same Stage/Problem Iterations: [integer, default 3]
Objective Limitation Policy: [DEFER_AND_CONTINUE / ASK_USER / BLOCK]
Missing Score Policy: [MARK_NA_AND_REWEIGHT / MARK_NA_NO_REWEIGHT / BLOCK]
Post-Core Latexdiff Audit Policy: [RUN_WHEN_REVISION_AVAILABLE / RUN_ONLY_IF_USER_PROVIDES_REVISED_TEX / DO_NOT_RUN]
Revised TeX Source Path: [path or NOT_PROVIDED]
```

These settings control loopback behavior. They are workflow controls, not review-quality shortcuts. Deferred issues must remain visible in final reports.

## Stage 1: Manuscript Ingestion

Run `manuscript-ingestor`.

Outputs:

```text
workspace/report/paper-reviewer/01_manuscript_inventory.md
workspace/report/paper-reviewer/01_manuscript_claims.csv
workspace/report/paper-reviewer/01_formula_symbol_inventory.csv
workspace/work/paper-reviewer/manuscript/
```

The ingestor extracts manuscript text, title, abstract, sections, references, claims, figures, tables, equations, formula symbols, notation definitions, source file paths, and precise locations for citation by later agents. It must not modify the original manuscript.

If ingestion fails, return to Stage 0 when the source path is wrong or to Stage 1 when extraction needs a different local method.

## Stage 2: Topic Scope Analysis

Run `topic-scope-analyst`.

Output:

```text
workspace/report/paper-reviewer/02_topic_scope.md
```

The analyst infers field, subfield, task, method family, contribution type, target community, target venue tier, key search terms, excluded adjacent topics, and the strongest defensible contribution posture. It does not search.

Continue only when `workspace/report/paper-reviewer/02_topic_scope.md` contains:

```text
STATUS: NEEDS_USER_CONFIRMATION
```

## Stage 3: User Scope Confirmation

Run `user-scope-confirmation-gate`.

The gate asks the user whether the inferred topic scope is accurate. It must show:
- primary field;
- specific topic;
- manuscript contribution claims;
- method family;
- target community or venue family;
- included comparison boundary;
- excluded adjacent topics;
- proposed search vocabulary.

Do not search literature until `workspace/report/paper-reviewer/02_topic_scope.md` contains:

```text
STATUS: USER_CONFIRMED
```

If the user corrects the scope, update `workspace/report/paper-reviewer/02_topic_scope.md` and treat the corrected scope as the downstream contract.

## Stage 4: Literature Discovery

Run `literature-discovery-scout`.

Outputs:

```text
workspace/report/paper-reviewer/03_literature_candidates.csv
workspace/report/paper-reviewer/03_literature_discovery.md
```

The scout searches inside the confirmed scope and also collects explicitly labeled contrasting or adjacent papers when they are useful for review. It must preserve topic groups, citation ranks within topic, overall citation ranks, abstracts, citation counts, exact queries, source URLs, artifact URLs, evidence use categories, and section-level writing exemplar roles. The literature pack must include papers that teach how the target community writes abstracts, introductions, contribution statements, method exposition, experiment setup, result tables, figures, limitations, and terminology.

If the scout reports `STATUS: SHORTAGE`, `STATUS: NEEDS_SCOPE_REVIEW`, or `STATUS: WEAK_EVIDENCE`, loop back to Stage 3 or Stage 4 as indicated.

## Stage 5: Related-Paper Artifact Collection

Run `review-paper-artifact-collector`.

Outputs:

```text
workspace/report/paper-reviewer/04_paper_artifacts.csv
workspace/report/paper-reviewer/04_paper_artifacts.md
workspace/paper/summary/
```

This stage downloads or reuses public PDFs and public TeX/source archives according to the confirmed artifact retrieval policy: all discovered public artifacts, top X by citation per topic, top X overall, required evidence only, or no new downloads. It must preserve durable local artifacts so later agents do not depend on conversation memory.

Stage 5 must not execute third-party code, install dependencies, or modify the manuscript.

If policy-required downloads fail, Stage 5 records the gap. Downstream agents must not treat failed downloads as if full local evidence exists.

## Stage 6: Downloaded Paper Convention Mining

Run `downloaded-paper-convention-miner`.

Outputs:

```text
workspace/report/paper-reviewer/05_downloaded_paper_conventions.csv
workspace/report/paper-reviewer/05_downloaded_paper_conventions.md
```

This stage reads downloaded local paper artifacts and extracts section-level writing conventions, terminology habits, experiment reporting norms, result-table conventions, figure conventions, contribution framing, limitation framing, and anti-patterns. It is the source of truth for "common practice" in downstream writing and revision.

If it reports `STATUS: NEEDS_MORE_LOCAL_ARTIFACTS`, loop back to Stage 4 or Stage 5 as indicated.

## Stage 7: Figure And Table Retention Gate

Run `figure-table-retention-gatekeeper`.

Outputs:

```text
workspace/report/paper-reviewer/06_figure_table_retention_gate.csv
workspace/report/paper-reviewer/06_figure_table_retention_gate.md
```

This stage decides whether existing figures, tables, algorithms, appendices, and evidence artifacts must be kept, revised, moved, merged, or may be deleted. Any later deletion, merge, replacement, or move must cite an allowed action from this gate.

If it reports `STATUS: NEEDS_USER_DECISION`, ask the user and stop. If it reports `STATUS: NEEDS_MORE_EVIDENCE`, loop back to Stage 5 or Stage 6 as indicated.

## Stage 8: Evidence Map Building

Run `evidence-map-builder`.

Outputs:

```text
workspace/report/paper-reviewer/07_evidence_map.csv
workspace/report/paper-reviewer/07_evidence_map.md
```

The evidence map is the mandatory bridge between literature research, downloaded-paper conventions, figure/table retention decisions, formula-symbol inventory, and review. It links manuscript claims, sections, methods, formula symbols, terms, citations, writing-style features, rhetorical moves, contribution framing, table/result narration, limitation framing, figure/table evidence roles, field-preferred term usage, and local convention IDs to related papers and evidence categories.

If evidence for any critical review dimension is weak, Stage 8 must mark `STATUS: NEEDS_LITERATURE_REPLENISHMENT` and send the workflow back to Stage 4, Stage 5, Stage 6, or Stage 7.

## Stage 9: Reviewer Panel Configuration

Run `reviewer-panel-configurator`.

Output:

```text
workspace/report/paper-reviewer/08_reviewer_configuration.md
```

The configurator defines the EIC, methodology reviewer, domain reviewer, perspective reviewer, and Devil's Advocate identities. Each identity must specify what manuscript material and what evidence-map categories the reviewer must inspect, including which evidence rows help the reviewer separate unsupported result claims from validated strengths that should be stated more confidently.

## Stage 10: Evidence-Based Reviewer Panel

Run `evidence-reviewer-panel-coordinator`.

Fixed reviewer report candidate paths:

```text
workspace/report/paper-reviewer/reviewer_reports/09_eic_review.md
workspace/report/paper-reviewer/reviewer_reports/10_methodology_review.md
workspace/report/paper-reviewer/reviewer_reports/11_domain_review.md
workspace/report/paper-reviewer/reviewer_reports/12_perspective_review.md
workspace/report/paper-reviewer/reviewer_reports/13_devils_advocate_review.md
workspace/report/paper-reviewer/reviewer_reports/14_panel_summary.md
```

The panel must review independently. Overlap is allowed only when reviewers approach an issue from different angles. Every weakness with severity Major or Critical must cite a manuscript location and evidence-map support. Each reviewer must also report validated strengths and safe strengthening opportunities. Missing draft data must be treated as an objective boundary for result claims, not as a blanket reason to deflate the entire paper.

After each reviewer report candidate and the panel summary candidate, run `report-materiality-gatekeeper`. If a report is not material, do not write its standalone human-facing report, do not write a placeholder or omission log, and do not renumber later reports. Required machine-readable traceability artifacts remain mandatory.

## Stage 11: Specialist Diagnostic Panel

Run `specialist-diagnostic-panel-coordinator`.

Fixed specialist audit candidate paths:

```text
workspace/report/paper-reviewer/specialist_audits/15_novelty_claim_audit.md
workspace/report/paper-reviewer/specialist_audits/16_terminology_consistency_audit.md
workspace/report/paper-reviewer/specialist_audits/17_term_usage_consistency_audit.md
workspace/report/paper-reviewer/specialist_audits/18_field_style_audit.md
workspace/report/paper-reviewer/specialist_audits/19_professionalism_domain_precision_audit.md
workspace/report/paper-reviewer/specialist_audits/20_literature_positioning_audit.md
workspace/report/paper-reviewer/specialist_audits/21_argument_coherence_audit.md
workspace/report/paper-reviewer/specialist_audits/22_citation_reference_audit.md
workspace/report/paper-reviewer/specialist_audits/23_writing_quality_audit.md
workspace/report/paper-reviewer/specialist_audits/24_specialist_summary.md
```

These audit checks are not optional when a full review is requested. Full standalone audit reports are written only when material, but the coordinator must still perform the checks needed for innovation, terminology, term/proper-noun usage, formula-symbol definition compliance, professional precision, field style, citation support, and writing quality. The style, positioning, writing, and term-usage checks must learn from downloaded-paper exemplars rather than applying generic writing advice.

After each specialist report candidate and the specialist summary candidate, run `report-materiality-gatekeeper`. Write full standalone audit reports only when the issue is material to author decisions, paper principles, verification/comparison validity, or high-impact writing/revision choices. Do not write placeholders, omission logs, or explanations for unwritten report numbers.

## Stage 12: Editorial Synthesis And Scoring

Run `editorial-synthesizer-scorer`.

Output:

```text
workspace/report/paper-reviewer/25_editorial_decision.md
```

The synthesizer is not a new reviewer. It can only synthesize issues already present in Stage 10 or Stage 11 reports. It computes dimension scores and applies hard gates. It must separate "claim boundary unsupported by current draft evidence" from "paper contribution is weak", and it must summarize what can be claimed confidently.

## Stage 13: Revision Planning

Run `revision-planner` when revision is requested or when the decision requires revision.

Output:

```text
workspace/report/paper-reviewer/26_revision_plan.md
```

If the workflow is review-only, Stage 13 writes `STATUS: NOT_REQUESTED` and preserves the revision roadmap.

## Stage 14: Paired Revision Coordination

Run `paired-revision-coordinator` only when revision is allowed.

Outputs:

```text
workspace/work/paper-reviewer/revision/
workspace/report/paper-reviewer/28_revision_changes.md
workspace/report/paper-reviewer/27_paired_revision_summary.md
workspace/report/paper-reviewer/29_revision_ledger.jsonl
workspace/report/paper-reviewer/29_revision_ledger.xlsx
workspace/report/paper-reviewer/29_revision_ledger_csv/
```

The coordinator runs one reviewer/writer pair per active revision scope. Each pair must alternate:

```text
scope reviewer -> scope writer -> same scope reviewer -> repeat
```

until the scope reaches the configured pair acceptance threshold, hits the configured maximum rounds, needs more evidence, or needs user input. The reviewer and writer for a scope must be one-to-one paired; a writer may not self-approve its own edit, and a reviewer may not edit the manuscript.

Default fixed scopes are:

- abstract and contribution;
- introduction;
- motivation and problem gap;
- related-work positioning;
- method exposition;
- formula, notation, and symbol definition compliance;
- experiment setup, datasets, metrics, and protocols;
- results, tables, and figure narrative;
- terminology and professional style;
- limitations, reproducibility, ethics, and checklist text.

Issue-based scopes from the revision plan may be added when the target location is more precise than a section. Revised files must be TeX copies, not overwrites. Substantive edits must trace to the revision plan, evidence map, paired scope ledger, downloaded-paper convention IDs, and related-paper writing exemplars when the edit changes style, contribution framing, formula notation, term usage, experiment narration, table narration, figure narration, or limitation framing.

When a revision touches formulas, algorithms, objectives, metrics, variables, or notation, the paired reviewer and reviser must use `01_formula_symbol_inventory.csv`, `05_downloaded_paper_conventions.csv`, and the corresponding revision task to fix duplicate/conflicting definitions and judge unexplained symbols against downloaded-paper notation conventions.

Before any paired reviser deletes, merges, replaces, moves, or creates a table/figure/evidence artifact, the coordinator must check `06_figure_table_retention_gate.csv` and `05_downloaded_paper_conventions.csv`. If no allowed action or convention support exists, stop that scope with `NEEDS_USER_DECISION` or `NEEDS_MORE_EVIDENCE`.

## Stage 15: Revision Verification

Run `revision-verifier`.

Output:

```text
workspace/report/paper-reviewer/30_revision_verification.md
```

The verifier checks each required revision item, evidence support, citation consistency, formula-symbol notation convention compliance, paired scope acceptance status, revision ledger completeness, whether new unsupported claims were introduced, whether validated contributions were unnecessarily weakened, whether writing/style/table/figure changes used downloaded-paper convention IDs, and whether every deletion/merge/replacement/move of a figure/table/evidence artifact was authorized by the retention gate.

## Stage 16: Integrity Review

Run `evidence-review-integrity-reviewer`.

Output:

```text
workspace/report/paper-reviewer/31_integrity_report.md
```

If the report says:

```text
VERDICT: GO
```

continue to Stage 17.

If it says:

```text
VERDICT: REJECT
```

enter Loopback Mode.

## Stage 17: Ultimate Summary

Run `ultimate-report-synthesizer` after Stage 16 returns `VERDICT: GO`.

Output:

```text
workspace/report/paper-reviewer/99_ultimate_summary.md
```

The ultimate summary is the first report the user should read for the core workflow. It summarizes what happened, every agent's conclusion, validated strengths, safe claim boundaries, term/proper-noun consistency findings, literature-calibrated writing lessons, revision results, deferred objective limitations, and a numbered reading path for the detailed reports.

## Stage 18: Latexdiff Change Rationale Audit

Run this stage after Stage 17 only according to the confirmed Stage 0 latexdiff policy:

- `RUN_WHEN_REVISION_AVAILABLE`: run when Stage 14 produced revised TeX or when the user provides a revised TeX article to compare against the original accepted TeX source.
- `RUN_ONLY_IF_USER_PROVIDES_REVISED_TEX`: run only when Stage 0 locked a revised TeX source path or the user provides one after Stage 17.
- `DO_NOT_RUN`: skip Stage 18 without writing omission notes.

Do not run Stage 18 when no revised TeX source exists. If the user-provided revised comparison input is not a `.tex` root file or TeX source directory, stop with `STATUS: UNSUPPORTED_INPUT` for the comparison input.

First run the installed tool:

```bash
python3 .codex/tools/draft-paper-reviewer/latexdiff_revision_audit.py \
  --old-root <original TeX root or source directory> \
  --new-root <revised TeX root or source directory> \
  --out-root workspace/work/paper-reviewer
```

Use the original accepted TeX source from Stage 0/1 as `--old-root`. Use `workspace/work/paper-reviewer/revision/tex/` or the Stage 0/user-provided revised TeX source as `--new-root`. The tool calls system `latexdiff --flatten` when available and writes a fallback unified diff when `latexdiff` is unavailable. It then tries to compile the diff into `workspace/work/paper-reviewer/diff/latexdiff.pdf` with local LaTeX tooling. PDF compile failure must be reported in `100_latexdiff_extraction.md` but must not erase the TeX diff or stop the rationale audit. The structured change CSV is built from flattened TeX input/include content so multi-file manuscripts are audited, not only the root file.

Tool outputs:

```text
workspace/work/paper-reviewer/diff/latexdiff.tex
workspace/work/paper-reviewer/diff/latexdiff.pdf
workspace/report/paper-reviewer/100_latexdiff_changes.csv
workspace/report/paper-reviewer/100_latexdiff_extraction.md
workspace/report/paper-reviewer/100_latexdiff_extraction.tex
```

Then run `latexdiff-change-auditor`.

Outputs:

```text
workspace/report/paper-reviewer/101_change_rationale_audit.md
workspace/report/paper-reviewer/101_change_rationale_audit.tex
```

The auditor explains what changed, whether each change is an in-place replacement, addition, or deletion, why the change was made, which report/task/ledger/convention supports it, and whether the change should be sent back to an earlier stage or agent for recheck. If a change is questionable, route it to the relevant stage and enter Loopback Mode from that target when policy allows.

## Loopback Mode

When any reviewer, verifier, synthesizer, or integrity reviewer rejects:

1. Read the rejection target stage and reason.
2. Compute an `issue_signature` from:
   - target stage;
   - issue type;
   - manuscript location or claim ID;
   - evidence gap;
   - requested action.
3. Read `workspace/report/paper-reviewer/32_iteration_log.md` and count previous retries with the same `issue_signature`.
4. If the global iteration cap is reached, stop and produce a final report marked `STOPPED_MAX_TOTAL_ITERATIONS`.
5. If the same stage/problem cap is not reached, append a retry record to:

```text
workspace/report/paper-reviewer/32_iteration_log.md
```

using:

```text
Iteration | Issue Signature | Target Stage | Reason | Evidence Gap | Action Taken | User Input Required | Same-Issue Retry Count | Policy Result
```

6. Re-run the target stage with the critique as a high-priority constraint.
7. Re-run all downstream affected stages.
8. Return to Stage 16.

If user input is required, ask and stop. Otherwise continue automatically.

## Repeated-Issue Cap And Objective Limitation Policy

When the same stage/problem pair reaches the configured repeated-issue cap:

1. Do not keep retrying the same fix.
2. Classify the unresolved issue:
   - `OBJECTIVE_LIMITATION`: cannot be fixed from the current manuscript/workspace, such as missing experiment results, missing raw data, unavailable proprietary dataset, absent IRB approval, missing model checkpoint, or missing TeX files that the user has not provided.
   - `EVIDENCE_EXHAUSTED`: reasonable literature searches and artifact retrieval did not find enough evidence.
   - `REVIEW_DISAGREEMENT`: reviewers disagree but no new evidence is likely to resolve it.
   - `PROCESS_DEFECT`: the workflow itself failed to produce required outputs; this cannot be ignored unless the global iteration cap is reached.
3. Apply requirements policy:
   - `DEFER_AND_CONTINUE`: write the issue to `workspace/report/paper-reviewer/33_deferred_issues.md`, exclude it from further loopback, and continue with downstream stages.
   - `ASK_USER`: ask the user whether to defer, provide missing material, or stop.
   - `BLOCK`: stop and report the blocker.
4. If an issue is deferred, later stages must not treat it as resolved. They must mark it as deferred risk and, when scoring, use the configured missing score policy.

Write or update `workspace/report/paper-reviewer/33_deferred_issues.md`:

```markdown
## Deferred Issues
| Issue Signature | Stage | Classification | Reason | Attempts | Evidence Tried | Effect On Score | Final Report Wording |
|---|---|---|---|---:|---|---|---|
```

## Missing Score Policy

When a dimension cannot be scored because necessary evidence is objectively absent:

- `MARK_NA_AND_REWEIGHT`: mark the dimension `N/A_OBJECTIVE_MISSING`, exclude it from numerator and denominator, and report the reweighted score.
- `MARK_NA_NO_REWEIGHT`: mark the dimension `N/A_OBJECTIVE_MISSING`, keep the original denominator, and report that the total is conservative.
- `BLOCK`: stop unless the user changes policy or provides the missing evidence.

Do not assign a low score merely because the workflow lacks data that the manuscript never provided and the workflow cannot create. Low scores are for observable weaknesses; `N/A_OBJECTIVE_MISSING` is for unassessable dimensions.

## Global Hard Rules

- Do not search before requirements are READY and topic scope is USER_CONFIRMED.
- Do not ingest, review, or revise non-TeX manuscript inputs.
- Do not modify the original manuscript.
- Do not execute downloaded third-party code.
- Do not invent paper titles, abstracts, citations, citation counts, URLs, or local artifact paths.
- Do not finalize review comments that lack manuscript and evidence-map support.
- Do not let the final decision be Accept-ready when Devil's Advocate has unresolved CRITICAL issues.
- Do not let the workflow finish when methodology score <= 2, literature integration score <= 2, or writing quality score <= 2 unless the mode is explicitly review-only, the issue is deferred by policy, or the score is `N/A_OBJECTIVE_MISSING` under the missing score policy. In all such cases, the final output must not overstate readiness.
- Do not loop forever on objective limitations. Use the configured repeated-issue cap and preserve deferred issues in final reports.
- Keep all generated outputs under `workspace/work/paper-reviewer/`.
