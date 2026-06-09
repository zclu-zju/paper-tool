# User-Required Parameters

This document defines the parameters the Deep Paper Search workflow may need from the user. The workflow should not ask for all of these at once. It should collect the minimal set required for the requested depth and only ask follow-up questions when the missing answer changes the search boundary, access model, budget, or final output.

## Required Before Search

These parameters are required before the workflow starts literature retrieval:

1. **Research seed type**: one of `DIRECTION`, `KEYWORDS`, `SEED_PAPER`, `MIXED`, or `UNKNOWN`.
2. **Research seed content**: the research direction, keyword set, seed paper path, seed paper title, seed paper abstract, or short description.
3. **Target domain or disambiguation hint**: the field or community the user intends, especially when terms are ambiguous across domains.
4. **Primary research objective**: what the search should explain or collect, such as mechanism understanding, survey corpus, benchmark comparison, method taxonomy, code-bearing papers, or near-exhaustive related work.
5. **Desired search depth**: `EXPLORATORY`, `DEEP_SURVEY`, `SYSTEMATIC_LIKE`, or `NEAR_EXHAUSTIVE`.
6. **Approximate output size**: target number of core papers, or permission for the workflow to choose a count from the depth contract.
7. **Time or recency requirement**: year range, recent-years window, include-foundational-work requirement, or no year restriction.
8. **Inclusion criteria**: required tasks, methods, datasets, venues, publication types, languages, or evidence standards.
9. **Exclusion criteria**: explicitly unwanted fields, tasks, application domains, paper types, or noisy meanings of shared terms.
10. **Final output format**: at minimum whether the user wants Markdown only, CSV/BibTeX/JSON, evidence graph, monitoring configuration, or all standard outputs.

If any of the above are absent, the first-stage agents should either infer a provisional value from evidence and record it as an assumption, or ask the user no more than three concise questions when the missing value would change the search boundary.

## Required Only For Code-Oriented Runs

Ask these only if the user wants code availability, repository verification, repository cloning, benchmark reproduction, or implementation-oriented analysis:

1. **Code requirement level**: `IGNORE_CODE`, `RECORD_CODE_SIGNALS`, `VERIFY_CODE_LINKS`, or `REQUIRE_CODE_AVAILABLE`.
2. **Repository cloning policy**: `DO_NOT_CLONE`, `CLONE_SELECTED`, `CLONE_ALL_VERIFIED`, or `ASK_BEFORE_EACH_CLONE`.
3. **Clone target directory**: default may be `workspace/work/deep-paper-search/code/` if the user accepts defaults.
4. **Repository access expectation**: public-only, private allowed, institution-hosted, unknown, or user-managed.
5. **Git LFS and submodule policy**: skip, fetch if needed, or ask before fetching.
6. **Reproducibility depth**: record repository only, inspect README, verify commit, run tests, or reproduce experiments.

The workflow must not ask the user to paste secrets. If authentication is required, ask the user to configure SSH, Git credential helper, GitHub CLI, or an environment variable in the local environment.

## Required Only For Paper Artifact Retrieval

Ask these only if the user wants local PDFs, TeX sources, supplementary files, or compiled paper artifacts:

1. **Artifact retrieval policy**: `DO_NOT_DOWNLOAD`, `DOWNLOAD_SELECTED`, `DOWNLOAD_ALL_IN_SCOPE`, or `DOWNLOAD_VERIFIED_CODE_ONLY`.
2. **Artifact types**: PDF, HTML snapshot, TeX source, supplementary files, dataset links, or all available public artifacts.
3. **Artifact target directory**: default may be `workspace/work/deep-paper-search/artifacts/` if the user accepts defaults.
4. **TeX compile policy**: `DOWNLOAD_ONLY`, `COMPILE_IF_ENV_AVAILABLE`, or `REQUIRE_COMPILE_SUCCESS`.
5. **Missing dependency policy**: skip and record, ask user to install, or fail the artifact stage.

The workflow may only download publicly accessible artifacts or artifacts the user is authorized to access. It must not bypass access controls.

## Optional Quality Preferences

These improve output quality but should not block search unless the user marks them as required:

1. Preferred databases or sources.
2. Preferred venues or excluded venues.
3. Citation-count preference or tolerance for new low-citation papers.
4. Whether to include preprints.
5. Whether to include surveys.
6. Whether to include patents, standards, and white papers as terminology evidence.
7. Preferred citation style for final reports.
8. Preferred language of final human-readable reports.
9. Maximum runtime, API budget, download budget, or token budget.
10. Whether the workflow should continue monitoring after the first run.

## Minimal Clarification Set

When the user gives only a rough topic, the workflow should usually ask these three questions first:

1. What search depth do you want: exploratory, deep survey, systematic-like, or near-exhaustive?
2. What final output do you want: paper list only, CSV/BibTeX/JSON package, evidence graph, coverage report, or all standard outputs?
3. Are there any hard inclusion or exclusion criteria, such as year range, target domain, paper type, dataset, method family, or venue?

If the answer gives permission to use sensible defaults, the workflow may proceed with a recorded default depth contract and ask fewer questions.
