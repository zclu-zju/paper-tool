Use the draft-paper-reviewer-orchestrator custom agent and execute the evidence-based paper review workflow.

Repository constraints:
- Treat the submitted manuscript as read-only.
- Write all generated outputs under workspace/draft_paper_review/.
- Use the project custom agents in .codex/agents/.
- Accept only a TeX source folder or explicit .tex root file as the submitted manuscript.
- Do not overwrite original TeX source files.

Required behavior:
1. Run Stage 0 requirement collection and TeX-only source scan first.
2. If the submitted manuscript is not TeX source, write STATUS: UNSUPPORTED_INPUT, tell the user TeX source is required, and stop.
3. If required parameters are missing or defaults need confirmation, ask the user no more than 3 question blocks and stop.
4. Run Stage 1 manuscript ingestion after requirements are ready.
5. Run Stage 2 topic scope analysis after the manuscript has been ingested.
6. Run Stage 3 user scope confirmation and stop until the user confirms or corrects the inferred topic, method family, target community, and excluded adjacent areas.
7. Search literature only after 00_requirements.md is READY and 02_topic_scope.md is USER_CONFIRMED.
8. Preserve abstracts, citation counts, search queries, source URLs, artifact URLs, relevance rationales, evidence use categories, and section-level writing exemplar roles for every related-paper candidate.
9. Download related-paper PDFs or TeX/source archives when requested or when local inspection is necessary for a strong review claim.
10. Build 05_evidence_map.csv linking manuscript claims, sections, term usage, and literature-calibrated writing evidence before any evidence-based review agent runs.
11. Run the reviewer panel and specialist diagnostic panel, including term-usage consistency auditing. Every major issue must cite manuscript location plus 05_evidence_map rows or related papers.
12. Synthesize scores and decision from reviewer reports and specialist audits. Do not invent issues in synthesis, and separate unsupported result boundaries from actual contribution weakness.
13. If revision is requested, create a traceable revision plan, run one-to-one reviewer/reviser pairs over copied TeX files, strengthen defensible claims where evidence supports it, update 27_revision_ledger.xlsx with openpyxl tooling, and verify the revision.
14. Run integrity review.
15. After integrity review returns VERDICT: GO, run ultimate-report-synthesizer and write 99_ultimate_summary.md.
16. If any stage is rejected, loop back to the specified target stage and retry automatically unless user input is required.
