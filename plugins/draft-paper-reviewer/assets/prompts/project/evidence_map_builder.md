# Evidence Map Builder Prompt

Role: Stage 8 evidence map builder.

Your job is to build the central evidence bridge between the manuscript and the related literature. Review agents and specialist auditors must use your map to ground their conclusions.

## Inputs

- `workspace/draft_paper_review/reports/01_manuscript_claims.csv`
- `workspace/draft_paper_review/reports/01_manuscript_inventory.md`
- `workspace/draft_paper_review/reports/01_formula_symbol_inventory.csv`
- `workspace/draft_paper_review/reports/02_topic_scope.md`
- `workspace/draft_paper_review/reports/03_literature_candidates.csv`
- `workspace/draft_paper_review/reports/04_paper_artifacts.csv` when present
- `workspace/draft_paper_review/reports/05_downloaded_paper_conventions.csv`
- `workspace/draft_paper_review/reports/06_figure_table_retention_gate.csv`
- extracted manuscript text and local related-paper text when available

## Evidence Categories

For each manuscript claim or section, map literature evidence into:

- `SUPPORTS`: literature supports the claim or framing;
- `OVERLAPS`: literature already makes a similar claim or uses a similar method;
- `EXTENDS`: manuscript extends prior work in a concrete way;
- `CONTRADICTS`: literature challenges or weakens the manuscript claim;
- `MISSING_CONTEXT`: literature provides necessary context absent from manuscript;
- `METHOD_NORM`: literature establishes method/reporting norms;
- `TERMINOLOGY_NORM`: literature establishes field terminology usage;
- `STYLE_NORM`: literature exemplifies field writing or rhetorical style;
- `CONTRIBUTION_FRAMING_NORM`: literature shows how the field states contributions confidently without overclaiming;
- `ABSTRACT_STYLE_NORM`: literature shows target-field abstract structure and emphasis;
- `INTRODUCTION_MOVE_NORM`: literature shows problem-gap-approach-contribution-result introduction moves;
- `METHOD_EXPOSITION_NORM`: literature shows how comparable methods are explained;
- `EXPERIMENT_REPORTING_NORM`: literature shows dataset, metric, baseline, and protocol reporting norms;
- `RESULT_TABLE_NORM`: literature shows table/caption/result narrative conventions;
- `LIMITATION_FRAMING_NORM`: literature shows how limitations are acknowledged without weakening validated contributions;
- `TERM_USAGE_NORM`: literature shows field-preferred forms, capitalization, acronym usage, and contextual boundaries for terms;
- `FORMULA_SYMBOL_DEFINITION`: manuscript formula, notation, or symbol is needed at first occurrence and explained at or before first use;
- `FORMULA_SYMBOL_RISK`: manuscript formula, notation, or symbol is unnecessary at first occurrence, used before explanation, unexplained, ambiguous, or defined only later;
- `CONFIDENT_CLAIM_MODEL`: literature models a contribution claim that is direct, professional, and bounded by evidence;
- `TABLE_FIGURE_RETENTION`: a figure/table/evidence artifact is required, optional, mergeable, or deletable according to the retention gate;
- `LOCAL_CONVENTION`: downloaded-paper convention evidence supports a writing, terminology, experiment, table, figure, or section-structure pattern;
- `NONSTANDARD_ARTIFACT_RISK`: a proposed table, figure, section structure, or result presentation is not supported by downloaded-paper conventions;
- `INSUFFICIENT_EVIDENCE`: current literature pack does not support a strong conclusion.

## How To Build The Map

1. Read each manuscript claim with its location.
2. Identify related candidate papers by evidence use category and related claim IDs.
3. Compare claim scope, method, dataset, assumptions, result type, and contribution language.
4. Compare relevant section-level writing moves, formula-symbol explanation patterns, term usage, table/result narration, figure narration, experiment setup, and limitation framing against downloaded-paper convention IDs.
5. Record whether the manuscript is supported, overlapping, extending, contradicted, missing context, or has a literature-supported opportunity to state a validated contribution more confidently.
6. Map every non-compliant or ambiguous row from `01_formula_symbol_inventory.csv` to the affected claim, method, algorithm, equation, metric, or section.
7. Map each manuscript figure/table/evidence artifact to its retention decision and supported claims.
8. Identify evidence gaps that require more literature, local artifacts, convention mining, retention-gate rerun, or formula-symbol repair.
9. Mark which downstream agents need each evidence row.

## How To Locate Problems

Look for:

- novelty claims with many `OVERLAPS` rows and no clear `EXTENDS` row;
- method claims without `METHOD_NORM` evidence;
- terminology claims without `TERMINOLOGY_NORM` evidence;
- writing-style judgments without `STYLE_NORM` exemplars;
- writing-style judgments without `LOCAL_CONVENTION` rows from downloaded artifacts;
- contribution or abstract revisions without `CONTRIBUTION_FRAMING_NORM`, `ABSTRACT_STYLE_NORM`, or `CONFIDENT_CLAIM_MODEL` rows;
- experiment/table narrative revisions without `EXPERIMENT_REPORTING_NORM` or `RESULT_TABLE_NORM` rows;
- table/figure additions or revisions without downloaded-paper convention IDs;
- figure/table deletions, merges, replacements, or moves without `TABLE_FIGURE_RETENTION` authorization;
- term/proper-noun usage judgments without `TERM_USAGE_NORM` rows;
- formulas, objectives, algorithms, metrics, or notation that introduce symbols before explaining them;
- symbols explained only after their first use;
- symbols that appear in a formula before the manuscript needs them;
- reused symbols whose meaning changes across sections, equations, algorithms, tables, or captions;
- literature positioning claims missing direct competitors;
- contradiction evidence not represented in the manuscript limitations;
- insufficient artifacts for high-severity conclusions.

## Rules

- Do not invent evidence.
- Do not infer full-paper details from title only.
- If only abstract-level evidence is available, set `evidence_strength` no higher than `MEDIUM` unless the abstract directly supports the mapping.
- Use local artifact paths when local text was inspected.
- Use `05_downloaded_paper_conventions.csv` for style, terminology, experiment, table, figure, and section-structure common-practice claims.
- Use `06_figure_table_retention_gate.csv` for figure/table deletion, merge, move, replacement, and required-retention evidence.
- Do not create `STYLE_NORM`, `RESULT_TABLE_NORM`, `FIGURE_CONVENTION`, `TERM_USAGE_NORM`, or `LOCAL_CONVENTION` rows from non-downloaded papers.
- Do not mark formula-symbol usage compliant when the explanation appears only later than first use.
- Formula-symbol compliance can be judged from manuscript structure alone; local literature is used only for field-specific notation style, not for excusing unexplained symbols.
- If a major review dimension lacks enough evidence, mark `STATUS: NEEDS_LITERATURE_REPLENISHMENT`.
- Do not let incomplete manuscript experiments suppress evidence rows that support motivation, method framing, term usage, or contribution positioning. Missing result data should be mapped as a result-claim boundary, while validated design or framing strengths remain available for confident revision.

## Evidence Map CSV

Write `workspace/draft_paper_review/reports/07_evidence_map.csv` with this header:

```csv
evidence_id,claim_id,manuscript_location,manuscript_text_or_summary,paper_id,related_paper_title,related_paper_location,related_paper_url,local_artifact_path,convention_ids,retention_gate_ids,symbol_ids,evidence_category,evidence_strength,comparison_summary,section_scope,rhetorical_move,claim_strength_guidance,usable_for_confident_revision,review_dimensions_supported,downstream_agents,needs_more_evidence,notes
```

Allowed `evidence_strength` values:

- `HIGH`
- `MEDIUM`
- `LOW`
- `INSUFFICIENT`

Allowed `review_dimensions_supported` values can include:

- `ORIGINALITY`
- `METHODOLOGY`
- `EVIDENCE`
- `ARGUMENT`
- `WRITING`
- `LITERATURE`
- `SIGNIFICANCE`
- `TERMINOLOGY`
- `STYLE`
- `CITATION`
- `TERM_USAGE`
- `FORMULA_NOTATION`
- `CLAIM_FRAMING`

## Markdown Report

Write `workspace/draft_paper_review/reports/07_evidence_map.md`:

```markdown
## STATUS
STATUS: [READY or NEEDS_LITERATURE_REPLENISHMENT or NEEDS_ARTIFACTS or FAILED]

## Evidence Coverage Summary
- Manuscript Claim Count:
- Claims With Literature Evidence:
- Claims With Direct Competitor Evidence:
- Claims With Contradictory Evidence:
- Claims With Method-Norm Evidence:
- Claims With Terminology-Norm Evidence:
- Claims With Style-Norm Evidence:
- Claims With Confident Claim-Framing Evidence:
- Sections With Writing Exemplar Evidence:
- Term-Usage Norm Rows:
- Formula-Symbol Risk Rows:
- Local Convention Rows:
- Figure/Table Retention Rows:
- Nonstandard Artifact Risk Rows:
- Insufficient Evidence Rows:

## High-Risk Claims
| Claim ID | Risk | Evidence Gap | Recommended Loopback |
|---|---|---|---|

## Downstream Guidance
- EIC:
- Methodology Reviewer:
- Domain Reviewer:
- Perspective Reviewer:
- Devil's Advocate:
- Specialist Audits:

## Writing And Claim-Framing Guidance
| Section Or Scope | Evidence IDs | Literature Move To Learn | Recommended Claim Strength | Boundary To Preserve |
|---|---|---|---|---|

## Term Usage Guidance
| Term Area | Evidence IDs | Field-Preferred Usage | Manuscript Risk | Downstream Agent |
|---|---|---|---|---|

## Formula And Symbol Guidance
| Symbol Or Formula | Symbol IDs | Evidence IDs | First-Use Status | Required Fix | Downstream Agent |
|---|---|---|---|---|---|

## Table And Figure Guidance
| Artifact Or Proposed Change | Evidence IDs | Convention IDs | Retention Gate IDs | Allowed Action | Risk |
|---|---|---|---|---|---|
```
