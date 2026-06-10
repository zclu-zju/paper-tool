# User-Required Parameters

This document defines how the Deep Paper Search workflow should obtain parameters. The preferred model is calibration-first. The user gives an initial research goal, the system runs a lightweight calibration search, then it presents a compact confirmation bundle and writes `config/deep-paper-search.yaml`. The workflow should not demand a complete config before it has tested whether the initial direction and keywords are accurate.

## Initial User Input

The user should initially provide one of the following:

1. A research direction or question.
2. A keyword idea.
3. A seed paper path, title, abstract, or summary.
4. A mixed request containing direction, constraints, and seed material.

This is enough to start calibration. The workflow should not ask for detailed inclusion criteria, output format, code cloning, or every keyword before calibration.

## Calibration Pass

The workflow should run a lightweight calibration pass before full deep search. This pass should:

1. Decompose the user goal into domain, task, object, method, setting, and possible evaluation target.
2. Disambiguate the domain when terms have multiple meanings.
3. Generate first-pass seed terms and aliases.
4. Compile a small number of Boolean and semantic queries.
5. Probe a small result set from open scholarly sources.
6. Extract observed terms from candidate titles and abstracts.
7. Produce candidate scope boundaries.
8. Produce a default config proposal.

The calibration pass is successful when it can show the user candidate keywords, candidate domain interpretation, likely in-scope themes, likely near-scope themes, and a few example candidate papers or paper-like records. It should not be treated as the final corpus.

## Confirmation Bundle

After calibration, the workflow should ask the user to confirm or edit a small bundle:

1. **Research direction or seed**: the topic, direction, keyword set, seed paper path, seed paper title, seed paper abstract, or short description.
2. **Interpreted domain**: the field or community inferred from calibration.
3. **Candidate keyword groups**: user terms, observed paper terms, aliases, and exclusion terms.
4. **Candidate scope boundaries**: in-scope, near-scope, and out-of-scope interpretations.
5. **Minimum core paper count**: the lower bound for relevant papers that must be found or else reported as `STOP_WITH_RISK`.
6. **Year policy**: a year range, recent-years window, all-years policy, or foundational-plus-recent policy.
7. **Search depth**: `EXPLORATORY`, `DEEP_SURVEY`, `SYSTEMATIC_LIKE`, or `NEAR_EXHAUSTIVE`.
8. **Paper artifact download policy**: no artifacts, PDFs only, TeX only, or both.

If the user accepts the bundle, the workflow proceeds to full deep search. If the user edits it, update `config/deep-paper-search.yaml` and then proceed.

## Defaults

Use these defaults unless calibration or the user indicates otherwise:

- `minimum_core_papers`: 30.
- `search_depth`: `DEEP_SURVEY`.
- `execution.todo_mode`: false.
- `year_policy.mode`: `FOUNDATIONAL_PLUS_RECENT`.
- `year_policy.recent_years`: 5.
- `artifact_download.paper_artifacts`: `NONE`, but ask the user if they want PDFs or TeX before artifact download stages.
- `code.record_code_availability`: true.
- `code.clone_repositories`: false.
- Primary final table and compact execution ledgers: enabled.
- Verbose debug artifacts: disabled.
- Inclusion policy: system-managed.

## TODO Mode

TODO mode is optional. If `execution.todo_mode` is true, the workflow behaves like a goal-driven execution loop. It creates a TODO queue after calibration, executes one TODO at a time, verifies completion, and may append new TODOs when audits reveal concrete unfinished work.

Use TODO mode when the user wants the system to keep working until no useful task remains. Do not use TODO mode for a quick one-pass search.

TODO mode files:

- `workspace/work/deep-paper-search/todo/active.todo`
- `workspace/work/deep-paper-search/todo/done.todo`
- `workspace/work/deep-paper-search/todo/todo_state.json`
- `workspace/work/deep-paper-search/todo/todo_log.md`

The workflow may stop in TODO mode only when the active TODO queue is empty, the continuation auditor says no new TODO is justified, and final stop validation passes. New TODOs must have evidence, source, priority, target stage or agent, and completion criteria. Duplicate, vague, or low-yield TODOs should be merged, rejected, or converted to residual risk.

## Search Depth Meaning

Search depth controls how hard the system works before it is allowed to stop:

- `EXPLORATORY`: find enough representative papers to understand the area. Use fewer expansion loops and lower coverage thresholds.
- `DEEP_SURVEY`: default mode. Search multiple sources, expand by terms, citations, authors, venues, datasets, and code signals, then run coverage audit.
- `SYSTEMATIC_LIKE`: stronger reproducibility. Preserve detailed query logs, inclusion and exclusion decisions, citation closure, and coverage evidence.
- `NEAR_EXHAUSTIVE`: highest effort. Continue until marginal yield, coverage audit, and adversarial review support stopping, or budget is exhausted with residual risk.

Depth does not mean "make the prompt longer." It controls iteration count, source diversity, citation closure strictness, coverage threshold, and adversarial review strictness.

## Default Inclusion Policy

The default inclusion policy is system-managed:

- Include a paper in the core corpus when the title, abstract, keywords, or available full text clearly match the user direction or a discovered equivalent term.
- Include a paper when it uses different terminology but matches the same task, mechanism, dataset, benchmark, or citation cluster.
- Keep near-scope papers outside the core corpus but mine them for terms, references, authors, venues, datasets, and code signals.
- Exclude papers whose overlap is only a shared word, a different domain sense, a generic background mention, or an unrelated method reused in a different task.
- Record relevance and reference value separately. A paper can be relevant but low quality, or near-scope but useful for discovering vocabulary.

The user may override inclusion and exclusion criteria in the config, but should not be forced to define them for ordinary runs.

## Code Policy

By default, the workflow records whether a paper appears to have open-source code and stores code URLs as signals. It does not clone repositories. Repository cloning is disabled because literature research usually needs code availability as metadata, not local repository state. Cloning should be enabled only when the user explicitly requests implementation inspection, reproduction, or local artifact collection.

## Paper Artifact Policy

PDF and TeX download should be explicitly controlled by the user because it affects storage, access, copyright constraints, and runtime. The workflow may ask:

1. Download no paper artifacts.
2. Download public PDFs only.
3. Download public TeX or source archives only.
4. Download both public PDFs and public TeX sources.

The workflow must not bypass access controls.

## Output and Ledger Policy

The user does not need to choose output formats for normal runs. The default primary output is:

- `workspace/work/deep-paper-search/final/final_papers.csv`
- `workspace/work/deep-paper-search/final/final_papers.xlsx` when spreadsheet export is enabled

The final table should consolidate the useful paper information into one row per paper. Required columns include title, authors, year, venue, DOI/arXiv identifiers, paper URL, abstract, abstract source, citation count, citation source, code availability, code URL, code evidence, relevance label, relevance score, value score, idea relation, quality notes, limitations, motivation, source query, discovery path, and `summary_zh` as the final column. The `summary_zh` cell must be written in Chinese and should summarize what the paper does, how closely it matches the user's direction or idea, the paper motivation, limitations, possible collision or relationship with the user's idea, and useful inspiration.

Compact execution ledgers are required even when verbose artifacts are disabled:

- `workspace/work/deep-paper-search/ledgers/run_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/stage_ledger.csv`
- `workspace/work/deep-paper-search/ledgers/stage_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/agent_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/query_ledger.jsonl`
- `workspace/work/deep-paper-search/ledgers/artifact_index.json`
- `workspace/work/deep-paper-search/ledgers/failure_ledger.jsonl`

These files are not optional noise. They are the minimum observability layer for subagent mode. They let the user locate which stage ran, which agent produced which artifact, where a query came from, why a loopback happened, and where a failure occurred. Verbose debug artifacts, raw dumps, large graphs, BibTeX, JSON corpus mirrors, and extra narrative reports should be enabled only when the config or user asks for them.

## Minimal Clarification Set

When the user gives only a rough topic, the workflow should usually ask these three questions first:

1. What is the exact research direction or seed paper?
2. What is the minimum number of relevant papers to find?
3. What year range or recency policy should be used?

If the direction is ambiguous, ask a domain clarification question. If the user did not specify artifact download, ask whether to download PDFs, TeX sources, both, or neither. Everything else can use defaults unless the user asks for tighter control.
