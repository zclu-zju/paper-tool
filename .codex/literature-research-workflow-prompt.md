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
7. Ask whether verified repositories should be cloned locally. Clone only when the user explicitly requests it.
8. If repository cloning is requested, clone verified repositories under workspace/literature_research/code/ and stop for local auth setup when SSH, tokens, private access, Git LFS, or submodules are needed.
9. Ask whether paper PDFs or TeX sources should be downloaded locally. Download only when the user explicitly requests it.
10. If paper artifact retrieval is requested, download requested PDFs/TeX sources under workspace/literature_research/papers/. If TeX compilation is requested, compile only when a local TeX toolchain is available, then verify whether the compiled PDF exists and record the result.
11. Produce final_papers.csv with title, year, venue, publication_type, paper_url, arxiv_id, code_available, code_url, code_evidence, source_query, relevance_rationale, clone_requested, clone_status, local_clone_path, commit_hash, artifact_requested, pdf_download_status, local_pdf_path, tex_download_status, local_tex_source_path, tex_compile_status, compiled_pdf_path, and status.
12. Run integrity review.
13. If review rejects any stage, loop back to the specified stage and retry automatically unless user input is required.
