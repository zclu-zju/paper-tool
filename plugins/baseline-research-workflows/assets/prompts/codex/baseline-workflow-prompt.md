# Baseline Discovery Codex CLI Prompt

Use this from the repository root:

```bash
codex --search --sandbox workspace-write --ask-for-approval never
```

Then paste:

```text
Use the baseline-orchestrator custom agent and execute the full baseline discovery workflow.

Repository constraints:
- Do not modify paper/ or prompts/.
- Write all generated outputs under workspace/reports/.
- Save safely retrieved baseline repositories under workspace/baselines/.
- Use the project custom agents in .codex/agents/.

Required flow:
1. Run paper-auditor first and wait for workspace/reports/audit_report.md.
2. Spawn literature-scout-arxiv, literature-scout-pwc, and literature-scout-venues in parallel after Stage 1.
3. Merge Stage 2 outputs into workspace/reports/literature_candidates.md, preserving arXiv IDs, URLs, public-code signals, and search queries. The first discovery round should aim for at least 20 candidates because no-code papers will be discarded.
   - Require at least 10 recent-three-year candidates when possible. With current date 2026-06-03, recent means years 2024-2026.
   - Older classic candidates may be used for remaining slots only when sorted by citation count within the locked field boundary. Preserve citation count/source and exact citation-search query.
4. Run oss-verifier and wait for workspace/reports/oss_verification.json, workspace/reports/baseline_registry.json, and workspace/reports/rejected_no_code.md. If .env contains GITHUB_TOKEN, use it for GitHub API search without printing the token. Search GitHub when papers do not include repo URLs, but accept and clone only repositories with concrete evidence. Use shallow clone only; never run third-party code.
5. Count accepted baselines in baseline_registry.json. Only status CLONED with local_path, commit_sha, and evidence counts. Target N = 10. Also count accepted recent-three-year baselines. Target R = 5.
6. If fewer than 10 accepted CLONED baselines exist, do not run experiment-designer yet. Return to Stage 2 and find additional in-domain public-code candidates, excluding every title/repository in rejected_no_code.md. Re-run Stage 3 and merge accepted repositories until N = 10 or the field is documented as exhausted after all sources and query variants have been tried.
7. If fewer than 5 accepted CLONED baselines are from years 2024-2026, do not run experiment-designer yet. Return to Stage 2 and find additional recent in-domain public-code candidates.
8. Run experiment-designer only after 10 accepted CLONED baselines exist and at least 5 are from years 2024-2026, then wait for workspace/reports/experiment_protocol.md.
9. Run integrity-reviewer and wait for workspace/reports/integrity_report.md.
10. If VERDICT: REJECT, follow prompts/orchestrator.md Loopback Mode, update workspace/reports/iteration_log.md, and retry automatically with no iteration-count or wall-clock runtime limit.
11. If access is denied, rate-limited, or temporarily unavailable, do not ask the user. Wait and retry automatically using reset/retry headers when available, otherwise exponential backoff. Record waits/retries in workspace/reports/retry_log.md.
12. Never ask for strategic intervention or manual approval. Continue until VERDICT: GO or the field is documented as exhausted after all query variants and sources have been tried.

Finish by summarizing the verdict and listing every report path.
```

For non-interactive execution:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/baseline-workflow-prompt.md
```
