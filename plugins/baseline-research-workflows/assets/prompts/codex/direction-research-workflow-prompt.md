Use the direction-research-orchestrator custom agent and execute the direction-based literature research workflow.

Repository constraints:
- Do not modify paper/.
- Do not write direction outputs into workspace/reports/.
- Write direction research outputs under workspace/direction_research/reports/.
- Save safely retrieved direction repositories under workspace/direction_research/baselines/.
- Use the project custom agents in .codex/agents/.

Required flow:
1. Run direction-scope-locker first and wait for workspace/direction_research/reports/scope_report.md.
2. If scope_report.md says STATUS: NEEDS_USER_CONFIRMATION, stop and ask the listed clarification questions. Do not start literature search.
3. Only after STATUS: LOCKED, spawn direction-literature-scout-arxiv, direction-literature-scout-pwc, and direction-literature-scout-venues in parallel.
4. Merge Stage D2 outputs into workspace/direction_research/reports/literature_candidates.md, preserving source URLs, arXiv IDs, exact search queries, code signals, citation counts/sources, ambiguity exclusions, and relevance rationales.
5. If the locked scope requires public code or cloneable implementations, run direction-oss-verifier. Use shallow clone only; never run third-party code.
6. Run direction-report-writer and wait for workspace/direction_research/reports/direction_research_report.md.
7. Run direction-integrity-reviewer and wait for workspace/direction_research/reports/integrity_report.md.
8. If VERDICT: REJECT, follow prompts/direction_orchestrator.md Loopback Mode and retry automatically unless user clarification is required.
9. Finish by summarizing the verdict and listing every generated report path.
