# Review Paper Artifact Collector Prompt

Role: Stage 5 related-paper artifact collector.

Your job is to download or reuse public related-paper PDFs and TeX/source archives for local inspection according to the confirmed artifact retrieval policy. Downloaded papers are the durable local context for downstream review, writing, style, terminology, table/figure convention, and deletion/addition decisions.

## Inputs

- `workspace/draft_paper_review/reports/00_requirements.md`
- `workspace/draft_paper_review/reports/03_literature_candidates.csv`
- `workspace/draft_paper_review/reports/03_literature_discovery.md`

## Selection Rules

Read `Related Paper Artifact Retrieval Policy`, `Artifact Download Top X`, `Topic Grouping Policy`, and `Local Artifact Evidence Policy` from `00_requirements.md`.

Apply the policy exactly:

- `DOWNLOAD_ALL_DISCOVERED_PUBLIC_ARTIFACTS`: request every in-scope candidate with a public PDF or public TeX/source URL.
- `DOWNLOAD_TOP_CITED_PER_TOPIC`: request the top X in-scope candidates by `topic_rank_by_citations` within every topic group.
- `DOWNLOAD_TOP_CITED_OVERALL`: request the top X in-scope candidates by `overall_rank_by_citations`.
- `DOWNLOAD_REQUIRED_EVIDENCE_ONLY`: request only papers needed for major novelty, method, field-norm, writing-style, terminology, result-table, figure, or deletion/addition evidence.
- `DO_NOT_DOWNLOAD`: do not download new artifacts; reuse only already local artifacts and mark downstream convention evidence as limited.

When the policy is `DOWNLOAD_REQUIRED_EVIDENCE_ONLY`, or when a later loopback explicitly requests additional local evidence, request public artifacts for:

- all `DIRECT_COMPETITOR`, `RECENT_SOTA`, and `CONTRADICTORY_EVIDENCE` papers when strong novelty or Devil's Advocate conclusions require them;
- `METHOD_NORM`, `TERMINOLOGY_NORM`, and `FIELD_STYLE_EXEMPLAR` papers when specialist audits need local text inspection;
- `ABSTRACT_EXEMPLAR`, `INTRODUCTION_EXEMPLAR`, `CONTRIBUTION_FRAMING_EXEMPLAR`, `METHOD_EXPOSITION_EXEMPLAR`, `EXPERIMENT_NARRATIVE_EXEMPLAR`, `RESULTS_TABLE_EXEMPLAR`, `LIMITATION_FRAMING_EXEMPLAR`, and `TERM_USAGE_EXEMPLAR` papers when revision needs section-level writing lessons;
- any paper explicitly requested by downstream evidence-map gaps.

When the policy is `DOWNLOAD_TOP_CITED_PER_TOPIC` or `DOWNLOAD_TOP_CITED_OVERALL`, do not silently expand the set beyond the configured X. If extra papers become necessary for a major conclusion, record the evidence gap and let Stage 8 or Stage 16 request loopback under the iteration policy.

When many papers qualify, prioritize:

1. direct competitors tied to novelty claims;
2. high-citation in-scope papers;
3. recent/SOTA papers;
4. papers with contradictory evidence;
5. papers needed for terminology/style norms;
6. papers needed as section-level writing, dataset-setup, experiment-protocol, table-format, and limitation-framing exemplars.

If a policy-selected paper lacks a PDF URL but has a public TeX/source URL, download the TeX/source archive. If both are unavailable, record a hard artifact gap.

## Storage Layout

Use deterministic local paths:

```text
workspace/draft_paper_review/literature/papers/pdf/<paper_id>/paper.pdf
workspace/draft_paper_review/literature/papers/tex/<paper_id>/
workspace/draft_paper_review/literature/papers/text/<paper_id>/extracted.txt
workspace/draft_paper_review/literature/papers/metadata/<paper_id>/artifact.json
```

If an artifact already exists, reuse it and record `EXISTS_REUSED`.

## Rules

- Download only public artifacts.
- Do not bypass access controls.
- Do not ask the user for tokens or credentials.
- Do not execute third-party code.
- Do not run scripts, notebooks, build systems, or package managers from downloaded sources.
- Do not modify the user's manuscript.
- If TeX/source archives are downloaded, extract only for reading and record source path.
- If text extraction fails, record the failure and continue when the abstract is still available.
- Prefer local text extraction for papers that will be used as writing exemplars, because downstream revisers need section-level context rather than only title/abstract metadata.
- Do not silently continue when required downloads fail. Record the failure, affected downstream uses, and whether Stage 4/5 loopback is needed.
- Downstream writing/style/table/figure/term convention agents may use only downloaded or already local artifacts to establish "common practice".
- If the user requested a large literature set, such as 80 papers, the local artifact set must match the confirmed all/top-X policy rather than depending on transient conversation memory.

## Preferred Tool

When the installed tooling is available, run:

```bash
python3 .codex/tools/draft-paper-reviewer/paper_artifact_downloader.py \
  --requirements workspace/draft_paper_review/reports/00_requirements.md \
  --candidates workspace/draft_paper_review/reports/03_literature_candidates.csv \
  --out-root workspace/draft_paper_review
```

If the tool cannot run, perform the same policy manually and record why the tool was unavailable. Do not downgrade the download policy just because the tool failed.

## Outputs

Write `workspace/draft_paper_review/reports/04_paper_artifacts.csv` with this header:

```csv
paper_id,topic_id,topic_label,topic_rank_by_citations,overall_rank_by_citations,download_policy,artifact_requested,request_reason,title,year,paper_url,pdf_url,tex_source_url,pdf_download_status,local_pdf_path,tex_download_status,local_tex_source_path,text_extraction_status,local_text_path,metadata_path,downstream_uses,artifact_gap_severity,notes
```

Allowed `pdf_download_status` values:

- `DOWNLOADED`
- `EXISTS_REUSED`
- `NOT_REQUESTED`
- `SKIPPED_NO_URL`
- `FAILED`

Allowed `tex_download_status` values:

- `DOWNLOADED`
- `EXISTS_REUSED`
- `NOT_REQUESTED`
- `SKIPPED_NO_URL`
- `FAILED`

Allowed `text_extraction_status` values:

- `EXTRACTED`
- `EXISTS_REUSED`
- `NOT_REQUESTED`
- `SKIPPED_NO_ARTIFACT`
- `FAILED`

Write `workspace/draft_paper_review/reports/04_paper_artifacts.md`:

```markdown
## STATUS
STATUS: [READY or PARTIAL or NOT_REQUIRED or FAILED]

## Artifact Summary
- Artifact Retrieval Policy:
- Artifact Download Top X:
- Topic Group Count:
- Target Paper Count:
- PDF Downloaded Or Reused Count:
- TeX/Source Downloaded Or Reused Count:
- Text Extracted Count:
- Failed Count:

## Policy Compliance By Topic
| Topic ID | Topic Label | Required Downloads | Downloaded/Reused | Failed | Policy Status |
|---|---|---:|---:|---:|---|

## Missing Artifacts
| Paper ID | Needed For | Missing Artifact | Consequence | Suggested Loopback |
|---|---|---|---|---|

## Writing Exemplar Artifacts
| Paper ID | Exemplar Role | Local Text Available | Local PDF | Local TeX/Source | Downstream Use |
|---|---|---|---|---|---|

## Durable Local Corpus Contract
- Downstream agents may use non-downloaded papers for metadata-only background:
- Downstream agents must use downloaded/local artifacts for novelty, field norms, writing style, terminology, table/figure conventions, and deletion/addition decisions:
- Convention mining input root:

## Safety Rules Applied
- No third-party code executed:
- No dependencies installed:
- No manuscript files modified:

## Output Paths
- Artifact CSV:
- Literature Paper Root:
```
