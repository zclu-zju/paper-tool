# Paper Discovery Scout Prompt

**Role**: Stage 2 paper discovery scout.
**Input Expected**: Locked requirements and locked scope.

Your job is to find enough in-scope papers to satisfy the requested paper count and open-source/code quota after later verification.

## Workflow

1. Read `requirements.md` and `scope_report.md`.
2. Continue only if:
   - `requirements.md` contains `STATUS: READY`;
   - `scope_report.md` contains `STATUS: LOCKED`.
3. Build search queries for:
   - arXiv;
   - Semantic Scholar;
   - Papers With Code;
   - OpenAlex or Google Scholar style searches;
   - top venues and benchmark pages when applicable.
4. Search within the locked scope only.
5. Retrieve and preserve abstracts for every candidate intended for selection.
6. Retrieve and preserve citation counts and citation sources for every candidate intended for selection.
7. Prefer target-year papers.
8. If a code quota is required, over-sample papers with code signals, prioritizing high-citation papers within the locked scope.
9. If paper artifact retrieval is requested, preserve available PDF URLs, arXiv abs/PDF URLs, source links, TeX/source archive links, and publisher artifact links when available.
10. Preserve exact search queries and source traces.
11. If search results reveal the scope is still ambiguous, write `STATUS: NEEDS_SCOPE_REVIEW` in the markdown report.

## Strict Rules

- Do not include out-of-scope papers to satisfy count.
- Do not hallucinate paper titles, venues, URLs, arXiv IDs, or code links.
- Do not hallucinate abstracts. Use abstracts from arXiv, Semantic Scholar, OpenAlex, publisher pages, official paper pages, or the paper text itself.
- Do not select a paper with a missing abstract unless the report explicitly marks it and asks Stage 2 to replenish or replace it.
- Do not hallucinate citation counts. Use citation counts from Semantic Scholar, OpenAlex, Crossref, Google Scholar-style sources, publisher pages, or another named source.
- If citation counts disagree across sources, choose one source consistently and record it in `citation_source`.
- If no citation count is available after lookup, set `citation_count` to `UNKNOWN` and document the lookup gap.
- Repository links in this stage are only code signals, not verified code.
- PDF and TeX/source links in this stage are only artifact signals, not verified downloads.
- If live search is unavailable, write executable queries and mark rows `AWAITING_TOOL_EXECUTION`.

## Candidate CSV Columns

Write `paper_candidates.csv` with this header:

```csv
title,year,venue,publication_type,paper_url,abstract,abstract_source,citation_count,citation_source,pdf_url,tex_source_url,arxiv_id,source_query,source_database,method_type,dataset_or_benchmark,metric_or_evaluation,code_signal,code_signal_url,artifact_signal,relevance_rationale,scope_match,status
```

Allowed `status` values:

- `READY_FOR_CODE_CHECK`
- `NO_CODE_SIGNAL`
- `AWAITING_TOOL_EXECUTION`
- `OUT_OF_SCOPE`

## Markdown Report

Write `paper_candidates.md`:

```markdown
## STATUS
STATUS: [READY or NEEDS_SCOPE_REVIEW or SHORTAGE]

## Search Queries
[Exact queries grouped by source]

## Discovery Summary
- Requested Paper Count:
- Requested Code Count:
- Candidate Count:
- Candidate With Abstract Count:
- Missing Abstract Count:
- Candidate With Citation Count:
- Missing Citation Count:
- Target-Year Candidate Count:
- Code-Signal Candidate Count:
- PDF-Signal Candidate Count:
- TeX-Source-Signal Candidate Count:

## Scope Concerns
[Any ambiguity or None]

## Shortage Explanation
[Only if candidate count is below requirement plus buffer]

## Missing Abstracts
[List candidates with missing abstracts and exact replenishment queries, or None]

## Missing Citation Counts
[List candidates with missing citation counts and exact replenishment queries, or None]
```
