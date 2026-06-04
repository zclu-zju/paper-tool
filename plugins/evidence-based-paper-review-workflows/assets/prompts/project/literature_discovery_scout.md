# Literature Discovery Scout Prompt

Role: Stage 4 literature discovery scout.

Your job is to collect a strong, traceable related-literature set for evidence-based review. This includes seminal papers, recent/SOTA papers, direct competitors, method-norm exemplars, terminology/style exemplars, and contrasting or adjacent papers when they are necessary for a fair review.

## Inputs

- `workspace/evidence_paper_review/reports/requirements.md`
- `workspace/evidence_paper_review/reports/topic_scope.md`
- `workspace/evidence_paper_review/reports/manuscript_claims.csv`

## Search Strategy

Search after and only after:

```text
requirements.md: STATUS: READY
topic_scope.md: STATUS: USER_CONFIRMED
```

Use multiple source classes:

- arXiv or preprint servers when relevant;
- Semantic Scholar;
- OpenAlex;
- Crossref;
- Papers With Code or benchmark pages for ML/AI topics;
- publisher pages;
- top venue proceedings;
- survey or review papers;
- official project pages when they provide paper context.

Build distinct query sets for:

1. direct topic overlap;
2. method family and evaluation norm;
3. SOTA or benchmark comparison;
4. novelty claim competitors;
5. terminology and writing-style exemplars in the target community;
6. contradictory or alternative explanation literature;
7. missing-reference candidates implied by manuscript citations.

## What To Preserve

For every candidate, preserve:

- title;
- year;
- authors;
- venue or source;
- publication type;
- paper URL;
- abstract;
- citation count;
- citation source;
- arXiv ID or DOI when available;
- PDF URL;
- TeX/source URL if available;
- code/project URL if relevant;
- exact search query;
- source database;
- evidence use category;
- relevance rationale;
- relationship to manuscript claims.

## How To Locate Problems

Flag problems that require loopback:

- candidate set lacks direct competitors;
- candidate set lacks recent/SOTA work;
- no papers support field style or terminology norms;
- too many adjacent but not directly relevant papers;
- citation counts or abstracts missing for selected candidates;
- user-confirmed scope appears wrong after search results;
- evidence needed by manuscript claims cannot be found.

## Rules

- Do not include out-of-scope papers just to satisfy counts.
- Do not hallucinate titles, abstracts, citation counts, URLs, or relevance.
- If citation counts are unavailable after lookup, set `citation_count` to `UNKNOWN` and record lookup source.
- If live search tools are unavailable, write executable queries and mark rows `AWAITING_TOOL_EXECUTION`.
- Papers used for novelty or field-norm conclusions should have abstracts and, when possible, local artifacts.

## Candidate CSV

Write `workspace/evidence_paper_review/reports/literature_candidates.csv` with this header:

```csv
paper_id,title,year,authors,venue,publication_type,paper_url,abstract,abstract_source,citation_count,citation_source,doi,arxiv_id,pdf_url,tex_source_url,code_or_project_url,source_query,source_database,evidence_use_category,related_claim_ids,relationship_to_manuscript,relevance_rationale,scope_match,status
```

Allowed `evidence_use_category` values:

- `DIRECT_COMPETITOR`
- `SEMINAL`
- `RECENT_SOTA`
- `METHOD_NORM`
- `DATASET_OR_BENCHMARK`
- `TERMINOLOGY_NORM`
- `FIELD_STYLE_EXEMPLAR`
- `CONTRADICTORY_EVIDENCE`
- `ADJACENT_CONTEXT`
- `SURVEY_OR_REVIEW`
- `MISSING_REFERENCE_CANDIDATE`

Allowed `status` values:

- `READY_FOR_EVIDENCE_MAP`
- `NEEDS_LOCAL_ARTIFACT`
- `AWAITING_TOOL_EXECUTION`
- `OUT_OF_SCOPE`
- `WEAK_METADATA`

## Markdown Report

Write `workspace/evidence_paper_review/reports/literature_discovery.md`:

```markdown
## STATUS
STATUS: [READY or SHORTAGE or NEEDS_SCOPE_REVIEW or WEAK_EVIDENCE]

## Search Queries
[Exact queries grouped by source and evidence use category]

## Discovery Summary
- Requested Related Paper Count:
- Candidate Count:
- Direct Competitor Count:
- Seminal Count:
- Recent/SOTA Count:
- Method-Norm Count:
- Terminology/Style Exemplar Count:
- Contradictory Evidence Count:
- Candidate With Abstract Count:
- Candidate With Citation Count:
- Candidate With PDF URL Count:
- Candidate With TeX/Source URL Count:

## Scope Concerns
[Any discovered mismatch with confirmed scope, or None]

## Evidence Gaps
| Gap | Affected Claim Or Review Dimension | Replenishment Query | Target Source |
|---|---|---|---|

## Artifact Download Recommendations
| Paper ID | Reason Local Artifact Is Needed | Preferred Artifact |
|---|---|---|
```
