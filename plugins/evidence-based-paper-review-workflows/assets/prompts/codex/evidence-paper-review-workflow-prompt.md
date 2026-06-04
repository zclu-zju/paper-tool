Use the evidence-paper-review-orchestrator custom agent and execute the evidence-based paper review workflow.

Repository constraints:
- Treat the submitted manuscript as read-only.
- Write all generated outputs under workspace/evidence_paper_review/.
- Use the project custom agents in .codex/agents/.
- Do not overwrite original PDF or TeX source files.

Required behavior:
1. Run Stage 0 requirement collection first.
2. If required parameters are missing, ask the user no more than 3 questions and stop.
3. Run Stage 1 manuscript ingestion after requirements are ready.
4. Run Stage 2 topic scope analysis after the manuscript has been ingested.
5. Run Stage 3 user scope confirmation and stop until the user confirms or corrects the inferred topic, method family, target community, and excluded adjacent areas.
6. Search literature only after requirements are READY and topic_scope.md is USER_CONFIRMED.
7. Preserve abstracts, citation counts, search queries, source URLs, artifact URLs, relevance rationales, and evidence use categories for every related-paper candidate.
8. Download related-paper PDFs or TeX/source archives when requested or when local inspection is necessary for a strong review claim.
9. Build evidence_map.csv linking manuscript claims and sections to literature evidence before any evidence-based review agent runs.
10. Run the reviewer panel and specialist diagnostic panel. Every major issue must cite manuscript location plus evidence_map rows or related papers.
11. Synthesize scores and decision from reviewer reports and specialist audits. Do not invent issues in synthesis.
12. If revision is requested, create a traceable revision plan, write revised copies under workspace/evidence_paper_review/revision/, and verify the revision.
13. Run integrity review.
14. If any stage is rejected, loop back to the specified target stage and retry automatically unless user input is required.
