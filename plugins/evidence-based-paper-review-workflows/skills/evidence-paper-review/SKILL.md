---
name: evidence-paper-review
description: Use for evidence-driven academic manuscript review in a Codex repo. Installs repo-local custom agents from this plugin, ingests a user-provided PDF or TeX source folder, infers and asks the user to confirm the paper topic, discovers and optionally downloads related papers, builds a local evidence map, runs multi-perspective reviewer and specialist audit agents whose findings must cite the manuscript and downloaded literature, synthesizes scores and decisions, optionally revises/polishes the manuscript, verifies revisions, and loops back until quality gates pass.
---

# Evidence Paper Review

This skill installs and launches an iterative manuscript review workflow. It is designed for the user's own research workflow, not for generic peer-review roleplay.

The workflow accepts:
- a manuscript PDF;
- a TeX source folder;
- a compiled PDF plus TeX source folder;
- optional target venue, target tier, review strictness, desired language, and revision preference.

The workflow must first infer the manuscript topic and comparison boundary, then ask the user whether the inferred topic is accurate. It must not search or review until the topic scope is confirmed.

## Install Agents

The plugin carries custom agent templates in `assets/agents/`, prompt protocols in `assets/prompts/`, and an installer script.

From a local clone:

```bash
python3 plugins/evidence-based-paper-review-workflows/scripts/install_project_agents.py --repo .
```

From an installed plugin cache, resolve the installer relative to this skill directory:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo>
```

Clean obsolete files from older local versions only when requested:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo> --clean-obsolete
```

The installer is conservative. It copies missing files, leaves identical files unchanged, reports conflicts without overwriting, and removes known obsolete files only when `--clean-obsolete` is passed.

## Launch

After installing agents, invoke:

```text
Use the evidence-paper-review-orchestrator custom agent and execute the evidence-based paper review workflow.
```

Or use the launcher file:

```bash
codex exec --search --sandbox workspace-write --ask-for-approval never - < .codex/evidence-paper-review-workflow-prompt.md
```

## Interaction Contract

Stage 0 must collect required parameters before any paper search or review:
- manuscript source type and path;
- whether the workflow may compile TeX if a TeX source is provided;
- target field, venue, or tier if known;
- target review strictness and desired output language;
- minimum related-paper count;
- minimum recent/SOTA related-paper count;
- whether related-paper PDFs or TeX sources must be downloaded locally;
- whether manuscript revision is requested or review-only mode is desired;
- final quality threshold, with 3.5/5 as the default only after stating it;
- maximum total workflow iterations, if the user wants a global cap;
- maximum repeated iterations for the same stage/problem pair, with 3 as the default after stating it;
- objective limitation policy for issues that cannot be fixed from the current manuscript, such as missing experiments, unavailable raw data, missing human-subject approvals, or unavailable proprietary artifacts;
- missing score policy for dimensions that cannot be assessed because required evidence is objectively absent;
- any inclusion/exclusion constraints for related literature.

Stage 2 infers the topic. Stage 3 must ask the user to confirm the inferred topic and excluded adjacent areas. The workflow must stop there until the user confirms or corrects the scope.

Only after:

```text
requirements.md: STATUS: READY
topic_scope.md: STATUS: USER_CONFIRMED
```

may the workflow search related papers.

## Evidence Rule

All review and audit conclusions must be traceable to:
- a manuscript location, such as page/section/paragraph, line, figure, table, claim ID, or TeX file path;
- one or more entries in `workspace/evidence_paper_review/reports/evidence_map.csv`;
- downloaded or verified related literature when the issue concerns novelty, terminology, field norms, literature positioning, SOTA comparison, methods, or writing style.

Generic comments such as "the novelty is weak" are invalid unless they name the overlapping prior work and explain the specific overlap.

## Outputs

All generated outputs go under:

```text
workspace/evidence_paper_review/
```

Main report paths:

```text
workspace/evidence_paper_review/reports/requirements.md
workspace/evidence_paper_review/reports/manuscript_inventory.md
workspace/evidence_paper_review/reports/topic_scope.md
workspace/evidence_paper_review/reports/literature_candidates.csv
workspace/evidence_paper_review/reports/paper_artifacts.csv
workspace/evidence_paper_review/reports/evidence_map.csv
workspace/evidence_paper_review/reports/reviewer_configuration.md
workspace/evidence_paper_review/reports/reviewer_reports/
workspace/evidence_paper_review/reports/specialist_audits/
workspace/evidence_paper_review/reports/editorial_decision.md
workspace/evidence_paper_review/reports/revision_plan.md
workspace/evidence_paper_review/reports/revision_verification.md
workspace/evidence_paper_review/reports/integrity_report.md
workspace/evidence_paper_review/reports/iteration_log.md
workspace/evidence_paper_review/revision/
workspace/evidence_paper_review/literature/papers/
```

## Score And Decision Contract

The final score uses seven 1-5 dimensions:

```text
Originality 15%
Methodological Rigor 25%
Evidence Sufficiency 20%
Argument Coherence 15%
Writing Quality 10%
Literature Integration 10%
Significance And Impact 5%
```

Default decision mapping:

```text
4.5-5.0 Accept-ready
3.5-4.4 Minor revision
2.5-3.4 Major revision
1.5-2.4 Reject / rebuild
1.0-1.4 Not review-ready
```

Hard gates:
- Devil's Advocate CRITICAL issue unresolved: cannot finalize unless the issue is objectively unfixable in the current manuscript cycle and has reached the configured repeated-issue iteration cap, in which case it must be marked `DEFERRED_OBJECTIVE_LIMITATION` and surfaced as a final risk.
- Methodology score <= 2: cannot finalize unless the low score is driven by objectively missing experiments/data that the workflow cannot create; then mark the dimension `N/A_OBJECTIVE_MISSING` or `DEFERRED_OBJECTIVE_LIMITATION` instead of forcing endless loopback.
- Literature Integration score <= 2: return to literature discovery, evidence map, or revision unless the configured repeated-issue cap has been reached for the same issue.
- Originality score <= 2 without a defensible repositioning path: cannot finalize as publish-ready; it may continue only as not-ready or deferred if the missing contribution requires new experiments or new data.
- Writing Quality score <= 2: must run revision/polish if revision is allowed; if review-only, mark not publish-ready.
- Any major review conclusion without evidence-map support: return to evidence-map building or review until the repeated-issue cap is reached, then mark the specific unsupported conclusion as excluded from scoring.

## Loopback

The integrity reviewer can reject and return to:
- Stage 0 Requirement Collector;
- Stage 1 Manuscript Ingestor;
- Stage 2 Topic Scope Analyst;
- Stage 3 User Scope Confirmation Gate;
- Stage 4 Literature Discovery Scout;
- Stage 5 Paper Artifact Collector;
- Stage 6 Evidence Map Builder;
- Stage 7 Reviewer Panel Configurator;
- Stage 8 Reviewer Panel;
- Stage 9 Specialist Diagnostic Panel;
- Stage 10 Editorial Synthesizer And Scorer;
- Stage 11 Revision Planner;
- Stage 12 Manuscript Polisher And Reviser;
- Stage 13 Revision Verifier.

If no new user input is required, the orchestrator retries automatically subject to the configured iteration policy. By default, the workflow has no global iteration cap, but the same stage/problem pair is retried at most 3 times unless the user sets another value. When the cap is reached, the issue is recorded in `iteration_log.md` and `deferred_issues.md`, excluded from further loopback, and carried into the final risk summary.
