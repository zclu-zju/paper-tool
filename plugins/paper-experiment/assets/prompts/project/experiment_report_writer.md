# Experiment Report Writer Prompt

**Role**: Stage 6 final CSV and summary writer.
**Input Expected**: Requirements, locked contract, transfer readiness, baseline inventory, rewrite plan, adapter plan, implementation manifest, validation results, and model profile.

Your job is to merge all stage outputs into a final model summary CSV and concise markdown summary. You must not invent missing validation, profiling, rewrite, adapter, preprocessing, or pretrained-weight results.

## Inputs

Read all of:

```text
workspace/report/paper-experiment/requirements.md
workspace/report/paper-experiment/experiment_contract.md
workspace/report/paper-experiment/transfer_readiness.md
workspace/report/paper-experiment/baseline_inventory.csv
workspace/report/paper-experiment/rewrite_plan.csv
workspace/report/paper-experiment/input_adapter_plan.csv
workspace/report/paper-experiment/implementation_manifest.csv
workspace/report/paper-experiment/validation_results.csv
workspace/report/paper-experiment/model_profile.csv
```

Optional but useful:

```text
workspace/report/paper-experiment/baseline_triage_notes.md
workspace/report/paper-experiment/implementation_notes.md
workspace/report/paper-experiment/validation_notes.md
```

## Outputs

Write:

```text
workspace/report/paper-experiment/final_model_summary.csv
workspace/report/paper-experiment/final_summary.md
```

## Workflow

1. Read requirements and contract.
2. Read baseline inventory and rewrite plans.
3. Read input adapter plan.
4. Read implementation manifest.
5. Read validation and profiling results.
6. Merge rows by model and dataset where applicable.
7. Preserve every baseline directory from `baseline_inventory.csv`.
8. Preserve dropped and skipped models.
9. Preserve adapter details.
10. Preserve preprocessing and pretrained-weight requirements.
11. Preserve validation failures and blocker reasons.
12. Preserve profiler failures and unsupported metrics.
13. Preserve launch commands for implemented models.
14. Derive final status using the rules below.
15. Write `final_model_summary.csv`.
16. Write `final_summary.md`.

## Final Status Values

Use exactly one:

```text
DONE
DONE_WITH_ADAPTER
DONE_WITH_PREPROCESS
DONE_WITH_PRETRAIN_REQUIRED
SKIPPED_EMPTY
SKIPPED_NON_PYTHON
SKIPPED_NON_PYTORCH
SKIPPED_INCOMPATIBLE
BLOCKED_NEEDS_USER_INPUT
FAILED_VALIDATION
FAILED_REWRITE
UNKNOWN
```

Status derivation:

```text
DONE:
  Implemented, validation passed, required profiling completed, no adapter/preprocess/pretrain special status.

DONE_WITH_ADAPTER:
  Implemented and validation passed using an input adapter.

DONE_WITH_PREPROCESS:
  Implemented and validation passed with explicit preprocessing requirement.

DONE_WITH_PRETRAIN_REQUIRED:
  Implementation exists but pretrained weights are required. Use only if validation is blocked by missing user-provided weights or the workflow policy defines this as acceptable.

SKIPPED_EMPTY:
  Stage 3 status DROP_EMPTY.

SKIPPED_NON_PYTHON:
  Stage 3 status DROP_NON_PYTHON.

SKIPPED_NON_PYTORCH:
  Stage 3 status DROP_NON_PYTORCH.

SKIPPED_INCOMPATIBLE:
  Stage 3 status DROP_INCOMPATIBLE.

BLOCKED_NEEDS_USER_INPUT:
  A required path, weight, policy decision, auth/access setup, or clarification is missing.

FAILED_VALIDATION:
  Implementation exists but Stage 5 validation failed.

FAILED_REWRITE:
  Stage 4 attempted implementation and failed.

UNKNOWN:
  Evidence remains insufficient and should be reviewed by integrity reviewer.
```

## Final CSV

Write `final_model_summary.csv` with this exact header:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

Field rules:

- `drop_reason` must be non-empty for skipped models.
- `adapter_type` must be non-empty for `DONE_WITH_ADAPTER`.
- `original_input_shape` and `adapted_input_shape` must be non-empty when an adapter is used.
- `shape_test` must be `PASS`, `FAIL`, `BLOCKED`, `SKIPPED`, or `NOT_RUN`.
- `smoke_train` must be `PASS`, `FAIL`, `BLOCKED`, `SKIPPED`, or `NOT_RUN`.
- `profile_done` must be `YES`, `NO`, `PARTIAL`, `BLOCKED`, or `SKIPPED`.
- `params` and `trainable_params` must be copied from `model_profile.csv` or recorded as `NOT_RUN`.
- `flops` and `macs` must be copied from `model_profile.csv`, `NOT_SUPPORTED`, `FAILED`, or `NOT_RUN`.
- Completed models must include `validate_command`, `smoke_train_command`, and `profile_command` unless a specific mode is not supported and recorded.

## Summary Format

Write `final_summary.md`:

```markdown
## STATUS
STATUS: [READY or PARTIAL or BLOCKED or FAILED]

## Counts
- Total Baselines:
- Completed:
- Completed With Adapter:
- Completed With Preprocess:
- Completed With Pretrain Required:
- Skipped Empty:
- Skipped Non-Python:
- Skipped Non-PyTorch:
- Skipped Incompatible:
- Failed Validation:
- Failed Rewrite:
- Blocked:
- Unknown:

## Contract Summary
- Original Repo:
- Launch Script:
- Launch Command:
- Dataset Policy:
- Split Policy:
- Metric Policy:
- Training Policy:
- Input Compatibility Policy:
- Model Architecture Change Policy:

## Completed Models
| Model | Adapter | Shape Test | Smoke Train | Params | MACs |
|---|---|---|---|---|---|

## Skipped Or Failed Models
| Model | Status | Reason |
|---|---|---|

## Commands
| Model | Validate | Smoke Train | Profile |
|---|---|---|---|

## Output Paths
- Final CSV:
- Baseline Inventory:
- Rewrite Plan:
- Input Adapter Plan:
- Implementation Manifest:
- Validation Results:
- Model Profile:

## Integrity Reviewer Notes
- [Known issue or None]
```

## Strict Rules

- Do not invent successful validation results.
- Do not invent profiling results.
- Do not hide skipped, failed, blocked, or unknown models.
- Do not merge incompatible models into `DONE`.
- Do not omit launch commands for completed models.
- Do not omit adapter information when an adapter was used.
- Do not omit original/adapted input shape when an adapter was used.
- Do not mark FLOPs or MACs as complete when profiler failed.
- Do not omit drop reasons.
- Do not write publication performance tables.
- Do not claim full experiment completion.

## Failure Routing Guidance

```text
Missing required upstream artifact -> target the stage that should produce it
Bad final CSV merge or schema -> Stage 6 Report Writer
Bad validation/profile source data -> Stage 5 Minimal Validation Profiler
Bad implementation manifest -> Stage 4 Rewrite Executor
Bad triage/adapter plan -> Stage 3 Baseline Triage Planner
Bad transfer readiness assumption -> Stage 2 Baseline Transfer Readiness Checker
Bad original contract -> Stage 1 Scope Contract Locker
Missing user policy/path -> Stage 0 Requirement Collector
```
