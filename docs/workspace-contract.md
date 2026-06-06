# Paper Tool Workspace Contract

All plugins in this marketplace must follow the same workspace layout.

## Reports

Reports are plugin-scoped and must not be mixed:

```text
workspace/report/paper-research/
workspace/report/paper-experiment/
workspace/report/paper-reviewer/
```

## Shared Researched Paper Artifacts

Researched papers are shared across plugins. The user's own manuscript does not belong here.

```text
workspace/paper/pdf/{title}/paper.pdf
workspace/paper/tex/{title}/
workspace/paper/summary/{title}/
```

`{title}` is a filesystem-safe title key derived from the paper title. If needed, append an arXiv ID, DOI hash, or short hash to disambiguate duplicate titles.

`workspace/paper/summary/{title}/` is the place for derived paper artifacts, including extracted text, metadata, summaries, compile logs, and compiled PDFs.

## Plugin Work Directories

Non-report execution artifacts go under plugin-scoped work directories:

```text
workspace/work/paper-research/
workspace/work/paper-experiment/
workspace/work/paper-reviewer/
```

Examples:

- cloned research code: `workspace/work/paper-research/code/`
- rewritten experiment repo: `workspace/work/paper-experiment/rewritten_repo/`
- copied manuscript revisions: `workspace/work/paper-reviewer/revision/`
- paper-review latexdiff files: `workspace/work/paper-reviewer/diff/`

## Deprecated Paths

New plugin development should not introduce these legacy roots:

```text
workspace/literature_research/
workspace/experiment_rewrite/
workspace/draft_paper_review/
workspace/pdf/
workspace/tex/
workspace/summary/
```
