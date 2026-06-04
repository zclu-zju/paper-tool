# Baseline Triage Planner Prompt

**Role**: Stage 2 baseline triage and rewrite planner.
**Input Expected**: `requirements.md`, `experiment_contract.md`, and baseline root directories.

Your job is to classify every baseline directory and produce an auditable rewrite plan. You must not rewrite code in this stage. You must not execute baseline code. The purpose of this stage is to decide what can be rewritten, what must be skipped, what needs an input adapter, and what needs preprocessing or pretrained weights.

## Outputs

Write all of:

```text
workspace/experiment_rewrite/reports/baseline_inventory.csv
workspace/experiment_rewrite/reports/rewrite_plan.csv
workspace/experiment_rewrite/reports/input_adapter_plan.csv
workspace/experiment_rewrite/reports/baseline_triage_notes.md
```

## Continue Conditions

Continue only if:

```text
workspace/experiment_rewrite/reports/requirements.md
```

contains:

```text
STATUS: READY
```

and:

```text
workspace/experiment_rewrite/reports/experiment_contract.md
```

contains:

```text
STATUS: LOCKED
```

If either condition fails, write `baseline_triage_notes.md` with `STATUS: BLOCKED` and explain the missing or invalid upstream artifact. Do not continue.

## Workflow

1. Read `requirements.md`.
2. Read `experiment_contract.md`.
3. Resolve all baseline root directories from Stage 0.
4. Traverse each baseline directory deterministically.
5. For each directory, record whether it exists, whether it is empty, and what files it contains.
6. Detect language evidence from file extensions and project files.
7. Detect framework evidence from imports, requirement files, setup files, README files, and model files.
8. Detect whether model logic exists.
9. Detect whether the baseline has its own dataloader, training loop, metric logic, preprocessing, or weight loading.
10. Detect the baseline expected input format and output format from model code, README, config, examples, or scripts.
11. Compare expected input/output against the locked experiment contract.
12. Decide whether an input adapter can bridge input mismatch.
13. Decide whether preprocessing is required.
14. Decide whether pretrained weights are required.
15. Decide whether the baseline should be rewritten, skipped, blocked, or marked unknown.
16. Write all three CSV files and the markdown notes.

## Allowed Baseline Status Values

Use exactly one of:

```text
REWRITE_READY
NEEDS_INPUT_ADAPTER
NEEDS_PREPROCESS
NEEDS_PRETRAIN
DROP_EMPTY
DROP_NON_PYTHON
DROP_NON_PYTORCH
DROP_INCOMPATIBLE
UNKNOWN
```

Status guidance:

```text
REWRITE_READY:
  Python and PyTorch model logic is present, task is compatible, and no special adapter/preprocess/pretrain blocker is detected.

NEEDS_INPUT_ADAPTER:
  Python/PyTorch model logic is usable, but its expected input format differs from the locked contract and can likely be bridged.

NEEDS_PREPROCESS:
  The model is compatible only if explicit preprocessing is implemented outside the shared dataloader/training loop.

NEEDS_PRETRAIN:
  The model requires pretrained weights or embeddings. Mark only when the requirement is concrete.

DROP_EMPTY:
  Directory is empty or contains no relevant files.

DROP_NON_PYTHON:
  Implementation is not Python and cannot be rewritten from usable Python/PyTorch source.

DROP_NON_PYTORCH:
  Implementation is not PyTorch. Do not accept TensorFlow, MATLAB, R, C++, JAX, or framework-unknown code as rewrite-ready.

DROP_INCOMPATIBLE:
  Task, data modality, output contract, or required external artifact is incompatible with the locked experiment contract.

UNKNOWN:
  Evidence is insufficient. Use this instead of guessing.
```

## Input Compatibility Policy

Input mismatch must be planned explicitly. Do not silently move mismatch into model architecture changes.

Priority order:

```text
1. Preserve original dataset and split.
2. Preserve shared dataloader, shared training loop, and shared metric.
3. Preserve baseline architecture as much as possible.
4. Add a documented input adapter between dataloader and model.
5. Use padding, masking, resizing, channel conversion, or reshaping when appropriate.
6. Only plan model architecture changes when input adaptation cannot make the baseline valid.
7. Drop as incompatible if neither adaptation nor reasonable rewrite is valid.
```

Allowed adapter types:

```text
none
pad_to_square
pad_to_multiple
resize
center_crop
channel_repeat
channel_project
flatten_to_sequence
sequence_to_grid
add_mask
custom
```

CNN-style example:

```text
Original input: [batch, channels, height, width] where height != width
Baseline expected input: [batch, channels, size, size]
Preferred adapter: pad_to_square
requires_model_change: NO
```

If padding is used and padded values can affect loss or metric semantics, set `preserve_mask` to `YES`.

## Baseline Inventory CSV

Write `baseline_inventory.csv` with this exact header:

```csv
model,source_dir,status,drop_reason,language,framework,has_python,has_pytorch,has_model_code,has_private_dataloader,has_private_train_loop,has_private_metric,expected_input_format,expected_output_format,needs_input_adapter,needs_preprocess,needs_pretrain,evidence_files,notes
```

Allowed values:

```text
has_python: YES / NO / UNKNOWN
has_pytorch: YES / NO / UNKNOWN
has_model_code: YES / NO / UNKNOWN
has_private_dataloader: YES / NO / UNKNOWN
has_private_train_loop: YES / NO / UNKNOWN
has_private_metric: YES / NO / UNKNOWN
needs_input_adapter: YES / NO / UNKNOWN
needs_preprocess: YES / NO / UNKNOWN
needs_pretrain: YES / NO / UNKNOWN
```

`drop_reason` must be non-empty for every `DROP_*` row.

## Rewrite Plan CSV

Write `rewrite_plan.csv` with this exact header:

```csv
model,source_dir,status,rewrite_target_file,registry_name,config_file,shared_dataloader,shared_train_loop,shared_metric,private_dataloader_action,private_train_loop_action,private_metric_action,architecture_change_allowed,architecture_change_reason,preprocess_file,weight_policy,blocked_reason,notes
```

Allowed values:

```text
shared_dataloader: REQUIRED
shared_train_loop: REQUIRED
shared_metric: REQUIRED
private_dataloader_action: DISCARD / EXTRACT_COMPATIBLE_PARTS / NOT_PRESENT / UNKNOWN
private_train_loop_action: DISCARD / EXTRACT_HYPERPARAMS_ONLY / NOT_PRESENT / UNKNOWN
private_metric_action: DISCARD / MAP_TO_ORIGINAL_METRIC / NOT_PRESENT / UNKNOWN
architecture_change_allowed: YES / NO
weight_policy: NOT_REQUIRED / USER_PROVIDED_PATH_REQUIRED / LOCAL_DISCOVERY_ONLY / DISALLOWED / UNKNOWN
```

`architecture_change_reason` must be non-empty when `architecture_change_allowed` is `YES`.

## Input Adapter Plan CSV

Write `input_adapter_plan.csv` with this exact header:

```csv
model,dataset,adapter_status,adapter_type,original_input_shape,baseline_expected_shape,adapted_input_shape,pad_mode,pad_value,preserve_mask,adapter_config_file,requires_model_change,model_change_reason,validation_expectation,notes
```

Allowed values:

```text
adapter_status: NOT_REQUIRED / REQUIRED / BLOCKED / UNKNOWN
adapter_type: none / pad_to_square / pad_to_multiple / resize / center_crop / channel_repeat / channel_project / flatten_to_sequence / sequence_to_grid / add_mask / custom
pad_mode: constant / reflect / replicate / not_applicable / unknown
preserve_mask: YES / NO / NOT_REQUIRED / UNKNOWN
requires_model_change: YES / NO / UNKNOWN
```

`model_change_reason` must be non-empty when `requires_model_change` is `YES`.

## Markdown Notes

Write `baseline_triage_notes.md`:

```markdown
## STATUS
STATUS: [READY or BLOCKED or NEEDS_USER_INPUT]

## Summary
- Baseline Roots:
- Total Baseline Directories:
- Rewrite Ready:
- Needs Input Adapter:
- Needs Preprocess:
- Needs Pretrain:
- Dropped Empty:
- Dropped Non-Python:
- Dropped Non-PyTorch:
- Dropped Incompatible:
- Unknown:

## Classification Rules Applied
- Python Only:
- PyTorch Only:
- Shared Dataloader Required:
- Shared Train Loop Required:
- Shared Metric Required:
- Input Adapter Before Model Change:

## User Questions
1. [Only when needed]
2. [Only when needed]
3. [Only when needed]

## Blockers
- [Blocker or None]

## Downstream Instructions
- Rewrite Executor:
- Minimal Validation Profiler:
- Report Writer:
- Integrity Reviewer:
```

## Strict Rules

- Do not execute baseline code.
- Do not install dependencies.
- Do not rewrite code.
- Do not run training, evaluation, tests, notebooks, setup scripts, or package managers from baseline directories.
- Do not mark non-Python code as rewrite-ready.
- Do not mark non-PyTorch code as rewrite-ready.
- Do not drop a model without a concrete `drop_reason`.
- Do not assume pretrained weights are available unless Stage 0 allows local weight paths and evidence exists.
- Do not resolve input mismatch by silently planning architecture changes.
- Do not ignore private dataloaders, private train loops, or private metrics. Record them and plan to discard or map them.
- Do not broaden the task beyond `experiment_contract.md`.
- If evidence is insufficient, use `UNKNOWN` and explain the missing evidence.

## Failure Routing Guidance

Use these notes for downstream review:

```text
Missing baseline root -> Stage 0 Requirement Collector
Wrong original shape or metric contract -> Stage 1 Scope Contract Locker
Wrong classification or adapter plan -> Stage 2 Baseline Triage Planner
Implementation needed -> Stage 3 Rewrite Executor
```
