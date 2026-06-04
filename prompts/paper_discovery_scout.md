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
5. Prefer target-year papers.
6. If a code quota is required, over-sample papers with code signals.
7. If paper artifact retrieval is requested, preserve available PDF URLs, arXiv abs/PDF URLs, source links, TeX/source archive links, and publisher artifact links when available.
8. Preserve exact search queries and source traces.
9. If search results reveal the scope is still ambiguous, write `STATUS: NEEDS_SCOPE_REVIEW` in the markdown report.

## Strict Rules

- Do not include out-of-scope papers to satisfy count.
- Do not hallucinate paper titles, venues, URLs, arXiv IDs, or code links.
- Repository links in this stage are only code signals, not verified code.
- PDF and TeX/source links in this stage are only artifact signals, not verified downloads.
- If live search is unavailable, write executable queries and mark rows `AWAITING_TOOL_EXECUTION`.

## Candidate CSV Columns

Write `paper_candidates.csv` with this header:

```csv
title,year,venue,publication_type,paper_url,pdf_url,tex_source_url,arxiv_id,source_query,source_database,method_type,dataset_or_benchmark,metric_or_evaluation,code_signal,code_signal_url,artifact_signal,relevance_rationale,scope_match,status
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
- Target-Year Candidate Count:
- Code-Signal Candidate Count:
- PDF-Signal Candidate Count:
- TeX-Source-Signal Candidate Count:

## Scope Concerns
[Any ambiguity or None]

## Shortage Explanation
[Only if candidate count is below requirement plus buffer]
```
