# Paper Experiment Multi-Agent Design

This design describes the current `paper-experiment` workflow. It keeps the original staged experiment rewrite logic and normalizes only names and filesystem roots for the shared paper-tool contract.

## Contract

Every stage writes auditable reports under:

```text
workspace/report/paper-experiment/
```

Non-report working files go under:

```text
workspace/work/paper-experiment/
workspace/work/paper-experiment/rewritten_repo/
```

## Report Artifacts

```text
workspace/report/paper-experiment/requirements.md
workspace/report/paper-experiment/experiment_contract.md
workspace/report/paper-experiment/transfer_readiness.md
workspace/report/paper-experiment/baseline_inventory.csv
workspace/report/paper-experiment/rewrite_plan.csv
workspace/report/paper-experiment/input_adapter_plan.csv
workspace/report/paper-experiment/baseline_triage_notes.md
workspace/report/paper-experiment/implementation_manifest.csv
workspace/report/paper-experiment/implementation_notes.md
workspace/report/paper-experiment/validation_results.csv
workspace/report/paper-experiment/model_profile.csv
workspace/report/paper-experiment/validation_notes.md
workspace/report/paper-experiment/final_model_summary.csv
workspace/report/paper-experiment/final_summary.md
workspace/report/paper-experiment/integrity_report.md
workspace/report/paper-experiment/iteration_log.md
```

## Stages

```text
Stage 0  experiment-requirement-collector
Stage 1  experiment-scope-contract-locker
Stage 2  baseline-transfer-readiness-checker
Stage 3  baseline-triage-planner
Stage 4  experiment-rewrite-executor
Stage 5  minimal-validation-profiler
Stage 6  experiment-report-writer
Stage 7  experiment-integrity-reviewer
```

Stage 7 may reject a downstream artifact and route the workflow back to the exact target stage named in its report. Loopback rows are appended to:

```text
workspace/report/paper-experiment/iteration_log.md
```
