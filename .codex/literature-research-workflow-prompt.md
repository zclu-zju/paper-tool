Use the literature-research-orchestrator custom agent and execute the interactive literature research workflow.

Repository constraints:
- Do not modify paper/ unless explicitly requested.
- Write all generated outputs under workspace/literature_research/.
- Use the project custom agents in .codex/agents/.

Required behavior:
1. Run Stage 0 requirement collection first.
2. If required parameters are missing, ask the user for them and stop. Do not search.
3. Run Stage 1 scope locking after requirements are ready.
4. If direction or seed-paper scope is ambiguous, ask the user to clarify and stop. Do not search.
5. Search papers only after requirements are READY and scope is LOCKED.
6. Verify code availability when the user requested an open-source/code quota.
7. Produce final_papers.csv with title, year, venue, publication_type, paper_url, arxiv_id, code_available, code_url, code_evidence, source_query, relevance_rationale, and status.
8. Run integrity review.
9. If review rejects any stage, loop back to the specified stage and retry automatically unless user input is required.
