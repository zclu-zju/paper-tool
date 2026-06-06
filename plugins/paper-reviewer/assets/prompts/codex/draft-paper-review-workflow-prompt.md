Use the draft-paper-reviewer-orchestrator custom agent and execute the evidence-based paper review workflow.

Repository constraints:
- Treat the submitted manuscript as read-only.
- Write generated reports under workspace/report/paper-reviewer/ and non-report working files under workspace/work/paper-reviewer/.
- Use the project custom agents in .codex/agents/.
- Accept only a TeX source folder or explicit .tex root file as the submitted manuscript.
- Do not overwrite original TeX source files.

Required behavior:
1. Run Stage 0 requirement collection and TeX-only source scan first.
2. If the submitted manuscript is not TeX source, write STATUS: UNSUPPORTED_INPUT, tell the user TeX source is required, and stop.
3. Confirm the post-core latexdiff audit policy in Stage 0 with a default of RUN_WHEN_REVISION_AVAILABLE, and record any user-provided revised TeX source path.
4. If required parameters are missing or defaults need confirmation, ask the user no more than 3 question blocks and stop.
5. Run Stage 1 manuscript ingestion after requirements are ready.
6. Run Stage 2 topic scope analysis after the manuscript has been ingested.
7. Run Stage 3 user scope confirmation and stop until the user confirms or corrects the inferred topic, method family, target community, and excluded adjacent areas.
8. Search literature only after 00_requirements.md is READY and 02_topic_scope.md is USER_CONFIRMED.
9. Preserve abstracts, citation counts, search queries, source URLs, artifact URLs, relevance rationales, evidence use categories, and section-level writing exemplar roles for every related-paper candidate.
10. Download related-paper PDFs or TeX/source archives according to the confirmed policy: all discovered public artifacts, top X per topic, top X overall, required evidence only, or no new downloads.
11. Mine downloaded/local papers into 05_downloaded_paper_conventions.csv before any writing/style/table/figure/term common-practice judgment.
12. Run the figure/table retention gate and write 06_figure_table_retention_gate.csv before any revision can delete, merge, replace, move, or create evidence artifacts.
13. Build 07_evidence_map.csv linking manuscript claims, sections, term usage, downloaded-paper conventions, figure/table retention decisions, and literature-calibrated writing evidence before any evidence-based review agent runs.
14. Run the reviewer panel and specialist diagnostic panel, including term-usage consistency auditing. Every major issue must cite manuscript location plus 07_evidence_map rows or downloaded/local paper evidence when field norms are involved.
15. Use report-materiality-gatekeeper for human-facing diagnostic reports: write material reports using fixed numbers, leave low-value reports unwritten without renumbering, placeholders, omission logs, or explanations.
16. Synthesize scores and decision from reviewer reports and specialist audits. Do not invent issues in synthesis, and separate unsupported result boundaries from actual contribution weakness.
17. If revision is requested, create a traceable revision plan, run one-to-one reviewer/reviser pairs over copied TeX files, strengthen defensible claims where evidence supports it, enforce downloaded-paper conventions and figure/table retention gates, update 29_revision_ledger.xlsx with openpyxl tooling, and verify the revision.
18. Run integrity review.
19. After integrity review returns VERDICT: GO, run ultimate-report-synthesizer and write 99_ultimate_summary.md.
20. If the confirmed latexdiff policy allows it and revised TeX exists, run latexdiff_revision_audit.py and latexdiff-change-auditor after 99_ultimate_summary.md. Write diff/latexdiff.tex, diff/latexdiff.pdf when local LaTeX compilation succeeds, 100_latexdiff_changes.csv, 100_latexdiff_extraction.md/.tex, and 101_change_rationale_audit.md/.tex.
21. If any stage is rejected, loop back to the specified target stage and retry automatically unless user input is required.
